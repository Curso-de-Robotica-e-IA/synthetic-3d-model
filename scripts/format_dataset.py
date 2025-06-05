import os
import shutil
import random
import yaml

def process_folder(input_folder, output_folder, split_ratio=0.8):
    # Cria as pastas de destino
    os.makedirs(os.path.join(output_folder, 'images/train'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'images/test'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels/train'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels/test'), exist_ok=True)

    # Lista todas as subpastas
    all_images = []
    all_labels = []
    
    for subfolder in os.listdir(input_folder):
        subfolder_path = os.path.join(input_folder, subfolder)
        if os.path.isdir(subfolder_path):
            for file in os.listdir(subfolder_path):
                if file.endswith('.png'):
                    img_path = os.path.join(subfolder_path, file)
                    label_path = os.path.splitext(img_path)[0] + '.txt'

                    if os.path.exists(label_path):
                        all_images.append(img_path)
                        all_labels.append(label_path)

    # Embaralha as imagens para dividir em treino/validação
    data = list(zip(all_images, all_labels))
    random.shuffle(data)

    # Divide em treino e validação
    train_data = data[:int(len(data) * split_ratio)]
    val_data = data[int(len(data) * split_ratio):]

    # Função para mover as imagens e labels
    def move_files(data, data_type):
        for img_path, label_path in data:
            img_dest = os.path.join(output_folder, f'images/{data_type}', os.path.basename(img_path))
            label_dest = os.path.join(output_folder, f'labels/{data_type}', os.path.basename(label_path))

            shutil.copy(img_path, img_dest)
            shutil.copy(label_path, label_dest)

    # Move os arquivos para a estrutura de pastas
    move_files(train_data, 'train')
    move_files(val_data, 'test')

    # Cria o arquivo YAML
    create_yaml(output_folder)

def create_yaml(output_folder):
    dataset_yaml = {
        'path': os.path.abspath(output_folder),  # Caminho absoluto da pasta raiz do dataset
        'train': 'images/train',  # Caminho relativo para as imagens de treino
        'val': 'images/test',  # Caminho relativo para as imagens de validação
        'names': {
            0: 'chave_fenda'  # Nome da classe (ajustado para o exemplo fornecido)
        }
    }

    # Salva o arquivo YAML
    with open(os.path.join(output_folder, 'dataset.yaml'), 'w') as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)

# Exemplo de uso
input_folder = './'
output_folder = '../formatted_dataset'
process_folder(input_folder, output_folder)
