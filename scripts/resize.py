import cv2
import os
import glob

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

def process_images(folder_path):
    image_extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff')
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))
    
    output_folder = os.path.join(folder_path, "resized")
    os.makedirs(output_folder, exist_ok=True)
    
    for image_path in image_paths:
        print(f"Processando: {image_path}")
        img = cv2.imread(image_path)
        img_resized = resize_and_crop(img)
        
        filename = os.path.basename(image_path)
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, img_resized)
        print(f"Imagem salva em: {output_path}")

if __name__ == "__main__":
    folder = input("Digite o caminho da pasta: ")
    process_images(folder)
