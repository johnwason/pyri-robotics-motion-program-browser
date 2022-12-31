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

@VueComponent
class ExecutionComponent(PyriVue):

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_execution_component.html")

    state = vue_prop()
    title = vue_prop()

def register_vue_components():
    vue_register_component("pyri-motion-program-opt-execution", ExecutionComponent)