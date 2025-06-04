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
        
        obj1.rotation_euler.z = -angle_rad
    
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
    
    def randomly_move_object(self, objects, x_range=(-0.3, 0.3), y_range=(-0.3, 0.3)):
        x = random.uniform(*x_range)
        y = random.uniform(*y_range)
        for obj in objects:
            # Move the object to a new random position
            obj.location = Vector((x, y, obj.location.z))
        return
            
    def reset_objects(self):
        for obj in self.objects:
            obj.rotation_euler = (0, 0, 0)
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