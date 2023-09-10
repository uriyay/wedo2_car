# wedo2_car
Code for controlling lego car built with wedo2 by using ESP32

# What it does
The cnc.py first sends a UDP broadcast packet (on a default port 7777) to advertise the UDP server that runs on this port.
The server handles JSON packets that can connect to the wedo2 car and control it.

# Instructions
1. First, build a steering lego car with Wedo2 as described [here](https://www.youtube.com/watch?v=k9LXXT0L71k&t=6s)
2. Upload a MicroPython firmware [to your ESP32](https://micropython.org/download/ESP32_GENERIC/)
(You might be able to use Mu Editor to burn the image, didn't check it though)
3. Create a config.json with this content:
```json
{
    "SSID": "YOUR_WIFI_SSID",
    "PASSWORD": "YOUR_WIFI_PASSWORD"
}
```
And upload it to your ESP32
4. Upload wedo2.py and cnc.py to the ESP32

# TODO
1. Uploader script
2. boot.py script that wait for a connection for a while
3. CNC client script
4. Connecting sensors to the ESP32
