from pyri.webui_browser.plugins.component import PyriWebUIBrowserComponentPluginFactory
from .motion_program_opt_input_data_component import register_vue_components as input_data_register_vue_components
from .motion_program_opt_acc_data_component import register_vue_components as acc_data_register_vue_components
from .motion_program_opt_execution_component import register_vue_components as exec_register_vue_components
from .motion_program_opt_redundancy_resolution_component import register_vue_components as redun_data_register_vue_components
from .motion_program_opt_motion_program_execution_component import register_vue_components as mp_exec_register_vue_components
from .motion_program_opt_motion_program_generation_component import register_vue_components as mp_gen_register_vue_components
from .motion_program_opt_motion_program_update_component import register_vue_components as mp_update_register_vue_components
from .motion_program_opt_component import register_vue_components as mp_opt_register_vue_components


class PyriRoboticsMPComponentsWebUIBrowserComponentPluginFactory(PyriWebUIBrowserComponentPluginFactory):
    def get_plugin_name(self) -> str:
        return "pyri-robotics-mp-browser"

    def register_components(self) -> None:
        input_data_register_vue_components()
        acc_data_register_vue_components()
        exec_register_vue_components()
        redun_data_register_vue_components()
        mp_exec_register_vue_components()
        mp_gen_register_vue_components()
        mp_update_register_vue_components()
        mp_opt_register_vue_components()

def get_webui_browser_component_factory():
    return PyriRoboticsMPComponentsWebUIBrowserComponentPluginFactory()