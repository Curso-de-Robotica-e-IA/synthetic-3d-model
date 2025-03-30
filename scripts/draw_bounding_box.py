import cv2
import os
import glob

def draw_bounding_box(image, bbox_file):
    with open(bbox_file, "r") as f:
        lines = f.readlines()
    
    h, w = image.shape[:2]
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        _, x_center, y_center, bbox_width, bbox_height = map(float, parts)
        
        x1 = int((x_center - bbox_width / 2) * w)
        y1 = int((y_center - bbox_height / 2) * h)
        x2 = int((x_center + bbox_width / 2) * w)
        y2 = int((y_center + bbox_height / 2) * h)
        
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return image

def process_images(folder_path):
    image_extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff')
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))
    
    for image_path in image_paths:
        txt_path = os.path.splitext(image_path)[0] + ".txt"
        if not os.path.exists(txt_path):
            print(f"Sem bounding box para: {image_path}")
            continue
        
        img = cv2.imread(image_path)
        if img is None:
            print(f"Erro ao carregar imagem: {image_path}")
            continue
        
        img_with_bbox = draw_bounding_box(img, txt_path)
        
        cv2.imshow("Bounding Box", img_with_bbox)
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        cv2.destroyAllWindows()

if __name__ == "__main__":
    folder = input("Digite o caminho da pasta: ")
    process_images(folder)
