from kili.plugins import PluginCore


class PluginHandler(PluginCore):
    def on_event(self, payload: dict) -> None:
        super().on_event(payload=payload)
