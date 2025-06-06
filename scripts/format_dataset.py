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
    
    # Armazena o número único de cada arquivo de imagem
    img_id = 0
    
    for subfolder in os.listdir(input_folder):
        subfolder_path = os.path.join(input_folder, subfolder)
        if os.path.isdir(subfolder_path):
            for file in os.listdir(subfolder_path):
                if file.endswith('.png'):
                    img_path = os.path.join(subfolder_path, file)
                    label_path = os.path.splitext(img_path)[0] + '.txt'

                    if os.path.exists(label_path):
                        # Cria os novos nomes para as imagens e labels
                        img_new_name = f"{subfolder}_{img_id}.png"
                        label_new_name = f"{subfolder}_{img_id}.txt"
                        
                        # Adiciona os caminhos de destino para as imagens e anotações
                        all_images.append((img_path, img_new_name))
                        all_labels.append((label_path, label_new_name))

                        # Incrementa o id único
                        img_id += 1

    # Embaralha as imagens para dividir em treino/validação
    data = list(zip(all_images, all_labels))
    random.shuffle(data)

    # Divide em treino e validação
    train_data = data[:int(len(data) * split_ratio)]
    val_data = data[int(len(data) * split_ratio):]

    # Função para mover as imagens e labels
    def move_files(data, data_type):
        for (img_path, img_new_name), (label_path, label_new_name) in data:
            # Define os caminhos de destino
            img_dest = os.path.join(output_folder, f'images/{data_type}', img_new_name)
            label_dest = os.path.join(output_folder, f'labels/{data_type}', label_new_name)

            # Copia as imagens e anotações para os diretórios de destino
            shutil.copy(img_path, img_dest)
            shutil.copy(label_path, label_dest)

    # Move os arquivos para a estrutura de pastas
    move_files(train_data, 'train')
    move_files(val_data, 'test')

    # Cria o arquivo YAML
    create_yaml(output_folder)

def create_yaml(output_folder):
    dataset_yaml = {
        'path': os.path.abspath(output_folder),
        'train': 'images/train', 
        'val': 'images/test',
        'names': {
            0: 'mosquito',
            1: 'allis',
            2: 'tesoura',
            3: 'dissecacao',
            4: 'bisturi'
        }
    }

    # Salva o arquivo YAML
    with open(os.path.join(output_folder, 'dataset.yaml'), 'w') as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)

# Exemplo de uso
input_folder = './'
output_folder = '../formatted_dataset'
process_folder(input_folder, output_folder)
