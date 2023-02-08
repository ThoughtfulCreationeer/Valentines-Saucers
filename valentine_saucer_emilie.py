"""
Valentine Saucers - Emilies saucer runs this code
_____________________________________________________________________________________

This project was inspired by and couldn´t have been made without the projects and documentation created be the following creators:

1. Uri Shaked´s MicroPython IoT Weather Station Example for Wokwi.com - https://wokwi.com/arduino/projects/322577683855704658
2. tayfunulu´s WiFi Manager - https://github.com/tayfunulu/WiFiManager
3. Randon nerd tutorials WiFi manager and LED documentation - Resp.
    a. https://randomnerdtutorials.com/micropython-wi-fi-manager-esp32-esp8266/
    b. https://randomnerdtutorials.com/esp32-esp8266-rgb-led-strip-web-server/
4. Bhavesh Kakwani MicroPython - MQTT tutorial on ESP32 - https://www.youtube.com/watch?v=BkXWInr-KWM
5. Albrecht Schmidt Sketching with Hardware at LMU - https://www.youtube.com/watch?v=K2m6ttZ1bJw

"""

from time import sleep
from machine import Pin, ADC, PWM, TouchPad
import ujson
from umqtt.simple import MQTTClient
import wifimgr


# MQTT Server Parameters
MQTT_CLIENT_ID      = "emilie"
MQTT_BROKER         = "eac7a3b1df514170b0cf7e6d64162653.s2.eu.hivemq.cloud"
MQTT_USER           = "emilie" #Emilie´s cup runs this code
MQTT_PASSWORD       = "LoveSince2021"
Temp_TOPIC_to_T     = b'temp_to_T'
Temp_TOPIC_to_E     = b'temp_to_E'
Color_TOPIC_to_T    = b'color_to_T' #The topic Emilie is writing to and Thoger is subscribing to
Color_TOPIC_to_E    = b'color_to_E' #The topic Thoger is writing to and Emilie is subscribing to

#preset variables
tmp36 = ADC(Pin(34))
tmp36.atten(ADC.ATTN_11DB)
touch1 = TouchPad(Pin(32))
touch2 = TouchPad(Pin(33))

greenLED = PWM(Pin(12))
redLED = PWM(Pin(27))
blueLED = PWM(Pin(26))

greenLED.freq(500)
redLED.freq(500)
blueLED.freq(500)

#Establishing color variables
colorpicker = 0
#list of colours respectively: Luminans Adjusted Mangenta, Blue, Luminans Adjusted Cyan, Green, Luminans Adjusted Yellow, Red, Dim White
LOC = [[8,0,8], [0,0,16], [0,8,8], [0,16,0], [8,8,0], [16,0,0], [1,1,1]] 
chosencolor = [1,1,1]
R = 1
G = 1
B = 1

#Startup
dimmingbrightness = 1023
for duty_cycle in range(25, 1024):
    redLED.duty(1*duty_cycle)
    greenLED.duty(1*duty_cycle)
    blueLED.duty(1*duty_cycle)
    sleep(0.003)
for duty_cycle in range(0, 1024):
    redLED.duty(1*dimmingbrightness)
    greenLED.duty(1*dimmingbrightness)
    blueLED.duty(1*dimmingbrightness)
    dimmingbrightness = dimmingbrightness-1
    sleep(0.003) 
    
sleep(0.1)

#Definitions
def rgb(r=1,g=1,b=1):
    
    dimmingbrightness = 63
    for duty_cycle in range(12, 63):
        redLED.duty(r*duty_cycle)
        greenLED.duty(g*duty_cycle)
        blueLED.duty(b*duty_cycle)
        sleep(0.02)
    for duty_cycle in range(12, 63):
        redLED.duty(r*dimmingbrightness)
        greenLED.duty(g*dimmingbrightness)
        blueLED.duty(b*dimmingbrightness)
        dimmingbrightness = dimmingbrightness-1
        sleep(0.02) 

#Callback function for color change based on subscription
#list of colours respectively: Luminans Adjusted Mangenta, Blue, Luminans Adjusted Cyan, Green, Luminans Adjusted Yellow, Red, Dim White
def sub_based_LED(topic, msg):
    global colorpicker
    
    if topic == Temp_TOPIC_to_E:
        print(msg)
        global loopcounter
        loopcounter = 10
        
    if topic == Color_TOPIC_to_E:
        print(msg)
        global loopcounter
        loopcounter = 1
        
        if msg == b'"Mangenta"':
            colorpicker = 0
        
        if msg == b'"Blue"':
            colorpicker = 1
            
        if msg == b'"Cyan"':
            colorpicker = 2
            
        if msg == b'"Green"':
            colorpicker = 3
            
        if msg == b'"Yellow"':
            colorpicker = 4
            
        if msg == b'"Red"':
            colorpicker = 5   
    global chosencolor
    chosencolor = LOC[colorpicker]
    
#Utilizing Tayfunu´s wifi manager
wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        greenLED.duty(0)
        redLED.duty(1023)
        blueLED.duty(0)

#Connect to the right MQTT server
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=7200, ssl=True, ssl_params={'server_hostname' : 'eac7a3b1df514170b0cf7e6d64162653.s2.eu.hivemq.cloud'})
client.connect()
print("Connected!")

#MQTT Subscription
client.set_callback(sub_based_LED)
client.subscribe(Color_TOPIC_to_E)
client.subscribe(Temp_TOPIC_to_E)

#Functional Loop
loopcounter = 0

while True:
    
#New Color
    
    rgb(R,G,B)
    
    loopcounter = loopcounter - 1

#Measure capasitance from sensor 1
    print("Reading of first sensor",touch1.read())

    if touch1.read() <= 110:
        colorpicker = colorpicker + 1
        loopcounter = 1
        
        if colorpicker >= 6:
            colorpicker = 0
            message = ujson.dumps("Mangenta")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 5:
            message = ujson.dumps("Red")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 4:
            message = ujson.dumps("Yellow")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 3:
            message = ujson.dumps("Green")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 2:
            message = ujson.dumps("Cyan")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 1:
            message = ujson.dumps("Blue")
            client.publish(Color_TOPIC_to_T, message)    
        chosencolor = LOC[colorpicker]
        
#Measure capasitance from sensor 2
    print("Reading of second sensor",touch2.read())
    
    if touch2.read() <= 110:
        colorpicker = colorpicker - 1
        loopcounter = 1
        if colorpicker == -1:
            colorpicker = 5
            message = ujson.dumps("Red")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 4:
            message = ujson.dumps("Yellow")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 3:
            message = ujson.dumps("Green")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 2:
            message = ujson.dumps("Cyan")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 1:
            message = ujson.dumps("Blue")
            client.publish(Color_TOPIC_to_T, message)
        if colorpicker == 0:
            message = ujson.dumps("Mangenta")
            client.publish(Color_TOPIC_to_T, message)    
        chosencolor = LOC[colorpicker]
  

#Function depending on own temperature measurements
    temperature = tmp36.read()
    print("Measuring temperature... ", temperature, end="")
    if temperature >= 780:
        print("temperature exeeded threshold with a temperature on:", temperature)
        message = ujson.dumps({"tet"}) #tet = temperature exeeded threshold
        client.publish(Temp_TOPIC_to_T, message)
        loopcounter = 10
        chosencolor = LOC[colorpicker]
    
#Function depending on subscription
  #Check on subscription for message
    client.check_msg()
    
    if loopcounter <= 0:
        chosencolor = LOC[6]
    
    
    print(chosencolor)    
    R = chosencolor[0]
    G = chosencolor[1]
    B = chosencolor[2]
    print("The new loopcounter is:", loopcounter)

    sleep(0.1)
