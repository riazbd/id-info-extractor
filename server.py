import re
from datetime import datetime
from flask import Flask, url_for, send_from_directory, request, jsonify
import logging
import os
from passporteye import read_mrz
from werkzeug.utils import secure_filename
from imageai.Detection import ObjectDetection

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath






@app.route('/', methods=['GET'])
def home():
    return 'This app is running successfully.'

@app.route('/card-info-extractor', methods=['POST'])
def api_id_card_info():
    app.logger.info(PROJECT_HOME)
    if (request.method == 'POST' and request.files['image']):
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        img_name = secure_filename(img.filename)
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        app.logger.info("saving {}".format(saved_path))
        img.save(saved_path)
        mrz = read_mrz(saved_path)

        # Person detection from Identity Card

        detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath(f'{PROJECT_HOME}/models/yolo.h5')
        detector.loadModel()
        detections = detector.detectObjectsFromImage(input_image=saved_path,
                                                     output_image_path=os.path.join(PROJECT_HOME, "newDetected", "imagenew.jpg"),
                                                     minimum_percentage_probability=60)

        if detections[0]["name"] == 'person':
            isPerson = True
            personPercentageProbability = f"{detections[0]['name']} {detections[0]['percentage_probability']}"
            personBoxPoints = detections[0]["box_points"]

        # END Person detection from Identity Card

        if mrz is not None:
            mrz_data = mrz.to_dict()
            firstName = mrz_data['names']
            deleted_substring = firstName.split("  ", 1)[0]
            firstName = deleted_substring
            lastName = mrz_data['surname']
            dateOfBirth = mrz_data['date_of_birth']
            dateOfBirth = datetime.strptime(dateOfBirth, '%y%m%d').strftime('%d/%m/%Y')
            country = mrz_data['country']
            nationality = mrz_data['nationality']
            gender = mrz_data['sex']
            idNo = mrz_data['number']



            response = {
                "data": [
                    {
                        "first_name": firstName,
                        "last_name": lastName,
                        "date_of_birth": dateOfBirth,
                        "gender": gender,
                        "country": country,
                        "nationality": nationality,
                        "id_no": idNo,
                        "isPerson": isPerson,
                        "personPercentageProbability": personPercentageProbability,
                        "personBoxPoints": personBoxPoints

                    }
                ]
            }

            return jsonify(response)

        if mrz is None:
            print("Sorry we couldn't read your provided Id card. Please ensure the text of you document is clear to read.")

    # return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
    else:
        return "Where is the image?"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
