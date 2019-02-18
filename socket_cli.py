from threading import Thread, Event
import threading
from argparse import ArgumentParser
import socket, time, sys
import logging

def get_ip():
    """
    Determine the local IP
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

parser = ArgumentParser()
parser.add_argument("--ap", help="Use default Tower AP port", action="store_true")
parser.add_argument("--bp", help="Use default Tower bay port", action="store_true")
parser.add_argument("-p", help="Port to target", default=None)
parser.add_argument("-a", help="Address to target, defaults to localhost", default=get_ip())

logging.basicConfig(
    filename='app.log',
    filemode='w',
    format='%(asctime)s-%(levelname)s-%(message)s',
    level=logging.INFO
)

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
                    logging.info("Exitting")
                    self.stop_flag.set()
                    break
                elif self.stop_flag.is_set():
                    # The reader thread might have noticed the connection has closed and set this flag
                    logging.info("Exitting")
                    break
                else:
                    try:
                        s.send(bytes(data_to_send, 'utf-8'))
                        logging.info("Sent: {}".format(data_to_send))
                    except:
                        logging.error("Failed to send, exitting")
                        print("Failed to send, exitting")
                        break
                    time.sleep(0.5)

            read_thread.join()

    def read_socket(self, connection):
        while True:
            if self.stop_flag.is_set():
                logging.debug("Killing socket reader")
                return

            try:
                read_value = connection.recv(1024).decode('utf-8')
                if read_value is "":
                    logging.info("Connection closed")
                    self.stop_flag.set()
                    continue

                logging.info("Received: {}".format(read_value))
            except:
                pass

if __name__=="__main__":
    parsed = parser.parse_args()
    print(parsed)
    addr = get_ip()

    if parsed.ap:
        port = 61000
        logging.debug("Targetting Tower default AP port {} on {}".format(port, addr))
    elif parsed.bp:
        port = 65432
        logging.debug("Targetting Tower default bay port {} on {}".format(port, addr))
    elif parsed.p is None:
        raise Exception("parameter -p is required if --ap or --bp aren't used")
    else:
        addr = parsed.a
        port = int(parsed.p)
        logging.debug("Targetting Tower port {} on {}".format(port, addr))

    cli = SocketCLI(addr=addr, port=port)
    cli.run()