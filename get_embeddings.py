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

# Папка с фотографиями
photo_folder = "photos/"

# Список эмбеддингов всех фотографий
embeddings = []

# Получение эмбеддингов для всех фотографий в папке
for photo_file in os.listdir(photo_folder):
    photo_path = os.path.join(photo_folder, photo_file)
    embedding = get_embedding(photo_path)
    embeddings.append(embedding)
    # print(list(embedding))
    
# print(embeddings[0])