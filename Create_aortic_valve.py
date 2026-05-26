bl_info = {
    "name": "Heart Valve Shape Creator",
    "blender": (3, 0, 0),
    "category": "Object",
    "version": (1, 0),
    "author": "Ilya",
    "description": "Create Aortic Valve"
}

import bpy
import math

# Расчет параметров на основе d
def calculate_parameters(d):
    ic = (math.pi * d) / 3
    L1 = 1.04 * ic + 6.17
    L2 = 1.21 * ic + 18.9
    y = 0.33 * ic + 10.05
    x = ic / 2

    # Расчет Z для сферы
    c = (L1 * 2) / math.pi
    f = 8 * x - 6 * c  # Используем x вместо j
    m = 6 * x**2 - 6 * x * c + c**2  # Используем x вместо j
    pds = f**2 - 24 * m  # Переименовано в pds

    # Проверка pds
    if pds < 0:
        raise ValueError(f"Math domain error: pds is negative ({pds})")

    z = (-f + math.sqrt(pds)) / 12

    # Расчет Y для параболы и треугольника – h
    h = 0.2 * x  # Используем x вместо j

    return x, y, z, h

# Оператор для создания всех фигур
class OBJECT_OT_add_all_surfaces(bpy.types.Operator):
    bl_idname = "object.add_all_surfaces"
    bl_label = "Add All Surfaces"
    bl_description = "Create Aortic Valve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            d = context.scene.custom_d_value
            t = context.scene.thickness_value
            x, y, z, h = calculate_parameters(d)
        except Exception as e:
            self.report({'ERROR'}, f"Error calculating parameters: {e}")
            return {'CANCELLED'}

        #for obj_name in ["Circle", "Triangle", "Bridge", "Cube", "Cube2", "Circle2"]:
        #    obj = bpy.data.objects.get(obj_name)
        #    if obj:
        #        bpy.data.objects.remove(obj, do_unlink=True)

        bpy.ops.object.select_all(action='SELECT')  # Выделить все объекты
        bpy.ops.object.delete()  # Удалить выделенные объекты

        def switch_to_object_mode():
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

        bridge, triangle, circle2 = None, None, None

        try:
            switch_to_object_mode()
            bpy.ops.mesh.primitive_xyz_function_surface(
                x_eq="cos(u)*sin(v)", y_eq="-cos(v)", z_eq="sin(u)*sin(v)",
                range_u_min=0.0, range_u_max=math.pi, range_u_step=128,
                range_v_min=0.0, range_v_max=math.pi/2, range_v_step=64,
                wrap_u=False, wrap_v=False, show_wire=False
            )
            circle = bpy.context.object
            circle.name = "Circle"
            circle.scale = (x, y, z)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add Circle surface: {e}")

        try:
            switch_to_object_mode()
            bpy.ops.mesh.primitive_xyz_function_surface(
                x_eq="cos(u)", y_eq="v*0.2", z_eq="sin(u)",
                range_u_min=0.0, range_u_max=math.pi, range_u_step=64,
                range_v_min=0.0, range_v_max=1.0, range_v_step=32,
                wrap_u=False, wrap_v=False, show_wire=False
            )
            triangle = bpy.context.object
            triangle.name = "Triangle"
            triangle.scale = (x, x, z)  # Y = X
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add Triangle surface: {e}")

        try:
            switch_to_object_mode()
            bpy.ops.mesh.primitive_xyz_function_surface(
                x_eq="v", y_eq="u", z_eq="-u**2+1",
                range_u_min=-1.1, range_u_max=1.1, range_u_step=128,
                range_v_min=-1.1, range_v_max=1.1, range_v_step=256,
                wrap_u=True, wrap_v=False, close_v=True, show_wire=False
            )
            bridge = bpy.context.object
            bridge.name = "Bridge"
            bridge.scale = (x, h, z)
            bridge.location.y = h
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add Bridge surface: {e}")

        if triangle and bridge:
            try:
                boolean_modifier = triangle.modifiers.new(name="Boolean", type='BOOLEAN')
                boolean_modifier.operation = 'DIFFERENCE'
                boolean_modifier.object = bridge
                boolean_modifier.solver = 'FAST'
                bpy.context.view_layer.objects.active = triangle
                bpy.ops.object.modifier_apply(modifier="Boolean")
                bpy.data.objects.remove(bridge, do_unlink=True)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to apply Boolean or delete Bridge: {e}")

        try:
            switch_to_object_mode()
            bpy.ops.mesh.primitive_xyz_function_surface(
                x_eq="cos(u)*sin(v)", y_eq="-cos(v)", z_eq="sin(u)*sin(v)",
                range_u_min=0.0, range_u_max=6.28, range_u_step=128,
                range_v_min=0.0, range_v_max=1.57, range_v_step=64,
                wrap_u=True, wrap_v=False, close_v=True, show_wire=True
            )
            circle2 = bpy.context.object
            circle2.name = "Circle2"
            circle2.scale = (x, y, z)
            circle2.location.y = 0.12  # Изменено положение
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add Circle2 surface: {e}")

        try:
            switch_to_object_mode()
            bpy.ops.mesh.primitive_cube_add(location=(0, -y / 2, t/2))
            cube = bpy.context.object
            cube.name = "Cube"
            cube.scale = (x, y / 2, t/2)

            if circle2:
                boolean_modifier = cube.modifiers.new(name="Boolean", type='BOOLEAN')
                boolean_modifier.operation = 'DIFFERENCE'
                boolean_modifier.object = circle2
                boolean_modifier.solver = 'FAST'
                bpy.context.view_layer.objects.active = cube
                bpy.ops.object.modifier_apply(modifier="Boolean")
                bpy.data.objects.remove(circle2, do_unlink=True)  # Удаляем второй круг
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add Cube or apply Boolean: {e}")


        for obj in [circle, triangle]:
            try:
                solidify_modifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
                solidify_modifier.thickness = t/12
                solidify_modifier.offset = 1
                solidify_modifier.use_even_offset = False
                solidify_modifier.use_rim = True
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier="Solidify")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to add or apply Solidify to {obj.name}: {e}")

        for obj in [circle, triangle, cube]:
            try:
                array_modifier = obj.modifiers.new(name="Array", type='ARRAY')
                array_modifier.count = 3
                array_modifier.relative_offset_displace = (1, 0, 0)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier="Array")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to add or apply Array to {obj.name}: {e}")
# Добавляем Cube2
        try:
            bpy.ops.mesh.primitive_cube_add(location=(x * 2, -y - 0.75*t, 0.25*t))  # Позиция Cube2
            cube2 = bpy.context.object
            cube2.name = "Cube2"
            cube2.scale = (x * 3, 0.75*t, 0.75*t)  # Масштаб Cube2 по X: x*3, Y и Z по t
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create Cube2: {e}")

        # Добавляем Cylinder
        try:
            bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=2, location=(x * 2, -y - 1.5*t, -t/2))
            cylinder = bpy.context.object
            cylinder.name = "Cylinder"
            cylinder.scale = (t*1.5, t*1.5, x * 3)  

            # Поворот цилиндра по оси Y на 90 градусов
            cylinder.rotation_euler[1] = math.radians(90)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create Cylinder: {e}")
            # Добавляем модификатор Boolean на Cube2
        try:
            if cube2 and cylinder:
                boolean_modifier = cube2.modifiers.new(name="Boolean", type='BOOLEAN')
                boolean_modifier.operation = 'UNION'  # Операция Union
                boolean_modifier.object = cylinder  # Объект для модификатора — Cylinder
                boolean_modifier.use_self = False  # Для предотвращения пересечения с самим собой

                # Применяем модификатор
                bpy.context.view_layer.objects.active = cube2
                bpy.ops.object.modifier_apply(modifier="Boolean")

                # Удаляем цилиндр, так как он больше не нужен
                bpy.data.objects.remove(cylinder, do_unlink=True)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply Boolean modifier: {e}")
        # Уменьшаем итоговые объекты на 0.1 относительно 3D-курсора
        
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'  # Устанавливаем Pivot Point в 3D-курсор
        bpy.context.scene.cursor.location = (0, 0, 0)  # Убедимся, что курсор находится в центре координат

        for obj in bpy.data.objects:
            bpy.context.view_layer.objects.active = obj  # Активируем объект
            bpy.ops.object.select_all(action='DESELECT')  # Снимаем выделение со всех объектов
            obj.select_set(True)  # Выделяем текущий объект
            bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))  # Масштабируем объект
            obj.select_set(False)  # Убираем выделение с объекта

        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'  # Возвращаем Pivot Point к значению по умолчанию
       
        return {'FINISHED'}
# Оператор для экспорта модели в STL с выбором пути и имени файла
class OBJECT_OT_export_stl(bpy.types.Operator):
    bl_idname = "object.export_stl"
    bl_label = "Export as STL"
    bl_description = "Export the selected objects to an STL file"

    # Свойства для хранения пути и имени файла
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", default="C:/Users/YourUsername/Documents/heart_valve_model.stl")
    scale: bpy.props.FloatProperty(name="Scale", description="Set scale for the exported STL", default=0.001,min=0.001, max=0.001)
    def execute(self, context):
        # Если файл не имеет расширения ".stl", добавляем его
        if not self.filepath.endswith(".stl"):
            self.filepath += ".stl"

        # Экспортируем модель в STL
        bpy.ops.export_mesh.stl(filepath=self.filepath, global_scale=self.scale)
        self.report({'INFO'}, f"Model exported to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Открытие диалога выбора файла
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):

        layout = self.layout

        layout.prop(self, "scale", text="Scale")
    
# Панель с кнопками
class OBJECT_PT_custom_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_custom_panel"
    bl_label = "Create Aortic Valve"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Heart Valve"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "custom_d_value", text="D Value")
        layout.prop(context.scene, "thickness_value", text="Thickness")
        layout.operator("object.add_all_surfaces", text="Create/Update Figures")
        # Добавляем кнопку экспорта в STL
        layout.operator("object.export_stl", text="Export as STL")

def register():
    bpy.utils.register_class(OBJECT_OT_add_all_surfaces)
    bpy.utils.register_class(OBJECT_OT_export_stl)
    bpy.utils.register_class(OBJECT_PT_custom_panel)
    bpy.types.Scene.custom_d_value = bpy.props.FloatProperty(
        name="D Value", description="Custom value D for calculations", default=25.0, min=12.0, max=45.0
    )
    bpy.types.Scene.thickness_value = bpy.props.FloatProperty(
        name="Thickness", description="Custom Thickness value", default=1.0, min=0.5, max=1.8
    )

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_all_surfaces)
    bpy.utils.unregister_class(OBJECT_OT_export_stl)
    bpy.utils.unregister_class(OBJECT_PT_custom_panel)
    del bpy.types.Scene.custom_d_value
    del bpy.types.Scene.thickness_value


if __name__ == "__main__":
    register()