bl_info = {
    "name": "Render time estimator",
    "author": "Lithika Senavirathne",
    "version": (1, 0),
    "blender": (3, 1, 0),
    "location": "3D Viewport > Tool > Cost Estimator",
    "description": "Render cost Estimator for Blender",
    "warning": "",
    "doc_url": "https://github.com/methsilusenavirathne",
    "category": "Render",
}

import bpy
import time
import platform
import os
import math
import winreg
import ctypes
import ctypes.wintypes

psapi = ctypes.windll.psapi



class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong),
        ('PageFaultCount', ctypes.c_ulong),
        ('PeakWorkingSetSize', ctypes.c_size_t),
        ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t),
        ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]

process = ctypes.windll.kernel32.GetCurrentProcess()
pmc = PROCESS_MEMORY_COUNTERS_EX()
psapi.GetProcessMemoryInfo(process, ctypes.byref(pmc), ctypes.sizeof(pmc))


physical_memory_bytes = ctypes.c_ulonglong()
ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(physical_memory_bytes))


def get_cpu_name():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
    cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
    return cpu_name


gpu_list = {
    "NVIDIA GeForce RTX 4090": {"vram": "24576 MB", "power": "72388"}, "NVIDIA GeForce RTX 4090 Laptop GPU": {"vram": "16384 MB", "power": "4312"}, "NVIDIA GeForce RTX 4070 Ti": {"vram": "12288 MB", "power": "4143"}, "NVIDIA GeForce RTX 3090": {"vram": "24576 MB", "power": "3816"}, "NVIDIA GeForce RTX 3080 Ti": {"vram": "12288 MB", "power": "3762"}, "NVIDIA GeForce RTX 4080 Laptop GPU": {"vram": "12288 MB", "power": "3709"}, "NVIDIA GeForce RTX 3090 Ti": {"vram": "24576 MB", "power": "3633"}, "RTX A6000": {"vram": "48640 MB", "power": "3396"}, "NVIDIA GeForce RTX 3080": {"vram": "10240 MB", "power": "3295"}, "A100-SXM4-40GB": {"vram": "40448 MB", "power": "3275"}, "NVIDIA GeForce RTX 4080": {"vram": "16384 MB", "power": "3058"}, "RTX A4500": {"vram": "20480 MB", "power": "2616"}, "RTX A5000": {"vram": "24320 MB", "power": "2594"}, "NVIDIA GeForce RTX 4060 Laptop GPU": {"vram": "8192 MB", "power": "2483"}, "NVIDIA GeForce RTX 3070 Ti": {"vram": "8192 MB", "power": "2459"}, "NVIDIA GeForce RTX 3080 Ti Laptop GPU": {"vram": "16384 MB", "power": "2255"}, "NVIDIA GeForce RTX 3070": {"vram": "8192 MB", "power": "2251"}, "NVIDIA GeForce RTX 3070 Laptop GPU": {"vram": "8192 MB", "power": "2185"}, "A10": {"vram": "22528 MB", "power": "2176"}, "RTX A5000 Laptop GPU": {"vram": "16384 MB", "power": "2134"}, "NVIDIA GeForce RTX 3080 Laptop GPU": {"vram": "16384 MB", "power": "2087"}, "RTX A4000": {"vram": "16128 MB", "power": "2081"}, "Quadro RTX 8000": {"vram": "49152 MB", "power": "2073"}, "Quadro RTX 6000": {"vram": "24576 MB", "power": "2004"}, "NVIDIA GeForce RTX 2080 Ti": {"vram": "11264 MB", "power": "1961"}, "NVIDIA GeForce RTX 3060 Ti": {"vram": "8192 MB", "power": "1909"}, "RTX A4000 Laptop GPU": {"vram": "8192 MB", "power": "1857"}, "NVIDIA GeForce RTX 3070 Ti Laptop GPU": {"vram": "8192 MB", "power": "1782"}, "NVIDIA GeForce RTX 3060 Laptop GPU": {"vram": "6144 MB", "power": "1681"}, "NVIDIA GeForce RTX 2070 SUPER": {"vram": "8192 MB", "power": "1603"}, "NVIDIA GeForce RTX 2080": {"vram": "8192 MB", "power": "1560"}, "NVIDIA GeForce RTX 3060": {"vram": "12288 MB", "power": "1555"}, "NVIDIA GeForce RTX 2080 SUPER": {"vram": "8192 MB", "power": "1549"}, "Quadro RTX 5000": {"vram": "16384 MB", "power": "1545"}, "GRID RTX6000-6Q": {"vram": "6144 MB", "power": "1543"}, "NVIDIA GeForce RTX 2070": {"vram": "7936 MB", "power": "1408"}, "Quadro RTX 4000": {"vram": "7936 MB", "power": "1400"}, "NVIDIA GeForce RTX 2060 SUPER": {"vram": "8192 MB", "power": "1323"}, "RTX A2000 12GB": {"vram": "12288 MB", "power": "1206"}, "NVIDIA GeForce RTX 2060": {"vram": "6144 MB", "power": "1038"}, "Tesla P100-PCIE-1": {"vram": "16384 MB", "power": "1037"}, "RTX A2000 Laptop GPU": {"vram": "4096 MB", "power": "1030"}, "Quadro RTX 3000": {"vram": "6144 MB", "power": "1018"}, "Tesla T4": {"vram": "15104 MB", "power": "991"}, "NVIDIA GeForce RTX 3050 Laptop GPU": {"vram": "4096 MB", "power": "948"}, "TITAN Xp COLLECTORS EDITION": {"vram": "12288 MB", "power": "868"}, "TITAN X (Pascal)": {"vram": "12288 MB", "power": "853"}, "TITAN Xp": {"vram": "12288 MB", "power": "812"}, "RTX A1000 Laptop GPU": {"vram": "4096 MB", "power": "785"}, "GRID RTX6000-4Q": {"vram": "4096 MB", "power": "770"}, "RTX A2000 8GB Laptop GPU": {"vram": "8192 MB", "power": "770"}, "Quadro P6000": {"vram": "24576 MB", "power": "730"}, "NVIDIA GeForce GTX 1660 SUPER": {"vram": "6144 MB", "power": "713"}, "P102-100": {"vram": "10240 MB", "power": "707"}, "NVIDIA GeForce GTX 1660 Ti": {"vram": "6144 MB", "power": "693"}, "NVIDIA GeForce GTX 1080 Ti": {"vram": "11264 MB", "power": "673"}, "NVIDIA GeForce RTX 3050 Ti Laptop GPU": {"vram": "4096 MB", "power": "658"}, "NVIDIA GeForce GTX 1660": {"vram": "6144 MB", "power": "622"}, "NVIDIA GeForce GTX 1070 Ti": {"vram": "8192 MB", "power": "549"}, "Quadro P5200": {"vram": "16384 MB", "power": "536"}, "P104-100": {"vram": "8192 MB", "power": "528"}, "NVIDIA GeForce GTX 1650 SUPER": {"vram": "4096 MB", "power": "487"}, "NVIDIA GeForce GTX 980 Ti": {"vram": "6144 MB", "power": "485"}, "Quadro M6000": {"vram": "24576 MB", "power": "480"}, "NVIDIA GeForce RTX 2050": {"vram": "4096 MB", "power": "462"}, "Quadro P5000": {"vram": "16384 MB", "power": "453"}, "A10-6Q": {"vram": "6144 MB", "power": "451"}, "Quadro P4000": {"vram": "8192 MB", "power": "445"}, "NVIDIA GeForce GTX 1650": {"vram": "4096 MB", "power": "440"}, "NVIDIA GeForce GTX 1070": {"vram": "8192 MB", "power": "438"}, "NVIDIA GeForce GTX 1650 Ti": {"vram": "4096 MB", "power": "405"}, "NVIDIA GeForce GTX 1080": {"vram": "8192 MB", "power": "395"}, "T1000": {"vram": "4096 MB", "power": "388"}, "T600 Laptop GPU": {"vram": "4096 MB", "power": "386"}, "NVIDIA GeForce GTX 980": {"vram": "4096 MB", "power": "369"}, "Quadro T1000": {"vram": "4096 MB", "power": "363"}, "T1200 Laptop GPU": {"vram": "4096 MB", "power": "355"}, "Quadro T2000": {"vram": "4096 MB", "power": "349"}, "NVIDIA GeForce GTX 1060 3GB": {"vram": "3072 MB", "power": "331"}, "T600": {"vram": "4096 MB", "power": "322"}, "Quadro M5000": {"vram": "8192 MB", "power": "316"}, "NVIDIA GeForce GTX 1060": {"vram": "6144 MB", "power": "313"}, "Quadro P2200": {"vram": "5120 MB", "power": "312"}, "NVIDIA GeForce GTX 980M": {"vram": "4096 MB", "power": "250"}, "P106-090": {"vram": "3072 MB", "power": "225"}, "Quadro M4000": {"vram": "8192 MB", "power": "218"}, "GRID M60-2Q": {"vram": "3840 MB", "power": "215"}, "NVIDIA GeForce GTX 1050 Ti": {"vram": "4096 MB", "power": "210"}, "NVIDIA GeForce MX550": {"vram": "1792 MB", "power": "205"}, "NVIDIA GeForce MX450": {"vram": "2048 MB", "power": "205"}, "NVIDIA GeForce GTX 970M": {"vram": "3072 MB", "power": "200"}, "T500": {"vram": "4096 MB", "power": "184"}, "NVIDIA GeForce GTX 960": {"vram": "2048 MB", "power": "179"}, "T400": {"vram": "2048 MB", "power": "177"}, "NVIDIA GeForce GTX 1050": {"vram": "3072 MB", "power": "176"}, "Quadro P1000": {"vram": "4096 MB", "power": "160"}, "Tesla M40": {"vram": "11520 MB", "power": "152"}, "NVIDIA GeForce GTX 965M": {"vram": "2048 MB", "power": "144"}, "NVIDIA GeForce GTX 960M": {"vram": "2048 MB", "power": "143"}, "Quadro P2000": {"vram": "4096 MB", "power": "139"}, "Quadro K2200": {"vram": "4096 MB", "power": "135"}, "NVIDIA GeForce GTX 860M": {"vram": "2048 MB", "power": "132"}, "NVIDIA GeForce GTX 970": {"vram": "4096 MB", "power": "131"}, "NVIDIA GeForce GTX 950": {"vram": "2048 MB", "power": "130"}, "NVIDIA GeForce MX350": {"vram": "2048 MB", "power": "128"}, "NVIDIA GeForce GTX 750": {"vram": "1024 MB", "power": "124"}, "Quadro P620": {"vram": "2048 MB", "power": "118"}, "Quadro M1000M": {"vram": "4096 MB", "power": "111"}, "NVIDIA GeForce GTX 750 Ti": {"vram": "4096 MB", "power": "108"}, "NVIDIA GeForce MX330": {"vram": "2048 MB", "power": "104"}, "NVIDIA GeForce GTX 850M": {"vram": "2048 MB", "power": "102"}, "Quadro M620": {"vram": "2048 MB", "power": "101"}, "NVIDIA GeForce MX250": {"vram": "2048 MB", "power": "99"}, "Quadro P600": {"vram": "2048 MB", "power": "99"}, "NVIDIA GeForce MX150": {"vram": "2048 MB", "power": "89"}, "Quadro M2000": {"vram": "4096 MB", "power": "87"}, "NVIDIA GeForce MX130": {"vram": "4096 MB", "power": "77"}, "NVIDIA GeForce 940MX": {"vram": "2048 MB", "power": "75"}, "Quadro K620": {"vram": "2048 MB", "power": "72"}, "NVIDIA GeForce GTX 745": {"vram": "4096 MB", "power": "68"}, "NVIDIA GeForce MX230": {"vram": "2048 MB", "power": "64"}, "NVIDIA GeForce GTX 950M": {"vram": "4096 MB", "power": "63"}, "Quadro P400": {"vram": "2048 MB", "power": "55"}, "NVIDIA GeForce MX110": {"vram": "2048 MB", "power": "52"}, "NVIDIA GeForce 840M": {"vram": "2048 MB", "power": "50"}, "NVIDIA GeForce 940M": {"vram": "2048 MB", "power": "45"}, "NVIDIA GeForce GT 1030": {"vram": "2048 MB", "power": "36"}, "NVIDIA GeForce 920MX": {"vram": "2048 MB", "power": "23"}
    }

user_gpu_model = bpy.context.preferences.addons["cycles"].preferences.devices[0].name
user_cpu_model = get_cpu_name()
total_ram_mb = int(physical_memory_bytes.value / 1024 )


if user_gpu_model in gpu_list:
    gpu_info = gpu_list[user_gpu_model]
else:
    print(f"Your GPU ({user_gpu_model}) was not found in the GPU directory.")

user_gpu_power = gpu_info["power"]
user_gpu_vram = gpu_info["vram"]

Base_Gpu = gpu_list["NVIDIA GeForce RTX 2060"]
Base_Gpu_power = Base_Gpu["power"]
Base_Gpu_price = 5




user_render_time = 0

def cost_calculation():
    num_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
    global user_render_time, render_time_hours, Render_cost
    render_time_hours = user_render_time / 3600
    Base_gpu_render_time = render_time_hours * float(user_gpu_power) / float(Base_Gpu_power)
    Render_cost = Base_gpu_render_time * Base_Gpu_price * num_frames

def render_frame():
    global user_render_time
    global start_time
    start_time = time.time()
    bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True, use_viewport=True, layer="", scene="")
    bpy.app.handlers.render_complete.append(on_render_complete)
    
def on_render_complete(scene):
    global user_render_time
    global start_time
    global end_time
    end_time = time.time()
    user_render_time = end_time - start_time
    cost_calculation()

    
render_time_hours = 0

class Render_frame_operator(bpy.types.Operator):
    bl_idname = "render_sample.frame"
    bl_label = "Render Sample Frame"

    def execute(self, context):
        global render_time_hours
        render_frame()
        return {'FINISHED'}

Render_cost = 0

class Cost_Calculation(bpy.types.Operator):
    bl_idname = "cost.calculation"
    bl_label = "Calculate Price"

    def execute(self, context):
        cost_calculation()
        return {'FINISHED'}

class Addon_Panel(bpy.types.Panel):
    bl_idname = "Cost_Estimator"
    bl_label = "Cost Estimator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RenderCalc"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 1.5
        row.alignment = 'CENTER'
        row.label(text="System Configuration", icon='INFO')
        box.separator()

        box.label(text=f"System GPU: {user_gpu_model} ({user_gpu_vram}, {user_gpu_power}%)")
        box.label(text=f"System CPU: {user_cpu_model}")
        box.label(text=f"System RAM: {total_ram_mb} MB")

        layout.separator()

        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 1.5
        row.alignment = 'CENTER'
        row.label(text="Render Settings", icon='RENDER_STILL')
        box.separator()

        box.label(text=f"Render Engine: {bpy.context.scene.render.engine}")
        box.label(text=f"Render Device: {bpy.context.scene.cycles.device}")
        box.label(text=f"Resolution: {bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")
        box.label(text=f"Samples: {bpy.context.scene.cycles.samples}")
        

        row = layout.row()
        row.alignment = 'CENTER'
        row.operator("render_sample.frame", text = "Render Current Frame")
        row.operator("cost.calculation", text = "Calculate price")
        box.label(text=f"Time : {user_render_time:.2f} seconds")
        box.label(text=f"Render Cost: {Render_cost:.3f} $")
        row = layout.row()
        row.operator("wm.url_open", text="Render for Low cost", icon='WORLD').url = "https://www.fiverr.com/share/E2PR77"

def register():
    bpy.utils.register_class(Addon_Panel)
    bpy.utils.register_class(Render_frame_operator)
    bpy.utils.register_class(Cost_Calculation)
    bpy.types.Scene.num_frames = bpy.props.IntProperty(name="Number of Frames")

def unregister():
    bpy.utils.unregister_class(Addon_Panel)
    bpy.utils.unregister_class(Render_frame_operator)
    bpy.utils.unregister_class(Cost_Calculation)
    del bpy.types.Scene.num_frames

if __name__ == "__main__":
    register()
