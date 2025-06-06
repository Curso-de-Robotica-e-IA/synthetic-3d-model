import bpy
import bpy_extras
from mathutils import Vector
import math
import random
import os
random.seed(42)

class AnnotationManager:
    def __init__(self, objects, class_id=0):
        self.objects = objects
        self.class_id = class_id
        self.bbox = self.get_bounding_box(objects)
        self.formatted_bbox = self.format_bounding_box(self.bbox)
    
    # Use this function to get the corners of the desired objects in the scene
    def get_bounding_box(self, objects=None):
        if objects is None:
            objects = self.objects

        scene = bpy.context.scene
        cam = scene.camera
        
        # Retorna a bounding box contendo todos os objetos
        if not objects:
            return None
        
        # Projeta cada canto da bounding box do objeto para a vista da câmera
        bbox_corners = [
            bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world @ Vector(corner))
            for obj in objects
            for corner in obj.bound_box
        ]
        if not bbox_corners:
            return None
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
    
    # Use this function to get the normalized annotation according to yolov9 standard    
    def format_bounding_box(self, bbox=None):
        if bbox is None:
            bbox = self.bbox
            
        scene = bpy.context.scene
        min_x, min_y, max_x, max_y = bbox
        class_id = self.class_id
        
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
        return (x_center, y_center, width, height, class_id)
    
    # Use this function to save the current anotation    
    def write_annotation(self, annotation_file, formatted_bbox=None):
        if formatted_bbox is None:
            formatted_bbox = self.formatted_bbox
        if formatted_bbox is None:
            return
        
        x_center, y_center, width, height, class_id = formatted_bbox
        
        annotation_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
        with open(annotation_file, "w") as f:
            f.write(annotation_line)
    
    # Use this function in case the object desired is moved
    def update_bounding_box(self):
        self.bbox = self.get_bounding_box()
        self.formatted_bbox = self.format_bounding_box()
     
     # Use this function in case the object desired is changed
    def update_object(self, objects):
        self.objects = objects
        self.update_bounding_box()

class sceneManager:
    def __init__(self, camera, plane, lights, plane_materials=None):
        if plane_materials is None:
            plane_materials = ["Fabric-03"]
        self.camera = camera
        self.plane = plane
        self.lights = lights
        self.plane_materials = plane_materials

    def setup_scene(self, camera_configs={"location": (0, 0, 2), "distortion": (0.1159, 2.8841, -0.0074, 0.0471, -11.8008), "focal_length": 35.0}, light_configs={"location": (0, 1, 2), "color": (1.0, 1.0, 1.0), "rotation": (0, 45, 0), "energy": 100}):
        # Configura a câmera
        self.setup_camera(camera_configs["location"], camera_configs["distortion"], camera_configs["focal_length"])

        # Configura a luz 
        self.light = self.setup_light(light_configs["location"], light_configs["rotation"], light_configs["color"], light_configs["energy"])

        # Configura o plano
        if len(self.plane_materials) > 0:
            for mat in self.plane_materials:
                if mat in bpy.data.materials:
                    self.plane.data.materials.append(bpy.data.materials[mat])
                else:
                    return
        else:
            self.plane.data.materials.clear()
            self.plane.data.materials.append(bpy.data.materials["Fabric-03"])
    
    def setup_camera(self, location, distortion, focal_length):
        # Configura a câmera
        if self.camera is None:
            bpy.ops.object.camera_add(location=location)
            self.camera = bpy.context.active_object
            self.camera.name = "Camera"
        else:
            if self.camera.name != "Camera":
                self.camera.name = "Camera"
        
        bpy.context.scene.camera = self.camera
        self.camera.data.type = 'PERSP'
        self.camera.data.lens = focal_length

        # Configura a distorção da lente
        ## TODO
    
    def setup_light(self, location, rotation, color, energy, light_index=0):
        # Configura a luz principal
        if self.lights is None or len(self.lights) == 0:
            bpy.ops.object.light_add(type='AREA', location=location, rotation=rotation)
            light = bpy.context.active_object
            self.lights = [light]
        else:
            light = self.lights[light_index]
        light.location = location
        light.rotation_euler = rotation
        light.data.type = 'AREA'
        light.data.color = color
        light.data.energy = energy
        light.name = "Light"
    
    def hide_other_objects(self, objects):
        selected_objects = objects
        for obj in bpy.context.scene.objects:
            # Não ocultar a câmera, luzes e o plano
            if obj.type == 'CAMERA' or obj.type == 'LIGHT' or obj.name == 'Plane':
                obj.hide_set(False)  # Mantém visível no viewport
                obj.hide_render = False  # Mantém visível na renderização
            elif obj not in selected_objects:
                obj.hide_set(True)  # Oculta no viewport
                obj.hide_render = True  # Oculta na renderização
            else:
                obj.hide_set(False)  # Torna visível no viewport
                obj.hide_render = False  # Torna visível na renderização

class ObjectManager:
    def __init__(self, objects):
        self.objects = objects
        self.flipped = False
    
    def open_and_close(self, angle_degrees, objects=None):
        if objects is None:
            objects = self.objects
        if not objects or len(objects) != 2:
            return
        
        obj1, obj2 = objects

        angle_rad = math.radians(angle_degrees)
        
        obj1.rotation_euler.z = obj2.rotation_euler.z - angle_rad
    
    def flip_objects(self):
        if not self.flipped:
            for obj in self.objects:
                obj.scale.z *= -1
            self.flipped = True
        else:
            for obj in self.objects:
                obj.scale.z *= -1
            self.flipped = False
    
    def rotate_objects(self, angle_degrees, axis='x'):
        angle_rad = math.radians(angle_degrees)
        for obj in self.objects:
            if axis == 'x':
                obj.rotation_euler.x += angle_rad
            elif axis == 'y':
                obj.rotation_euler.y += angle_rad
            elif axis == 'z':
                obj.rotation_euler.z += angle_rad
            else:
                raise ValueError("Axis must be 'x', 'y', or 'z'.")
    
    def move_objects(self, location):
        for obj in self.objects:
            obj.location = location
    
    def randomly_move(self, x_range=(-0.3, 0.3), y_range=(-0.3, 0.3), objects=None):
        if objects is None:
            objects = self.objects

        # Pega as coordenadas globais iniciais de todos os objetos
        initial_positions = {obj: obj.location.copy() for obj in objects}

        # Verifica se a lista de objetos tem mais de um item
        if len(objects) != 2:
            # Mova o único objeto individualmente
            x = random.uniform(*x_range) + initial_positions[objects[0]].x
            y = random.uniform(*y_range) + initial_positions[objects[0]].y
            obj = objects[0]
            obj.location.x = x
            obj.location.y = y
            return
        
        # Se for composto por 2 objetos, move ambos juntos
        obj1, obj2 = objects
        x = random.uniform(*x_range) + initial_positions[obj1].x
        y = random.uniform(*y_range) + initial_positions[obj1].y

        # Move os dois objetos para a nova posição aleatória baseada nas posições iniciais
        obj1.location.x = x
        obj1.location.y = y
        obj2.location.x = x
        obj2.location.y = y
            
    def reset_objects(self):
        for obj in self.objects:
            obj.rotation_euler = (0, 0, 0)
            obj.location = (0, 0, 0)
            obj.scale = (1, 1, 1)
            obj.hide_set(False)
        self.flipped = False
    
    def ocult_objects(self, objects=None):
        if objects is None:
            objects = self.objects
        for obj in objects:
            obj.hide_set(True)
    
    def return_objects(self):
        return self.objects

def generate_scenario(output_dir):
    object_count = 0

    object_class = 0

    # Process type 1: Open and close objects
    for objects in instruments1:
        object_manager = ObjectManager(objects)
        annotation_manager = AnnotationManager(objects, class_id=object_class)

        # Reset the objects to their initial state
        object_manager.reset_objects()

        # Hide other objects in the scene
        scene_manager.hide_other_objects(objects)

        # Generate variations
        angles = [ 30, 45, 60, 75 ]

        rotation_angles = [0, 30, 60, 90]

        for angle in angles:
            # Open and close the objects
            object_manager.open_and_close(angle)

            for rotation_angle in rotation_angles:
                # Flip the objects
                object_manager.flip_objects()

                # Randomly move the objects to a new position
                object_manager.randomly_move(x_range=(-0.1, 0.1), y_range=(-0.1, 0.1), objects=objects)
                # Rotate the objects in z axis
                object_manager.rotate_objects(rotation_angle, axis='z')
                
                # Save the rendered image
                bpy.context.scene.render.filepath = f"{output_dir}/{object_count}.png"
                bpy.ops.render.render(write_still=True)

                # Update the bounding box and write the annotation
                annotation_manager.update_bounding_box()
                annotation_manager.write_annotation(f"{output_dir}/{object_count}.txt")
                
                object_count += 1
        
        object_class += 1

    # Process type 2: Objects of four sides of interest
    for objects in instruments2:
        object_manager = ObjectManager(objects)
        annotation_manager = AnnotationManager(objects, class_id=object_class)

        # Reset the objects to their initial state
        object_manager.reset_objects()

        # Hide other objects in the scene
        scene_manager.hide_other_objects(objects)

        # Generate variations
        angles = [0, 90, 180, 270]

        rotation_angles = [0, 30, 60, 90]

        for angle in angles:
            # Rotate the objects in x axis
            object_manager.rotate_objects(angle)

            for rotation_angle in rotation_angles:

                # Randomly move the objects to a new position
                object_manager.randomly_move(x_range=(-0.1, 0.1), y_range=(-0.1, 0.1), objects=objects)
                # Rotate the objects in z axis
                object_manager.rotate_objects(rotation_angle, axis='z')
                
                # Save the rendered image
                bpy.context.scene.render.filepath = f"{output_dir}/{object_count}.png"
                bpy.ops.render.render(write_still=True)

                # Update the bounding box and write the annotation
                annotation_manager.update_bounding_box()
                annotation_manager.write_annotation(f"{output_dir}/{object_count}.txt")
                
                object_count += 1
        object_class += 1

    # Process type 3: Objects of two sides of interest
    for objects in instruments3:
        object_manager = ObjectManager(objects)
        annotation_manager = AnnotationManager(objects, class_id=object_class)

        # Reset the objects to their initial state
        object_manager.reset_objects()

        # Hide other objects in the scene
        scene_manager.hide_other_objects(objects)

        # Generate variations
        angles = [0, 180]

        rotation_angles = [0, 15, 30, 45, 60, 75, 90, 105]

        for angle in angles:
            # Rotate the objects in x axis
            object_manager.rotate_objects(angle)

            for rotation_angle in rotation_angles:
                # Randomly move the objects to a new position
                object_manager.randomly_move(x_range=(-0.1, 0.1), y_range=(-0.1, 0.1), objects=objects)
                # Rotate the objects in z axis
                object_manager.rotate_objects(rotation_angle, axis='z')
                
                # Save the rendered image
                bpy.context.scene.render.filepath = f"{output_dir}/{object_count}.png"
                bpy.ops.render.render(write_still=True)

                # Update the bounding box and write the annotation
                annotation_manager.update_bounding_box()
                annotation_manager.write_annotation(f"{output_dir}/{object_count}.txt")
                
                object_count += 1
        object_class += 1

# Initialize the SceneManager with the camera, circle, plane, lights, and materials
camera = bpy.data.objects.get("Camera")
plane = bpy.data.objects.get("Plane")
light_obj = bpy.data.objects.get("Light")
lights = [light_obj] if light_obj else []
scene_manager = sceneManager(camera, plane, lights, plane_materials=["Fabric-03"])

# Initialize list of objects of eacht type
instruments1 = [[bpy.data.objects["Mosquito.001"], bpy.data.objects["Mosquito.002"]], [bpy.data.objects["Allis.044"], bpy.data.objects["Allis.033"]], [bpy.data.objects["Tesoura.052"], bpy.data.objects["Tesoura.051"]]]
#instruments1 = [[bpy.data.objects["Cube.052"], bpy.data.objects["Cube.051"]]]
instruments2 = [[bpy.data.objects["Pinca.002"]]]
instruments3 = [[bpy.data.objects["Bisturi.003"]]]

### 

# Scenarios
camera_configs = {
    "location": (0, 0, 2),
    "distortion": (0.1159, 2.8841, -0.0074, 0.0471, -11.8008),
    "focal_length": 35.0
}

light_configs = {
    "location": (0, 0, 2),
    "color": (1, 1, 1),
    "rotation": (0, 0, 0),
    "energy": 100
}

scene_manager.setup_scene(camera_configs, light_configs)
output_dir = f"/home/jedl/Documents/synthetic-3d-model/datasets/dataset_1"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generate scenario
generate_scenario(output_dir)