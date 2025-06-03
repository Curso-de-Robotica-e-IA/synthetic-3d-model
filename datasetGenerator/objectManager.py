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
        half_angle = angle_rad / 2
        
        obj1.rotation_euler.z = -half_angle
        obj2.rotation_euler.z = half_angle
    
    def flip_objects(self):
        if not self.flipped:
            for obj in self.objects:
                obj.scale.z *= -1
            self.flipped = True
        else:
            for obj in self.objects:
                obj.scale.z *= -1
            self.flipped = False
    
    def rotate_objects(self, angle_degrees):
        angle_rad = math.radians(angle_degrees)
        for obj in self.objects:
            obj.rotation_euler.x += angle_rad
    
    def move_objects(self, location):
        for obj in self.objects:
            obj.location = location
            
    def reset_objects(self):
        for obj in self.objects:
            obj.rotation_euler = (0, 0, 0)
            obj.scale = (1, 1, 1)
        self.flipped = False
    
    def return_objects(self):
        return self.objects