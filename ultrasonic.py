from machine import Pin, time_pulse_us
from time import sleep, ticks_ms

SOUND_SPEED = 0.034

#This code is taken from https://randomnerdtutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
class UltraSonic:
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        self.echo_timeout_us=500*2*30
        self.pTrigger = Pin(trigger_pin, Pin.OUT)
        self.pEcho = Pin(echo_pin, mode=Pin.IN, pull=None)

    def get_distance(self):
        # set the value low then high
        self.pTrigger.value(1)
        #sleep 10 ms
        sleep(0.01)
        self.pTrigger.value(0)

        duration_us = time_pulse_us(self.pEcho, 1, self.echo_timeout_us)
        distance_cm = duration_us * (SOUND_SPEED / 2)
        return distance_cm
