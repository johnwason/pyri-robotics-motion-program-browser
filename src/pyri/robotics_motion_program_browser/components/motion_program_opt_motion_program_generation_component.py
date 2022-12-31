import asyncio
from typing import List, Dict, Callable, Any

import importlib_resources
from pyri.webui_browser.util import to_js2
import js
from RobotRaconteur.Client import *
import traceback
import numpy as np
import io
from pyri.webui_browser.pyri_vue import PyriVue, VueComponent, vue_method, vue_data, vue_prop, vue_register_component
from .motion_opt_page import MotionOptPage

@VueComponent
class MotionProgramGenerationComponent(MotionOptPage):
    
    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_motion_program_generation_component.html")

    greedy_threshold = vue_data(0.1)
    velocity = vue_data(0.1)
    blend_radius = vue_data(0.05)
    motion_program_global_name = vue_data("")
    motion_program_parameters_global_name = vue_data("")
    robot_local_device_name = vue_data("robot")
    tool_local_device_name = vue_data("tool")
    tool_surface_offset = vue_data("")

    def __init__(self):
        super().__init__()

    async def do_alg(self):
        try:

            curve_js = self.get_ref_pyobj("motion_program_generation_curve_js_file").get_sheet_data()
            acc_data = await self.get_ref_pyobj("motion_program_gen_acc_data").read_acc_file()
            input_parameters = {
                "curve_js": RR.VarValue(curve_js, "double[*]"),
                "greedy_threshold": RR.VarValue(float(self.greedy_threshold), "double"),
                "velocity": RR.VarValue(float(self.velocity), "double"),
                "blend_radius": RR.VarValue(float(self.blend_radius), "double"),
                "robot_local_device_name": RR.VarValue(self.robot_local_device_name, "string"),
                "robot_acc_data": RR.VarValue(np.array(acc_data, dtype=np.uint8),"uint8"),
                "tool_local_device_name": RR.VarValue(self.tool_local_device_name, "string"),
                "motion_program_global_name": RR.VarValue(self.motion_program_global_name, "string"),
                "motion_program_parameters_global_name": RR.VarValue(self.motion_program_parameters_global_name, "string"),
                "tool_surface_offset": RR.VarValue(float(self.tool_surface_offset), "double"),                          
            }

                
        except:
            js.alert(f"Motion program parameter error:\n\n{traceback.format_exc()}")
            self.execution_state = "done"
            self.mp_opt_gen = None
            return

        await self._do_alg_base("motion_program_generation", input_parameters)

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-motion-program-generation', MotionProgramGenerationComponent)
