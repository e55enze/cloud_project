from flask import Flask, redirect, request, render_template, jsonify, url_for
import boto3
import os
import requests
from botocore.exceptions import NoCredentialsError
import config as cfg
from config import *
import recognize as rcg
import json

app = Flask(__name__, template_folder='../templates', static_folder='../static')

s3 = boto3.client(
    's3',
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Нет файла для загрузки'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Не выбрано изображение'}), 400
    
    # Сохранение изображения
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    file.save(file_path)
    return jsonify({'message': 'Файл успешно загружен'}), 200


@app.route('/recognize-text', methods=['POST'])
def recognize_text():
    if 'image' not in request.files:
        return jsonify({'error': 'Нет файла для отправки'}), 400
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Не выбрано изображение'}), 400
    file_name = file.filename
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    file_mimeType = file.content_type.split("/")[1].upper()
    content_base_64 = rcg.encode_file(file_path)
    json_path = rcg.create_body_request(content_base_64, file_mimeType)
    data_json = rcg.read_body_json(json_path)
    print(data_json.get('mimeType'))
    
    data = {
        "mimeType": data_json.get('mimeType'),
        "languageCodes": ["*"],
        "content": data_json.get('content')
    }

    headers= {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {:s}".format(API_KEY),
        "x-folder-id": X_FOLDER_ID,
        "x-data-logging-enabled": "true"}
    
    # Отправляем POST-запрос к API
    response = requests.post(url=URL_RECOGNIZE, headers=headers, data=json.dumps(data))

    # Обрабатываем ответ от API
    if response.status_code == 200:
        # Получаем байты из ответа и декодируем в UTF-8
        json_response_dec = response.content.decode('utf-8')
        print('json response dec (type): ', type(json_response_dec))
        # Преобразуем строку в JSON-объект
        json_response = json.loads(json_response_dec)
        json_path = rcg.save_output_json(json_response)

        if json_path != '':
            # file_path - путь к изображению, file_name - названия изображения
            output_image_path = rcg.draw_bounding_boxes(json_path, file_path, file_name)

            if output_image_path != False:
                # Создаем относительный путь для изображения
                relative_path = 'images/recognized/' + file_name  # Здесь проверьте правильный относительный путь
                output_image_url = url_for('static', filename=relative_path)  # Получаем URL для доступа к изображению
                print(output_image_url)

                full_text = json_response['result']['textAnnotation']['fullText'].strip()

                # Возвращаем путь к изображению вместе с ответом
                return jsonify({
                    'data': response.json(), 
                    'output_image_path': output_image_url,
                    'full_text': full_text
                }), 200
            else:
                print('Ошибка! Файл не был сохранен по данному пути:', output_image_path)

    else:
        return jsonify({"error": response.text}), response.status_code
    

@app.route('/upload-to-bucket', methods=['POST'])
def upload_file_to_bucket():
    bucket_name = 'ccv-rgb'
    print('service name: {}\nendpoint url: {}'.format(SERVICE_NAME, ENDPOINT_URL))
    session = boto3.session.Session()
    s3 = session.client(
        service_name = SERVICE_NAME,
        endpoint_url = ENDPOINT_URL
    )

    if 'image' not in request.files:
        return jsonify({'error': 'Нет файла для загрузки'}), 400

    file = request.files['image']
    file_name = file.filename
    file_path = os.path.join(UPLOADS_DIR, file_name)
    print('file path:', file_path)

    if file.filename == '':
        return jsonify({'error': 'Не выбрано изображение'}), 400

    try:
        s3.upload_file(file_path, bucket_name, file_name)
        print('File has been uploaded')
        return jsonify({'message': 'Файл успешно загружен'}), 200
    
    except NoCredentialsError:
        return jsonify({'error': 'Проблема с доступом к S3'}), 403


@app.route('/buckets', methods=['GET'])
def list_buckets():
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    print(buckets)
    return jsonify(buckets)

@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['name']
    print('bucket-name',bucket_name)
    s3.create_bucket(Bucket=bucket_name)
    return redirect(url_for('index'))

@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    bucket_name = request.form['bucket']
    s3.delete_bucket(Bucket=bucket_name)
    return redirect(url_for('index'))

@app.route('/list_objects', methods=['POST'])
def list_objects():
    bucket_name = request.form['name']
    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        objects = [obj['Key'] for obj in response['Contents']]
    else:
        objects = []
    return jsonify(objects)

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request)
    bucket_name = request.form['bucket']
    
    file = request.files['file']
    s3.upload_fileobj(file, bucket_name, file.filename)
    return redirect(url_for('index'))

@app.route('/delete_object', methods=['POST'])
def delete_object():
    bucket_name = request.form['bucket']
    object_name = request.form['name']
    s3.delete_object(Bucket=bucket_name, Key=object_name)
    return redirect(url_for('index'))

@app.route('/delete_all_objects', methods=['POST'])
def delete_all_objects():
    bucket_name = request.form.get('name')
    if not bucket_name:
        return jsonify({'error': 'Имя бакета не указано'}), 400

    try:
        objects_to_delete = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' not in objects_to_delete:
            return jsonify({'message': 'Содержимое бакета пусто или не существует'}), 200

        # Создаем список с объектами для удаления
        objects = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
        
        return jsonify({'message': 'Все объекты были успешно удалены из бакета'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)