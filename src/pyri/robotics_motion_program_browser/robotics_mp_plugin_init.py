from typing import List, Dict, Callable, Any, NamedTuple, TYPE_CHECKING, Tuple, Awaitable
from pyri.webui_browser.plugins.plugin_init import PyriWebUIPluginInitFactory

async def plugin_init(core):
    core.device_manager.connect_device("robotics_mp_opt")

    await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.js")
    await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.css")
    await core.js_loader.load_js_src("https://unpkg.com/xlsx@0.13.0/xlsx.js")
    await core.js_loader.load_js_src("/plugins/pyri-robotics-motion-program/xlsxspread.js")

class PyriRoboticsMPWebUIPluginFactory(PyriWebUIPluginInitFactory):

    def get_plugin_name(self) -> str:
        return "pyri-robotics-motion-program-browser"

    def get_plugin_init(self) -> Tuple[Callable[["PyriWebUIBrowser"], Awaitable], List[str]]:
        return plugin_init, []

def get_webui_browser_plugin_init_factory():
    return PyriRoboticsMPWebUIPluginFactory()