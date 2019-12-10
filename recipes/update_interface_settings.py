import getpass
import json

from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground

email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')


with open('./conf/new_interface_settings.json', 'r') as f:
    interface_settings = json.load(f)

kauth = KiliAuth(email=email, password=password)
playground = Playground(kauth)

tools = playground.get_tools(project_id=project_id)

assert len(tools) == 1
tool_id = tools[0]['id']
name = tools[0]['name']
tool_type = tools[0]['toolType']

playground.update_tool(tool_id=tool_id, project_id=project_id, name=name, tool_type=tool_type,
                       json_settings=interface_settings)
