# (GNU GPL) <2022> <Taiseibutsu>" Developed for Blender 3.2
# This program is free software: you can redistribute it and/or modify it, WITHOUT ANY WARRANTY that you wont focus on the non selected void from the meshes of tomorrow.

bl_info = {
    "name": "View to individual selection (TB)",
    "author": "Taiseibutsu",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "Move view to individual selection",
    "warning": "",
    "doc_url": "",
    "category": "TB",
}
import bpy, bmesh,mathutils
from bpy.props import BoolProperty, IntProperty, EnumProperty

def no_selection_to_go(self, context):
    self.layout.label(text="Desired active vertex out of selection")

def calculate_max_v():
    tbctsprop = bpy.context.scene.tb_vts_prop
    bm=bmesh.from_edit_mesh(bpy.context.active_object.data)
    numberidx = 0
    if tbctsprop.selmode == "VERTEX":
        sel = bm.verts
    elif tbctsprop.selmode == "EDGE":
        sel = bm.edges
    elif tbctsprop.selmode == "FACE":
        sel = bm.faces
    for i,v in enumerate(sel):
            if v.select:
                numberidx = numberidx + 1
    tbctsprop.maxnumber = numberidx
    
class tb_vts_prop(bpy.types.PropertyGroup):
    number :IntProperty(
        name = "Active Vertex",
        description = "Active_Vertex",
        min = 1,
        default=1)
    error :BoolProperty()
    maxnumber :IntProperty()    
    selmode :EnumProperty(
        name = "Select mode",
        description = "Mode to set selection",
        items= [('VERTEX','vertex','Vertex', 'VERTEXSEL', 0),
                ('EDGE','edge','Edge', 'EDGESEL', 1),
                ('FACE', 'face', 'Faces','FACESEL',2)
        ])       
class TB_VtS_OT_PREV(bpy.types.Operator):
    bl_idname = "tb_ops.viewtosel_prev"
    bl_label = "Prev"
    bl_options = {'REGISTER', 'UNDO'}
    def draw_header(self,context):
        layout = self.layout
    def execute(self, context):
        tbctsprop = bpy.context.scene.tb_vts_prop
        if tbctsprop.number > 1:
            tbctsprop.number -= 1
            bpy.ops.tb_ops.viewtosel()
        else:
            bpy.context.window_manager.popup_menu(no_selection_to_go, title="Out of selection", icon='ERROR')
        return {'FINISHED'}
class TB_VtS_OT_NEXT(bpy.types.Operator):
    bl_idname = "tb_ops.viewtosel_next"
    bl_label = "Next"
    bl_options = {'REGISTER', 'UNDO'}
    def draw_header(self,context):
        layout = self.layout
    def execute(self, context):
        tbctsprop = bpy.context.scene.tb_vts_prop
        calculate_max_v()
        if tbctsprop.number < tbctsprop.maxnumber:
            tbctsprop.number += 1
            bpy.ops.tb_ops.viewtosel()
        else:
            bpy.context.window_manager.popup_menu(no_selection_to_go, title="Out of selection", icon='ERROR')            
        return {'FINISHED'}
class TB_OT_operator(bpy.types.Operator):
    bl_idname = "tb_ops.viewtosel"
    bl_label = "Camera to selection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        vl = context.space_data.region_3d.view_location
        ac_ob = bpy.context.active_object
        ac_obd = ac_ob.data
        tbctsprop = bpy.context.scene.tb_vts_prop
        bm=bmesh.from_edit_mesh(ac_obd)
        varonce = False
        numberidx = 0
        if tbctsprop.selmode == "VERTEX":
            sel = bm.verts
        elif tbctsprop.selmode == "EDGE":
            sel = bm.edges
        elif tbctsprop.selmode == "FACE":
            sel = bm.faces
        for i,s in enumerate(sel):
            if s.select:
                if numberidx == (tbctsprop.number - 1):
                    mat = ac_ob.matrix_world
                    if tbctsprop.selmode == "VERTEX":
                        loc = mat @ s.co
                    else:
                        verts = s.verts
                        pos = mathutils.Vector((0.0, 0.0, 0.0))
                        for tmp_V in verts:
                            pos = pos + tmp_V.co 
                        if tbctsprop.selmode == "EDGE": 
                            loc = mat @ (pos / 2.0)
                        else:
                            loc = mat @ (pos / len(verts))
                    vl.x = loc[0]
                    vl.y = loc[1]
                    vl.z = loc[2]
                    print("View to" + str(loc))
                numberidx = numberidx + 1
        if (tbctsprop.number) > numberidx:
            varonce = True
            tbctsprop.error = True
            tbctsprop.maxnumber = numberidx
        else:
            varonce = False
            tbctsprop.error = False
            tbctsprop.maxnumber = numberidx
        return {'FINISHED'}

class TB_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "View to selection"
    bl_category = "TB"
    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'  
    def draw_header(self,context):
        layout = self.layout
        layout.label(text="",icon='CAMERA_DATA')
    def draw(self, context):
        if context.active_object.type == 'MESH':
            if context.active_object.mode == 'EDIT':
                tbctsprop = bpy.context.scene.tb_vts_prop
                layout = self.layout
                bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
                if tbctsprop.selmode == "VERTEX":
                    maxnum = [ v.index for v in bm.verts if v.select ]
                elif tbctsprop.selmode == "EDGE":
                    maxnum = [ e.index for e in bm.edges if e.select ]
                elif tbctsprop.selmode == "FACE":
                    maxnum = [ f.index for f in bm.faces if f.select ]
                row = layout.row(align=True)
                row.prop(tbctsprop,"selmode",text=" ",expand=True)
                row = layout.row(align=True)
                row.label(text="Selected_vetices:" + str(len(maxnum)))
                if tbctsprop.error:
                    row = layout.row(align=True)
                    if tbctsprop.maxnumber == 0:
                        row.label(text="Vertex selection not initialiced",icon='ERROR')
                    else:
                        row.label(text="Vertex to target out of range",icon='ERROR')
                        row.label(text="Expected values: from 1 to " + str(tbctsprop.maxnumber),icon='BLANK1') 
                row = layout.row(align=True)
                row.prop(tbctsprop,"number")
                row.operator("tb_ops.viewtosel",icon='RESTRICT_SELECT_OFF')
        row = layout.row()
        row.operator("tb_ops.viewtosel_prev",icon='FRAME_PREV')
        row.operator("tb_ops.viewtosel_next",icon='FRAME_NEXT')
classes = (
    tb_vts_prop,
    TB_PT_panel,
    TB_OT_operator,
    TB_VtS_OT_NEXT,
    TB_VtS_OT_PREV
    )
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.tb_vts_prop = bpy.props.PointerProperty(type=tb_vts_prop)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.tb_vts_prop
if __name__ == "__main__":
    register()
