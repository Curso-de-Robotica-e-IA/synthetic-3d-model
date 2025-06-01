import os
import shutil

# Extensões válidas para imagens
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

def is_image(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def sanitize_filename(path):
    # Remove caracteres inválidos e substitui separadores
    return path.replace(os.sep, "_").replace(":", "").replace(" ", "_")

def process_images(source_dir, destination_dir):
    os.makedirs(destination_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if is_image(file):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, start=source_dir)
                sanitized_name = sanitize_filename(relative_path)
                destination_path = os.path.join(destination_dir, sanitized_name)

                shutil.copy2(full_path, destination_path)
                print(f"Imagem copiada: {destination_path}")

# Exemplo de uso
source_folder = "../validation"
destination_folder = "../validation_organized"

process_images(source_folder, destination_folder)
