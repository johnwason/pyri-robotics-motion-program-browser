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
    
    mp_input_data_component = load_input_data_component(core)

    mp_opt_panel = MotionOptPanel(core, core.device_manager)

    mp_opt_panel_vue = js.Vue.new(to_js2({
        "el": "#motion_program_opt",
        "components": {
            "motion-program-opt-panel-input-data-component": mp_input_data_component
        },
        "data": {
            "op_selected": "redundancy_resolution",
            "redundancy_resolution_curve_js_output_variable": ""
        },
        "methods": {
        }
    }))


    mp_opt_panel.init_vue(mp_opt_panel_vue)

class MotionOptPanel:
    def __init__(self, core, device_manager):
        self.vue = None
        self.core = core
        self.device_manager = device_manager
        self.xsprs = dict()

    def init_vue(self,vue):
        self.vue = vue
       

def vue_obj_method(fn_name):
    def fn(js_this,*args):
        obj = getattr(js_this,"$data").obj
        py_fn = getattr(obj,fn_name)
        py_fn(args)
    return js.wrap_js_this(create_proxy(fn))

def load_input_data_component(core):

    def mp_input_data_component_mounted(js_this):

        obj = InputDataComponent(js_this, core)

    mp_input_data_component_html = importlib_resources.read_text(__package__,"motion_program_opt_panel_input_data_component.html")

    mp_input_data_component = js.Vue.extend(to_js2({
        "template": mp_input_data_component_html,
        "props": ["name", "title", "subtitle", "data_file"],
        "data": lambda js_this: to_js2({
            "obj": None
        }),
        "methods": {
            "load_from_variable": vue_obj_method("load_from_variable"),
            "load_from_csv": vue_obj_method("load_from_csv"),
            "load_from_csv2": vue_obj_method("load_from_csv2"),
            "clear_table": vue_obj_method("clear_table"),
            "get_sheet_data": vue_obj_method("get_sheet_data")
        },
        "mounted": js.wrap_js_this(create_once_callable(mp_input_data_component_mounted))

    })
    )

    return mp_input_data_component

class InputDataComponent:
    def __init__(self,vue,core):
        self.vue = vue
        self.core = core
        getattr(vue,"$data").obj = self
        self.xspr = None
        self.name = getattr(vue,"$props").name
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

    def load_from_variable(self, *args):
        js.alert("load_from_variable")

    def load_from_csv(self, *args):
        getattr(self.vue,"$bvModal").show(f"mp_opt_{self.name}_file_modal")

    def load_from_csv2(self, *args):
        try:
            self.core.create_task(self.do_load_from_csv())
        except:
            js.alert(f"Error displaying motion program opt results:\n\n{traceback.format_exc()}")

    async def do_load_from_csv(self):
        try:
            
            file_input_file = getattr(getattr(self.vue, "$props"), f"data_file")
            
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

    def clear_table(self, elem_id, *args):
        self.xspr.loadData({})

    def get_sheet_data(self):
        # TODO: more efficient way to get data from xspr into numpy
        new_wb = js.xtos(self.xspr.getData())
        csv_dat = js.XLSX.utils.sheet_to_csv(getattr(new_wb.Sheets,new_wb.SheetNames[0]))
        csv_dat_io = io.StringIO(csv_dat)
        np_dat = np.genfromtxt(csv_dat_io, dtype=np.float64, delimiter=",")
        return np_dat
