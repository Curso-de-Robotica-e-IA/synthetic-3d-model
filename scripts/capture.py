import bpy
import os
import time
import math
import bpy_extras
from mathutils import Vector
from pathlib import Path

# Número de frames e caminho para salvar as imagens
num_frames = 5
base_path = "C:/Users/nrc2/Downloads/Capturas_Blender"

# Cria a pasta base, se não existir
if not os.path.exists(base_path):
    os.makedirs(base_path)

# Define a pasta de anotações separada
annotations_dir = Path(base_path) / "annotations"
if not annotations_dir.exists():
    annotations_dir.mkdir(parents=True)

def create_or_configure_circle(circle_name, location, rotation_degs, scale_value):

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

# Cria/configura os círculos (caso não existam)
circle = create_or_configure_circle(
    circle_name="Circle",
    location=(0, 0, 0),
    rotation_degs=(0, 90, 0),
    scale_value=2.095
)

circle2 = create_or_configure_circle(
    circle_name="Circle.2",
    location=(0, 0, 0),
    rotation_degs=(0, 90, 90),
    scale_value=2.095
)

# Verifica existência dos objetos
if "Camera" and "Circle" and "Cylinder.001" and "Light.001" not in bpy.data.objects:
    print("Falta algum objeto!")
    exit()

camera = bpy.data.objects["Camera"]
circle = bpy.data.objects["Circle"]
circle2 = bpy.data.objects["Circle.2"]
cylinder_obj = bpy.data.objects["Cylinder.001"]  # Objeto a ser anotado

camera.location = [-0.6074, -0.78266, 0.002921]

light = bpy.data.objects["Light.001"]
temp_colors = {
    3000: (1.0, 0.76, 0.64),
    4500: (1.0, 0.85, 0.7),
    6500: (1.0, 1.0, 1.0),
    8000: (0.85, 0.92, 1.0)
}

light_positions = [
    (2, 2, 2),
    (2, -2, 2),
    (-2, 2, 2),
    (-2, -2, 2),
]

def get_bounding_box(obj_name):
   
    obj = bpy.data.objects[obj_name]
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

def write_annotations(obj_name, image_path, annotations_folder, class_id=0):
 
    scene = bpy.context.scene
    min_x, min_y, max_x, max_y = get_bounding_box(obj_name)
    
    x_center = (min_x + max_x) / 2
    y_center = (min_y + max_y) / 2
    width = max_x - min_x
    height = max_y - min_y
    
    x_center /= scene.render.resolution_x
    y_center /= scene.render.resolution_y
    width /= scene.render.resolution_x
    height /= scene.render.resolution_y
    
    if x_center < 0 or x_center > 1 or y_center < 0 or y_center > 1:
        print(f"Objeto {obj_name} fora dos limites, anotação não gerada.")
        return
    
    annotation_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
    annotation_file = annotations_folder / f"{Path(image_path).stem}.txt"
    with open(annotation_file, "w") as f:
        f.write(annotation_line)

def ensure_track_to(obj, target):
    """Adiciona ou configura um constraint TRACK_TO em 'obj' para apontar para 'target'."""
    for c in obj.constraints:
        if c.type == 'TRACK_TO':
            c.target = target
            return
    track_to = obj.constraints.new(type='TRACK_TO')
    track_to.target = target  
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'

def render_trajectory(
    circle_obj, 
    prefix, 
    do_lens_variation=False, 
    do_cylinder_rotation=False,
    do_light_variation=False
):
    """
    Renderiza a trajetória da câmera presa ao círculo para diferentes frames.
    
    Parâmetros:
      - do_lens_variation: Se True, variação de valores de lente.
      - do_cylinder_rotation: Se True, rotaciona o objeto (eixo Z).
      - do_light_variation: Se True, variação na posição e temperatura da luz.
    """
    camera.parent = circle_obj
    ensure_track_to(camera, circle_obj)

    if do_lens_variation:
        lens_values = [20, 35, 55]
    else:
        lens_values = [camera.data.lens]

    if do_cylinder_rotation:
        cylinder_angles = list(range(0, 361, 60))
    else:
        cylinder_angles = [0]

    if do_light_variation:
        possible_positions = light_positions
        possible_temps = list(temp_colors.keys())
    else:
        possible_positions = [light.location.copy()]
        current_color = light.data.color
        possible_temps = [6500]
        temp_colors[6500] = (current_color[0], current_color[1], current_color[2])

    total_subframes = (
        num_frames 
        * len(lens_values) 
        * len(cylinder_angles)
        * len(possible_positions)
        * len(possible_temps)
    )
    subframe_count = 0
    start_time = time.time()

    for frame_idx in range(num_frames):
       
        angle = ((-130 * (math.pi / 180)) / num_frames) * frame_idx
        circle_obj.rotation_euler[0] = angle

        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        for lens in lens_values:
            camera.data.lens = lens

            for cyl_angle_deg in cylinder_angles:
                cylinder_obj.rotation_euler[2] = math.radians(cyl_angle_deg)

                for pos in possible_positions:
                    light.location = pos

                    for temp in possible_temps:
                        if temp in temp_colors:
                            light.data.color = temp_colors[temp]
                        bpy.context.view_layer.update()

                       
                        file_name = f"{prefix}_{subframe_count:04d}.png"
                        file_path = os.path.join(base_path, file_name)
                        bpy.context.scene.render.filepath = file_path

                        # Renderiza a imagem
                        frame_start_time = time.time()
                        bpy.ops.render.render(write_still=True)
                        frame_end_time = time.time()

                        # Salva a anotação YOLO na pasta separada
                        write_annotations("Cylinder", file_path, annotations_dir)

                        subframe_count += 1
                        elapsed_time = frame_end_time - start_time
                        time_per_subframe = frame_end_time - frame_start_time
                        remaining_time = (total_subframes - subframe_count) * time_per_subframe

                        print(
                            f"{prefix} - Frame {frame_idx + 1}/{num_frames} | "
                            f"Lens={lens}mm | "
                            f"CylAngle={cyl_angle_deg}° | "
                            f"LightPos={pos} | "
                            f"Temp={temp}K | "
                            f"CircAngle={math.degrees(angle):.2f}°"
                        )
                        print(
                            f"Tempo subframe: {time_per_subframe:.2f}s | "
                            f"Decorrido: {elapsed_time:.2f}s | "
                            f"Restante: {remaining_time:.2f}s"
                        )
                        
    circle_obj.rotation_euler[0] = 0
    cylinder_obj.rotation_euler[2] = 0
    bpy.context.view_layer.update()
    print(f"Captura da trajetória '{prefix}' concluída!")

# Configurações de renderização
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Chamada da função principal (exemplo: variação apenas na luz)
render_trajectory(circle, "Cylinder", False, False, False)

# Exemplos de chamadas com diferentes cenários:
# Exemplo 1) Sem variações extras:
# render_trajectory(circle, "Cube_no_variation", False, False, False)
# Exemplo 2) Variação de lentes:
# render_trajectory(circle2, "Cube_lenses", do_lens_variation=True, do_cylinder_rotation=False, do_light_variation=False)
# Exemplo 3) Rotação do objeto:
# render_trajectory(circle, "Cube_objrot", do_lens_variation=False, do_cylinder_rotation=True, do_light_variation=False)
# Exemplo 4) Lentes + rotação do objeto:
# render_trajectory(circle2, "Cube_both", True, True, False)
# Exemplo 5) Apenas variação da luz:
# render_trajectory(circle, "Cube_lightOnly", False, False, True)
# Exemplo 6) Tudo habilitado:
# render_trajectory(circle2, "Cube_all", True, True, True)
