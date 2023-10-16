import os
import csv
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import os

# Загрузка предобученной модели ResNet
model = models.resnet50(pretrained=True)
model.eval()

# Предварительная обработка изображения
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Функция для получения эмбеддинга из изображения
def get_embedding(image_path):
    image = preprocess(Image.open(image_path).convert('RGB'))
    image = torch.unsqueeze(image, 0)
    with torch.no_grad():
        embedding = model(image)
    return embedding.squeeze().numpy()

# Замените на нужный путь до папки в вашей системе
directory = 'photos/'

# Получение списка файлов в указанной папке
file_list = os.listdir(directory)

# Сортировка списка файлов
file_list.sort()

   
    
# Открытие (или создание) csv файла
with open('items.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Определение заголовка
    writer.writerow(["image","embedding"])
    # Запись имен файлов в столбец
    for filename in file_list:
        photo_path = os.path.join(directory, filename)
        embedding = list(get_embedding(photo_path))
        
        writer.writerow([filename,embedding])