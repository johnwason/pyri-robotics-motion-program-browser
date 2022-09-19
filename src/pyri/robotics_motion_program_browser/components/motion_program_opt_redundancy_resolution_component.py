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
class RedundancyResolutionComponent(MotionOptPage):
    
    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_redundancy_resolution_component.html")

    curve_global_name = vue_data("")
    curve_js_global_name = vue_data("")
    curve_base_global_name = vue_data("")
    curve_pose_global_name = vue_data("")
    plots_global_name = vue_data("")

    def __init__(self):
        super().__init__()

    async def do_alg(self):
        try:

            curve = self.get_ref_pyobj("redundancy_resolution_curve_file").get_sheet_data()
            input_parameters = {
                "curve": RR.VarValue(curve, "double[*]"),
                "curve_global_name": RR.VarValue(self.curve_global_name, "string"),
                "curve_js_global_name": RR.VarValue(self.curve_js_global_name, "string"),
                "curve_base_global_name": RR.VarValue(self.curve_base_global_name, "string"),
                "curve_pose_global_name": RR.VarValue(self.curve_pose_global_name, "string"),
                "plots_global_name": RR.VarValue(self.plots_global_name, "string")            
            }

                
        except:
            js.alert(f"Motion program parameter error:\n\n{traceback.format_exc()}")        
            self.execution_state = "done"
            self.mp_opt_gen = None
            return

        await self._do_alg_base("redundancy_resolution", input_parameters)

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-redundancy-resolution', RedundancyResolutionComponent)