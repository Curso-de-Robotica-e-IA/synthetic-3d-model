import bpy
import bpy_extras

class AnnotationManager:
    def __init__(self, objects):
        self.objects = objects
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
        class_id = 0
        
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
        
        x_center, y_center, width, height, class_id = formatted_bbox
        
        annotation_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
        with open(annotation_file, "w") as f:
            f.write(annotation_line)
    
    # Use this function in case the object desired is moved
    def update_bounding_box(self):
        self.get_bounding_box()
        self.format_bounding_box()
     
     # Use this function in case the object desired is changed
    def update_object(self, objects):
        self.objects = objects
        self.update()