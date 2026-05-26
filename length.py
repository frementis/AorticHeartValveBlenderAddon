bl_info = {
    "name": "Sum Edge Lengths with Scale",
    "blender": (3, 0, 0),
    "category": "Mesh",
    "description": "Calculates the total length of selected edges in Edit Mode, taking object scale into account",
}

import bpy
import bmesh

class MESH_OT_sum_edge_lengths(bpy.types.Operator):
    """Operator to sum lengths of selected edges, accounting for object scale"""
    bl_idname = "mesh.sum_edge_lengths"
    bl_label = "Sum Edge Lengths"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.active_object

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        # Switch to Edit Mode if not already in it
        if bpy.context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Must be in Edit Mode")
            return {'CANCELLED'}
        
        # Get mesh data with bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Get object scale (to take into account scaling in object mode)
        scale = obj.scale
        
        # Variable to store the sum of edge lengths
        total_length = 0.0

        # Loop through edges and sum the lengths of selected edges
        for edge in bm.edges:
            if edge.select:  # Check if edge is selected
                v1, v2 = edge.verts
                # Compute the length considering the object's scale
                edge_length = (v1.co - v2.co).length
                edge_length_scaled = edge_length * scale.length  # Apply scaling
                total_length += edge_length_scaled
        
        # Output the result to the system info window and report
        self.report({'INFO'}, f"Total length of selected edges: {total_length:.2f}")
        
        return {'FINISHED'}

# Panel to hold the button
class VIEW3D_PT_sum_edge_lengths_panel(bpy.types.Panel):
    """Panel for Sum Edge Lengths operator"""
    bl_label = "Sum Edge Lengths"
    bl_idname = "VIEW3D_PT_sum_edge_lengths_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.sum_edge_lengths", text="Calculate Total Edge Length")

# Register the addon
def menu_func(self, context):
    self.layout.operator(MESH_OT_sum_edge_lengths.bl_idname)

def register():
    bpy.utils.register_class(MESH_OT_sum_edge_lengths)
    bpy.utils.register_class(VIEW3D_PT_sum_edge_lengths_panel)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MESH_OT_sum_edge_lengths)
    bpy.utils.unregister_class(VIEW3D_PT_sum_edge_lengths_panel)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)

if __name__ == "__main__":
    register()
