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
from pyodide import create_proxy

@VueComponent
class InputDataComponent(PyriVue):
    def __init__(self):
        super().__init__()        
        self.xspr = None

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_input_data_component.html")

    name = vue_prop()
    title = vue_prop()
    subtitle = vue_prop()
    data_file = vue_data()

    def mounted(self):
        super().mounted()
        self.init_sheet()

    def init_sheet(self):
        sheet = self.refs.input_sheet
        assert sheet is not None
        xspr_options = to_js2({
            "view": {
                "height": lambda: sheet.clientHeight,
                "width": lambda: sheet.clientWidth
            }
        })

        self.xspr = js.x_spreadsheet(sheet,xspr_options)

    def core_ready(self):
        super().core_ready()
        async def trigger_resize():
            await self.next_tick()
            await asyncio.sleep(0.05)
            js.window.dispatchEvent(js.Event.new('resize'))

        self.core.create_task(trigger_resize())

        try:
            def do_observe(entries, observer):
                for i in range(len(entries)):
                    if (entries[i].intersectionRatio > 0):
                        js.window.dispatchEvent(js.Event.new('resize'))

            self.intersection_observer = js.IntersectionObserver.new(create_proxy(do_observe)).observe(self.refs.input_sheet)
        except:
            print("Failed to create data input observer")
            traceback.print_exc()

    @vue_method
    async def load_from_variable(self, *args):
        try:
            variable_name = js.prompt("Variable Name")
            if variable_name is None:
                return

            var_storage = self.core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()
            variable_rr = await var_storage.async_getf_variable_value("globals", variable_name, None)

            assert variable_rr.datatype == "double[*]", "Variable must be a 2D array"
            variable_csv_io = io.StringIO()
            np.savetxt(variable_csv_io, variable_rr.data, delimiter=",")
            variable_csv_b = variable_csv_io.getvalue().encode("ascii")
            print(f"variable_csv_b: {variable_csv_b}")

            wb = js.XLSX.read(to_js2(variable_csv_b), to_js2({'type': 'array'}))
            data = js.stox(wb)
            print(f"data[0].rows.object_keys() {data[0].rows.object_keys()}")
            data[0].rows.len=len(data[0].rows.object_keys())
            self.xspr.loadData(data)
        except:
            js.alert(f"Error loading data from variable:\n\n{traceback.format_exc()}")

    @vue_method
    def load_from_csv(self, *args):
        self.bv_modal.show(f"mp_opt_{self.name}_file_modal")

    @vue_method
    async def load_from_csv2(self, *args):
        try:
            
            file_input_file = self.data_file
            
            file_future = asyncio.Future()

            def file_done(res):
                file_bytes = js.Uint8Array.new(res.target.result)
                file_future.set_result(file_bytes)

            def file_err(res):
                file_future.set_exception(res.to_py())

            file_reader = js.FileReader.new()
            file_reader.onload=file_done
            file_reader.onerror=file_err

            file_reader.readAsArrayBuffer(file_input_file)

            file_bytes = await file_future

            wb = js.XLSX.read(file_bytes, to_js2({'type': 'array'}))
            data = js.stox(wb)
            data[0].rows.len=len(data[0].rows.object_keys())
            self.xspr.loadData(data)
        except:
            js.alert(f"Error displaying motion program opt results:\n\n{traceback.format_exc()}")

    @vue_method
    def clear_table(self, elem_id, *args):
        self.xspr.loadData({})

    def get_sheet_data(self):
        # TODO: more efficient way to get data from xspr into numpy
        new_wb = js.xtos(self.xspr.getData())
        csv_dat = js.XLSX.utils.sheet_to_csv(getattr(new_wb.Sheets,new_wb.SheetNames[0]))
        csv_dat_io = io.StringIO(csv_dat)
        np_dat = np.genfromtxt(csv_dat_io, dtype=np.float64, delimiter=",")
        return np_dat


    def before_destroy(self):
        super().before_destroy()
        try:
            self.intersection_observer.disconnect()
            self.intersection_observer = None
        except:
            pass

def register_vue_components():
    vue_register_component('pyri-motion-program-opt-input-data', InputDataComponent)
