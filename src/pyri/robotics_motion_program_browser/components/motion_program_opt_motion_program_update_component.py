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
class MotionProgramUpdateComponent(MotionOptPage):
    
    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_motion_program_update_component.html")

    motion_program_global_name = vue_data("")
    motion_program_parameters_global_name = vue_data("")
    robot_local_device_name = vue_data("robot")
    tool_local_device_name = vue_data("tool")
    tool_surface_offset = vue_data("")
    velocity = vue_data(0.1)
    blend_radius = vue_data(0.1)
    mp_gen_params = vue_data("")
    error_tol = vue_data(0.5)
    angerr_tol = vue_data(3.0)
    velstd_tol = vue_data(5.0)
    iter_max = vue_data(100)
    ext_start = vue_data(100)
    ext_end = vue_data(100)
    real_robot = vue_data(False)

    def __init__(self):
        super().__init__()

    async def do_alg(self):
        try:

            curve_base = self.get_ref_pyobj("motion_program_update_curve_base_file").get_sheet_data()
            acc_data = await self.get_ref_pyobj("motion_program_update_acc_data").read_acc_file()
            input_parameters = {
                "curve_base": RR.VarValue(curve_base, "double[*]"),
                "robot_local_device_name": RR.VarValue(self.robot_local_device_name, "string"),
                "robot_acc_data": RR.VarValue(np.array(acc_data, dtype=np.uint8),"uint8"),
                "tool_local_device_name": RR.VarValue(self.tool_local_device_name, "string"),
                "motion_program_global_name": RR.VarValue(self.motion_program_global_name, "string"),
                "motion_program_parameters_global_name": RR.VarValue(self.motion_program_parameters_global_name, "string"),
                "tool_surface_offset": RR.VarValue(float(self.tool_surface_offset), "double"),                          
                "mp_gen_params": RR.VarValue(self.mp_gen_params, "string"),
                "velocity": RR.VarValue(float(self.velocity), "double"),
                "blend_radius": RR.VarValue(float(self.blend_radius), "double"),
                "error_tol": RR.VarValue(float(self.error_tol), "double"),
                "angerr_tol": RR.VarValue(float(self.angerr_tol), "double"),
                "velstd_tol": RR.VarValue(float(self.velstd_tol), "double"),
                "iter_max": RR.VarValue(int(self.iter_max), "int32"),
                "ext_start": RR.VarValue(int(self.ext_start), "int32"),
                "ext_end": RR.VarValue(int(self.ext_end), "int32"),
                "real_robot": RR.VarValue(bool(self.real_robot), "bool"),
            }

                
        except:
            js.alert(f"Motion program parameter error:\n\n{traceback.format_exc()}")
            self.execution_state = "done"
            self.mp_opt_gen = None
            return

        await self._do_alg_base("motion_program_update", input_parameters)

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-motion-program-update', MotionProgramUpdateComponent)
