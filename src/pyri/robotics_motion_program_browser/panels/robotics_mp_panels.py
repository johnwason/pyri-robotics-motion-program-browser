from typing import List, Dict, Callable, Any, Tuple
from pyri.webui_browser.plugins.panel import PyriWebUIBrowserPanelInfo, PyriWebUIBrowserPanelPluginFactory
from pyri.webui_browser.golden_layout import PyriGoldenLayoutPanelConfig

_panel_infos = {
    "motion_program_opt": PyriWebUIBrowserPanelInfo(
        title="Motion Program Opt",
        description="Motion program optimization algorithms",
        panel_type="motion_program_opt",
        panel_category = "robotics",
        component_type = "pyri-motion-program-opt",
        priority=5000
    )
}

_panel_default_configs = {
    "motion_program_opt": PyriGoldenLayoutPanelConfig(
        component_type=_panel_infos["motion_program_opt"].component_type,
        panel_id = "motion_program_opt",
        panel_title = "Motion Program Opt",
        closeable= False
    )
}

class MotionProgramOptWebUIBrowserPanelPluginFactory(PyriWebUIBrowserPanelPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return "pyri-robotics-motion-program-browser"

    def get_panels_infos(self) -> Dict[str,PyriWebUIBrowserPanelInfo]:
        return _panel_infos

    def get_default_panels(self, layout_config: str = "default") -> List[Tuple[PyriWebUIBrowserPanelInfo, "PyriGoldenLayoutPanelConfig"]]:
        if layout_config.lower() == "default":
            return [
                (_panel_infos["motion_program_opt"], _panel_default_configs["motion_program_opt"])
            ]
        else:
            return []
    

def get_webui_browser_panel_factory():
    return MotionProgramOptWebUIBrowserPanelPluginFactory()