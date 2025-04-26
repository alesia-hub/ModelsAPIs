from io import BytesIO
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from DBConnect import MongoConnect
import requests
import bcrypt
import numpy as np
import spacy

import keras
from keras import applications, utils
from PIL import Image

app = Flask(__name__)
api = Api(app)

# Load pre-trained model from ImageNet - global DB of pre-trained models
pretrained_model = applications.InceptionV3(include_top=True,
                                                weights="imagenet")

dbClient = MongoConnect("mongodbVSCodePlaygroundDB")
CollectionUsers = "Users"

def user_exists(username):
    filter = {"username": username}
    if dbClient.count_documents_per_query(CollectionUsers, filter) == 0:
        return False
    else: return True

def json_message_response(error_code, message):
    return jsonify({
            "Status": error_code,
            "Message": message
        })

def verify_password(username, password):
    """ Function will validate the given password for a provided user
    """
    _filter = ({"username": username})
    hashed_pw = dbClient.read_doc_from_collection(CollectionUsers,_filter)

    if bcrypt.hashpw(password.encode('utf-8'), hashed_pw["password"]) == hashed_pw["password"]:
        return 1
    else:
        ret_json = {
                "Status": 404,
                "Message": "Invalid Password provided"
            }
        return ret_json

def count_tokens(username):
    """ Function to validate the number of Tokens for a user.
    Will:
        - read collection and get number of tokens for given user
        - return number of Tokens per user
    """
    _filter = ({"username": username})
    document = dbClient.read_doc_from_collection(CollectionUsers,_filter)
    return document["tokens"]

class Register(Resource):
    """Initial User Registration.
    Parameters from request:
        - username
        - password
    """
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        if user_exists(username):
            return json_message_response(301,
                                         "User already exits. Please select uinque username.")

        hashed_psw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        _user = {
            'username': username,
            'password': hashed_psw,
            'tokens': 4
        }
        dbClient.insert_into_collection(CollectionUsers, _user)
        return json_message_response(200,
                                     "You have successfully signed up for the API.")

class Classify(Resource):
    """ Class will run Imnage Classification and will print predition percentage on what is the image about.
    Using pre-trained models from ImageNet online source.
    """
    def post(self):
        """Main method of the class to read request from users and run Image classification model"""
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        image_url = posted_data["url"]

        if not user_exists(username):
            return json_message_response(301,'User already exits. Please select uinque username.')

        correct_psw = verify_password(username, password)
        if not isinstance(correct_psw, int):
            return jsonify(correct_psw)

        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return json_message_response(301, 'Not Enough Tokens.')
        
        if not image_url:
            return json_message_response(400, 'URL is not provided.')
        
        # Classification:
        # 1. Load Image from URL
        new_response = requests.get(image_url, timeout=30)
        img = Image.open(BytesIO(new_response.content))

        # 2. Pre-process the Image
        img = img.resize((299, 299))
        img_array = utils.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = applications.inception_v3.preprocess_input(img_array)

        # 3. Make prediction and send a response:
        prediction = pretrained_model.predict(img_array)
        actual_pred = keras.applications.imagenet_utils.decode_predictions(prediction, top=5)
        print("Now actual Predictions: ")
        print(actual_pred)

        # actual prediction looks like:
        # [[('n02099601', 'golden_retriever', 0.7660876), ('n02097474', 'Tibetan_terrier', 0.035889715), ('n02099712', 'Labrador_retriever', 0.02641374), ('n02113712', 'miniature_poodle', 0.0061243298), ('n02108551', 'Tibetan_mastiff', 0.0056402674)]]

        # Taking a token for a job:
        filter = {
            'username': username,
        }
        update = { "$set": {
            'tokens': num_tokens-1
        }}
        dbClient.update_collection(CollectionUsers, filter, update)

        ret_json = {}
        for pred in actual_pred[0]:
            ret_json[pred[1]] = float(pred[2]*100)
        return jsonify(ret_json)

class Detect(Resource):
    """ Class responsible for text comparisong and finding similarities.
    Using spacy library to run similarity.
    """
    def post(self):
        """ Main method of the class to read request for text comparison. """
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        text1 = posted_data["text1"]
        text2 = posted_data["text2"]

        if not user_exists(username):
            return json_message_response(301, "User already exits. Please select uinque username.")

        correct_psw = verify_password(username, password)
        if not isinstance(correct_psw, int):
            return jsonify(correct_psw)

        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return json_message_response(301, 'Not Enough Tokens.')

        # Comparisong:
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        # Ration is a number between 0 and 1
        # Closer to 1 the more similar text2 to text1
        ratio = text1.similarity(text2)

        # Taking some tokens for a job:
        _filter = {
            'username': username,
        }
        _update = { "$set": {
            'tokens': num_tokens-1
        }}
        dbClient.update_collection(CollectionUsers, _filter, _update)

        ret_json = {
            "status": 200,
            "similarity": ratio,
            "Message": "Similarity score calculated successfully."
        }
        return ret_json

class Refill(Resource):
    """Class for supporting refill API: to add up more tokens.
        API should contains following fields in POST request:
            - username: name of the user
            - admin_pw: we need special admin password to perform refilling operation
            - refill: amount of tokens to add
    """
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        refill_amount = posted_data["refill"]

        if not user_exists(username):
            return json_message_response(301, "Invalid username.")

        _filter = {
            'username': username,
        }
        _update = { "$set": {
            'tokens': refill_amount
        }}
        dbClient.update_collection(CollectionUsers, _filter, _update)
        return json_message_response(200, 'Rrefilled Successfully.')


# Registration of Resources for API:
api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Detect, '/compare')
api.add_resource(Refill, '/refill')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
