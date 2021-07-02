from flask import Flask, render_template, request , redirect, url_for, request
import RPi.GPIO as GPIO
import signal
import sys
import ssl
import os
from threading import Thread
from time import sleep
from datetime import datetime
app = Flask (__name__)


#===============================================================================
# Initial Setup

# Constants
danLight_version = '1.0a'

lounge_button_gpio = 5
kitchen_button_gpio = 22
rumpus_button_gpio = 27			
bedroom_button_gpio = 17
attic_button_gpio = 4

lounge_led_gpio = 21
kitchen_led_gpio = 20
rumpus_led_gpio = 16
bedroom_led_gpio = 12
attic_led_gpio = 25

refresh_DNS_time = 900.0	#Dns refersh time in seconds (900sec = 15mins)
update_DNS_script = '/home/pi/updateDNS'
# Variables

lounge_state =  0
kitchen_state =  0
rumpus_state =  0
bedroom_state =  0
attic_state =  0

# Setup GPIO pins for inputs or outputs
GPIO.setmode(GPIO.BCM)		# setup fro broadcom mode
GPIO.setup([lounge_button_gpio, kitchen_button_gpio, rumpus_button_gpio, bedroom_button_gpio, attic_button_gpio ],GPIO.IN, pull_up_down=GPIO.PUD_UP) #setup inputs
GPIO.setup([lounge_led_gpio, kitchen_led_gpio, rumpus_led_gpio, bedroom_led_gpio,attic_led_gpio ],GPIO.OUT)	#setup outputs
#===============================================================================
#

# Debounce. button_input = is read input. button_gpio is the button input pin number / gpio number
def debounce(button_input,button_gpio):
		global ISR_called
		debounce_state1 = button_input
		debounce_state2 = button_input
		while debounce_state1 == debounce_state2:
			sleep(0.4)
			debounce_state2 = GPIO.input(button_gpio)

# Button input monitor thread (t1)
# Monitors 5 buttons for light switching
def button_read_loop():
	global lounge_button_gpio
	global kitchen_button_gpio
	global rumpus_button_gpio
	global bedroom_button_gpio
	global attic_buttom_gpio

	# Button monitoring via button scanning
	while True:
		button_input1 = GPIO.input(lounge_button_gpio)
		if button_input1 == False:
			debounce(button_input1,lounge_button_gpio)
			toggle_lounge()
			
		button_input2 = GPIO.input(kitchen_button_gpio)
		if button_input2 == False:
			debounce(button_input2,kitchen_button_gpio)
			toggle_kitchen()

		button_input3 = GPIO.input(rumpus_button_gpio)
		if button_input3 == False:
			debounce(button_input3,rumpus_button_gpio)
			toggle_rumpus()
			
		button_input4 = GPIO.input(bedroom_button_gpio)
		if button_input4 == False:
			debounce(button_input4,bedroom_button_gpio)
			toggle_bedroom()			

		button_input5 = GPIO.input(attic_button_gpio)
		if button_input5 == False:
			debounce(button_input5,attic_button_gpio)
			toggle_attic()

# puts current state into log file and logs trigger of lights changing
def update_file(function_type='not specified'):
	global lounge_state
	log_file = "./static/log.txt"
			
	file = open(log_file, 'a')
	log_time = str(datetime.now())

	file_data =  '<LOG>\n'\
			'time='+log_time+'\n'\
			'type='+function_type+'\n'\
			'lounge_light_state='+ str(lounge_state)+'\n'\
			'kitchen_light_state='+ str(kitchen_state)+'\n'\
			'rumpus_light_state='+ str(rumpus_state)+'\n'\
			'bedroom_light_state='+ str(bedroom_state)+'\n'\
			'attic_light_state='+ str(attic_state)+'\n'\
			+'<END LOG>\n\n'
	print(file_data)
	file.write(file_data)
	file.close()

#------------------------------------------------
# functions to turn lights on or off
def toggle_lounge(function_type='not specified'):
	global lounge_state
	if lounge_state == 1:
		GPIO.output(lounge_led_gpio, GPIO.LOW)
		lounge_state = 0
	else:
		GPIO.output(lounge_led_gpio, GPIO.HIGH)
		lounge_state = 1
	update_file(function_type)

def toggle_kitchen(function_type='not specified'):
	global kitchen_state
	if kitchen_state == 1:
		GPIO.output(kitchen_led_gpio, GPIO.LOW)
		kitchen_state = 0
	else:
		GPIO.output(kitchen_led_gpio, GPIO.HIGH)
		kitchen_state = 1
	update_file(function_type)

def toggle_bedroom(function_type='not specified'):
	global bedroom_state
	if bedroom_state == 1:
		GPIO.output(bedroom_led_gpio, GPIO.LOW)
		bedroom_state = 0
	else:
		GPIO.output(bedroom_led_gpio, GPIO.HIGH)
		bedroom_state = 1
	update_file(function_type)

def toggle_rumpus(function_type='not specified'):
	global rumpus_state
	if rumpus_state == 1:
		GPIO.output(rumpus_led_gpio, GPIO.LOW)
		rumpus_state = 0
	else:
		GPIO.output(rumpus_led_gpio, GPIO.HIGH)
		rumpus_state = 1
	update_file(function_type)

def toggle_attic(function_type='not specified'):
	global attic_state
	if attic_state == 1:
		GPIO.output(attic_led_gpio, GPIO.LOW)
		attic_state = 0
	else:
		GPIO.output(attic_led_gpio, GPIO.HIGH)
		attic_state = 1
	update_file(function_type)
#------------------------------------------------
# lts_mode for all lights in the house - on, off or late are valid modes
# default to off if invalid parameter passed

def lts_mode(all_state='off'):
	global lounge_state, kitchen_state, bedroom_state, rumpus_state, attic_state
	
	# ALl Lts on Modes
	if all_state == 'on':
		GPIO.output(lounge_led_gpio, GPIO.HIGH)
		lounge_state = 1
		GPIO.output(kitchen_led_gpio, GPIO.HIGH)
		kitchen_state = 1
		GPIO.output(bedroom_led_gpio, GPIO.HIGH)
		bedroom_state = 1
		GPIO.output(rumpus_led_gpio, GPIO.HIGH)
		rumpus_state = 1
		GPIO.output(attic_led_gpio, GPIO.HIGH)
		attic_state = 1

	# Late mode setting
	elif all_state =='late':
		GPIO.output(lounge_led_gpio, GPIO.LOW)
		lounge_state = 0
		GPIO.output(kitchen_led_gpio, GPIO.HIGH)
		kitchen_state = 1
		GPIO.output(bedroom_led_gpio, GPIO.LOW)
		bedroom_state = 0
		GPIO.output(rumpus_led_gpio, GPIO.HIGH)
		rumpus_state = 1
		GPIO.output(attic_led_gpio, GPIO.LOW)
		attic_state = 0

	# All Lts Off mode otherwise
	else:
		GPIO.output(lounge_led_gpio, GPIO.LOW)
		lounge_state = 0
		GPIO.output(kitchen_led_gpio, GPIO.LOW)
		kitchen_state = 0
		GPIO.output(bedroom_led_gpio, GPIO.LOW)
		bedroom_state = 0
		GPIO.output(rumpus_led_gpio, GPIO.LOW)
		rumpus_state = 0
		GPIO.output(attic_led_gpio, GPIO.LOW)
		attic_state = 0

	print('all lts to', all_state)
	update_file('mode button: web-all-'+all_state)

#===============================================================================
#	Web URL routes from browser GET sends

# refresh coming in from web interface (html)
@app.route('/refresh/', methods=['GET'])
def refresh_lounge_state():
	global lounge_state
	global kitchen_state
	global bedroom_state
	global rumpus_state
	global attic_state
	print('<Web Refresh>\n' + \
		'lounge_light_state='+ str(lounge_state)+'\n'\
	'kitchen_light_state='+ str(kitchen_state)+'\n'\
	'rumpus_light_state='+ str(rumpus_state)+'\n'\
	'bedroom_light_state='+ str(bedroom_state)+'\n'\
	'attic_light_state='+ str(attic_state)+'\n')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state, rumpus_state = rumpus_state, attic_state=attic_state)

# Default web route (first open html)
@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state, rumpus_state = rumpus_state, attic_state=attic_state)
	
# Lounge Button Push from web page action
@app.route('/Lounge-Button-Push/')
def lounge():
	toggle_lounge('web-lounge-push')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state, rumpus_state = rumpus_state, attic_state=attic_state)
	
# Kitchen Button Push from web page action
@app.route('/Kitchen-Button-Push/')
def kitchen():
	toggle_kitchen('web-kitchen-push')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state, rumpus_state = rumpus_state, attic_state=attic_state)

# Bedroom Button Push from web page action
@app.route('/Bedroom-Button-Push/')
def bedroom():
	toggle_bedroom('web-bedroom-push')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state, rumpus_state = rumpus_state, attic_state=attic_state)

# Rumpus Button Push from web page action
@app.route('/Rumpus-Button-Push/')
def rumpus():
	toggle_rumpus('web-rumpus-push')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state, rumpus_state = rumpus_state, attic_state=attic_state)

# Attic Button Push from web page action
@app.route('/Attic-Button-Push/')
def attic():
	toggle_attic('web-attic-push')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state,rumpus_state = rumpus_state,attic_state=attic_state)

# All Lts On Mode
@app.route('/Mode-All-On/')
def all_on():
	lts_mode('on')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state,rumpus_state = rumpus_state,attic_state=attic_state)

# All Lts Off Mode
@app.route('/Mode-All-Off/')
def all_off():
	lts_mode('off')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state,rumpus_state = rumpus_state,attic_state=attic_state)
# All Lts Late Mode
@app.route('/Mode-Late/')
def late():
	lts_mode('late')
	return render_template('index.html', lounge_state=lounge_state, kitchen_state=kitchen_state, bedroom_state=bedroom_state,rumpus_state = rumpus_state,attic_state=attic_state)

# Default Button Push from web page action
@app.route('/Button-Push/')
def default():
	toggle_lounge('')
	return render_template('index.html', lounge_state=lounge_state)

#==============================================================================
# Final Setups

update_file('danLigt Server Start UP')	# Put server initialisation into log file
lts_mode('off')				# Start control with all lts off
print('danLight Version',danLight_version)
#===============================================================================
#	Keypad / button thread setup and SSL/Flask Server setup.

if __name__ == '__main__':
	t1 = Thread(target = button_read_loop) # Setup button read loop thread
	t1.setDaemon(True)
	t1.start()

	app.run(ssl_context=('cert.pem','key.pem'), debug = False, host = '0.0.0.0', port=443) # Run Flask with ssl
	signal.pause()
