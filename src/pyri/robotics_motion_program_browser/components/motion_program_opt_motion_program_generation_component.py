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

    total_seg = vue_data(100)
    velocity = vue_data(1)
    blend_radius = vue_data(0.05)
    motion_program_global_name = vue_data("")
    motion_program_parameters_global_name = vue_data("")

    def __init__(self):
        super().__init__()

    async def do_alg(self):
        try:

            curve_js = self.get_ref_pyobj("motion_program_generation_curve_js_file").get_sheet_data()
            print(f"total_seg: {self.total_seg}")
            input_parameters = {
                "curve_js": RR.VarValue(curve_js, "double[*]"),
                "total_seg": RR.VarValue(int(self.total_seg), "uint32"),
                "velocity": RR.VarValue(float(self.velocity), "double"),
                "blend_radius": RR.VarValue(float(self.blend_radius), "double"),
                "motion_program_global_name": RR.VarValue(self.motion_program_global_name, "string"),
                "motion_program_parameters_global_name": RR.VarValue(self.motion_program_parameters_global_name, "string"),                            
            }

                
        except:
            js.alert(f"Motion program parameter error:\n\n{traceback.format_exc()}")
            return
        finally:
            self.execution_state = "done"
            self.mp_opt_gen = None

        await self._do_alg_base("motion_program_generation", input_parameters)

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-motion-program-generation', MotionProgramGenerationComponent)
