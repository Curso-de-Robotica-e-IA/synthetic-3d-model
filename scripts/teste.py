import cv2
import os
import glob

images_dir = "C:/Users/nrc2/Downloads/Capturas_Blender"
annotations_dir = os.path.join(images_dir, "annotations")

image_files = glob.glob(os.path.join(images_dir, "*.png"))

if not image_files:
    print("Nenhuma imagem encontrada na pasta especificada.")
    exit()

for image_file in image_files:

    image = cv2.imread(image_file)
    if image is None:
        continue

    h, w, _ = image.shape

  
    base_name = os.path.splitext(os.path.basename(image_file))[0]
    annotation_file = os.path.join(annotations_dir, base_name + ".txt")

    if os.path.exists(annotation_file):
        with open(annotation_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            # Formato YOLO: <class_id> <x_center> <y_center> <width> <height>
            class_id, x_center_norm, y_center_norm, width_norm, height_norm = parts
            x_center_norm = float(x_center_norm)
            y_center_norm = float(y_center_norm)
            width_norm = float(width_norm)
            height_norm = float(height_norm)

            # Converte as coordenadas normalizadas para pixels
            x_center = int(x_center_norm * w)
            y_center = int((1 - y_center_norm) * h) 
            bbox_width = int(width_norm * w)
            bbox_height = int(height_norm * h)

            # Define os pontos superior esquerdo e inferior direito da caixa
            x1 = int(x_center - bbox_width / 2)
            y1 = int(y_center - bbox_height / 2)
            x2 = int(x_center + bbox_width / 2)
            y2 = int(y_center + bbox_height / 2)

            # Verifica se as coordenadas estão dentro da imagem
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"ID:{class_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    else:
        print(f"Arquivo de anotação não encontrado para {base_name}")

    cv2.imshow("Verificação de Bounding Box", image)
    key = cv2.waitKey(0)
    if key == 27:  # Se pressionar ESC, encerra
        break

cv2.destroyAllWindows()
