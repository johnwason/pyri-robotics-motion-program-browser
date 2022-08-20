from typing import List, Dict, Callable, Any, Tuple
from pyri.webui_browser.plugins.variable_dialog import PyriWebUIBrowserVariableDialogInfo, PyriWebUIBrowserVariableDialogPluginFactory, PyriWebUIBrowserVariableDialogBase
from pyri.webui_browser import PyriWebUIBrowser
from .new_motion_program_from_trajectory_dialog import show_new_motion_program_from_trajectory_dialog

_variable_dialog_infos = {
    ("experimental.robotics.motion_program.MotionProgram",("optimized_motion_program")): \
        PyriWebUIBrowserVariableDialogInfo(
            "robot_mp_from_trajectory",
            "Robot Motion Program From Trajectory",
            "experimental.robotics.motion_program.MotionProgram",
            ["optimized_motion_program"],
            "Create an optimized robot motion program from an arbitrary trajectory",
        ),
}

class PyriRobotMPWebUIBrowserVariableDialogPluginFactory(PyriWebUIBrowserVariableDialogPluginFactory):
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return "pyri-robotics-motion-program-browser"

    def get_variable_dialog_infos(self) -> Dict[Tuple[str,Tuple[str]],PyriWebUIBrowserVariableDialogInfo]:
        return _variable_dialog_infos

    def show_variable_new_dialog(self, new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser") -> None:
        if variable_type == "experimental.robotics.motion_program.MotionProgram" and "optimized_motion_program" in variable_tags:
            show_new_motion_program_from_trajectory_dialog(new_name, variable_type, variable_tags, core)
            return
        assert False, "Invalid new variable dialog type requested"

    def show_variable_edit_dialog(self, variable_name: str, variable_type: str, variable_tags: List[str], core: "PyriWebUIBrowser") -> None:
        raise NotImplementedError()

def get_webui_browser_variable_dialog_factory():
    return PyriRobotMPWebUIBrowserVariableDialogPluginFactory()