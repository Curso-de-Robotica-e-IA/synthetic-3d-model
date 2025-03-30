import bpy
import bpy_extras
import os
import time
import math
import random
from mathutils import Vector
from pathlib import Path

class DatasetGenerator:
    def __init__(self, object=None, plane_materials=[]):
        self.plane_materials = plane_materials
        self.obj = object
        self.num_frames = 1

        self.camera = bpy.data.objects["Camera"]
        self.circle = bpy.data.objects["Circle"]
        self.plane = bpy.data.objects["Plane"]
        
        # Configura o render
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        bpy.context.scene.render.image_settings.file_format = 'PNG'

        # Configura o cenário
        self.setup_scene()

    def setup_scene(self):
        # Configura a câmera
        self.camera.data.lens = 35
        self.camera.data.clip_start = 0.1
        self.camera.data.clip_end = 1000
        self.camera.location = [ -1.5, 0, 0]

        # Configura o círculo
        self.circle = self.configure_circle(
            circle_name="Circle",
            location=(0, 0, 0),
            rotation_degs=(0, 90, 0),
            scale_value=2.095
        )

        # Configura a luz principal
        self.light = self.configure_main_light(
            light_name="Light.001",
            location=(0, 0, 2),
            color=(1.0, 1.0, 1.0)
        )

        # Configura o objeto
        if self.obj is not None:
            self.obj.location = (0, -0.53363, 0.1)
            self.obj.rotation_euler = (0, 90, 0)

        # Configura o plano
        if len(self.plane_materials) > 0:
            for mat in self.plane_materials:
                if mat in bpy.data.materials:
                    self.plane.data.materials.append(bpy.data.materials[mat])
                else:
                    print(f"Material {mat} não encontrado.")
        else:
            self.plane.data.materials.clear()
            self.plane.data.materials.append(bpy.data.materials["Fabric-03"])
    
    def configure_circle(self, circle_name, location, rotation_degs, scale_value):
        if circle_name in bpy.data.objects:
            circle_obj = bpy.data.objects[circle_name]
        else:
            bpy.ops.mesh.primitive_circle_add(radius=1, location=(0, 0, 0))
            circle_obj = bpy.context.active_object
            circle_obj.name = circle_name
        
        circle_obj.location = location
        circle_obj.rotation_mode = 'YZX'
        circle_obj.rotation_euler = tuple(math.radians(a) for a in rotation_degs)
        circle_obj.scale = (scale_value, scale_value, scale_value)
        
        return circle_obj
    
    def configure_main_light(self, light_name, location, color):
        if light_name in bpy.data.objects:
            light_obj = bpy.data.objects[light_name]
        else:
            bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
            light_obj = bpy.context.active_object
            light_obj.name = light_name
        
        light_obj.location = location
        light_obj.data.color = color
        return light_obj
    
    def randomly_move_object_xy(self, obj_to_change, x_range=(-0.3, 0.3), y_range=(-0.3, 0.3)):
        obj_to_change.location = Vector((0.0, 0.0, 0.0))
        obj_to_change.location.x = random.uniform(*x_range)
        obj_to_change.location.y = random.uniform(*y_range)
    
    def replace_material(self, obj, obj_data, mat_src, mat_dst):
        for i in range(len(obj_data.materials)):
            if obj_data.materials[i] == mat_src:
                obj_data.materials[i] = mat_dst
    
    def ensure_track_to(self, obj, target):
        for c in obj.constraints:
            if c.type == 'TRACK_TO':
                c.target = target
                return
        track_to = obj.constraints.new(type='TRACK_TO')
        track_to.target = target  
        track_to.track_axis = 'TRACK_NEGATIVE_Z'
        track_to.up_axis = 'UP_Y'
    
    def get_bounding_box(self, obj):
        obj = obj
        scene = bpy.context.scene
        cam = scene.camera

        # Projeta cada canto da bounding box do objeto para a vista da câmera
        bbox_corners = [
            bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world @ Vector(corner))
            for corner in obj.bound_box
        ]
        
        min_x = min(corner.x for corner in bbox_corners)
        max_x = max(corner.x for corner in bbox_corners)
        min_y = min(corner.y for corner in bbox_corners)
        max_y = max(corner.y for corner in bbox_corners)
    
        # Converte para pixels (usando a resolução da render)
        min_x *= scene.render.resolution_x
        max_x *= scene.render.resolution_x
        min_y *= scene.render.resolution_y
        max_y *= scene.render.resolution_y

        return (min_x, min_y, max_x, max_y)

    def write_annotations(self, obj, image_path, annotations_folder, class_id=0):
    
        scene = bpy.context.scene
        min_x, min_y, max_x, max_y = self.get_bounding_box(obj)
        
        x_center = (min_x + max_x) / 2
        y_center = scene.render.resolution_y - (min_y + max_y) / 2
        width = max_x - min_x
        height = max_y - min_y
        
        x_center /= scene.render.resolution_x
        y_center /= scene.render.resolution_y
        width /= scene.render.resolution_x
        height /= scene.render.resolution_y
        
        if x_center < 0 or x_center > 1 or y_center < 0 or y_center > 1:
            print(f"Objeto fora dos limites, anotação não gerada.")
            return
        
        annotation_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
        annotation_file = annotations_folder / f"{Path(image_path).stem}.txt"
        with open(annotation_file, "w") as f:
            f.write(annotation_line)
    
    def render(self, prefix, base_path="/home/julia/Downloads/Capturas_Blender", lens_values=[], cylinder_angles=[], temp_colors={}, light_positions=[], random_moves=False, cable_materials=[]):
        base_path = base_path
        annotations_dir = Path(base_path) / "annotations"

        # Cria a pasta base, se não existir
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Cria a pasta de anotações, se não existir
        if not os.path.exists(annotations_dir):
            annotations_dir.mkdir(parents=True)
        
        # Configura a câmera
        self.camera.parent = self.circle
        self.ensure_track_to(self.camera, self.circle)

        # Configura as posições da iluminação variável
        if light_positions:
            possible_positions = light_positions
        else:
            possible_positions = [self.light.location.copy()]
        
        # Configura as temp. da iluminação variável
        if temp_colors:
            possible_temps = list(temp_colors.keys())
        else:
            possible_temps = [6500]
            temp_colors[6500] = (self.light.data.color[0], self.light.data.color[1], self.light.data.color[2])
        
        # Garante que o objeto esteja na posição correta
        self.obj.location = (0, 0, 0)
        self.obj.rotation_euler = (0, math.radians(90), 0)

        # Gera as imagens
        subframe_count = 0
        for lens in lens_values:
            self.camera.data.lens = lens

            for cyl_angle_deg in cylinder_angles:
                self.obj.rotation_euler = (0, math.radians(90), math.radians(cyl_angle_deg))

                for pos in possible_positions:
                    self.light.location = pos

                    for temp in possible_temps:
                        if temp in temp_colors:
                            self.light.data.color = temp_colors[temp]
                        
                        bpy.context.view_layer.update()
                        
                        if random_moves:
                            if lens < 35:
                                self.obj.location = (0, 0, 0)
                                self.randomly_move_object_xy(self.obj, x_range=(-0.1, 0.1), y_range=(-0.1, 0.1))
                            else:
                                self.randomly_move_object_xy(self.obj)
                        
                        if subframe_count % 2 == 0 and len(cable_materials) > 1:
                            self.replace_material(self.obj, self.obj.data, bpy.data.materials[cable_materials[0]], bpy.data.materials[cable_materials[1]])
                        elif len(cable_materials) > 1:
                            self.replace_material(self.obj, self.obj.data, bpy.data.materials[cable_materials[1]], bpy.data.materials[cable_materials[0]])
                        
                        bpy.context.view_layer.update()
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

                        file_name = f"{prefix}_{subframe_count:04d}.png"
                        file_path = os.path.join(base_path, file_name)
                        bpy.context.scene.render.filepath = file_path

                        # Renderiza a imagem
                        bpy.ops.render.render(write_still=True)

                        # Salva a anotação YOLO na pasta separada
                        self.write_annotations(self.obj, file_path, annotations_dir)

                        subframe_count += 1

        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# Exemplo de uso

datasetGenerator = DatasetGenerator(
    object=bpy.data.objects["Cylinder"],
    plane_materials=["Fabric-03"]
)

# Dataset 1: Rotations
temp_colors = {
    4500: (1.0, 0.85, 0.7),
}

light_positions = [
    (0.6, 0.6, 2),
]

lens_values = [50]
cylinder_angles = list(range(0, 360, 1))
base_path = "/home/julia/Downloads/dataset_1"

datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 2: Lens Variations
temp_colors = {
    4500: (1.0, 0.85, 0.7),
}

light_positions = [
    (0.6, 0.6, 2),
]

lens_values = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
cylinder_angles = list(range(0, 360, 15))
base_path = "/home/julia/Downloads/dataset_2"

datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 3: Light Variations (position)
temp_colors = {
    4500: (1.0, 0.85, 0.7),
}

light_positions = [
    (0.7, 0.7, 2),
    (0.7, -0.7, 2),
    (-0.7, 0.7, 2),
    (-0.7, -0.7, 2),
    (0.0, 0.0, 2),
    (0.7, 0.0, 2),
    (-0.7, 0.0, 2),
    (0.0, 0.7, 2),
    (0.0, -0.7, 2),
    (0.4, 0.4, 2),
    (-0.4, -0.4, 2),
    (0.4, -0.4, 2),
    (-0.4, 0.4, 2),
    (0.3, -0.6, 2),
    (-0.3, 0.6, 2),
]

lens_values = [50]
cylinder_angles = list(range(0, 360, 15))
base_path = "/home/julia/Downloads/dataset_3"

datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 4: Light Variations (temperatures)
temp_colors = {
    3000: (1.0, 0.76, 0.64),
    3400: (1.0, 0.79, 0.66),
    3800: (1.0, 0.81, 0.68),
    4200: (1.0, 0.83, 0.69),
    4500: (1.0, 0.85, 0.70),
    4800: (1.0, 0.89, 0.74),
    5100: (1.0, 0.92, 0.78),
    5400: (1.0, 0.95, 0.84),
    5700: (1.0, 0.97, 0.90),
    6000: (1.0, 0.99, 0.96),
    6500: (1.0, 1.0, 1.0),
    6800: (0.94, 0.97, 1.0),
    7100: (0.91, 0.95, 1.0),
    7500: (0.88, 0.93, 1.0),
    8000: (0.85, 0.92, 1.0)
}

light_positions = [
    (0.6, 0.6, 2),
]

lens_values = [50]
cylinder_angles = list(range(0, 360, 15))
base_path = "/home/julia/Downloads/dataset_4"

datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 5: Light Variations (positions and temperatures)

temp_colors = {
    3000: (1.0, 0.76, 0.64),
    3800: (1.0, 0.81, 0.68),
    4800: (1.0, 0.89, 0.74),
    5100: (1.0, 0.92, 0.78),
    6500: (1.00, 1.00, 1.00),
}

light_positions = [
    (-0.7, -0.7, 2),
    (0.7, -0.7, 2),
    (-0.7, 0.7, 2)
]

lens_values = [50]
cylinder_angles = list(range(0, 360, 15))
base_path = "/home/julia/Downloads/dataset_5"

datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 6: Light and Lens Variations (positions)
temp_colors = {
    4500: (1.0, 0.85, 0.7),
}

light_positions = [
    (0.6, 0.6, 2),
    (0.6, -0.6, 2),
    (-0.6, 0.6, 2),
]

lens_values = [ 30, 35, 45, 55, 65]
cylinder_angles = list(range(0, 360, 15))
base_path = "/home/julia/Downloads/dataset_6"
datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 7: Light and Lens Variations (temperatures)
temp_colors = {
    3000: (1.0, 0.76, 0.64),
    4500: (1.0, 0.85, 0.7),
    6500: (1.0, 1.0, 1.0),
}
light_positions = [
    (0.6, 0.6, 2),
]
lens_values = [ 30, 35, 45, 55, 65]
cylinder_angles = list(range(0, 360, 15))
base_path = "/home/julia/Downloads/dataset_7"
datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 8: All Variations
temp_colors = {
    3000: (1.0, 0.76, 0.64),
    4500: (1.0, 0.85, 0.7),
    6500: (1.0, 1.0, 1.0),
}
light_positions = [
    (0.6, 0.6, 2),
    (0.6, -0.6, 2),
    (-0.6, 0.6, 2),
]

lens_values = [ 35, 45, 55]
cylinder_angles = list(range(0, 360, 24))
base_path = "/home/julia/Downloads/dataset_8"
datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Fabric-03"]
)

# Dataset 9: All Variations with two cables
temp_colors = {
    3000: (1.0, 0.76, 0.64),
    4500: (1.0, 0.85, 0.7),
    6500: (1.0, 1.0, 1.0),
}
light_positions = [
    (0.6, 0.6, 2),
    (0.6, -0.6, 2),
    (-0.6, 0.6, 2),
]

lens_values = [ 35, 45, 55]
cylinder_angles = list(range(0, 360, 24))
base_path = "/home/julia/Downloads/dataset_9"
datasetGenerator.render(
    prefix="cylinder",
    base_path=base_path,
    lens_values=lens_values,
    cylinder_angles=cylinder_angles,
    temp_colors=temp_colors,
    light_positions=light_positions,
    random_moves=True,
    cable_materials=["Plastic-01", "Plastic-02"]
)