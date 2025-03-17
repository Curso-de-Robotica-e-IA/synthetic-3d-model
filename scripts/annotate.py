import cv2
import os
import glob

def draw_bbox(event, x, y, flags, param):
    global ix, iy, drawing, img_copy, bbox
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img_resized.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        bbox = (ix, iy, x, y)
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)

def resize_and_crop(img):
    target_size = 640
    h, w = img.shape[:2]
    
    # Redimensiona mantendo a proporção para que a altura seja 640
    scale = target_size / h
    new_w = int(w * scale)
    img_resized = cv2.resize(img, (new_w, target_size))
    
    # Recorta a largura centralmente para ficar 640x640
    start_x = max(0, (new_w - target_size) // 2)
    img_cropped = img_resized[:, start_x:start_x + target_size]
    
    return img_cropped

def process_image(image_path):
    global img, img_resized, img_copy, drawing, bbox
    
    img = cv2.imread(image_path)
    img_resized = resize_and_crop(img)
    img_copy = img_resized.copy()
    drawing = False
    bbox = None
    
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", draw_bbox)
    
    while True:
        cv2.imshow("Image", img_copy)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') and bbox:  # Salvar bounding box ao pressionar 's'
            txt_path = image_path.rsplit(".", 1)[0] + ".txt"
            x_center = (bbox[0] + bbox[2]) / 2 / 640
            y_center = (bbox[1] + bbox[3]) / 2 / 640
            bbox_width = abs(bbox[2] - bbox[0]) / 640
            bbox_height = abs(bbox[3] - bbox[1]) / 640
            
            with open(txt_path, "w") as f:
                f.write(f"0 {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
            print(f"Bounding box salva em: {txt_path}")
            break
        
        elif key == ord('d'):  # Salvar anotação sem objetos ao pressionar 'd'
            txt_path = image_path.rsplit(".", 1)[0] + ".txt"
            with open(txt_path, "w") as f:
                pass  # Criar arquivo vazio
            print(f"Nenhum objeto detectado, anotação vazia salva em: {txt_path}")
            break
        
        elif key == ord('q'):  # Sair sem salvar ao pressionar 'q'
            break
    
    cv2.destroyAllWindows()

def main(folder_path):
    image_extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff')
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))
    
    for image_path in image_paths:
        print(f"Processando: {image_path}")
        process_image(image_path)

if __name__ == "__main__":
    folder = input("Digite o caminho da pasta: ")
    main(folder)
