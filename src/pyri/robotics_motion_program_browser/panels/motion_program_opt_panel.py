import asyncio
import json
from typing import List, Dict, Callable, Any
import uuid

from pyri.webui_browser.plugins.panel import PyriWebUIBrowserPanelBase
from pyri.webui_browser import PyriWebUIBrowser
import importlib_resources
from pyri.webui_browser.util import to_js2
import js
from RobotRaconteur.Client import *
import traceback
from pyodide import create_once_callable, create_proxy
import numpy as np
import io
from pyri.webui_browser.pyri_vue import PyriVue, VueComponent, vue_method, vue_data, vue_prop, vue_computed


async def add_motion_program_opt_panel(panel_type: str, core: PyriWebUIBrowser, parent_element: Any):

    core.device_manager.connect_device("robotics_mp_opt")

    await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.js")
    await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.css")
    await core.js_loader.load_js_src("https://unpkg.com/xlsx@0.13.0/xlsx.js")
    await core.js_loader.load_js_src("/plugins/pyri-robotics-motion-program/xlsxspread.js")
    
    mp_panel_html = importlib_resources.read_text(__package__,"motion_program_opt_panel.html")

    mp_panel_config = {
        "type": "component",
        "componentName": "motion_program_opt",
        "componentState": {},
        "title": "Motion Program Opt",
        "id": "motion_program_opt",
        "isClosable": False
    }

    gl = core.layout.layout

    def register_mp_panel(container, state):
        container.getElement().html(mp_panel_html)

    core.layout.register_component("motion_program_opt",register_mp_panel)

    core.layout.layout.root.getItemsById("program")[0].addChild(to_js2(mp_panel_config))
    
    mp_opt_panel = MotionOptPanel(core, "#motion_program_opt")



@VueComponent
class InputDataComponent(PyriVue):
    def __init__(self):
        super().__init__()        
        self.xspr = None

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_panel_input_data_component.html")

    name = vue_prop()
    title = vue_prop()
    subtitle = vue_prop()
    data_file = vue_data()

    def mounted(self):
        self.init_sheet()

    def init_sheet(self):
        el = getattr(self.vue,"$el")
        sheet = el.querySelector("#mp_opt_" + self.name)
        assert sheet is not None
        xspr_options = to_js2({
            "view": {
                "height": lambda: sheet.clientHeight,
                "width": lambda: sheet.clientWidth
            }
        })

        self.xspr = js.x_spreadsheet(sheet,xspr_options)

    @vue_method
    def load_from_variable(self, *args):
        js.alert("load_from_variable")

    @vue_method
    def load_from_csv(self, *args):
        self.bvModal.show(f"mp_opt_{self.name}_file_modal")

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

@VueComponent
class LogComponent(PyriVue):

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_panel_log_component.html")

    log_lines = vue_data([])

    def append_log_line(self, log_line: str):
        print(f"append_log_line {log_line}")
        # Use JS lines directly
        log_lines_js = self.log_lines
        log_lines_js.push(log_line)
        self.log_lines = log_lines_js

    def append_log_lines(self, log_lines: List[str]):
        if len(log_lines) == 0:
            return
        print(f"append_log_lines {log_lines}")
        # Use JS lines directly
        log_lines_js = self.log_lines
        for l in log_lines:
            log_lines_js.push(l)
        self.log_lines = log_lines_js

    def clear_log(self):
        self.log_lines = to_js2([])

@VueComponent
class ExecutionComponent(PyriVue):

    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_panel_execution_component.html")

    state = vue_prop()

@VueComponent
class RedundancyResolutionComponent(PyriVue):
    
    vue_template = importlib_resources.read_text(__package__,"motion_program_opt_panel_redundancy_resolution_component.html")

    vue_components = {
                        "motion-program-opt-panel-input-data-component": InputDataComponent,
                        "motion-program-opt-panel-log-component": LogComponent,
                        "motion-program-opt-panel-execution-component": ExecutionComponent
    }

    execution_state = vue_data("idle")

    def __init__(self):
        self.mp_opt_gen = None

    @vue_method
    def run(self):
        
        self.execution_state = "running"
        self.core.create_task(self.do_alg())
    
    @vue_method
    def abort(self):
        self.execution_state = "done"
        if self.mp_opt_gen is not None:
            try:
                self.mp_opt_gen.Abort()
            except:
                pass

    @vue_method
    def reset(self):
        self.execution_state = "idle"
        self.log.clear_log()

    @property
    def log(self):
        return self.get_ref_pyobj("redundancy_resolution_log")

    async def do_alg(self):
        try:

            curve_js = self.get_ref_pyobj("redundancy_resolution_curve_file").get_sheet_data()
            input_parameters = {
                "curve_js": RR.VarValue(curve_js, "double[*]")
            }

            mp_opt_service = self.core.device_manager.get_device_subscription("robotics_mp_opt").GetDefaultClient()
            self.mp_opt_gen = await mp_opt_service.async_motion_program_opt("redundancy_resolution", input_parameters, None)
           
            while True:
                try:
                    res = await self.mp_opt_gen.AsyncNext(None,None)
                    if res.log_output:
                        self.log.append_log_lines(res.log_output)
                except RR.StopIterationException:
                    break
        
            self.log.append_log_line("Done!")
                
        except:
            js.alert(f"Motion program optimization failed:\n\n{traceback.format_exc()}")
        finally:
            self.execution_state = "done"
            self.mp_opt_gen = None


class MotionOptPanel(PyriVue):
    def __init__(self, core, el):
        super().__init__(core, el)
        
    vue_components={
        "motion-program-opt-panel-redundancy-resolution-component": RedundancyResolutionComponent
    }

    op_selected = vue_data("redundancy_resolution")
    
    redundancy_resolution_curve_js_output_variable = vue_data("")


