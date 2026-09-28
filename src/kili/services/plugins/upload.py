"""Class to upload a plugin."""

import ast
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union
from zipfile import ZipFile

from typing_extensions import LiteralString

from kili.adapters.http_client import HttpClient
from kili.core.constants import (
    mime_extensions_for_py_scripts,
    mime_extensions_for_txt_files,
)
from kili.core.graphql.operations.plugin.mutations import (
    GQL_CREATE_PLUGIN,
    GQL_CREATE_PLUGIN_RUNNER,
    GQL_CREATE_WEBHOOK,
    GQL_GENERATE_UPDATE_URL,
    GQL_UPDATE_PLUGIN_RUNNER,
    GQL_UPDATE_WEBHOOK,
)
from kili.core.graphql.operations.plugin.queries import GQL_GET_PLUGIN_RUNNER_STATUS
from kili.core.helpers import get_mime_type
from kili.services.plugins.tools import check_errors_plugin_upload
from kili.utils import bucket
from kili.utils.tempfile import TemporaryDirectory

from .exceptions import PluginCreationError
from .helpers import get_logger

if TYPE_CHECKING:
    from kili.client import Kili

NUMBER_TRIES_RUNNER_STATUS = 20

POSSIBLE_HANDLERS = {
    "on_submit": "onSubmit",
    "on_review": "onReview",
    "on_custom_interface_click": "onCustomInterfaceClick",
    "on_send_back_to_queue": "onSendBackToQueue",
}

DECORATOR_NAME = "on_kili_event"
DECORATOR_MODULES = ("kili.plugins", "kili.services.plugins.events")


def check_file_mime_type(
    path: Path, compatible_mime_extensions: list[str], verbose: bool = True
) -> bool:
    """Returns true if the mime type of the file corresponds to one of compatible_mime_extensions."""
    mime_type = get_mime_type(path.as_posix())

    if not compatible_mime_extensions or mime_type is None:
        return False

    correct_mime_type = mime_type in compatible_mime_extensions

    if verbose and not correct_mime_type:
        print(
            f"File mime type for {path} is {mime_type} and does not correspond"
            "to the type of the project. "
            f"File mime type should be one of {compatible_mime_extensions}"
        )
    return correct_mime_type


def check_file_is_py(path: Path, verbose: bool = True) -> bool:
    """Returns true if the mime type of the file corresponds to a python file."""
    return check_file_mime_type(path, mime_extensions_for_py_scripts, verbose)


def check_file_is_txt(path: Path, verbose: bool = True) -> bool:
    """Returns true if the mime type of the file corresponds to a .txt file."""
    return check_file_mime_type(path, mime_extensions_for_txt_files, verbose)


def check_file_contains_handler(path: Path) -> tuple[bool, Optional[list[str]], bool]:
    """Test if the file is a python file with the right content.

    Return true if the file contain PluginHandler Class.
    Return the list of handlers or None if they are present in the file.
    Return true if the file contains on_event method.
    """
    with path.open(encoding="utf-8") as file:
        module = ast.parse(file.read())
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "PluginHandler":
            handlers = [
                POSSIBLE_HANDLERS[child.name]
                for child in node.body
                if isinstance(child, ast.FunctionDef) and child.name in POSSIBLE_HANDLERS
            ]
            has_on_event = any(
                isinstance(child, ast.FunctionDef) and child.name == "on_event"
                for child in node.body
            )
            return (True, handlers, has_on_event) if handlers else (True, None, has_on_event)
    return False, None, False


class _ImportedNames:
    """What the imports of a plugin file bind the decorator and the kili_events names to."""

    def __init__(self, module: ast.Module) -> None:
        self.decorators: set[str] = set()
        self.events: dict[str, str] = {}
        self.event_modules: set[str] = set()
        for node in ast.walk(module):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    local_name = alias.asname or alias.name
                    if node.module in DECORATOR_MODULES and alias.name == DECORATOR_NAME:
                        self.decorators.add(local_name)
                    elif node.module == "kili" and alias.name == "plugins":
                        self.decorators.add(f"{local_name}.{DECORATOR_NAME}")
                    elif node.module == "kili_events":
                        self.events[local_name] = alias.name
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in DECORATOR_MODULES:
                        self.decorators.add(f"{alias.asname or alias.name}.{DECORATOR_NAME}")
                    elif alias.name == "kili_events":
                        self.event_modules.add(alias.asname or alias.name)

    def event_name(self, argument: ast.expr) -> Optional[str]:
        """The kili_events name an argument refers to, if it is one."""
        if isinstance(argument, ast.Name):
            return self.events.get(argument.id)
        if (
            isinstance(argument, ast.Attribute)
            and isinstance(argument.value, ast.Name)
            and argument.value.id in self.event_modules
        ):
            return argument.attr
        return None


def _argument_patterns(argument: ast.expr, names: _ImportedNames) -> list[str]:
    """The patterns one argument of @on_kili_event subscribes to, read without running it."""
    # Imported here, not at the top: kili_events loads a pydantic model per event, which only
    # a plugin upload needs — not every `import kili`.
    import kili_events  # pylint: disable=import-outside-toplevel

    from kili.services.plugins.events import (  # pylint: disable=import-outside-toplevel
        event_patterns,
    )

    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
        patterns = event_patterns(argument.value)
        if not kili_events.events_matching(argument.value):
            raise ValueError(f"'{argument.value}' matches no Kili event. Is there a typo?")
        return list(patterns)

    event_name = names.event_name(argument)
    event = getattr(kili_events, event_name, None) if event_name else None
    if event is None:
        raise ValueError(
            f"'{ast.unparse(argument)}' is not a kili_events name, so the events it stands for"
            " cannot be read from the plugin's code. Pass a model or a family imported from"
            " kili_events (AssetSkippedEvent, AssetWorkflowEvent), or a pattern string"
            " ('label.workflow.*')."
        )
    return list(event_patterns(event))


def find_event_subscriptions(path: Path) -> dict[str, list[str]]:
    """Return the patterns each method of PluginHandler subscribes to with @on_kili_event.

    The plugin's code is read, never run: the arguments must be kili_events names or strings.
    """
    with path.open(encoding="utf-8") as file:
        module = ast.parse(file.read())
    names = _ImportedNames(module)
    subscriptions: dict[str, list[str]] = {}
    for node in module.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "PluginHandler"):
            continue
        for method in node.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            for decorator in method.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                if ast.unparse(target) not in names.decorators:
                    continue
                if not isinstance(decorator, ast.Call) or not decorator.args:
                    raise ValueError(
                        f"PluginHandler.{method.name}: @{DECORATOR_NAME} needs the events to"
                        f" receive, e.g. @{DECORATOR_NAME}(AssetSkippedEvent)."
                    )
                try:
                    patterns = [
                        pattern
                        for argument in decorator.args
                        for pattern in _argument_patterns(argument, names)
                    ]
                except (TypeError, ValueError) as error:
                    raise ValueError(f"PluginHandler.{method.name}: {error}") from error
                subscriptions.setdefault(method.name, []).extend(patterns)
    return subscriptions


class WebhookUploader:
    """Class to create a webhook."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        kili: "Kili",
        webhook_url: str,
        plugin_name: str,
        header: Optional[str],
        verbose: bool,
        handler_types: Optional[list[str]],
        event_matcher: Optional[list[str]],
    ) -> None:
        self.kili = kili
        self.webhook_url = webhook_url
        self.plugin_name = plugin_name or self.webhook_url
        self.header = header
        self.verbose = verbose
        self.handler_types = handler_types
        self.event_matcher = event_matcher

    def create_webhook(self) -> str:
        """Create a webhook receiving Kili events."""
        variables = {
            "eventMatcher": self.event_matcher,
            "handlerTypes": self.handler_types,
            "pluginName": self.plugin_name,
            "webhookUrl": self.webhook_url,
            "header": self.header,
        }

        result = self.kili.graphql_client.execute(GQL_CREATE_WEBHOOK, variables)

        return self.kili.format_result("data", result)

    def update_webhook(self) -> str:
        """Update a webhook receiving Kili events."""
        variables = {
            "eventMatcher": self.event_matcher,
            "handlerTypes": self.handler_types,
            "pluginName": self.plugin_name,
            "webhookUrl": self.webhook_url,
            "header": self.header,
        }

        result = self.kili.graphql_client.execute(GQL_UPDATE_WEBHOOK, variables)

        return self.kili.format_result("data", result)


class PluginUploader:
    """Class to upload a plugin."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        kili: "Kili",
        plugin_path: str,
        plugin_name: Optional[str],
        verbose: bool,
        http_client: HttpClient,
        event_matcher: Optional[list[str]],
    ) -> None:
        self.kili = kili
        self.plugin_path = Path(plugin_path)
        self.http_client = http_client
        self.event_matcher = event_matcher

        if (not self.plugin_path.is_dir()) and (not self.plugin_path.is_file()):
            raise FileNotFoundError(
                f"The provided path '{plugin_path}' is neither a directory nor a file. The absolute"
                f" path is the following: '{self.plugin_path.absolute()}'"
            )

        if plugin_name:
            self.plugin_name = plugin_name
        else:
            self.plugin_name = self.plugin_path.name
        self.verbose = verbose
        self.handler_types = None

    def _retrieve_plugin_src(self) -> list[Path]:
        """Retrieve script from plugin_path and execute it to prevent an upload with indentation errors."""
        if self.plugin_path.is_dir():
            file_path = self.plugin_path / "main.py"
            if not file_path.is_file():
                raise FileNotFoundError(
                    f"No main.py file in the provided folder: {self.plugin_path.absolute()}"
                )
            self._check_handlers(
                file_path, "PluginHandler class is not present in your main.py file."
            )

            return list(self.plugin_path.glob("**/*.py"))

        file_path = self.plugin_path

        if not check_file_is_py(file_path, self.verbose):
            raise ValueError("Wrong file format.")

        self._check_handlers(file_path, "PluginHandler class is not present in your plugin file.")

        return [file_path]

    def _check_handlers(self, file_path: Path, no_plugin_handler_message: str) -> None:
        """Check how the plugin receives events, and set the handler types or event matcher."""
        contains_handler, handler_types, has_on_event = check_file_contains_handler(file_path)
        if not contains_handler:
            raise ValueError(no_plugin_handler_message)

        subscriptions = find_event_subscriptions(file_path)
        if subscriptions:
            if handler_types:
                raise ValueError(
                    "A plugin either implements on_submit, on_review, on_custom_interface_click"
                    " and on_send_back_to_queue, or subscribes to events with @on_kili_event:"
                    " not both."
                )
            if has_on_event:
                raise ValueError(
                    "on_event would stop the events reaching the methods decorated with"
                    " @on_kili_event: remove it from PluginHandler."
                )
            if self.event_matcher:
                raise ValueError(
                    "The events come from the @on_kili_event decorators: upload without"
                    " event_matcher."
                )
            self.event_matcher = sorted(
                {pattern for patterns in subscriptions.values() for pattern in patterns}
            )
        elif has_on_event:
            if not self.event_matcher:
                raise ValueError("Event matcher is required for plugins with on_event method.")
            get_logger().warning(
                "Overriding on_event is deprecated: decorate methods with @on_kili_event to"
                " receive typed events. on_event now receives the whole event: the fields it"
                " read are under payload['payload']."
            )

        if handler_types and self.event_matcher:
            raise ValueError("Cannot have both handler types and event matcher.")

        self.handler_types = handler_types

    def _retrieve_requirements(self) -> Union[Path, None]:
        """Retrieve script from file_path and execute it to prevent an upload with indentation errors."""
        if not self.plugin_path.is_dir():
            return None

        file_path = self.plugin_path / "requirements.txt"
        if not file_path.is_file():
            logger = get_logger()
            logger.info(
                f"No requirements.txt file in the provided folder: {self.plugin_path.absolute()}"
            )
            return None

        if not check_file_is_txt(file_path, self.verbose):
            raise ValueError("Wrong file format.")

        return file_path

    @staticmethod
    def _parse_script(script_path: Path) -> None:
        """Method to detect indentation and class errors in the script."""
        with script_path.open("r", encoding="utf-8") as file:
            source_code = file.read()

        # We execute the source code to prevent the upload of a file with SyntaxError
        compile(source_code, "<string>", "exec")

    @staticmethod
    def _upload_file(zip_path: Path, url: str, http_client: HttpClient) -> None:
        """Upload a file to a signed url and returns the url with the file_id."""
        bucket.upload_data_via_rest(url, zip_path.read_bytes(), "application/zip", http_client)

    def _retrieve_upload_url(self, is_updating_plugin: bool) -> str:
        """Retrieve an upload url from the backend."""
        variables = {"pluginName": self.plugin_name}

        if is_updating_plugin:
            result = self.kili.graphql_client.execute(GQL_GENERATE_UPDATE_URL, variables)
        else:
            result = self.kili.graphql_client.execute(GQL_CREATE_PLUGIN, variables)

        check_errors_plugin_upload(result, self.plugin_path, self.plugin_name)
        return self.kili.format_result("data", result)

    def _create_zip(self, tmp_directory: Path) -> Path:
        """Create a zip file from python file and requirements.txt.

        (if user has defined a path to a requirements.txt)
        """
        file_paths = self._retrieve_plugin_src()

        for path in file_paths:
            self._parse_script(path)

        requirements_path = self._retrieve_requirements()

        zip_path = tmp_directory / "archive.zip"

        with ZipFile(zip_path, "w") as archive:
            if len(file_paths) == 1:
                archive.write(file_paths[0], "main.py")

            else:
                for path in file_paths:
                    archive.write(path, path.relative_to(self.plugin_path))

            if requirements_path:
                archive.write(requirements_path, requirements_path.relative_to(self.plugin_path))

        return zip_path

    def _upload_script(self, is_updating_plugin: bool) -> None:
        """Upload a script to Kili bucket."""
        with TemporaryDirectory() as tmp_directory:
            zip_path = self._create_zip(tmp_directory)

            upload_url = self._retrieve_upload_url(is_updating_plugin)

            self._upload_file(zip_path, upload_url, self.http_client)

    def _create_plugin_runner(self) -> Any:
        """Create plugin's runner."""
        variables = {
            "pluginName": self.plugin_name,
            "handlerTypes": self.handler_types,
            "eventMatcher": self.event_matcher,
        }

        result = self.kili.graphql_client.execute(GQL_CREATE_PLUGIN_RUNNER, variables)
        return self.kili.format_result("data", result)

    def _check_plugin_runner_status(self, update: bool = False) -> LiteralString:
        """Check the status of a plugin's runner until it is active."""
        logger = get_logger()

        action = "updated" if update else "created"

        logger.info(f"Plugin is being {action}... This should take few minutes.")

        n_tries = 0
        status = None

        while n_tries < NUMBER_TRIES_RUNNER_STATUS:
            time.sleep(15)

            status = self.get_plugin_runner_status()

            if status in ("ACTIVE", "FAILED"):
                break

            logger.info(f"Status : {status}...")

            n_tries += 1

        # this represents the case where the plugin is still deploying
        # after 150 tries (37.5 minutes)
        if status == "DEPLOYING" and n_tries == 150:
            raise RuntimeError(
                "We could not check your plugin was deployed in time. Please check again the"
                " status of the plugin after some minutes with the command:"
                f' kili.get_plugin_status("{self.plugin_name}"). If the status is different than'
                " DEPLOYING or ACTIVE, please check your plugin's code and try to overwrite the"
                " plugin with a new version of the code (you can use kili.update_plugin() for"
                " that)."
            )

        if status != "ACTIVE":
            raise PluginCreationError(
                "There was some error during the creation of the plugin. Please check your"
                " plugin's code and try to overwrite the plugin with a new version of the code"
                " (you can use kili.update_plugin() for that). Hint: You can get build errors"
                f' using: kili.get_plugin_build_errors(plugin_name="{self.plugin_name}")'
            )

        message = f"Plugin {action} successfully"
        logger.info(message)

        return message

    def get_plugin_runner_status(self) -> Any:
        """Get the status of a plugin's runner."""
        variables = {"name": self.plugin_name}

        result = self.kili.graphql_client.execute(GQL_GET_PLUGIN_RUNNER_STATUS, variables)

        return self.kili.format_result("data", result)

    def create_plugin(self):
        """Create a plugin in Kili."""
        self._upload_script(False)

        self._create_plugin_runner()

        return self._check_plugin_runner_status()

    def _update_plugin_runner(self) -> Any:
        """Update plugin's runner."""
        variables = {
            "pluginName": self.plugin_name,
            "handlerTypes": self.handler_types,
            "eventMatcher": self.event_matcher,
        }

        result = self.kili.graphql_client.execute(GQL_UPDATE_PLUGIN_RUNNER, variables)
        return self.kili.format_result("data", result)

    def update_plugin(self):
        """Update a plugin in Kili."""
        self._upload_script(True)

        self._update_plugin_runner()

        return self._check_plugin_runner_status(update=True)
