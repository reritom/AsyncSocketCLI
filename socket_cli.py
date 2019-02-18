from threading import Thread, Event
import threading
from argparse import ArgumentParser
import socket, time, sys
from tools import get_ip
import logging

parser = ArgumentParser()
parser.add_argument("--ap", help="Use default Tower AP port", action="store_true")
parser.add_argument("--bp", help="Use default Tower bay port", action="store_true")
parser.add_argument("-p", help="Port to target", default=None)
parser.add_argument("-a", help="Address to target, defaults to localhost", default=get_ip())

class SocketCLI:
    def __init__(self, port, addr):
        self.port = port
        self.addr = addr
        self.stop_flag = Event()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.addr, self.port))
            s.settimeout(0)

            read_thread = Thread(target=self.read_socket, args=(s,))
            read_thread.start()

            while True:
                data_to_send = input("Send: ")

                if data_to_send in ['/exit', '/kill', '']:
                    print("Exitting")
                    self.stop_flag.set()
                    break
                else:
                    try:
                        s.send(bytes(data_to_send, 'utf-8'))
                    except:
                        print("Failed to send, exitting")
                    time.sleep(0.5)

            read_thread.join()

    def read_socket(self, connection):
        while True:
            if self.stop_flag.is_set():
                print("Killing socket reader")
                return

            try:
                read_value = connection.recv(1024).decode('utf-8')
                if read_value is "":
                    print("\b\b\b\b\b\bConnection closed", flush=True)
                    self.stop_flag.set()
                    continue

                print("Read: {}".format(read_value))
            except:
                pass

if __name__=="__main__":
    parsed = parser.parse_args()
    print(parsed)
    addr = get_ip()

    if parsed.ap:
        port = 61000
        print("Targetting Tower default AP port {} on {}".format(port, addr))
    elif parsed.bp:
        port = 65432
        print("Targetting Tower default bay port {} on {}".format(port, addr))
    elif parsed.p is None:
        raise Exception("parameter -p is required if --ap or --bp aren't used")
    else:
        addr = parsed.a
        port = int(parsed.p)
        print("Targetting Tower port {} on {}".format(port, addr))

    cli = SocketCLI(addr=addr, port=port)
    cli.run()