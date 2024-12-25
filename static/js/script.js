// Функция отрисовки входного изображения в img_input_wrapper
function renderInputImage(imageFile) {
    let img_input_wrapper = document.querySelector('.img_input_wrapper');
    console.log(imageFile)
    console.log(img_input_wrapper);
    let reader = new FileReader();
    reader.readAsDataURL(imageFile);
    reader.onload = function () {
        const element = document.getElementById("image-input")
        // console.log(element)
        if (element != null){
            element.remove()
        }
        let img_input = document.createElement('img');
        img_input.setAttribute("id", "image-input");
        img_input_wrapper.appendChild(img_input);
        img_input.src = reader.result;
    }
}

// Функция отрисовки выходного изображения (с баундинг боксами) в img_output_wrapper
function renderOutputImage(data) {
    let imgOutputWrapper = document.querySelector('.img_output_wrapper');
    const outputImagePath = data.output_image_path;
    console.log('Путь к изображению с bounding box:', outputImagePath);

    if (!outputImagePath) {
        console.error('Нет пути к изображению');
        return; 
    }
    let imgOutput = document.createElement('img');
    imgOutput.setAttribute("id", "image-output");
    imgOutput.src = outputImagePath;

    // Обработчик события для проверки загрузки изображения
    imgOutput.onload = function() {
        console.log('Изображение успешно загружено');
    }

    imgOutput.onerror = function() {
        console.error('Ошибка загрузки изображения. Убедитесь, что путь к изображению правильный.');
    }

    const existingImg = document.getElementById("image-output");
    if (existingImg) {
        existingImg.remove(); // Удаляем предыдущее изображение, если оно есть
    }
    imgOutputWrapper.appendChild(imgOutput); // Добавляем новое изображение в обертку
}


function setFullTextFromImg(data){
    // let textArea = document.querySelector('#recognized_txt');
    let textArea = document.getElementById('recognized_txt'); 
    const fullTxt = data.full_text
    textArea.value =fullTxt
}

document.getElementById('recognize-form').onsubmit = function(event) {
    event.preventDefault();  // Предотвращаем стандартное поведение формы
    const imageFile = document.getElementById('imageInput').files[0];
    console.log(imageFile)
    var formData = new FormData();
    formData.append('image', imageFile);
    fetch('/recognize-text', {
        method: 'POST', // или другой метод в зависимости от вашего API
        body: formData // здесь вы отправляете данные
    })
    .then(response => {
        if (!response.ok) {

            return response.json().then(errorData => {
                // console.error('Ошибка:', errorData.error);
                str_error = [errorData.error, response.statusText, response.status]
                throw new Error(str_error.join(", ")); 
            });
        }
        return response.json(); // Если ошибок нет, возвращаем данные
    })
    .then(data => {
        console.log('Успех:', data); // Успешный ответ
        renderOutputImage(data)
        setFullTextFromImg(data)
    })
    .catch(error => {
        console.error('Произошла ошибка:', error); // Выводим информацию об ошибке
    });
}

// Функция загрузки изображения на сервер
function uploadImage() {
    const imageFile = document.getElementById('imageInput').files[0];
    console.log('img file', imageFile)
    const formData = new FormData();
    formData.append('image', imageFile);

    renderInputImage(imageFile);

    fetch('/upload-image', { 
        method: 'POST', 
        body: formData 
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Сетевая ошибка: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        alert(data.message);
    })
    .catch(error => console.error('Ошибка:', error));
}


document.getElementById('upload-form').onsubmit = function(event) {
    event.preventDefault();  // Предотвращаем стандартное поведение формы
    const imageFile = document.getElementById('imageInput').files[0];
    console.log(imageFile)
    var formData = new FormData();
    formData.append('image', imageFile);
    fetch('/upload-to-bucket', {
        method: 'POST', // или другой метод в зависимости от вашего API
        body: formData // здесь вы отправляете данные
    })
    .then(response => {
        if (!response.ok) {

            return response.json().then(errorData => {
                // console.error('Ошибка:', errorData.error);
                str_error = [errorData.error, response.statusText, response.status]
                throw new Error(str_error.join(", ")); 
            });
        }
        return response.json(); // Если ошибок нет, возвращаем данные
    })
    .then(data => {
        console.log('Успех:', data); // Обрабатываем успешный ответ
    })
    .catch(error => {
        console.error('Произошла ошибка:', error); // Выводим информацию об ошибке
    });
}

// =====================
// Работа с бакетами
// =====================

// Загрузка бакетов после полной загрузки страницы
window.onload = function() {
    loadBuckets();
};

// Создание бакета
document.getElementById('createBucketForm').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    await fetch('/create_bucket', { method: 'POST', body: formData });
    loadBuckets();
};

// Удаление бакета
document.getElementById('deleteBucketForm').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    try {
        const response = await fetch('/delete_bucket', { method: 'POST', body: formData });

        if (!response.ok) {
            const errorData = await response.json();
            // Показываем всплывающее окно с сообщением об ошибке
            alert(`Ошибка: ${errorData.error || 'Неизвестная ошибка'}`);
        } else {
            // loadObjects(formData.get('bucket'));
            loadBuckets();
            // loadObjects();
            // Показываем всплывающее окно об успешном удалении
            alert('Бакет успешно удален.');
        }
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
};

// Загрузка файла в бакет
document.getElementById('objectForm').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    await fetch('/upload', { method: 'POST', body: formData });
    loadObjects(formData.get('bucket'));
};

// Событие при нажатии кнопки "Обновить список"
document.getElementById('updateButton').addEventListener('click', function() {
    const bucketName = document.getElementById('objectForm').elements.bucket.value;
    loadObjects(bucketName); // Обновляем список объектов в ведре
});

// Удаление объекта из бакета
document.getElementById('deleteObjectForm').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    await fetch('/delete_object', { method: 'POST', body: formData });
    loadObjects(formData.get('bucket'));
};

// Обработчик для удаления всех объектов из бакета
document.getElementById('deleteAllButton').addEventListener('click', async function() {
    const bucketName = document.getElementById('deleteObjectForm').elements.bucket.value;
    if (confirm(`Вы уверены, что хотите удалить все объекты из бакета "${bucketName}"?`)) {
        const formData = new FormData();
        formData.append('name', bucketName);
        
        await fetch('/delete_all_objects', { method: 'POST', body: formData })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка удаления всех объектов');
                }
                loadObjects(bucketName); // Обновляем список после удаления
            })
            .catch(error => console.error('Ошибка:', error));
    }
});

// Загрузка бакетов из облака 
async function loadBuckets() {
    const response = await fetch('/buckets');
    const buckets = await response.json();
    const bucketList = document.getElementById('bucketList');
    bucketList.innerHTML = '';
    buckets.forEach(bucket => {
        const li = document.createElement('li');
        li.textContent = bucket;
        bucketList.appendChild(li);
    });
}

// Загрузка объектов бакета 
async function loadObjects(bucketName) {
    const formData = new FormData();
    formData.append('name', bucketName);
    const response = await fetch('/list_objects', { method: 'POST', body: formData });
    const objects = await response.json();
    const objectList = document.getElementById('objectList');
    objectList.innerHTML = '';
    objects.forEach(obj => {
        const li = document.createElement('li');
        li.textContent = obj;
        objectList.appendChild(li);
    });
}