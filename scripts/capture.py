import bpy
import os
import time
import math

num_frames = 5
path = "C:/Users/nrc2/Downloads/Capturas_Blender"

if not os.path.exists(path):
    os.makedirs(path)

def create_or_configure_circle(circle_name, location, rotation_degs, scale_value):
    """
    Garante que exista um objeto com o nome 'circle_name'.
    Se não existir, cria um novo (mesh circle).
    Em seguida, configura location, rotation e scale.
    """
    if circle_name in bpy.data.objects:
        circle_obj = bpy.data.objects[circle_name]
    else:
        bpy.ops.mesh.primitive_circle_add(radius=1, location=(0,0,0))
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
    scale_value=1.095
)

circle2 = create_or_configure_circle(
    circle_name="Circle.2",
    location=(0, 0, 0),
    rotation_degs=(0, 90, 90),
    scale_value=1.095
)

# Verifica existência dos objetos
if "Camera" and "Circle" and "Cube" and "Light" not in bpy.data.objects:
    print("Falta algum objeto!")
    exit()

camera = bpy.data.objects["Camera"]
circle = bpy.data.objects["Circle"]
circle2 = bpy.data.objects["Circle.2"]
cylinder_obj = bpy.data.objects["Cube"]  #Coloque o objeto aqui

light = bpy.data.objects["Light"]
temp_colors = {
    3000: (1.0, 0.76, 0.64),  # tom mais alaranjado
    4500: (1.0, 0.85, 0.7),   # tom neutro/quente
    6500: (1.0, 1.0, 1.0),    # branco neutro
    8000: (0.85, 0.92, 1.0)   # tom mais azulado
}

light_positions = [
    (2, 2, 2),
    (2, -2, 2),
    (-2, 2, 2),
    (-2, -2, 2),
]

def ensure_track_to(obj, target):
    """ um constraint TRACK_TO em 'obj' apontando para 'target'."""
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
      - do_lens_variation: Se True, percorre vários valores de lente.
      - do_cylinder_rotation: Se True, rotaciona o objeto.
      - do_light_variation: Se True, percorre posições e temperaturas de cor para a luz.
    """
    camera.parent = circle_obj
    ensure_track_to(camera, circle_obj)
-
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
                        else:
                            pass

                        # Atualiza a cena antes de renderizar
                        bpy.context.view_layer.update()

                        # Define o nome do arquivo
                        file_name = (
                            f"{prefix}_frame{frame_idx:03d}"
                            f"_lens{lens}"
                            f"_cylAngle{cyl_angle_deg:03d}"
                            f"_lightPos{pos[0]:.1f}_{pos[1]:.1f}_{pos[2]:.1f}"
                            f"_temp{temp}.png"
                        )
                        file_path = os.path.join(path, file_name)
                        bpy.context.scene.render.filepath = file_path

                        # Renderização
                        frame_start_time = time.time()
                        bpy.ops.render.render(write_still=True)
                        frame_end_time = time.time()

                        # Progresso
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

#Chamada da função principal
render_trajectory(circle, "circle1", False, False, True)

# Exemplos de chamadas com diferentes cenários:

# Exemplo 1) Nenhuma variação extra
# (Sem lentes, sem rotação de objeto, sem variação de luz) render_trajectory(circle, "circle1_no_variation", False, False, False)

# Exemplo 2) Só variação de lentes
# render_trajectory(circle2, "circle2_lenses", do_lens_variation=True, do_cylinder_rotation=False, do_light_variation=False)

# Exemplo 3) Só rotação do objeto
# render_trajectory(circle, "circle1_objrot", do_lens_variation=False, do_cylinder_rotation=True, do_light_variation=False)

# Exemplo 4) Variação de lentes + rotação do objeto
# render_trajectory(circle2, "circle2_both", True, True, False)

# Exemplo 5) Variação da luz (posição e temperatura), mas sem lentes nem rotação
# render_trajectory(circle, "circle1_lightOnly", False, False, True)

# Exemplo 6) Tudo habilitado: lentes, rotação do objeto e luz
# render_trajectory(circle2, "circle2_all", True, True, True)