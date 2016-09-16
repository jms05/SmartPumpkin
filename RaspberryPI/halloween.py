import sys
import time
import signal
import os
import RPi.GPIO as GPIO
import random
from multiprocessing import Process
from nrf24 import NRF24
import spidev

GPIO.setmode(GPIO.BCM)

Pumpkin = 17 #pumkin gpio pin on relay
light = 18	#light gpio pin on relay

RF_CH=0x53 #comunnication channel


on = False
off = True

filenameLog = "SmartPmpkin.log"


GPIO.setup(light,GPIO.OUT)
GPIO.setup(Pumpkin,GPIO.OUT)
GPIO.output(light, off)
GPIO.output(Pumpkin, on)

soundfolder = "/home/pi/halloween/sounds" #where the sound animations 
songs = []
debug=False
doorbell = soundfolder + os.sep+"0.wav"
gost = soundfolder + os.sep+"go.wav"
doorrange = soundfolder + os.sep+"drange.wav"



#read info from songs to play
for i in range(1, 7):
        songs.append(soundfolder+os.sep+str(i)+".wav") #add the songs names to a  raaay to random
tempos = [16,9,10,6,10,7] #lenght of esch song
nsongs = len(songs)

def log(exception):
   	date = str(datetime.datetime.now())
   	f=open(filenameLog,"a")
   	f.write(date+":"+str(exception)+"\n")
	f.close()


def osErro(erro="---"): #to do when appens an error
	GPIO.output(light, off)
	GPIO.output(Pumpkin, on)
	GPIO.cleanup()
	log(erro)
	os.system("sudo reboot") #this reboot the pi (the python script should start at boot)

def setupReciver():
        pipes = [[0xf0, 0xf0, 0xf0, 0xf0, 0xe1], [0xf0, 0xf0, 0xf0, 0xf0, 0xd2]]
        radioN = NRF24()
        radioN.begin(0, 0,25,18) #set gpio 25 as CE pin
        radioN.setRetries(15,15)
        radioN.setPayloadSize(32)
        radioN.setChannel(RF_CH)
        radioN.setDataRate(NRF24.BR_250KBPS)
        radioN.setPALevel(NRF24.PA_MAX)
        radioN.setCRCLength(NRF24.CRC_8);
        radioN.setAutoAck(1)
		radioN.enableDynamicAck()
        radioN.openWritingPipe(pipes[0])
        radioN.openReadingPipe(1, pipes[1])

        radioN.startListening()
        radioN.stopListening()

        radioN.startListening()
        return radioN

try:
	radio= setupReciver()
except Exception as e:
	osErro(erro=e)

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


#Code to recive a message from arduino 

def reciveFromRemote():
	#outT,outH,outL,outP,outR,
    pipe = [0]
	print "Espera receber"
    	while not radio.available(pipe, True):
        	time.sleep(1000/100000.0)
	recv_buffer = []
    	radio.read(recv_buffer)
    	out = ''.join(chr(i) for i in recv_buffer)
    	print "Recived: " +out
	return out

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
		reciveFromRemote() #espera receber as mensagem do arduino quando recebe pode fazer animacao
		soundi = i % nsongs
		soundi2 = random.randint(1,len(songs)-1)
		while soundi == soundi2:
			soundi2 = random.randint(1,len(songs)-1)
		play = True
		doAnimation(soundi,soundi2)
		play =False
		i+=1


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		osErro(erro=e)