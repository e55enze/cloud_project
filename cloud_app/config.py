import boto3
import os

IMAGES_FOLDER = 'images'
PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
UPLOADS_DIR = os.path.join(PROJECT_DIR, 'static', IMAGES_FOLDER, 'uploads')
RECOGNIZED_DIR = os.path.join(PROJECT_DIR, 'static', IMAGES_FOLDER, 'recognized')

# cloud settings
SERVICE_NAME = 's3'
ENDPOINT_URL = 'https://storage.yandexcloud.net'
URL_RECOGNIZE = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

# ID каталога
X_FOLDER_ID = "b1ggiju886isv7qqdb3v"
# Authorization
API_KEY = "AQVNxDIJMzEoCvXqr733MF6danFzajMSlVq7IFwU"

path_file = "B:\Projects\VSCode\magistry\\3sem\cloud_project\\" 