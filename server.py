import re
from datetime import datetime
from flask import Flask, url_for, send_from_directory, request, jsonify
import logging
import os
from PIL import Image
import pytesseract
import argparse
import cv2
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
    if (request.method == 'POST' and request.files['image'] and request.files['image-front']):
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        imgFront = request.files['image-front']
        img_name = secure_filename(img.filename)
        img_name_front = secure_filename(imgFront.filename)
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        saved_path_front = os.path.join(app.config['UPLOAD_FOLDER'], img_name_front)
        app.logger.info("saving {}".format(saved_path))
        app.logger.info("saving {}".format(saved_path_front))
        img.save(saved_path)
        imgFront.save(saved_path_front)
        mrz = read_mrz(saved_path)
        mrz_front = read_mrz(saved_path_front)
        
        print(mrz_front)
        print(mrz)

        # Person detection from Identity Card

        detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath(f'{PROJECT_HOME}/models/yolo.h5')
        detector.loadModel()
        detections = detector.detectObjectsFromImage(input_image=saved_path_front,
                                                     output_image_path=os.path.join(PROJECT_HOME, "newDetected", "imagenew.jpg"),
                                                     minimum_percentage_probability=60)
                                                     
        print(detections)

        if detections != []:
          if detections[0]["name"] == 'person':
            isPerson = True
            personPercentageProbability = f"{detections[0]['name']} {detections[0]['percentage_probability']}"
            personBoxPoints = detections[0]["box_points"]
            
        # Read front side
            
        path_to_tesseract = r"/usr/bin/tesseract"
        
        img_open = Image.open(saved_path_front)
        pytesseract.tesseract_cmd = path_to_tesseract
        
        front_text = pytesseract.image_to_string(img_open)
        
        final_front_text = front_text[:-1]
            
        #End Read front side

        # END Person detection from Identity Card
        try:
            if mrz is not None:
                mrz_data = mrz.to_dict()
                firstName = mrz_data['names']
                deleted_substring = firstName.split("  ", 1)[0]
                firstName = deleted_substring
                lastName = mrz_data['surname']
                dateOfBirth = mrz_data['date_of_birth']
                dateOfBirth = datetime.strptime(dateOfBirth, '%y%m%d').strftime('%d/%m/%Y')
                exp_date = mrz_data['expiration_date']
                exp_date = datetime.strptime(exp_date, '%y%m%d').strftime('%d/%m/%Y')
                country = mrz_data['country']
                nationality = mrz_data['nationality']
                gender = mrz_data['sex']
                idNo = mrz_data['number']
                
                # Read front side
                
                path_to_tesseract = r"/usr/bin/tesseract"
                
                img_open = Image.open(saved_path_front)
                pytesseract.tesseract_cmd = path_to_tesseract
                
                front_text = pytesseract.image_to_string(img_open)
                
                final_front_text = front_text[:-1]
                
                #End Read front side
    
    
                if (firstName.lower() in final_front_text.lower()) or (lastName.lower() in final_front_text.lower()) or (idNo.lower() in final_front_text.lower()):
    
                    response = {
                        "data": [
                            {
                                "parsed_data": [
                                
                                  mrz_data,
                                
                            ],
                                "message": "Successfully Read",
                                "front_text": final_front_text,
                                "first_name": firstName,
                                "last_name": lastName,
                                "date_of_birth": dateOfBirth,
                                "exp_date": exp_date,
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
                    
                else:
                
                    response = {
                    
                      "data": [
                            {
                            "message": "Invalid Id Card."
                            }
                          ]
                        }
                
                    return jsonify(response)
                    
            # for passport etc
            
            elif mrz_front is not None:
                mrz_data = mrz_front.to_dict()
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
                
                # Read front side
                
                path_to_tesseract = r"/usr/bin/tesseract"
                
                img_open = Image.open(saved_path_front)
                pytesseract.tesseract_cmd = path_to_tesseract
                
                front_text = pytesseract.image_to_string(img_open)
                
                final_front_text = front_text[:-1]
                
                #End Read front side
    
    
                if (firstName.lower() in final_front_text.lower()) or (lastName.lower() in final_front_text.lower()) or (idNo.lower() in final_front_text.lower()):
    
                    response = {
                        "data": [
                            {    "parsed_data": [
                                
                                  mrz_data,
                                
                            ],
                                "message": "Successfully Read",
                                "front_text": final_front_text,
                                "first_name": firstName,
                                "last_name": lastName,
                                "date_of_birth": dateOfBirth,
                                "exp_date": exp_date,
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
                    
                else:
                
                    response = {
                    
                      "data": [
                            {
                            "message": "Invalid Id Card."
                            }
                          ]
                        }
                
                    return jsonify(response)
            
            #end of passport validation
                    
    
            elif mrz is None:
            #else:
                response = {
                    "data": [
                        {
                            "message": "Sorry we couldn't read your provided Id card. Please ensure the text of your document is clear to read."
                        }
                    ]
                }
                
                return jsonify(response)
            else:
                response = {
                    "data": [
                        {
                            "message": "Sorry, we encountered an unknown problem."
                        }
                    ]
                }
                
                return jsonify(response)
        except:
        
              response = {
                    "data": [
                        {
                            "message": "Sorry, something is wrong."
                        }
                    ]
                }
                
              return jsonify(response)
            
            
        
    # return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
    else:
        response = {
                    "data": [
                        {
                            "message": "Please provide all documents."
                        }
                    ]
                }
                
        return jsonify(response)



# for passport

@app.route('/passport-info-extractor', methods=['POST'])
def api_passport_info():
    app.logger.info(PROJECT_HOME)
    if (request.method == 'POST' and request.files['front-image']):
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['front-image']
        img_name = secure_filename(img.filename)
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        # app.logger.info("saving {}".format(saved_path))
        img.save(saved_path)
        mrz = read_mrz(saved_path)
        print(mrz)

        # Person detection from Identity Card

        detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath(f'{PROJECT_HOME}/models/yolo.h5')
        detector.loadModel()
        detections = detector.detectObjectsFromImage(input_image=saved_path,
                                                     output_image_path=os.path.join(PROJECT_HOME, "newDetected", "imagenew.jpg"),
                                                     minimum_percentage_probability=60)
                                                     
        print(detections)

        if detections != []:
          if detections[0]["name"] == 'person':
            isPerson = True
            personPercentageProbability = f"{detections[0]['name']} {detections[0]['percentage_probability']}"
            personBoxPoints = detections[0]["box_points"]
            
        # Read front side
            
        path_to_tesseract = r"/usr/bin/tesseract"
        
        img_open = Image.open(saved_path)
        pytesseract.tesseract_cmd = path_to_tesseract
        
        front_text = pytesseract.image_to_string(img_open)
        
        final_front_text = front_text[:-1]
            
        #End Read front side

        # END Person detection from Identity Card
        try:
            if mrz is not None:
                mrz_data = mrz.to_dict()
                firstName = mrz_data['names']
                deleted_substring = firstName.split("  ", 1)[0]
                firstName = deleted_substring
                lastName = mrz_data['surname']
                dateOfBirth = mrz_data['date_of_birth']
                dateOfBirth = datetime.strptime(dateOfBirth, '%y%m%d').strftime('%d/%m/%Y')
                exp_date = mrz_data['expiration_date']
                exp_date = datetime.strptime(exp_date, '%y%m%d').strftime('%d/%m/%Y')
                country = mrz_data['country']
                nationality = mrz_data['nationality']
                gender = mrz_data['sex']
                idNo = mrz_data['number']
                
                # Read front side
                
                # path_to_tesseract = r"/usr/bin/tesseract"
                
                # img_open = Image.open(saved_path_front)
                # pytesseract.tesseract_cmd = path_to_tesseract
                
                # front_text = pytesseract.image_to_string(img_open)
                
                # final_front_text = front_text[:-1]
                
                # #End Read front side
    
    
                if (firstName.lower() in final_front_text.lower()) or (lastName.lower() in final_front_text.lower()) or (idNo.lower() in final_front_text.lower()):
    
                    response = {
                        "data": [
                            {
                                "parsed_data": [
                                
                                  mrz_data,
                                
                            ],
                                "message": "Successfully Read",
                                "front_text": final_front_text,
                                "first_name": firstName,
                                "last_name": lastName,
                                "date_of_birth": dateOfBirth,
                                "exp_date": exp_date,
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
                    
                else:
                
                    response = {
                    
                      "data": [
                            {
                            "message": "Invalid Id Card."
                            }
                          ]
                        }
                
                    return jsonify(response)
                    
    
            elif mrz is None:
            #else:
                response = {
                    "data": [
                        {
                            "message": "Sorry we couldn't read your provided Id card. Please ensure the text of your document is clear to read."
                        }
                    ]
                }
                
                return jsonify(response)
            else:
                response = {
                    "data": [
                        {
                            "message": "Sorry, we encountered an unknown problem."
                        }
                    ]
                }
                
                return jsonify(response)
        except:
        
              response = {
                    "data": [
                        {
                            "message": "Sorry, something is wrong."
                        }
                    ]
                }
                
              return jsonify(response)
            
            
        
    # return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
    else:
        response = {
                    "data": [
                        {
                            "message": "Please provide all documents."
                        }
                    ]
                }
                
        return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
