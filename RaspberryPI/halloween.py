import sys
import time
import signal
import os
import RPi.GPIO as GPIO
import random
from multiprocessing import Process
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
Pumpkin = 17 
light = 18
TRIG = 23
ECHO = 24
try:
	GPIO.cleanup()
except:
	pass

on = False
off = True
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(light,GPIO.OUT)
GPIO.setup(Pumpkin,GPIO.OUT)
GPIO.output(light, off)
GPIO.output(Pumpkin, on)
soundfolder = "/home/pi/halloween/sounds"
songs = []
debug=False
doorbell = soundfolder + os.sep+"0.wav"
gost = soundfolder + os.sep+"go.wav"
doorrange = soundfolder + os.sep+"drange.wav"

for i in range(1, 7):
        songs.append(soundfolder+os.sep+str(i)+".wav")
tempos = [16,9,10,6,10,7]
nsongs = len(songs)

def osErro():
	GPIO.output(light, off)
	GPIO.output(Pumpkin, on)
	os.system("sudo reboot")

def getdistance2(TRIG,ECHO):
	GPIO.output(TRIG, False)
	GPIO.output(TRIG, True)
	while GPIO.input(ECHO)==0:
		pulse_start = time.time()
	while GPIO.input(ECHO)==1:
		pulse_end = time.time()
	pulse_duration = pulse_end - pulse_start
	distance = pulse_duration * 17150
	return round(distance, 2)

def getdistance(TRIG,ECHO):
	time.sleep(0.1)
	GPIO.output(TRIG,1)
	time.sleep(0.00001)
	GPIO.output(TRIG,0)
	while GPIO.input(ECHO)==0:
		pass
	start = time.time()
	while GPIO.input(ECHO)==1:
		pass
	stop= time.time()
	ret= (stop-start)*17000
	return ret



def SoundVar(s1,s2):
	if 0!=os.system("aplay " + songs[s1]): osErro()
        time.sleep(0.5)
        if 0!=os.system("aplay " + songs[s2]): osErro()

def Gost():
	if 0!=os.system("aplay " + doorrange): osErro()
        if 0!=os.system("aplay " + gost): osErro()
	if 0!=os.system("aplay " + gost): osErro()


def Soundanimation(s1, s2):
	if 0!=os.system("aplay " + doorbell): osErro()
	if 0!=os.system("aplay " + doorbell): osErro()
	time.sleep(1)
	p=Process(target=SoundVar,args=(s1,s2,))
	p.start()
	return p

def Lanim0(tp):
	v=0
	while v<tp:
		GPIO.output(Pumpkin, on)
		time.sleep(0.5)
		GPIO.output(Pumpkin, off)
		time.sleep(0.5)
		v+=1

def Lanim1(tp):
        v=0
        while v<tp:
		GPIO.output(Pumpkin, on)
		GPIO.output(light, on)
		time.sleep(0.5)
		GPIO.output(Pumpkin, off)
		GPIO.output(light, off)
		time.sleep(0.5)
		v+=1

def Lanim2(tp):
        v=0
        while v<tp:
		GPIO.output(Pumpkin, on)
		GPIO.output(light, off)
		time.sleep(0.5)
		GPIO.output(Pumpkin, off)
		GPIO.output(light, on)
		time.sleep(0.5)
		v+=1

def Lanim3(tp):
        v=0
        while v<tp:
                GPIO.output(light, off)
                time.sleep(0.5)
                GPIO.output(light, on)
                time.sleep(0.5)
                v+=1

def Lanim4(tp):
	time.sleep(tp)

def Lightanimation(tp):
	animid = random.randint(0,4)
	#print "Anime: " + str(animid)
	if animid<=2:
		GPIO.output(light, on)
		GPIO.output(Pumpkin, off)
		animid = random.randint(0,2)
		if animid ==0:
			Lanim0(tp)
		elif animid ==1:
			Lanim1(tp)
		else:
			Lanim2(tp)
	else:
	#elif animid<=4:
		GPIO.output(light, on)
		if animid==3:
			Lanim3(tp)
		else: Lanim4(tp)
		
	GPIO.output(light, off)
	GPIO.output(Pumpkin, on)


def doAnimation(i1,i2):
	p= Soundanimation(i1,i2)
	Lightanimation(tempos[i1]+tempos[i2]+1)
	p.join()

def main():

	play = False

	def handlerAlarm(*args):
        	if play:
                	signal.alarm(5*60)
        	else:
                	p=Process(target=Gost)
                	p.start()
                	Lightanimation(22)
                	p.join()
                	signal.alarm(30*60)


	signal.signal(signal.SIGALRM, handlerAlarm)
	
	signal.alarm(1)
	time.sleep(2)
	i=0
	while True:
		if debug:
			dist = 70
		else:
#			print "Vou ler Dist"
			dist = getdistance(TRIG,ECHO)
#			print "Distancia: " + str(dist)
		if dist>15 and dist<150:
			soundi = i % nsongs
			soundi2 = random.randint(1,len(songs)-1)
			while soundi == soundi2:
				soundi2 = random.randint(1,len(songs)-1)
			play = True
			doAnimation(soundi,soundi2)
			play =False
			i+=1
			time.sleep(10) #se algem ativar o sensor fica inativo por 2min	
		else:
			time.sleep(5) 


if __name__ == '__main__':
	i=0
	while(i<5):
		i+=1
		print "Dist: " +str(getdistance(TRIG,ECHO))
#		v=raw_input()
#	while True:
#		try:
#			main()
#		except:
#			print "ERROR"
	main()
