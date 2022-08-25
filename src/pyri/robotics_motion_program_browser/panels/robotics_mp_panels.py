from typing import List, Dict, Callable, Any
from pyri.webui_browser.plugins.panel import PyriWebUIBrowserPanelInfo, PyriWebUIBrowserPanelPluginFactory, PyriWebUIBrowserPanelBase
from pyri.webui_browser import PyriWebUIBrowser
from .motion_program_opt_panel import add_motion_program_opt_panel

_panel_infos = {
    "motion_program_opt": PyriWebUIBrowserPanelInfo(
        title="Motion Program Opt",
        panel_type="motion_program_opt",
        priority=5000
    )
}

class MotionProgramOptWebUIBrowserPanelPluginFactory(PyriWebUIBrowserPanelPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return "pyri-robotics-motion-program-opt"

    def get_panels_infos(self) -> Dict[str,PyriWebUIBrowserPanelInfo]:
        return _panel_infos

    async def add_panel(self, panel_type: str, core: PyriWebUIBrowser, parent_element: Any) -> PyriWebUIBrowserPanelBase:
        if panel_type == "motion_program_opt":
            return await add_motion_program_opt_panel(panel_type, core, parent_element)
        assert False, f"Unknown panel_type \"{panel_type}\" specified"

def get_webui_browser_panel_factory():
    return MotionProgramOptWebUIBrowserPanelPluginFactory()