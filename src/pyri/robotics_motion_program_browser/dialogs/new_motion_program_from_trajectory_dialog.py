import asyncio
import io
import re
import time
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

    async def do_motion_program_opt(self, input_trajectory, trajectory_format, frame, robot_local_device_name, 
        robot_origin_calib_global_name, tool_pose, opt_params, new_name):
        try:
            mp_opt_service = self.core.device_manager.get_device_subscription("robotics_mp_opt").GetDefaultClient()
            mp_opt_gen = await mp_opt_service.async_greedy_fitting_motion_program_opt(input_trajectory, trajectory_format, frame, 
                robot_local_device_name, robot_origin_calib_global_name, tool_pose, opt_params, new_name, None)
            
            self.core.create_task(display_opt_results(mp_opt_gen, self.new_name, self.core, self.device_manager))

        except:
            js.alert(f"Motion program optimization failed:\n\n{traceback.format_exc()}")

    def handle_next(self,*args):
        try:
            robot_local_device_name = getattr(self.vue,"$data").robot_selected
            robot_origin_calib_global_name = getattr(self.vue,"$data").robot_calibration_selected
            trajectory_format = getattr(self.vue,"$data").trajectory_file_format_selected
            frame = getattr(self.vue,"$data").trajectory_data_frame_selected

            # TODO: more efficient way to get data from xspr into numpy
            new_wb = js.xtos(self.xspr.getData())
            csv_dat = js.XLSX.utils.sheet_to_csv(getattr(new_wb.Sheets,new_wb.SheetNames[0]))
            csv_dat_io = io.StringIO(csv_dat)
            np_dat = np.genfromtxt(csv_dat_io, dtype=np.float64, delimiter=",")

            tool_xyz = np.zeros((3,),dtype=np.float64)
            tool_rpy = np.zeros((3,),dtype=np.float64)
            tool_xyz[0] = float(getattr(self.vue,"$data").tool_pose_x)
            tool_xyz[1] = float(getattr(self.vue,"$data").tool_pose_y)
            tool_xyz[2] = float(getattr(self.vue,"$data").tool_pose_z)
            tool_rpy[0] = float(getattr(self.vue,"$data").tool_pose_r_r)
            tool_rpy[1] = float(getattr(self.vue,"$data").tool_pose_r_p)
            tool_rpy[2] = float(getattr(self.vue,"$data").tool_pose_r_y)

            tool_rpy = np.deg2rad(tool_rpy)

            robotics_mp_opt = self.core.device_manager.get_device_subscription("robotics_mp_opt").GetDefaultClient()
            geom_util = GeometryUtil(client_obj = robotics_mp_opt)
            tool_pose = geom_util.xyz_rpy_to_pose(tool_xyz, tool_rpy)

            # TODO: Add user inputs
            params = {
                "velocity": RR.VarValue(0.1,"double"),
                "blend_radius": RR.VarValue(0.05,"double"),
                "max_error_threshold": RR.VarValue(0.02,"double")
            }
            
            self.core.create_task(self.do_motion_program_opt(np_dat, trajectory_format, frame, robot_local_device_name,
                robot_origin_calib_global_name, tool_pose, params, self.new_name))

        except:
            js.alert(f"Motion program optimization failed:\n\n{traceback.format_exc()}")

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

        core.device_manager.connect_device("robotics_mp_opt")

        await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.js")
        await core.js_loader.load_js_src("https://unpkg.com/x-data-spreadsheet@1.1.9/dist/xspreadsheet.css")
        await core.js_loader.load_js_src("https://unpkg.com/xlsx@0.13.0/xlsx.js")
        await core.js_loader.load_js_src("/plugins/pyri-robotics-motion-program/xlsxspread.js")
        
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
                "robot_calibration_selected": "",
                "tool_pose_x": 0,
                "tool_pose_y": 0,
                "tool_pose_z": 0,
                "tool_pose_r_r": 0,
                "tool_pose_r_p": 0,
                "tool_pose_r_y": 0
                
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
        robot_names = util.get_devices_with_type(core, "experimental.robotics.motion_program.MotionProgramRobot")
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
                {"value": "robot", "text": "Robot Base"},
                {"value": "world", "text": "World"}
            ]
        )
        getattr(dialog, "$data").trajectory_data_frame_selected = "robot"
        
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


async def display_opt_results(mp_opt_gen, new_name, core, device_manager):

    try:
        opt_results_id = "motion_program_opt_results_" + str(time.time()).replace(".","")

        opt_results_panel_html = importlib_resources.read_text(__package__,"opt_results_panel.html")
        opt_results_panel_html = opt_results_panel_html.replace("@motion_program_opt_results_id@", opt_results_id)

        opt_results_panel_config = {
            "type": "component",
            "componentName": opt_results_id,
            "componentState": {},
            "title": "Motion Program Optimization Results",
            "id": opt_results_id,
            "isClosable": True
        }

        def register_opt_results_panel(container, state):
            container.getElement().html(opt_results_panel_html)

        core.layout.register_component(opt_results_id,register_opt_results_panel)

        core.layout.layout.root.getItemsById("program")[0].addChild(to_js2(opt_results_panel_config))

        await RRN.AsyncSleep(0.001, None)

        # el = js.document.querySelector(f"#{opt_results_id}")
        # el.querySelector("#global_var_name").textContent = new_name
        # log_el = el.querySelector("#log_output")
        # for l in res.log_output:
        #     span = js.document.createElement('div')
        #     span.innerText = l
        #     span.style = "white-space: pre-line"
        #     css_classes = ["text-monospace", "d-block"]
        #     span.className = " ".join(css_classes)
        #     log_el.append(span)

        def abort_opt(*args):
            try:
                mp_opt_gen.AsyncAbort(None)
            finally:
                pass

        log_lines = to_js2([])

        opt_results_vue = js.Vue.new(to_js2({
            "el": f"#{opt_results_id}",
            "components": {
                "BootstrapTable": js.window.BootstrapTable
            },
            "data":
            {   
                "global_var_name": new_name,
                "log_output": log_lines,
                "running": True,
                "done": False,
                "created_variables": [],
                "created_variables_columns":
                [
                    {
                        "field": "contents",
                        "title": "Variable Contents"
                    },
                    {
                        "field": "variable_name",
                        "title": "Global variable name"
                    },
                    {
                        "field": "description",
                        "title": "Description"
                    }
                ]
            },
            "methods":
            {
                "abort": abort_opt
            }
        }))

        res = None
        while True:
            try:
                res = await mp_opt_gen.AsyncNext(None,None)
                if res.log_output:
                    for l in res.log_output:
                        log_lines.push(to_js2(l))
                    getattr(opt_results_vue,"$data").log_lines = log_lines
                    print(l)
            except RR.StopIterationException:
                break
        
        log_lines.push("Done!")

        created_vars = []
        for res_var in res.result.result_global_variables:
            created_vars.append({
                "contents": res_var.title,
                "variable_name": res_var.global_name,
                "description": res_var.short_description
            })
        
        getattr(opt_results_vue,"$data").created_variables = to_js2(created_vars)

        getattr(opt_results_vue,"$data").log_lines = log_lines
        getattr(opt_results_vue,"$data").running = False
        getattr(opt_results_vue,"$data").done = True

    except:
        try:
            getattr(opt_results_vue,"$data").running = False
        except:
            pass
        js.alert(f"Error displaying motion program opt results:\n\n{traceback.format_exc()}")
