import RPi.GPIO as GPIO
import time
import picamera
import indicoio as ino
from settings import auth
import json
from watson_developer_cloud import VisualRecognitionV3
from os.path import join, dirname
from PyDictionary import PyDictionary
import nltk
import subprocess
import warnings

warnings.filterwarnings('ignore')

sw_in = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sw_in, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(sw_in, GPIO.FALLING)

cam = picamera.PiCamera()
cam.rotation = -90
#cam.start_preview()

dict = PyDictionary()

visual_recognition = VisualRecognitionV3('2016-05-20', api_key=auth["api_key"])

while True:
    if GPIO.event_detected(sw_in):
        GPIO.remove_event_detect(sw_in)
        now = time.time()
        count = 1
        GPIO.add_event_detect(sw_in,GPIO.RISING)
        while time.time() < now + 1: # 1 second period
            if GPIO.event_detected(sw_in):
                count +=1
                time.sleep(.3) # debounce 
        #print count
        if count <= 2:
            cam.capture("image.jpg")
            with open(join(dirname(__file__), "image.jpg"), "rb") as image_file:
                watson_out = visual_recognition.classify(images_file=image_file, 
                                                         threshold = 0.1)
            watson_classes = watson_out["images"][0]["classifiers"][0]["classes"]
            #sorted(watson_classes, key=lambda pred: -pred["score"])
            top_word = {"score": 0, "class":""}
            top_color = {"score": 0, "class":""}
            second_word = top_word
            second_color = top_color
            third_word = top_word
            print "Watson: "
            for wclass in watson_classes:
                print wclass["class"], wclass["score"]
                if "color" in wclass["class"]:
                    if wclass["score"] > top_color["score"]:
                        second_color = top_color
                        top_color = wclass
                    elif wclass["score"] > second_color["score"]:
                        second_color = wclass
                else:
                    if wclass["score"] > top_word["score"]:
                        second_word = top_word
                        top_word = wclass
                    elif wclass["score"] > second_word["score"]:
                        second_word = wclass
                    elif wclass["score"] > third_word["score"]:
                        third_word = wclass
            text = "This is a"
            if top_color["score"] != 0:
                if top_color["class"][0].lower() in "aeiou":
                    text += "n " + top_color["class"][:-6]
                else:
                    text += " " + top_color["class"][:-6] 
            #print top_word, top_color, second_word, second_color
            text += " " + top_word["class"] + "."
            if top_word["class"].count(" ") == 0:
                tags = [(top_word["class"], "NN")]
            else:
                tokens = nltk.word_tokenize(top_word["class"])
                tags = nltk.pos_tag(tokens)
            print "\nGrammar:", tags
            for item in tags:
                val = dict.meaning(item[0])
                #print "val:", val
                if val is not None:
                    text += " A"
                    if item[0][0].lower() in "aeiou":
                        text += "n" 
                    if "Noun" in val and item[1] == "NN":
                        text += " " + item[0] + " is a Noun meaning "  + val["Noun"][0] + "."
                        break
                    else:
                        pos = next(iter(val))
                        text += " " + item[0] + " is a " + pos + " meaning " + val[pos][0] + "."
            if second_word["score"] != 0:
                text += " This could also be a"
                if second_color["score"] != 0:
                    if second_color["class"][0].lower() in "aeiou":
                        text += "n"
                text += " " + second_color["class"][:-5] + " " + second_word["class"]
                if third_word["score"] != 0:
                    text += " or a"
                    if third_word["class"][0].lower() in "aeiou":
                        text += "n"
                    text += " " + third_word["class"]
                text += "."
            print "\nGenerated Text:", text
            subprocess.call(["pico2wave", "-w", "description.wav",text])
            subprocess.call(["aplay", "description.wav"])
            #time.sleep(0.1)
        else:
            cam.capture("face.jpg")
            #out = ino.image_recognition("image.jpg", top_n=5)
            emotions = ino.fer("face.jpg")
            #print(emotions)
            emotes = sorted(emotions, key=lambda k: -emotions[k])[:3]
            semotes = []
            for emote in emotes:
                if emote == "Sad": semotes.append("sad")
                elif emote == "Fear": semotes.append("afraid")
                elif emote == "Angry": semotes.append("mad")
                elif emote == "Neutral": semotes.append("neutral")
                elif emote == "Happy": semotes.append("happy")
                else: semotes.append("surprised")
            text = "The person is " + semotes[0] + ", " + semotes[1] + ", and " + semotes[2] + "."
            print text
            subprocess.call(["pico2wave", "-w", "emotion.wav",text])
            subprocess.call(["aplay", "emotion.wav"])


        GPIO.remove_event_detect(sw_in)
        GPIO.add_event_detect(sw_in,GPIO.FALLING)

