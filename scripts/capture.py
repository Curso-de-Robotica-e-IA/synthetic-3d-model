import bpy
import os
import time
import math

num_frames = 5
path = "C:/Users/nrc2/Downloads/Capturas_Blender"

if not os.path.exists(path):
    os.makedirs(path)

if "Circle" and "Camera" not in bpy.data.objects:
    print("Plataforma nao encontrada")
    exit()
else:
    print('Plataforma OK!')

camera = bpy.data.objects["Camera"]
circle = bpy.data.objects["Circle"]

camera.parent = circle

initial_camera_offset = camera.location - circle.location

if not any(constraint.type == 'TRACK_TO' for constraint in camera.constraints):
    track_to = camera.constraints.new(type='TRACK_TO')
    track_to.target = circle  
    track_to.track_axis = 'TRACK_NEGATIVE_Z'  
    track_to.up_axis = 'UP_Y'  

bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.render.image_settings.file_format = 'PNG'

start_time = time.time()

for frames in range(num_frames):
    
    #bpy.context.scene.frame_set(frames)
    
    angle = ((-130*(math.pi/180))/num_frames) * frames
    
    circle.rotation_euler[0] = angle
    
    bpy.context.view_layer.update()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    
    file = os.path.join(path, f"frame_{frames:03d}.png")
    bpy.context.scene.render.filepath = file
  
    frame_start_time = time.time()  
    bpy.ops.render.render(write_still=True)
    frame_end_time = time.time()  
    
    elapsed_time = frame_end_time - start_time
    time_per_frame = frame_end_time - frame_start_time
    remaining_time = (num_frames - (frames + 1)) * time_per_frame

    #progresso
    print(f"Quadro {frames + 1}/{num_frames}: Ângulo: {math.degrees(angle):.2f}°")
    print(f"Tempo do quadro: {time_per_frame:.2f} segundos")
    print(f"Tempo total decorrido: {elapsed_time:.2f} segundos")
    print(f"Tempo restante estimado: {remaining_time:.2f} segundos")
    
circle.rotation_euler[0] = 0
bpy.context.view_layer.update()

print("Captura concluída!")