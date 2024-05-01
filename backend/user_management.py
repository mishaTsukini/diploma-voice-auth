from flask import redirect, url_for, render_template
from utilities import create_user_directory
import os, shutil
import voice_processing
import numpy
import scipy
from sklearn.mixture import GaussianMixture
import pickle
import speech_recognition
from faker import Faker
from yandex_speechkit import Session, ShortAudioRecognition
from fuzzywuzzy import fuzz

def enroll_user(request):
    global username
    global user_directory

    if request.method == 'POST':
        data = request.get_json()

        username = data['username']
        password = data['password']
        repassword = data['repassword']

        user_directory = "Users/" + username + "/"

        # Create target directory & all intermediate directories if don't exists
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

def authenticate_user(request):
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
            return "User exist"

        else:
            print("[ * ] The user profile does not exists ...")
            return "Doesn't exist"

    else:
        print('its coming here')
        return render_template('auth.html')
    
def biometrics(request):
    global user_directory
    print("[ DEBUG ] : User directory is : ", user_directory)

    if request.method == 'POST':
        pass
    else:
        # MFCC
        print("Into the biometrics route.")

        directory = os.fsencode(user_directory)
        features = numpy.asarray(())

        for file in os.listdir(directory):
            filename_wav = os.fsdecode(file)
            if filename_wav.endswith(".wav"):
                print("[biometrics] : Reading audio files for processing ...")
                (rate, signal) = scipy.io.wavfile.read(user_directory + filename_wav)

                extracted_features = voice_processing.extract_features(rate, signal)

                if features.size == 0:
                    features = extracted_features
                else:
                    features = numpy.vstack((features, extracted_features))

            else:
                continue

        # GaussianMixture Model
        print("[ * ] Building Gaussian Mixture Model ...")

        gmm = GaussianMixture(n_components=16,
                            max_iter=200,
                            covariance_type='diag',
                            n_init=3)

        gmm.fit(features)
        print("[ * ] Modeling completed for user :" + username +
            " with data point = " + str(features.shape))

        # dumping the trained gaussian model
        # picklefile = path.split("-")[0]+".gmm"
        print("[ * ] Saving model object ...")
        pickle.dump(gmm, open("Models/" + str(username) +
                            ".gmm", "wb"), protocol=None)
        print("[ * ] Object has been successfully written to Models/" +
            username + ".gmm ...")
        print("\n\n[ * ] User has been successfully enrolled ...")

        features = numpy.asarray(())

        return "User has been successfully enrolled ...!!"
    

def verify(request):
    global username
    global filename
    global user_directory
    global filename_wav

    print("[ DEBUG ] : user directory : " , user_directory)
    print("[ DEBUG ] : filename : " , filename)
    print("[ DEBUG ] : filename_wav : " , filename_wav)

    # ------------------------------------------------------------------------------------------------------------------------------------#
    #                                                                   LTSD and MFCC                                                     #
    # ------------------------------------------------------------------------------------------------------------------------------------#

    (rate, signal) = scipy.io.wavfile.read(filename_wav)

    extracted_features = voice_processing.extract_features(rate, signal)

    # ------------------------------------------------------------------------------------------------------------------------------------#
    #                                                          Loading the Gaussian Models                                                #
    # ------------------------------------------------------------------------------------------------------------------------------------#

    gmm_models = [os.path.join(user_directory, user)
                  for user in os.listdir(user_directory)
                  if user.endswith('.gmm')]

    # print("GMM Models : " + str(gmm_models))

    # Load the Gaussian user Models
    models = [pickle.load(open(user, 'rb')) for user in gmm_models]

    user_list = [user.split("/")[-1].split(".gmm")[0]
                 for user in gmm_models]

    log_likelihood = numpy.zeros(len(models))

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

def voice(request):
    global user_directory
    global filename_wav
    session = Session.from_api_key('AQVNy2C7z8MvjjZ09jcFA6nZQCVVy9Knfak6521B')

    print("[ DEBUG ] : User directory at voice : ", user_directory)

    if request.method == 'POST':
        global random_words
        global username

        filename_wav = user_directory + "-".join(random_words) + '.wav'
        with open(filename_wav, 'wb') as f:
            f.write(request.data)

        with open(filename_wav, 'rb') as audio_file:
            data = audio_file.read()
        recognize_short_audio = ShortAudioRecognition(session)
        recognized_text = recognize_short_audio.recognize(data, format='lpcm')
        

        print("Yandex SpeechKit thinks you said : " + recognized_text)
        print("Yandex SpeechKit Fuzzy partial score : " + str(fuzz.partial_ratio(random_words, recognized_text)))
        print("Yandex SpeechKit Fuzzy score : " + str(fuzz.ratio(random_words, recognized_text)))       

        if fuzz.ratio(random_words, recognized_text) < 65:
            print(
                "\nСлова, которые вы произнесли, не совсем верны. Пожалуйста, попробуйте еще раз...")
            os.remove(filename_wav)
            return "fail"
        else:
            pass

        return "pass"

    else:
        return render_template('voice.html')
