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
import base64

def svg_to_data_url(svg_np):
    svg_b64 = base64.b64encode(bytearray(svg_np)).decode("ascii")

    return f"data:image/svg+xml;base64,{svg_b64}"

@VueComponent
class MotionProgramExecComponent(PyriVue):
    
    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_motion_program_execution_component.html")

    execution_state = vue_data("idle")

    plots = vue_data([])

    motion_program_global_name = vue_data("")
    nominal_curve_global_name = vue_data("")
    joint_log_global_name = vue_data("")
    plots_global_name = vue_data("")
    robot_mp_local_device_name = vue_data("robot")
    tool_mp_local_device_name = vue_data("tool")

    def __init__(self):
        super().__init__()
        self.mp_exec_gen = None

    @vue_method
    def run(self):
        
        self.execution_state = "running"
        self.core.create_task(self.exec_motion_program())
    
    @vue_method
    async def abort(self):
        self.execution_state = "done"
        if self.mp_exec_gen is not None:            
            await self.mp_exec_gen.AsyncAbort(None)            

    @vue_method
    def reset(self):
        self.execution_state = "idle"
        self.log.clear_output()
        self.plots = to_js2([])

    @property
    def log(self):
        return self.get_ref_pyobj("motion_program_exec_log")


    async def exec_motion_program(self):
        try:
            
            robot_name = self.robot_mp_local_device_name
            tool_name = self.tool_mp_local_device_name
            mp_name = self.motion_program_global_name

            input_parameters = {
                "joint_log_global_name": RR.VarValue(self.joint_log_global_name, "string"),
                "nominal_curve_global_name": RR.VarValue(self.nominal_curve_global_name, "string"),
                "plots_global_name": RR.VarValue(self.plots_global_name, "string"),                            
            }

            mp_opt_service = self.core.device_manager.get_device_subscription("robotics_mp_opt").GetDefaultClient()
            self.mp_exec_gen = await mp_opt_service.async_motion_program_exec(robot_name, tool_name, mp_name, input_parameters, None)
           
            while True:
                try:
                    res = await self.mp_exec_gen.AsyncNext(None,None)
                    if res.log_output:
                        self.log.append_output_lines(res.log_output)
                    
                    if res.plots:
                        try:
                            for plot_name,plot in res.plots.items():
                                self.plots.push(to_js2({
                                    "plot_name": plot_name,
                                    "plot_data_url": svg_to_data_url(plot)
                                }))

                        except:
                            js.alert(f"Error generating plots:\n\n{traceback.format_exc()}")

                except RR.StopIterationException:
                    break
        
        except:
            js.alert(f"Motion program execution failed:\n\n{traceback.format_exc()}")
        finally:
            self.execution_state = "done"
            self.mp_opt_gen = None

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-motion-program-execution', MotionProgramExecComponent)
