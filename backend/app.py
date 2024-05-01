from flask import Flask, render_template, request
import user_management
import voice_processing
import scipy
import os
import numpy
import pickle
from sklearn.mixture import GaussianMixture

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('main.html')

@app.route('/enroll', methods=["GET", "POST"])
def enroll():
    return user_management.enroll_user(request)

@app.route('/auth', methods=['POST', 'GET'])
def auth():
    return user_management.authenticate_user(request)

@app.route('/vad', methods=['GET', 'POST'])
def vad():
    return voice_processing.process_voice_activity(request)

@app.route('/biometrics', methods=['GET', 'POST'])
def biometrics():
    return user_management.biometrics(request)

@app.route("/verify", methods=['GET'])
def verify():
    return user_management.verify(request)

@app.route("/verify", methods=['GET'])
def voice():
    return user_management.voice(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)