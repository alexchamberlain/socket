# Copyright (c) Alex Chamberlain 2012
import socket
import argparse
from pprint import pprint

HOST = ''
PORT = 50005
BUF_SIZE = 500

def echo_client(ns):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  s.sendto(ns.msg.encode('utf-8'), (ns.host, ns.port))
  b, a = s.recvfrom(ns.buf_size)
  print("Client received {} bytes from {}:{}".format(len(b), a[0], a[1]))
  print("Remote: {}".format(b.decode('utf-8')))

def echo_server(ns):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.bind((ns.host, ns.port))
  
  while True:
    b, a = s.recvfrom(ns.buf_size)
    print("Server received {} bytes from {}:{}".format(len(b), a[0], a[1]))
    print("Client: {}".format(b.decode('utf-8')))
    s.sendto(b, a)
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', action='store_true', default=False, dest='server')
  parser.add_argument('-H', default='', dest='host')
  parser.add_argument('-P', default=50005, dest='port')
  parser.add_argument('--buffer-size', default=500, dest='buf_size')
  parser.add_argument('msg', nargs='?', default='Hello World')
  ns = parser.parse_args()

  if(ns.server):
    echo_server(ns)
  else:
    echo_client(ns)
