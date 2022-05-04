from flask import Flask
import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import easyocr
import cv2
import numpy as np
import matplotlib.pyplot as plt

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = '1234567890'
app.config['SESSION_TYPE'] = 'filesystem'
app.debug = True
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        reader = easyocr.Reader(['en'])
        result = reader.readtext('static/uploads/'+filename,paragraph="False")
        img = cv2.imread('static/uploads/'+filename)
        spacer = 100
        font = cv2.FONT_HERSHEY_SIMPLEX

        for detection in result: 
            top_left = tuple(detection[0][0])
            bottom_right = tuple(detection[0][2])
            text = detection[1]
            img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
            img = cv2.putText(img,text,(20,spacer), font, 0.5,(0,255,0),2,cv2.LINE_AA)
            spacer+=15

        plt.figure(figsize=(10,10))
        plt.imshow(img)
        plt.savefig('static/uploads/finaloutput.png')
        flash('Image successfully uploaded,processed and displayed below')
        finalimg = 'finaloutput.png'
        return render_template('upload.html', filename=filename,result = finalimg)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run()