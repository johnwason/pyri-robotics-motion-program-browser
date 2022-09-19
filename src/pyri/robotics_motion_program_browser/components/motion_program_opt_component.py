import asyncio
from typing import List, Dict, Callable, Any

import importlib_resources
from pyri.webui_browser.util import to_js2
import js
from RobotRaconteur.Client import *
import traceback

from pyri.webui_browser.pyri_vue import PyriVue, VueComponent, vue_method, vue_data, vue_watch, vue_register_component

@VueComponent
class MotionOptComponent(PyriVue):

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_component.html")

    def __init__(self):
        super().__init__()
        
    op_selected = vue_data("redundancy_resolution")
    
    redundancy_resolution_curve_js_output_variable = vue_data("")

    @vue_watch("op_selected")
    async def op_selected_watch(self, *args):
        await self.next_tick()
        await asyncio.sleep(0.05)
        js.window.dispatchEvent(js.Event.new('resize'))

def register_vue_components():
    vue_register_component('pyri-motion-program-opt', MotionOptComponent)
