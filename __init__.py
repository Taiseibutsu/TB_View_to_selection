bl_info = {
    "name": "Viewport to selection",
    "author": "Taiseibutsu",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "Viewport to selection",
    "warning": "",
    "doc_url": "",
    "category": "",
}
import bpy
import bmesh
from bpy.props import BoolProperty, IntProperty
class tb_vts_prop(bpy.types.PropertyGroup):
    number :IntProperty(
        name = "Active Vertex",
        description = "Active_Vertex",
        min = 1,
        default=1)
    error :BoolProperty()
    maxnumber :IntProperty()    
class TB_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Viewport to selection"
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
class TB_OT_operator(bpy.types.Operator):
    bl_idname = "tb_ops.viewtosel"
    bl_label = "Camera to selection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        vl = context.space_data.region_3d.view_location
        tbctsprop = bpy.context.scene.tb_vts_prop
        bm=bmesh.from_edit_mesh(context.active_object.data)
        varonce = False
        numberidx = 0
        for i,v in enumerate(bm.verts):
            if v.select:
                if numberidx == (tbctsprop.number - 1):
                    print(v.co)
                    vl.x = v.co[0]
                    vl.y = v.co[1]
                    vl.z = v.co[2] 
                numberidx = numberidx + 1
        if (tbctsprop.number) > numberidx:
            varonce = True
            tbctsprop.error = True
            tbctsprop.maxnumber = numberidx
        else:
            varonce = False
            tbctsprop.error = False
        return {'FINISHED'}
classes = (
    tb_vts_prop,
    TB_PT_panel,
    TB_OT_operator,
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
