import os
import shutil
import uuid

def collect_images_and_labels(source_folder, dest_folder):
    """
    Copia todas as imagens e arquivos .txt de uma pasta (incluindo subpastas) para
    as pastas 'images' e 'labels' em um diretório de destino, garantindo nomes únicos
    e mantendo a correspondência correta entre imagens e anotações.
    Também cria 'validation.txt' com os caminhos relativos das imagens.

    Args:
        source_folder (str): Caminho da pasta de origem.
        dest_folder (str): Caminho da pasta de destino.
    """
    images_path = os.path.join(dest_folder, "images")
    labels_path = os.path.join(dest_folder, "labels")
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(labels_path, exist_ok=True)
    
    image_extensions = ('.jpg', '.jpeg', '.png')
    all_images = []
    
    # Percorrer todas as pastas e subpastas
    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_ext = os.path.splitext(file)
            
            if file.endswith(image_extensions):
                unique_name = f"validation_{uuid.uuid4().hex}{file_ext}"
                dest_image_path = os.path.join(images_path, unique_name)
                shutil.copy(file_path, dest_image_path)
                
                # Verificar se há um arquivo de anotação correspondente
                label_source = os.path.join(root, f"{file_name}.txt")
                if os.path.exists(label_source):
                    dest_label_path = os.path.join(labels_path, unique_name.replace(file_ext, '.txt'))
                    shutil.copy(label_source, dest_label_path)
                    all_images.append(f"images/{unique_name}")
                else:
                    print(f"[AVISO] Nenhuma anotação encontrada para {file}, imagem ignorada.")
    
    # Criar arquivo validation.txt
    validation_file = os.path.join(dest_folder, "validation.txt")
    with open(validation_file, "w") as f:
        f.write("\n".join(all_images) + "\n")
    
    print("Coleta concluída! Todas as imagens e labels foram copiadas e renomeadas corretamente.")

# Exemplo de uso
collect_images_and_labels("./", "../data_treated_2/")