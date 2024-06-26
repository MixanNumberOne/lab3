import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
from flask import Flask, request, redirect, url_for, render_template


app = Flask(__name__,static_folder='static/images')


UPLOAD_FOLDER = '/home/MixanNumberOne/mysite/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SECRET_KEY = "6LdYsNkpAAAAAJyabUN9JPxk2N95fQ_PY1zUnI5q"
SITE_KEY = "6LdYsNkpAAAAADQzo8unRpIfeETUYACvsyCpEyD-"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            return "Ошибка проверки капчи"

        file = request.files['image']
        level = float(request.form['level'])
        file.filename = 'image'
        file.name = file.name + '.jpg'

        file_path = os.path.join('/home/MixanNumberOne/mysite/static/images', file.name)
        file.save(file_path)

        image = Image.open(file_path)
        image_contrast = np.array(image)
        image_contrast = image_contrast.astype(float)
        image_contrast = image_contrast * level
        image_contrast = np.clip(image_contrast,0,255)
        image_contrast = image_contrast.astype(np.uint8)
        image_contrast = Image.fromarray(image_contrast)

        # Создание гистограмм для изображений
        original_hist = image.histogram()
        contrast_hist = image_contrast.histogram()

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(original_hist, color='b')
        plt.title('Original Image Histogram')
        plt.xlabel('Интенсивность пикселей')
        plt.ylabel('Частота')
        plt.subplot(1, 2, 2)
        plt.plot(contrast_hist, color='r')
        plt.title('Rotated Image Histogram')
        plt.xlabel('Интенсивность пикселей')
        plt.ylabel('Частота')

        image_contrast_path = os.path.join('/home/MixanNumberOne/mysite/static/images','contrast.png')
        histograms_path = os.path.join('/home/MixanNumberOne/mysite/static/images', 'histograms.png')
        plt.savefig(histograms_path)
        image_contrast.save(image_contrast_path)

        return render_template('index.html',
                               original_image='image.jpg',
                               rotated_image='contrast.png',
                               histograms='histograms.png')

    return render_template('index.html', site_key=SITE_KEY)

def verify_recaptcha(recaptcha_response):
    payload = {
        'secret': SECRET_KEY,
        'response': recaptcha_response
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = response.json()
    return result['success']

if __name__ == '__main__':
    app.run(port=8001)