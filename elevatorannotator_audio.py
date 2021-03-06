#!/usr/bin/python
import vlc
import time
import os
import pyttsx
import pyaudio
import speech_recognition as sr
import random
import datetime
import threading
from threading import Timer
import thread, sys
from mutagen.mp3 import MP3
from mutagen.asf import ASF
import RPi.GPIO as GPIO
import os
import Adafruit_CharLCD as LCD
import picamera
from gpiozero import MotionSensor

## Initialize board and GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 16
pir = MotionSensor(16) 

# LCD pin configuration:
lcd_rs        = 25 
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows    = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

camera = picamera.PiCamera()
camera.vflip = True

## Defined variables
startingTime = 0
helloNo = str(random.randrange(1,3))
thankNo = str(random.randrange(1,3))
repeatNo = str(random.randrange(1,3))
musicNo = str(random.randrange(1,11))
instruNo = random.randrange(0,3)
positionNo = [0.25, 0.5, 0.75]
seek = random.choice(positionNo)
instruments =['violin','trumpet','piano']

## Record variables
record = ""
participationAns = ""
participationAttempts_list = []*2
musicName = ""
instrumentName = ""
instrumentAns = ""
instrumentAttempts_list = []*2

## Answers' handling functions
def repeatAgain():
    print (">> Play repeat again")
    Play(getAudio("repeat",repeatNo),0)
    setDelay("repeat",repeatNo)
    return recogniseMe(mic)

def isInvalidAnswer(answer):
    return answer == None

def isYesAnswer(answer):
    return ('yes' in answer) or ('ye' in answer) or ('ya' in answer)

def isNoAnswer(answer):
    return ('no' in answer) or ('nu' in answer) or ('ne' in answer)

## Annotation's handling functions
def handleYesAnswer():
	lcd.clear()
	lcd.message('Check bit.ly/\ne-annotator ;)')
	Play(getAudio("thankyou",thankNo),0)
	setDelay("thankyou",thankNo)
	instrumentAttempts_list.append("T")
	registerRecord("instrument","yes")
	print (">> Handled yes instrument answer")

def handleNoAnswer(ansType):
	lcd.clear()
	lcd.message('Check bit.ly/\ne-annotator ;)')
	Play(getAudio("thankyou", thankNo), 0)
	setDelay("thankyou", thankNo)
	if ansType == "instrument":
		instrumentAttempts_list.append("T")
	registerRecord(ansType,"no")
	print (">> Handled no instrument answer")

def registerNoParticipation():
	lcd.clear()
	lcd.message('Check bit.ly/\ne-annotator ;)')
	Play(getAudio("thankyou", thankNo), 0)
	setDelay("thankyou", thankNo)
	participationAttempts_list.append("F")
	registerRecord("participation","na")
	return 0

def registerNoInstrument():
	lcd.clear()
	lcd.message('Check bit.ly/\ne-annotator ;)')
	Play(getAudio("thankyou", thankNo), 0)
	setDelay("thankyou", thankNo)
	instrumentAttempts_list.append("F")
	registerRecord("instrument","na")

def registerRecord(ansType,ans):
    registeringTime = time.time()
    length = registeringTime - startingTime
    print length
    listPart = ''.join(participationAttempts_list)
    listInst = ''.join(instrumentAttempts_list)

    if  (ansType == "participation") and (ans == "no"):
		record = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + str(len(participationAttempts_list)) + '\t' + "NO" + '\t' + listPart + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + str(length) + '\n'
    elif (ansType == "participation") and (ans == "na"):
        record = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + str(len(participationAttempts_list)) + '\t' + "NA" + '\t' + listPart + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + 'NA' + '\t' + str(length) + '\n'
    elif (ansType == "instrument") and (ans == "yes"):
        record = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + str(len(participationAttempts_list)) + '\t' + "YES" + '\t' + listPart + '\t' + 'sound' + str(musicNo) + '\t' + str(seek) + '\t' + instruments[instruNo] + '\t' + str(len(instrumentAttempts_list)) + '\t' + "YES" + '\t' + listInst + '\t' + str(length) + '\n'
    elif (ansType == "instrument") and (ans == "no"):
        record = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + str(len(participationAttempts_list)) + '\t' + "YES" + '\t' + listPart + '\t' + 'sound' + str(musicNo) + '\t' + str(seek) + '\t' + instruments[instruNo] + '\t' + str(len(instrumentAttempts_list)) + '\t' + "NO" + '\t' + listInst + '\t' + str(length) + '\n'
    elif (ansType == "instrument") and (ans == "na"):
        record = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + str(len(participationAttempts_list)) + '\t' + "YES" + '\t' + listPart + '\t' + 'sound' + str(musicNo) + '\t' + str(seek) + '\t' + instruments[instruNo] + '\t' + str(len(instrumentAttempts_list)) + '\t' + "NA" + '\t' + listInst + '\t' + str(length) + '\n'
    else:
        print (">> Error before registering record")

    print ("Record: " + record)
    meta = open('/home/pi/Documents/ElevatorAnnotator/experiment2.tsv', 'a')
    meta.write(record)
    meta.close()
    camera.capture('/home/pi/Documents/ElevatorAnnotator/images/img_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H-%M-%S') + '.jpg')
    time.sleep(5)

def handleOtherInstrumentAnswer():
    answer = repeatAgain()
    if(isYesAnswer(answer)):
        handleYesAnswer()
        return 0
    elif(isNoAnswer(answer)):
        handleNoAnswer("instrument")
        return 0
    else:
        pass

def handleOtherParticipationAnswer():
    participationAnswer = repeatAgain()
    if isYesAnswer(participationAnswer):
        participationAttempts_list.append("T")
        playMusic()
        return True
    elif isNoAnswer(participationAnswer):
		lcd.clear()
		lcd.message('Check bit.ly/\neannotator ;)')
		Play(getAudio("thankyou", thankNo), 0)
		setDelay("thankyou", thankNo)
		participationAttempts_list.append("T")
		registerRecord("participation","no")
		return 0
    else:
        pass
        
## Simplified functions
def getAudio(audioType, no):
    audioDir = ''
    if audioType == "hello":
        audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/hello" + str(no) + ".wma"
        return audioDir
    elif audioType == "repeat":
        audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/pleaserepeat" + str(no) + ".wma"
        return audioDir
    elif audioType == "thankyou":
        audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/thankyou" + str(no) + ".wma"
        return audioDir
    elif audioType == "instrument":
        if no == 0:
            audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/violin.wma"
            return audioDir
        elif no == 1:
            audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/trumpet.wma"
            return audioDir
        elif no == 2:
            audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/piano.wma"
            return audioDir
        else:
            print "Error: Failed to get instrument"
    elif audioType == "beep":
		audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/beep" + str(no) + ".wma"
		return audioDir
    elif audioType == "music":
        audioDir = "/home/pi/Documents/ElevatorAnnotator/Music/sound" + str(no) + ".mp3"
        return audioDir
    elif audioType == "answer":
		audioDir = "/home/pi/Documents/ElevatorAnnotator/Voice/yesorno" + str(no) + ".wma"
		return audioDir
    else:
        print ("Error: Failed to get audio")

def getLength(audioDir, audioFormat):
    audioLen = 0
    if audioFormat == "mp3":
        audioLen = MP3(audioDir).info.length
        return audioLen
    elif audioFormat == "wma":
        audioLen = ASF(audioDir).info.length
        return audioLen
    else:
        print ("Error: Failed to get audio format")

def getPosition(audioLen, position):
    audioPosition = position * audioLen
    return audioPosition

def setDelay(audioType,no):
    time.sleep(getLength(getAudio(audioType,no),"wma") + 0.25)


def recogniseMe(mic):
    r = sr.Recognizer()

    try:
		with sr.Microphone(mic, sample_rate=44100) as source:
			r.dynamic_energy_treshold = False
			r.energy_treshold = 4000
			Play(getAudio("beep", 5), 0)
			setDelay("beep", 5)
			print("Say something!")
			lcd.clear()
			lcd.message('Speak now. Answer\nonly once YES/NO')
			audio = r.listen(source)
			answer=str(r.recognize_sphinx(audio))
			print("Sphinx thinks you said " + answer)
			answer=answer.lower()
			with open('/home/pi/Documents/ElevatorAnnotator/recordings/audio_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H-%M-%S') + '.wav', "wb") as f:
				f.write(audio.get_wav_data())
			return answer
    except sr.UnknownValueError:
		print("Google Speech Recognition could not understand audio")
		return None
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None
  
    #finally:
	#	with open('/home/pi/Documents/ElevatorAnnotator/recordings/audio_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H-%M-%S') + '.wav', "wb") as f:
	#		f.write(audio.get_wav_data())

def Play(sound,delay):
    p = vlc.MediaPlayer(sound)
    p.play()
    if (delay>0):
        p.set_position(delay)
        time.sleep(5)
        p.stop()

def playMusic():
    print (">> Play music")
    Play(getAudio("music", musicNo), seek)

def showLCDYesorNo():
	lcd.clear()
	lcd.blink(True)
	lcd.message('Answer w/ YES/NO\nafter the beep1x')

## Main functions for annotation: by voice and push button inputs
def startVoiceAnnotation():
	del participationAttempts_list[:]
	del instrumentAttempts_list[:]

	print participationAttempts_list
	print instrumentAttempts_list
	
	global startingTime
	startingTime = time.time()
	print startingTime
	global helloNo
	helloNo = str(random.randrange(1,3))
	global thankNo
	thankNo = str(random.randrange(1,3))
	global repeatNo
	repeatNo = str(random.randrange(1,3))
	global musicNo
	musicNo = str(random.randrange(1,11))
	global instruNo
	instruNo = random.randrange(0,3)
	global seek
	seek = random.choice(positionNo)
	
	print (">> Start annotation")
	log = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + "Motion detected" + '\n'
	meta = open('/home/pi/Documents/ElevatorAnnotator/motionLog.tsv', 'a')
	meta.write(log)
	meta.close()
	
	global mic
	mic = 0
	playMusic()

	print (">> Play hello" + helloNo)
	Play(getAudio("hello",helloNo),0)
	setDelay("hello",helloNo)
	
	Play(getAudio("answer",1),0)
	setDelay("answer",1)
	
	showLCDYesorNo()

	print (">> Get participation answer")
	participationAnswer = recogniseMe(mic)

	participationAttempt = 1
	while participationAttempt <= 3:
		#try:
		participationAttempt += 1
		if isInvalidAnswer(participationAnswer):
			participationAttempts_list.append("F")
			participationAnswer = repeatAgain()
		elif isYesAnswer(participationAnswer):
			participationAttempts_list.append("T")
			playMusic()
			break
		elif isNoAnswer(participationAnswer):
			lcd.clear()
			lcd.message('Check bit.ly/\ne-annotator ;)')
			Play(getAudio("thankyou", thankNo), 0)
			setDelay("thankyou", thankNo)
			participationAttempts_list.append("T")
			registerRecord("participation","no")
			return 0
		else:
			if (participationAttempt == 3):
				time.sleep(0.5)
				Play(getAudio("beep", 2), 0)
				setDelay("beep", 2)
				print ("Participation attempts exceeded")
				participationAttempts_list.append("F")
				registerNoParticipation()
				return 0
			if handleOtherParticipationAnswer() is True:
				break
			else:
				pass

	print (">> Play instrument: " + instruments[instruNo])
	Play(getAudio("instrument",instruNo),0)
	setDelay("instrument",int(instruNo))

	print (">> Get instrument answer")
	instrumentAnswer = recogniseMe(mic)

	instrumentAttempt = 1
	while instrumentAttempt <= 3:
		try:
			if isInvalidAnswer(instrumentAnswer):
				instrumentAttempts_list.append("F")
				instrumentAnswer = repeatAgain()
			elif isYesAnswer(instrumentAnswer):
				handleYesAnswer()
				return 0
			elif isNoAnswer(instrumentAnswer):
				handleNoAnswer("instrument")
				return 0
			else:
				if (instrumentAttempt == 3):
					time.sleep(0.5)
					Play(getAudio("beep", 2), 0)
					setDelay("beep", 2)
					instrumentAttempts_list.append("F")
					print ("Instrument attempts exceeded")
					registerNoInstrument()
					return 0
			instrumentAttempt += 1
		except Exception:
			print (">> Got an Exception" + str(Exception))
			Play(getAudio("repeat", repeatNo), 0)
			setDelay("repeat", repeatNo)

def MOTION(PIR_PIN):
    print (">> Motion Detected!")
    lcd.clear()
    lcd.message('Hello there :)')
    with open("/home/pi/Documents/ElevatorAnnotator/hello.txt", "w") as outfile:
		outfile.write("hello")
    print (">> Execute annotation script")
    startVoiceAnnotation()
    log2 = datetime.datetime.fromtimestamp(startingTime).strftime('%Y%m%d-%H:%M:%S') + '\t' + "Annotation is executed" + '\n'
    meta = open('/home/pi/Documents/ElevatorAnnotator/motionLog.tsv', 'a')
    meta.write(log2)
    meta.close()
    lcd.clear()


def main():
	while True:
		pir.wait_for_motion()
		MOTION(16)
		pir.wait_for_no_motion()

if __name__ == '__main__':
	lcd.clear()
	time.sleep(2)
	print (">> Board is ready")
	lcd.message('Board is ready')
	main()
