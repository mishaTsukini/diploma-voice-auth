import pickle
import datetime
import os                                               # For creating directories
import shutil                                           # For deleting directories

import matplotlib.pyplot as plt
import numpy
import scipy.cluster
import scipy.io.wavfile
import speech_recognition
from fuzzywuzzy import fuzz
from python_speech_features import mfcc
from faker import Faker
from sklearn import preprocessing
from sklearn.mixture import GaussianMixture as gaussian_mixture

from speechkit import Session, ShortAudioRecognition, RecognitionLongAudio

import psycopg2
import boto3
import config
import datetime

from flask import Flask, render_template, request, jsonify, url_for, redirect, abort, session, json

PORT = 8080

# Global Variables
random_words = []
random_string = ""
username = ""
filename = ""
filename_wav = ""

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('main.html')


@app.route('/enroll', methods=["GET", "POST"])
def enroll():
    global username
    global user_directory


    if request.method == 'POST':
        data = request.get_json()

        username = data['username']
        password = data['password']
        repassword = data['repassword']
        # Store user info in PostgreSQL
        user_directory = "Users/" + username + "/"
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)
            print("[ * ] Directory ", username,  " Created ...")
        else:
            print("[ * ] Directory ", username,  " already exists ...")
            print("[ * ] Overwriting existing directory ...")
            shutil.rmtree(user_directory, ignore_errors=False, onerror=None)
            os.makedirs(user_directory)
            print("[ * ] Directory ", username,  " Created ...")

        return redirect(url_for('voice'))

    else:
        return render_template('enroll.html')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    global username
    global user_directory
    global filename


    user_exist = False

    if request.method == 'POST':

        data = request.get_json()
        print(data)
        user_directory = 'Models/'
        username = data['username']
        password = data['password']

        print("[ DEBUG ] : What is the username at auth : ", username)

        print("[ DEBUG ] : What is the user directory at auth : ", user_directory)
        print("os.fsencode(user_directory : ", os.fsencode(user_directory))
        directory = os.fsencode(user_directory)
        print("directory : ", os.listdir(directory)[1:])

        for file in os.listdir(directory):
            print("file : ", file)
            filename = os.fsdecode(file)
            if filename.startswith(username):
                print("filename : ", filename)
                user_exist = True
                break
            else:
                pass

        if user_exist:
            print("[ * ] The user profile exists ...")
            return redirect(url_for('verify'))

        else:
            print("[ * ] The user profile does not exists ...")
            return "Doesn't exist"
        

    else:
        print('its coming here')
        return render_template('auth.html')


@app.route('/vad', methods=['GET', 'POST'])
def vad():
    if request.method == 'POST':
        global random_words

        f = open('./static/audio/background_noise.wav', 'wb')
        f.write(request.data)
        f.close()

        background_noise = speech_recognition.AudioFile(
            './static/audio/background_noise.wav')
        with background_noise as source:
            speech_recognition.Recognizer().adjust_for_ambient_noise(source, duration=5)

        print("Voice activity detection complete ...")

        fake = Faker('ru_RU')
        random_words = [fake.word() for _ in range(5)]
        print(random_words)

        return "  ".join(random_words)

    else:
        background_noise = speech_recognition.AudioFile(
            './static/audio/background_noise.wav')
        with background_noise as source:
            speech_recognition.Recognizer().adjust_for_ambient_noise(source, duration=5)

        print("Voice activity detection complete ...")

        fake = Faker('ru_RU')
        random_words = [fake.word() for _ in range(5)]
        print(random_words)

        return "  ".join(random_words)


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    global user_directory
    global filename_wav
    #session = Session.from_jwt(jwt_token='eyJhbGciOiJQUzI1NiIsImtpZCI6ImFqZTRyZWZxNmhvOGxybDJuYm8wIiwidHlwIjoiSldUIn0.eyJhdWQiOiJodHRwczovL2lhbS5hcGkuY2xvdWQueWFuZGV4Lm5ldC9pYW0vdjEvdG9rZW5zIiwiaXNzIjoiYWplbjBzbjJrb2VjZmJ2MWpkOHYiLCJpYXQiOjE3MTM3MDY3NTMsImV4cCI6MTcxMzcwNzExM30.T2dWKMmAoa9bP107oMHqouy5K13LDQOhKOJ8U-lw8L7t4OMhKajA_30QSAuvE9v2SWH7uHdsUyFIXhndYu5tX94ubk9srd3VgO3zXgyxlIr7uZTVxoiIyRr4t-H39-IRBp1mCtHEuj_evt2aWdYLPWcs_L9hogRRHs6imMUeaCnovkxIONXUA_shz_wlajZg7qBOfmdSO3E5k7oABdCs0G7GxnmqJHUnLwnIOVRq7s331OGj8y2ft5WkoDfZO5xPB6hhSszudBdj4QVsQtt6sCmBAKF25uE13pEuYQPg1yAy_ABxShMykppRXeA0R6cQ9pkfrKz86Hz74Fcer6KSdA')

    if request.method == 'POST':
        #global random_words
        global username

        filename_wav = user_directory + "/" + username + ".wav"
        with open(filename_wav, 'wb') as f:
            f.write(request.data)

        #with open(filename_wav, 'rb') as audio_file:
        #    data = audio_file.read()
        #recognizeLongAudio = RecognitionLongAudio(session, 'ajen0sn2koecfbv1jd8v')
        #recognizeLongAudio.send_for_recognition(filename_wav)
        #if recognizeLongAudio.get_recognition_results():
        #    data = recognizeLongAudio.get_data()
        #recognized_text = recognizeLongAudio.get_raw_text()
        #recognize_short_audio = ShortAudioRecognition(session)
        #recognized_text = recognize_short_audio.recognize(data, format='lpcm')
        

        #print("Yandex SpeechKit thinks you said : " + recognized_text)
        #print("Yandex SpeechKit Fuzzy partial score : " + str(fuzz.partial_ratio(random_words, recognized_text)))
        #print("Yandex SpeechKit Fuzzy score : " + str(fuzz.ratio(random_words, recognized_text)))       

        #if fuzz.ratio(random_words, recognized_text) < 65:
        #    print(
        #        "\nСлова, которые вы произнесли, не совсем верны. Пожалуйста, попробуйте еще раз...")
        #    os.remove(filename_wav)
        #    return "fail"
        #else:
        #    pass


        return redirect(url_for('biometrics'))

    else:
        return render_template('voice.html')


@app.route('/biometrics', methods=['GET', 'POST'])
def biometrics():
    global user_directory
    print("[ DEBUG ] : Into the biometrics route.")

    if request.method == 'POST':
        pass
    else:
        print("Into the biometrics route.")

        directory = os.fsencode(user_directory)
        features = numpy.asarray(())

        for file in os.listdir(directory):
            filename_wav = os.fsdecode(file)
            if filename_wav.endswith(".wav"):
                print("[biometrics] : Reading audio files for processing ...")
                (rate, signal) = scipy.io.wavfile.read(user_directory + filename_wav)

                extracted_features = extract_features(rate, signal)

                if features.size == 0:
                    features = extracted_features
                else:
                    features = numpy.vstack((features, extracted_features))

        # Ensure features is a 2D array
        if len(features.shape) == 1:
            features = features.reshape(-1, 1)

        print("[ * ] Building Gaussian Mixture Model ...")

        gmm = gaussian_mixture(n_components=16, max_iter=200, covariance_type='diag', n_init=3)

        gmm.fit(features)
        print("[ * ] Modeling completed for user: " + username + " with data point = " + str(features.shape))

        pickle.dump(gmm, open("Models/" + str(username) + ".gmm", "wb"), protocol=None)
        print("[ * ] Object has been successfully written to Models/" + username + ".gmm ...")
        print("\n\n[ * ] User has been successfully enrolled ...")

        return "User has been successfully enrolled ...!!"


@app.route("/verify", methods=['GET', 'POST'])
def verify():
    global username
    global filename
    global user_directory
    global filename_wav
    #filename_wav = "Users" + "/" + username + "/" + username + ".wav"

    print("[ DEBUG ] : Into the verify route.")
    if request.method == 'POST':
        # ------------------------------------------------------------------------------------------------------------------------------------#
        #                                                                   LTSD and MFCC                                                     #
        # ------------------------------------------------------------------------------------------------------------------------------------#

        (rate, signal) = scipy.io.wavfile.read(filename_wav)

        extracted_features = extract_features(rate, signal)

        # ------------------------------------------------------------------------------------------------------------------------------------#
        #                                                          Loading the Gaussian Models                                                #
        # ------------------------------------------------------------------------------------------------------------------------------------#

        # Load the Gaussian user Models from Yandex Object Storage
        gmm_models = [os.path.join(user_directory, user)
                    for user in os.listdir(user_directory)
                    if user.endswith('.gmm')] # Placeholder for loaded GMM models
        
        models = [pickle.load(open(user, 'rb')) for user in gmm_models]
        user_list = [user.split("/")[-1].split(".gmm")[0]
                    for user in gmm_models]
        log_likelihood = numpy.zeros(len(models))
        print(gmm_models)
        for i in range(len(models)):
            gmm = models[i]  # checking with each model one by one
            scores = numpy.array(gmm.score(extracted_features))
            log_likelihood[i] = scores.sum()

        print("Log liklihood : " + str(log_likelihood))

        identified_user = numpy.argmax(log_likelihood)

        print("[ * ] Identified User : " + str(identified_user) +
            " - " + user_list[identified_user])

        auth_message = ""

        if user_list[identified_user] == username:
            print("[ * ] You have been authenticated!")
            auth_message = "success"
        else:
            print("[ * ] Sorry you have not been authenticated")
            auth_message = "fail"

        return auth_message



def calculate_delta(array):
    """Calculate and returns the delta of given feature vector matrix
    (https://appliedmachinelearning.blog/2017/11/14/spoken-speaker-identification-based-on-gaussian-mixture-models-python-implementation/)"""

    print("[Delta] : Calculating delta")

    rows, cols = array.shape
    deltas = numpy.zeros((rows, 20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first = 0
            else:
                first = i-j
            if i+j > rows - 1:
                second = rows - 1
            else:
                second = i+j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]]-array[index[0][1]] +
                     (2 * (array[index[1][0]]-array[index[1][1]]))) / 10
    return deltas


def extract_features(rate, signal):
    print("[extract_features] : Exctracting features ...")

    mfcc_feat = mfcc(signal,
                     rate,
                     winlen=0.020,  # remove if not requred
                     preemph=0.95,
                     numcep=20,
                     nfft=1024,
                     
                     ceplifter=15,
                     highfreq=6000,
                     nfilt=55,

                     appendEnergy=False)

    mfcc_feat = preprocessing.scale(mfcc_feat)

    delta_feat = calculate_delta(mfcc_feat)

    combined_features = numpy.hstack((mfcc_feat, delta_feat))

    return combined_features


def upload_gmm_to_yandex_storage(gmm_object, bucket, object_name):
    # Serialize GMM object
    gmm_bytes = pickle.dumps(gmm_object)
    # Create a temporary file to hold the GMM bytes
    tmp_gmm_file = "temp_gmm.pkl"
    with open(tmp_gmm_file, 'wb') as f:
        f.write(gmm_bytes)
    
    # Upload the GMM file
    s3_client = boto3.client('s3', endpoint_url='https://storage.yandexcloud.net',
                             aws_access_key_id='your_access_key_id',
                             aws_secret_access_key='your_secret_access_key')
    try:
        response = s3_client.upload_file(tmp_gmm_file, bucket, object_name)
    except Exception as e:
        print(e)
        return False
    finally:
        # Ensure the temporary file is deleted after upload
        os.remove(tmp_gmm_file)
    return True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
