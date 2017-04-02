# ContextCam
ContextCam is a project from [HackPrinceton](hackprinceton.com) Spring 2017. ContextCam runs on the Raspberry PI with a RPi Cameram, a single push button, and a mobile power source. It takes a picture, runs it through Watson and Indico to get context about the image. Then, through use of nltk and PyDictionary, it generates a description about the image and outputs as audio.

The positioning of the object is important, preferably in the center with a monochromatic background for better results. It currently takes top three predictions and forms a description with them. For emotional analysis, it gets the top three emotions and describes the person. 

## Demo

[Demo](https://www.youtube.com/watch?v=RN4BMc_6jNQ)

[Project at devpost](https://devpost.com/software/contextcam)


## Code Structure

* `main.py`
The main process, does API calls, receive button and camera inputs, process labels, grammar, outputs to audio. 
All dependencies can be found at the top of the file to download.
* `settings.py`
Not present but has the Watson BlueMix API authentication. 
* `.indicorc`
Also not present, stored in home directory and has Indico API authentication.

## Reference

1. Bird, Steven, Edward Loper and Ewan Klein (2009), Natural Language Processing with Python. O’Reilly Media Inc.
