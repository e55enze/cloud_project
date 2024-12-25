import base64
import json
import config as cfg
from config import *
import json
from PIL import Image, ImageDraw

# Функция для кодирования файла
def encode_file(file_path):
  with open(file_path, "rb") as fid:
      file_content = fid.read()
  return base64.b64encode(file_content).decode("utf-8")

def create_body_request(encoded_content, file_mimeType):
    data = {
        "mimeType": file_mimeType,
        "languageCodes": ["*"],
        "model": "page",
        "content": encoded_content
    }
    json_name = 'body.json'
    json_path = os.path.join(PROJECT_DIR, 'data/input', json_name)
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    print("Файл body.json успешно создан.")
    return json_path

def read_body_json(json_path):
    # Чтение содержимого файла body.json
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def save_output_json(json_response):
    json_name = 'data.json'
    json_path = os.path.join(PROJECT_DIR, 'data/output', json_name)
    # Сохраняем в файл
    with open(json_path , 'w', encoding='utf-8') as json_file:
        json.dump(json_response, json_file, ensure_ascii=False, indent=4) 
    print("Файл data.json успешно сохранен.")
    return json_path 

def draw_bounding_boxes(json_path, image_path, img_name):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Извлекаем bounding boxes из JSON
    blocks = data['result']['textAnnotation']['blocks']
    for block in blocks:
        for line in block['lines']:
            # Получаем координаты bounding box для линии
            bounding_box = line['boundingBox']['vertices']
            print(bounding_box)
            coordinates = [(int(vertex['x']), int(vertex['y'])) for vertex in bounding_box]
            
            # Рисуем ограничивающий прямоугольник
            draw.line(coordinates + [coordinates[0]], fill='red', width=4)

    # Сохраняем изображение с нарисованными bounding boxes
    output_image_path = os.path.join(RECOGNIZED_DIR, img_name)
    image.save(output_image_path)
    if os.path.exists(output_image_path):
        return output_image_path
    else:
        return False