bl_info = {
    "name": "TB_Viewport to selection",
    "author": "Taiseibutsu",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "Viewport to selection",
    "warning": "",
    "doc_url": "",
    "category": "TB",
}
import bpy
import bmesh
from bpy.props import BoolProperty, IntProperty

def no_selection_to_go(self, context):
    self.layout.label(text="Desired active vertex out of selection")
def calculate_max_v(self, context):
    numberidx = 0
    for i,v in enumerate(bm.verts):
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
class TB_VtS_OT_PREV(bpy.types.Operator):
    bl_idname = "tb_ops.viewtosel_prev"
    bl_label = "Prev"
    bl_options = {'REGISTER', 'UNDO'}
    def draw_header(self,context):
        layout = self.layout
        layout.label(icon='FRAME_PREV')
    def execute(self, context):
        if tbctsprop.number > 1:
            tbctsprop.number -= 1
        else:
            bpy.context.window_manager.popup_menu(no_selection_to_go, title="Out of selection", icon='ERROR')
class TB_VtS_OT_NEXT(bpy.types.Operator):-
    bl_idname = "tb_ops.viewtosel_next"
    bl_label = "Next"
    bl_options = {'REGISTER', 'UNDO'}
    def draw_header(self,context):
        layout = self.layout
        layout.label(icon='FRAME_NEXT')
    def execute(self, context):
        calculate_max_v()
        if tbctsprop.number < tbctsprop.maxnumber:
            tbctsprop.number += 1
        else:
            bpy.context.window_manager.popup_menu(no_selection_to_go, title="Out of selection", icon='ERROR')            
class TB_OT_operator(bpy.types.Operator):-
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
        for i,v in enumerate(bm.verts):
            if v.select:
                if numberidx == (tbctsprop.number - 1):
                    mat = ac_ob.matrix_world
                    loc = mat @ v.co
                    vl.x = loc[0]
                    vl.y = loc[1]
                    vl.z = loc[2]
                numberidx = numberidx + 1
        if (tbctsprop.number) > numberidx:
            varonce = True
            tbctsprop.error = True
            tbctsprop.maxnumber = numberidx
        else:
            varonce = False
            tbctsprop.error = False
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
        layout = self.layout
        tbctsprop = bpy.context.scene.tb_vts_prop
        if tbctsprop.error:
            if tbctsprop.maxnumber == 0:
                layout.label(text="Vertex selection not initialiced",icon='ERROR')
            else:
                layout.label(text="Vertex to target out of range",icon='ERROR')
                layout.label(text="Expected values: from 1 to " + str(tbctsprop.maxnumber),icon='BLANK1') 
        if context.active_object.type == 'MESH':
            if context.active_object.mode == 'EDIT':
                layout.prop(tbctsprop,"number")
                layout.operator("tb_ops.viewtosel",icon='RESTRICT_SELECT_OFF')
        row = layout.row()
        row.operator(tb_ops.viewtosel_prev
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
