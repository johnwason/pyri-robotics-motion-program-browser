import asyncio
import io
import re
import js
from RobotRaconteur.Client import *
import importlib_resources
import traceback
import numpy as np
import base64
from RobotRaconteurCompanion.Util.GeometryUtil import GeometryUtil
from pyri.webui_browser import util
from pyri.webui_browser.util import to_js2


class NewOptRobotMPDialog:
    def __init__(self, new_name, core, device_manager):
        self.vue = None
        self.core = core
        self.device_manager = device_manager
        self.new_name = new_name

    def init_vue(self,vue):
        self.vue = vue

    def handle_next(self,*args):
        try:
            robot_local_device_name = getattr(self.vue,"$data").robot_selected

            # TODO: more efficient way to get data from xspr into numpy
            new_wb = js.xtos(self.xspr.getData())
            csv_dat = js.XLSX.utils.sheet_to_csv(getattr(new_wb.Sheets,new_wb.SheetNames[0]))
            csv_dat_io = io.StringIO(csv_dat)
            np_dat = np.genfromtxt(csv_dat_io, dtype=np.float64, delimiter=",")
            js.alert(f"Ready to run motion algorithm with data shape: {str(np_dat.shape)}")
        except:
            traceback.print_exc()

    def handle_hidden(self,*args):
        try:
            l = getattr(self.vue,"$el")
            l.parentElement.removeChild(l)
        except:
            traceback.print_exc()

    def trajectory_file_upload(self,*args):
        self.core.create_task(self.do_trajectory_file_upload())

    async def do_trajectory_file_upload(self):
        try:
            vue_trajectory_file = getattr(self.vue,"$data").trajectory_file

            file_future = asyncio.Future()

            def file_done(res):
                file_bytes = js.Uint8Array.new(res.target.result)
                file_future.set_result(file_bytes)

            def file_err(res):
                file_future.set_exception(res.to_py())

            file_reader = js.FileReader.new()
            file_reader.onload=file_done
            file_reader.onerror=file_err

            file_reader.readAsArrayBuffer(vue_trajectory_file)

            file_bytes = await file_future

            wb = js.XLSX.read(file_bytes, to_js2({'type': 'array'}))
            data = js.stox(wb)
            data[0].rows.len=len(data[0].rows.object_keys())
            self.xspr.loadData(data)

            xspr_data = self.xspr.getData()[0]
            if xspr_data.rows.len == 0:
                raise Exception("Traject file empty!")
            first_row = getattr(xspr_data.rows,"0")
            is_first_row_header = False
            first_row_cells = first_row.cells
            i = 0
            first_row_text = []
            number_re = re.compile(r"^\s*([+-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?)\s*$")
            while True:
                try:
                    cell = getattr(first_row_cells,f"{i}")
                    cell_text = str(cell.text)
                    first_row_text.append(cell_text)
                    if number_re.match(cell_text) is None:
                        is_first_row_header = True
                    i+=1
                except AttributeError:
                    break

            if is_first_row_header:
                first_row_text2 = [a.strip().lower() for a in first_row_text]

                if first_row_text2 == ["x","y","z","i","j","k"]:
                    getattr(self.vue,"$data").trajectory_file_format_selected = "trajectory-data-format-p-n"
                    #  delattr(xspr_data.rows,"0")
                    #  self.xspr.loadData(xspr_data)
                    xspr_sheet = self.xspr.sheet
                    js.console.log("data")
                    js.console.log(xspr_sheet.data)
                    js.console.log("selector")
                    js.console.log(xspr_sheet.data.selector)
                    xspr_sheet.data.selector.setIndexes(0,0)
                    xspr_sheet.data.delete("row")
                    xspr_sheet.reload()
                    js.alert("Detected (x,y,z) (i,j,k) data format from header. Deleting first row!")
                else:
                    js.alert("Detected header but did not recognize data format! Delete header row before submitting!")

        except:
            js.alert(f"Trajectory file upload failed:\n\n{traceback.format_exc()}")

    def init_sheet(self):
        sheet = js.document.getElementById('robot_mp_trajectory_sheet')
        assert sheet is not None
        xspr_options = to_js2({
            "view": {
                "height": lambda: sheet.clientHeight,
                "width": lambda: sheet.clientWidth
            }
        })
        self.xspr = js.x_spreadsheet(sheet,xspr_options)

    def trajectory_data_clear(self,*args):
        self.xspr.loadData({})



async def do_show_new_motion_program_from_trajectory_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    try:

        await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.js")
        await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.css")
        await core.js_loader.load_js_src("https://unpkg.com/xlsx@0.13.0/xlsx.js")
        await core.js_loader.load_js_src("/plugins/pyri-robotics-motion-program/xlsxspread.js")
        
        #core.device_manager.connect_device("vision_robot_calibration")

        dialog_html = importlib_resources.read_text(__package__,"new_motion_program_from_trajectory_dialog.html")

        dialog_obj = NewOptRobotMPDialog(new_name, core, core.device_manager)

        el = js.document.createElement('div')
        el.id = "new_motion_program_from_trajectory_dialog_wrapper"
        js.document.getElementById("wrapper").appendChild(el)

        dialog = js.Vue.new(to_js2({
            "el": "#new_motion_program_from_trajectory_dialog_wrapper",
            "template": dialog_html,
            "data":
            {
                "robot_selected": "",
                "robot_select_options": [],
                "trajectory_file": None,
                "trajectory_file_format_options" : [],
                "trajectory_file_format_selected": "",
                "trajectory_data_frame_options": [],
                "trajectory_data_frame_selected": "",
                "robot_calibration_options": [],
                "robot_calibration_selected": ""
                
            },
            "methods":
            {
                "handle_next": dialog_obj.handle_next,
                "handle_hidden": dialog_obj.handle_hidden,
                "trajectory_file_upload": dialog_obj.trajectory_file_upload,
                "trajectory_data_clear": dialog_obj.trajectory_data_clear
            }
        }))

        dialog_obj.init_vue(dialog)

        robots = []
        robot_names = util.get_devices_with_type(core, "com.robotraconteur.robotics.robot.Robot")
        robots = util.device_names_to_dropdown_options(robot_names)
        
        getattr(dialog,"$data").robot_select_options = to_js2(robots)
        if len(robots) > 0:
            getattr(dialog,"$data").robot_selected = robots[0]["value"]

        getattr(dialog,"$data").trajectory_file_format_options = to_js2(
            [
                {"value": "trajectory-data-format-p-n", "text": "Position, Normal (x,y,z,i,j,k)"},
                {"value": "trajectory-data-format-p-R", "text": "Position, Rotation (x,y,z,R11,R12,R13,R21,R22,R23,R31,R32,R33"},
                {"value": "trajectory-data-format-joints6", "text": "Joints 6 axis (q1,q2,q3,q4,q5,q6)"},
                {"value": "trajectory-data-format-joints7", "text": "Joints 6 axis (q1,q2,q3,q4,q5,q6,q7)"}
            ]
        )
        getattr(dialog,"$data").trajectory_file_format_selected = "trajectory-data-format-p-n"

        getattr(dialog,"$data").trajectory_data_frame_options = to_js2(
            [
                {"value": "trajectory-data-frame-robot", "text": "Robot Base"},
                {"value": "trajectory-data-frame-world", "text": "World"}
            ]
        )
        getattr(dialog, "$data").trajectory_data_frame_selected = "trajectory-data-frame-world"
        
        # db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()

        db = core.device_manager.get_device_subscription("variable_storage").GetDefaultClient()

        calib_var_names = await db.async_filter_variables("globals","",["robot_origin_pose_calibration"],None)
        calib_vars = []
        for v in calib_var_names:
            calib_vars.append({"value": v, "text": v})
        getattr(dialog,"$data").robot_calibration_options = to_js2(calib_vars)
        if len(calib_vars) > 0:
            getattr(dialog,"$data").robot_calibration_selected = calib_vars[0]["value"]

        getattr(dialog,"$bvModal").show("new_motion_program_from_trajectory_dialog")

        await RRN.AsyncSleep(0.01, None)
        dialog_obj.init_sheet()
    except:
        #js.alert(f"Motion program creation failed:\n\n{traceback.format_exc()}")
        print(f"Motion program creation failed:\n\n{traceback.format_exc()}")

def show_new_motion_program_from_trajectory_dialog(new_name: str, variable_type: str, variable_tags: str, core: "PyriWebUIBrowser"):
    core.create_task(do_show_new_motion_program_from_trajectory_dialog(new_name, variable_type, variable_tags, core))