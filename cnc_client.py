import socket
import struct
import json
import re
from scapy.all import sniff, UDP
from time import sleep

PORT = 7777

class CNCClient:
    def __init__(self, ip=None, port=None):
        self.ip = None
        self.port = None
        if ip:
            self.ip = ip
        if port:
            self.port = port
        if (not self.ip) or (not self.port):
            #get the connection details automatically
            self.ip, self.port = self.get_connection_details()

        print('connecting to ip={}, port={}'.format(self.ip, self.port))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

    def get_connection_details(self):
        pkts = sniff(count=1, filter="udp and port 7777")
        data = bytes(pkts[0][UDP].payload)
        data = data.decode()
        m = re.search('.*ip=(.+), port=(\d+)', data)
        ip, port = m.groups()
        port = int(port)
        return ip, port
    
    def connect(self):
        self.sock.sendto(b'HELLO', (self.ip, self.port))

    def send_command(self, json_obj):
        data = json.dumps(json_obj).encode()
        print('sending command: {}'.format(data))
        self.sock.sendto(struct.pack('<H', len(data)), (self.ip, self.port))
        self.sock.sendto(data, (self.ip, self.port))
        recv_data, _ = self.sock.recvfrom(1024)
        resp_len = struct.unpack('<H', recv_data[:2])[0]
        resp = recv_data[2:2 + resp_len]
        resp_json = json.loads(resp)
        print('response: ' + str(resp_json))
        return resp_json

    def quit(self):
        self.send_command({'cmd': 'quit'})

    def echo(self):
        self.send_command({'cmd': 'echo'})

    def wedo2_connect(self):
        self.send_command({'cmd': 'connect'})

    def wedo2_disconnect(self):
        self.send_command({'cmd': 'disconnect'})

    def wedo2_is_connected(self):
        resp = self.send_command({'cmd': 'is_connected'})
        if resp['msg'] == 'True':
            return True
        return False

    def up(self):
        self.send_command({'cmd': 'up'})

    def down(self):
        self.send_command({'cmd': 'down'})

    def right(self):
        self.send_command({'cmd': 'right'})

    def left(self):
        self.send_command({'cmd': 'left'})

    def get_distance(self):
        resp = self.send_command({'cmd': 'distance'})
        if resp['res'] == 1:
            raise Exception('Cannot get distance, ultrasonic sensor is not configured')
        distance = float(resp['msg'])
        return distance


if __name__ == '__main__':
    c = CNCClient()
    c.connect()
    c.echo()
    print('distance = ' + str(c.get_distance()))
    for i in range(5):
        _ = input('Power on wedo2 car and press ENTER')
        c.wedo2_connect()
        if c.wedo2_is_connected():
            break
    c.up()
    sleep(3)
    c.wedo2_disconnect()
    c.quit()