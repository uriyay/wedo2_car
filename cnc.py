import json
import network
import socket
import struct
from time import sleep

from wedo2 import wedo2

wlan = network.WLAN(network.STA_IF)
config = json.load(open('config.json'))

PORT = 7777

def init_network():
    #Notice that Windows blocks incoming connections..
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(config['SSID'], config['PASSWORD'])
        while not wlan.isconnected():
            pass

    wlan_config = wlan.ifconfig()
    print('network config:', wlan_config)
    return wlan_config

class CNC:
    def __init__(self, port=PORT):
        self.is_running = False
        self.port = port
        self.wlan_config = init_network()
        self.ip = self.wlan_config[0]
        self.wedo = None

    def advertise(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        sock.bind((self.ip, self.port))
        msg = ('Hello from CNC, listening on UDP socket ip=' + self.ip + ', port=' + str(self.port)).encode()
        sock.sendto(msg, ("255.255.255.255", self.port))
        sock.close()

    def run(self):
        self.advertise()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        sock.bind((self.ip, self.port))
        sock.listen(1)
        self.is_running = True
        while self.is_running:
            client, clientaddr = sock.accept()
            self.handle_client(self, client)
        sock.close()

    def response(self, client, res):
        data = json.dumps(res).encode()
        client.write(struct.pack('<H', len(data)) + data)

    def handle_client(self, client):
        is_client_running = True
        while is_client_running:
            datalen = struct.unpack('<H', client.read(2))
            data = client.read(datalen)
            cmd = json.loads(data)
            if cmd['cmd'] == 'quit':
                self.response(client, {'res': '0', 'msg': 'bye!'})
                self.is_running = False
                is_client_running = False
            elif cmd['cmd'] == 'connect':
                try:
                    self.wedo = wedo2.Wedo2()
                    self.wedo.scan()
                    self.response(client, {'res': '0', 'msg': 'wedo2 connected!'})
                except Exception as e:
                    self.response(client, {'res': '1', 'msg': 'Failed to connect wedo2, error: ' + str(e)})
                    self.wedo = None
            elif cmd['cmd'] == 'disconnect':
                if self.wedo:
                    try:
                        self.wedo.disconnect()
                        self.response(client, {'res': '0', 'msg': 'wedo2 disconnected!'})
                    except Exception as e:
                        self.response(client, {'res': '1', 'msg': 'Failed to disconnect wedo2, error: ' + str(e)})
                    self.wedo = None
            elif cmd['cmd'] == 'up':
                if not self.wedo:
                    self.response(client, {'res': '1', 'msg': 'wedo2 is not connected!'})
                else:
                    try:
                        #TODO: parameters can be passed in the json later
                        self.wedo.motor_turn(0, 100)
                        sleep(1)
                        self.wedo.motor_break(0)
                        self.response(client, {'res': '0', 'msg': 'up succeeded'})
                    except Exception as e:
                        self.response(client, {'res': '1', 'msg': 'up failed: ' + str(e)})
            elif cmd['cmd'] == 'down':
                if not self.wedo:
                    self.response(client, {'res': '1', 'msg': 'wedo2 is not connected!'})
                else:
                    try:
                        self.wedo.motor_turn(0, -100)
                        sleep(1)
                        self.wedo.motor_break(0)
                        self.response(client, {'res': '0', 'msg': 'down succeeded'})
                    except Exception as e:
                        self.response(client, {'res': '1', 'msg': 'down failed: ' + str(e)})
            elif cmd['cmd'] == 'right':
                if not self.wedo:
                    self.response(client, {'res': '1', 'msg': 'wedo2 is not connected!'})
                else:
                    try:
                        self.wedo.motor_turn(1, 10)
                        sleep(2)
                        self.wedo.motor_break(1)
                        self.response(client, {'res': '0', 'msg': 'right succeeded'})
                    except Exception as e:
                        self.response(client, {'res': '1', 'msg': 'right failed: ' + str(e)})
            elif cmd['cmd'] == 'left':
                if not self.wedo:
                    self.response(client, {'res': '1', 'msg': 'wedo2 is not connected!'})
                else:
                    try:
                        self.wedo.motor_turn(1, -10)
                        sleep(2)
                        self.wedo.motor_break(1)
                        self.response(client, {'res': '0', 'msg': 'left succeeded'})
                    except Exception as e:
                        self.response(client, {'res': '1', 'msg': 'left failed: ' + str(e)})

