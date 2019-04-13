from sys import byteorder
from array import array
from struct import pack
import sys
import pyaudio
import wave
import random
import copy
import math
import threading
import tkinter as tk
import numpy as np
from tkinter import *

result=0
CHUNK = 1024
CHANNELS = 1
RECORD_SECONDS = 4
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
THRESHOLD = 200
SILENT_CHUNKS = 3 * 44100 / 1024  
FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
TRIM_APPEND = RATE / 4

def is_silent(data_chunk):
   
    return max(data_chunk) < THRESHOLD

def normalize(data_all):
    
    normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))

    r = array('h')
    for i in data_all:
        r.append(int(i * normalize_factor))
    return r

def trim(data_all):
	_from = 0
	
	_to = len(data_all) - 1
	for i, b in enumerate(data_all):
		if abs(b) > THRESHOLD:
			_from = max(0, i - TRIM_APPEND)
			break

	for i, b in enumerate(reversed(data_all)):
		if abs(b) > THRESHOLD:
			_to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
			break
	
	return copy.deepcopy(data_all[int(_from):(int(_to) + 1)])


	
	
    
def record():
	"""Record a word or words from the microphone and 
	return the data as an array of signed shorts."""

	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

	num_silent = 0
	snd_started = False
	data_all = array('h')

	while True:
		# little endian, signed short
		data_chunk = array('h', stream.read(CHUNK_SIZE))
		if byteorder == 'big':
			data_chunk.byteswap()
		data_all.extend(data_chunk)

		silent = is_silent(data_chunk)

		if snd_started:
			if silent:
				num_silent += 1
			else:
				num_silent += 0
		elif not silent and not snd_started:
			snd_started = True

		if snd_started and silent:
			if num_silent > 30:
				break
              

	sample_width = p.get_sample_size(FORMAT)
	stream.stop_stream()
	stream.close()
	p.terminate()

	data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
	data_all = normalize(data_all)
	return sample_width, data_all
def hist(c):
	val=len(c)
	for x in range(val):
		if math.isnan(c[x]):
			c[x]=0
	hist1,bins1 = np.histogram(c,bins = [0,50,100,200,400,600,800,1000,1500,3000,6000,12000,20000,30000]) 
	return hist1
	
def histogram():
	c = [0]*13
	for i in range (1,15):
		temp=filename
		temp=temp+"/"+str(i)+".wav"
		a = getfreq(temp)
		hist1=hist(a)
		for x in range(0,13):
			z=c[x]
			c[x]=z+hist1[x]
	
	temp1=[0]*13
	val=len(c)
	for x in range(0,13):
		temp1[x]=c[x]/14
		
		
	b = getfreq('sample.wav')
	
	val=len(b)
	for x in range(val):
		if math.isnan(b[x]):
			b[x]=0
	 
	hist2,bins2 = np.histogram(b,bins = [0,50,100,200,400,600,800,1000,1500,3000,6000,12000,20000,30000])
	print (temp1)
	print (hist2)
	compare(temp1,hist2)
	


	
	
	
def rec_destroy():
	
	#rec.destroy()
	histogram()


def record_to_file():
	
	sample_width, data=record()

	wave_file = wave.open('sample.wav', 'wb')
	wave_file.setnchannels(CHANNELS)
	wave_file.setsampwidth(sample_width)
	wave_file.setframerate(RATE)
	wave_file.writeframes(data)
	wave_file.close()
	rec_destroy()
	
	

		
def play():
	LISTFILE = ['Apple','Banana','Cherry','Grapes','Mango','Orange','Papaya','Pineapple','Strawberry','Watermelon']
	global filename
	filename= random.choice(LISTFILE)
	play1()

		
	
def play1():
	
	temp=filename+"/1.wav"
	chunk = 1024 
	f = wave.open(temp,"rb")  
	p = pyaudio.PyAudio()  
 
	stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
					channels = f.getnchannels(),  
					rate = f.getframerate(),  
					output = True)  

	data = f.readframes(chunk)  
	

	while data:  
		stream.write(data)  
		data = f.readframes(chunk)  

  
	stream.stop_stream()  
	stream.close()  
	p.terminate()  
	
def getfreq(path_loc):
	
	freq = []
	chunk = 2048
	temp1=path_loc
	if(path_loc=="sample.wav"):
	

		wf = wave.open(path_loc, 'rb')
		swidth = wf.getsampwidth()
		RATE = wf.getframerate()

		window = np.blackman(chunk)

		p = pyaudio.PyAudio()
		stream = p.open(format =
						p.get_format_from_width(wf.getsampwidth()),
						channels = wf.getnchannels(),
						rate = RATE,
						output = True)


		data = wf.readframes(chunk)

		while len(data) == chunk*swidth:
		
			#stream.write(data)
		
			indata = np.array(wave.struct.unpack("%dh"%(len(data)/swidth),\
											 data))*window
		
			fftData=abs(np.fft.rfft(indata))**2
	   
			which = fftData[1:].argmax() + 1
			
			if which != len(fftData)-1:
				y0,y1,y2 = np.log(fftData[which-1:which+2:])
				x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
				
				thefreq = (which+x1)*RATE/chunk
				freq.append(thefreq)
			else:
				thefreq = which*RATE/chunk
				freq.append(thefreq)
		
			data = wf.readframes(chunk)
		if data:
			stream.write(data)
		stream.close()
		p.terminate()
		
	else:
		
		wf = wave.open(path_loc, 'rb')
		swidth = wf.getsampwidth()
		RATE = wf.getframerate()

		window = np.blackman(chunk)

		p = pyaudio.PyAudio()
		stream = p.open(format =
						p.get_format_from_width(wf.getsampwidth()),
						channels = wf.getnchannels(),
						rate = RATE,
						output = True)


		data = wf.readframes(chunk)

		while len(data) == chunk*swidth:
			
				#stream.write(data)
		
			indata = np.array(wave.struct.unpack("%dh"%(len(data)/swidth),\
											 data))*window
			
			fftData=abs(np.fft.rfft(indata))**2
		   
			which = fftData[1:].argmax() + 1
				
			if which != len(fftData)-1:
				y0,y1,y2 = np.log(fftData[which-1:which+2:])
				x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
				
				thefreq = (which+x1)*RATE/chunk
				freq.append(thefreq)
			else:
				thefreq = which*RATE/chunk
				freq.append(thefreq)
		
			data = wf.readframes(chunk)
		if data:
			stream.write(data)
		stream.close()
		p.terminate()
			
		
			
		
	return freq

def rec():
	
	global rec
	rec=tk.Tk()
	rec.title("Recording...")
	rec.geometry("200x100")
	rec.resizable(0,0)
	b1=tk.Button(rec, text="Start",command=record_to_file).grid(sticky='',row=0)
	b=tk.Button(rec, text="Stop",command=rec_destroy).grid(sticky='',row=0,column=1)
	
	rec.mainloop()

def compare(p,q):
	
	global result
	a=p
	b=q
	count=0
	total=0
	x=len(a)
	y=len(b)
	if x<y :
		val=x
	else:
		val=y
	
	for x in range(val):
			
		total=total+1
		
		
				
		if a[x]-3<=b[x]<=a[x]+2:
			count=count+1
	
	result = count*100/total
	result1=int(result)
	l5=tk.Label(top,text=result1, font=('Arial',22)).grid(sticky='',row=6,column=0)
	if result>70:
		game()
	
	
	
	
def game():
	global score
	from math import sqrt
	from random import shuffle
	HEIGHT = 500
	WIDTH = 500
	window = Tk()
	colors = ["darkred", "green", "blue", "purple", "pink", "lime"]
	health = {
		"ammount" : 3,
		"color": "green"
	}
	window.title("Bubble Blaster")
	c = Canvas(window, width=WIDTH, height=HEIGHT, bg="darkblue")
	c.pack()
	ship_id = c.create_polygon(5, 5, 5, 25, 30, 15, fill="green")
	ship_id2 = c.create_oval(0, 0, 30, 30, outline="red")
	SHIP_R = 15
	MID_X = WIDTH / 2
	MID_Y = HEIGHT / 2
	c.move(ship_id, MID_X, MID_Y)
	c.move(ship_id2, MID_X, MID_Y)
	ship_spd = 10
	score = 0
	def move_ship(event):
		if event.keysym == "Up":
			c.move(ship_id, 0, -ship_spd)
			c.move(ship_id2, 0, -ship_spd)
		elif event.keysym == "Down":
			c.move(ship_id, 0, ship_spd)
			c.move(ship_id2, 0, ship_spd)
		elif event.keysym == "Left":
			c.move(ship_id, -ship_spd, 0)
			c.move(ship_id2,  -ship_spd, 0)
		elif event.keysym == "Right":
			c.move(ship_id, ship_spd, 0)
			c.move(ship_id2,  ship_spd, 0)
		elif event.keysym == "P":
			score += 10000
	c.bind_all('<Key>', move_ship)
	from random import randint
	bub_id = list()
	bub_r = list()
	bub_speed = list()
	bub_id_e = list()
	bub_r_e = list()
	bub_speed_e = list()
	min_bub_r = 10
	max_bub_r = 30
	max_bub_spd = 10
	gap = 100
	def create_bubble():
		x = WIDTH + gap
		y = randint(0, HEIGHT)
		r = randint(min_bub_r, max_bub_r)
		id1 = c.create_oval(x - r, y - r, x + r, y + r, outline="white", fill="lightblue")
		bub_id.append(id1)
		bub_r.append(r)
		bub_speed.append(randint(5, max_bub_spd))
	def create_bubble_e():
		x = WIDTH + gap
		y = randint(0, HEIGHT)
		r = randint(min_bub_r, max_bub_r)
		id1 = c.create_oval(x - r, y - r, x + r, y + r, outline="black", fill="red")
		bub_id_e.append(id1)
		bub_r_e.append(r)
		bub_speed_e.append(randint(6, max_bub_spd))
	def create_bubble_r():
		x = WIDTH + gap
		y = randint(0, HEIGHT)
		r = randint(min_bub_r, max_bub_r)
		id1 = c.create_oval(x - r, y - r, x + r, y + r, outline="white", fill=colors[0])
		bub_id.append(id1)
		bub_r.append(r)
		bub_speed.append(randint(6, max_bub_spd))
	def move_bubbles():
		for i in range(len(bub_id)):
			c.move(bub_id[i], -bub_speed[i], 0)
		for i in range(len(bub_id_e)):
			c.move(bub_id_e[i], -bub_speed_e[i], 0)
	from time import sleep, time
	bub_chance = 30
	def get_coords(id_num):
		pos = c.coords(id_num)
		x = (pos[0] + pos[2]) / 2
		y = (pos[1] + pos[3]) / 2
		return x, y
	def del_bubble(i):
		del bub_r[i]
		del bub_speed[i]
		c.delete(bub_id[i])
		del bub_id[i]
	def clean():
		for i in range(len(bub_id) -1, -1, -1):
			x, y = get_coords(bub_id[i])
			if x < -gap:
				del_bubble(i)
	def distance(id1, id2):
		x1, y1 = get_coords(id1)
		x2, y2 = get_coords(id2)
		return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
	def  collision():
		points = 0
		for bub in range(len(bub_id) -1, -1, -1):
			if distance(ship_id2, bub_id[bub]) < (SHIP_R + bub_r[bub]):
				points += (bub_r[bub] + bub_speed[bub])
				del_bubble(bub)
		return points
	def cleanAll():
		for i in range(len(bub_id) -1, -1, -1):
			x, y = get_coords(bub_id[i])
			del_bubble(i)
	def  collision_e():
		for bub in range(len(bub_id_e) -1, -1, -1):
			if distance(ship_id2, bub_id_e[bub]) < (SHIP_R + bub_r_e[bub]):
				window.destroy()
				#print("You were killed by a red bubble...")
				#print("You got ", score, " score!")
				sleep(100)            
	c.create_text(50, 30, text="SCORE", fill="white")
	st = c.create_text(50, 50, fill="white")
	c.create_text(100, 30, text="TIME", fill="white")
	tt = c.create_text(100, 50, fill="white")
	def show(score):
		c.itemconfig(st, text=str(score))
	evil_bub = 50
	#MAIN GAME LOOP
	while True:
		if randint(1, bub_chance) == 1:
			create_bubble()
		if randint(1, evil_bub) == 1:
			create_bubble_e()
		if randint(1, 100) == 1:
			create_bubble_r()
		move_bubbles()
		collision_e()
		clean()
		score += collision()
		if score >= 400:
			evil_bub = 40
			bub_chance = 25
			if score >= 1000:
				evil_bub = 30
				bub_chance = 20
		show(score)
		window.update()
		shuffle(colors)
		sleep(0.01)
		l6=tk.Label(top,text="Score=%s"%(score), font=('Arial',22)).grid(sticky='',row=7,column=0)
	
	
def frame():
	
	global top
	top=tk.Tk()
	top.title("Speech Therapy")
	top.geometry("500x500")
	top.resizable(0, 0)
	
	l1=tk.Label(top,text="Speech Therapy",font=('Arial',44)).grid(sticky='')
	
	l2=tk.Label(top,text="Press play to play the Audio", font=('Arial',22)).grid(sticky='')
	b2=tk.Button(top,text="Play",command=play).grid(row=2,column=0)
	l3=tk.Label(top,text="Press Record to start recording", font=('Arial',22)).grid(sticky='',row=3,column=0)
	
	b3=tk.Button(top,text="Record",command=record_to_file).grid(row=4,column=0)
	
	l4=tk.Label(top,text="Result:", font=('Arial',22)).grid(sticky='',row=5,column=0)
	
	
	l5=tk.Label(top,text=result, font=('Arial',22)).grid(sticky='',row=6,column=0)
	
	
	
	
	top.mainloop()
			

if __name__ == '__main__':
	
	
	LISTFILE = ['Apple','Banana','Cherry','Grapes','Mango','Orange','Papaya','Pineapple','Strawberry','Watermelon']
	global filename
	filename= random.choice(LISTFILE)
	frame()
	