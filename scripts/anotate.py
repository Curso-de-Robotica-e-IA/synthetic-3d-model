import cv2
import os
import numpy as np

# Configurações
RESIZED_WIDTH = 640
RESIZED_HEIGHT = 640
SAVE_RESIZED_IMAGES = True
RESIZED_IMAGE_FOLDER = "../dataset/images640"
IMAGE_FOLDER = "../dataset/images"
LABEL_FOLDER = "../dataset/labels"
CLASSES = ["afastador", "bisturi", "dissecacao", "tesoura", "mosquito", "allis"]

os.makedirs(RESIZED_IMAGE_FOLDER, exist_ok=True)
os.makedirs(LABEL_FOLDER, exist_ok=True)

current_class = 0
drawing = False
ix, iy = -1, -1
bbox = []

def letterbox(img, new_shape=(640, 640), color=(174, 173, 28)):
    shape = img.shape[:2]  # (h, w)
    ratio = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpadded = (int(round(shape[1] * ratio)), int(round(shape[0] * ratio)))
    img_resized = cv2.resize(img, new_unpadded, interpolation=cv2.INTER_LINEAR)

    dw = new_shape[1] - new_unpadded[0]
    dh = new_shape[0] - new_unpadded[1]
    top, bottom = dh // 2, dh - dh // 2
    left, right = dw // 2, dw - dw // 2

    img_padded = cv2.copyMakeBorder(img_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img_padded, ratio, (left, top)

def draw_bbox(event, x, y, flags, param):
    global ix, iy, drawing, bbox, img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp = img.copy()
        cv2.rectangle(temp, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow("image", temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x_min, x_max = sorted([ix, x])
        y_min, y_max = sorted([iy, y])
        bbox.append([current_class, x_min, y_min, x_max, y_max])
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(img, CLASSES[current_class], (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
        cv2.imshow("image", img)

def save_annotations(label_path, bbox_list, img_width, img_height):
    with open(label_path, 'w') as f:
        for cls_id, x1, y1, x2, y2 in bbox_list:
            x_center = ((x1 + x2) / 2) / img_width
            y_center = ((y1 + y2) / 2) / img_height
            w = (x2 - x1) / img_width
            h = (y2 - y1) / img_height
            f.write(f"{cls_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

# Loop por imagem
for filename in sorted(os.listdir(IMAGE_FOLDER)):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    img_path = os.path.join(IMAGE_FOLDER, filename)
    label_path = os.path.join(LABEL_FOLDER, os.path.splitext(filename)[0] + ".txt")
    bbox = []

    original_img = cv2.imread(img_path)
    img, ratio, (pad_x, pad_y) = letterbox(original_img, new_shape=(RESIZED_HEIGHT, RESIZED_WIDTH))

    if SAVE_RESIZED_IMAGES:
        resized_save_path = os.path.join(RESIZED_IMAGE_FOLDER, filename)
        cv2.imwrite(resized_save_path, img)

    h, w = img.shape[:2]
    clone = img.copy()

    cv2.imshow("image", img)
    cv2.setMouseCallback("image", draw_bbox)

    while True:
        key = cv2.waitKey(0)

        if key == ord('c'):
            current_class = (current_class + 1) % len(CLASSES)
            print(f"Classe atual: {CLASSES[current_class]} ({current_class})")

        elif key == ord('s'):
            save_annotations(label_path, bbox, w, h)
            print(f"Anotações salvas para {filename}")
            break

        elif key == ord('r'):
            bbox = []
            img = clone.copy()
            cv2.imshow("image", img)

        elif key == ord('d'):
            if bbox:
                removed = bbox.pop()
                print(f"Bounding box removida: {removed}")
                img = clone.copy()
                for cls_id, x1, y1, x2, y2 in bbox:
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, CLASSES[cls_id], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
                cv2.imshow("image", img)
            else:
                print("Nenhuma bounding box para remover.")

        elif key == 27:  # ESC
            print("Saindo...")
            exit()

cv2.destroyAllWindows()
