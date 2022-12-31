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
import pickle

@VueComponent
class AccDataComponent(PyriVue):
    def __init__(self):
        super().__init__()

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_acc_data_component.html")

    name = vue_prop()
    label = vue_prop()
    acc_file = vue_data()

    async def read_acc_file(self):
        file_input_file = self.acc_file
            
        file_future = asyncio.Future()

        def file_done(res):
            file_bytes = res.target.result
            file_future.set_result(file_bytes)

        def file_err(res):
            file_future.set_exception(res.to_py())

        file_reader = js.FileReader.new()
        file_reader.onload=file_done
        file_reader.onerror=file_err

        file_reader.readAsArrayBuffer(file_input_file)

        file_bytes = await file_future

        return bytearray(file_bytes.to_py())

        # with io.BytesIO(file_bytes.to_py()) as f:
        #     acc_data = pickle.load(f)

        # return acc_data

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-acc-data-input', AccDataComponent)