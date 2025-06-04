class sceneManager:
    def __init__(self, camera, plane, lights, plane_materials=None):
        if plane_materials is None:
            plane_materials = ["Fabric-03"]
        self.camera = camera
        self.plane = plane
        self.lights = lights
        self.plane_materials = plane_materials

    def setup_scene(self, camera_configs={"location": (0, 0, 2)}, light_configs={"location": (0, 1, 2), "color": (1.0, 1.0, 1.0), "rotation": (0, 45, 0)}):
        # Configura a câmera
        self.setup_camera(camera_configs["location"])

        # Configura a luz 
        self.light = self.setup_light(light_configs["location"], light_configs["rotation"], light_configs["color"])

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
    
    def setup_camera(self, location):
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
        self.camera.data.lens = 35
    
    def setup_light(self, location, rotation, color, light_index=0):
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
        light.data.energy = 1000
        light.name = "Light"