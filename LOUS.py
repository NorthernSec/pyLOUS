#!/usr/bin/env python3.3
# -*- coding: utf8 -*-
#
# Large Object UDP Streaming
#
# Copyright (c) 2015	NorthernSec
# Copyright (c) 2015	Pieter-Jan Moreels

# Imports
import socket
import struct
import threading
import zlib
import time

class LOUS_Sender():
  def __init__(self, compression=False, chunkSize=8192):
    self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.compression=compression
    self.chunkSize=chunkSize
    self.seq=0

  def send(self, data, address):
    #TODO: We will have to handle large sequence numbers, exceeding the maximum positive of an int
    try:
      if self.compression:
        data = zlib.compress(data)
      chunks = [data[i:i+self.chunkSize] for i in range(0, len(data), self.chunkSize)]
      for i, chunk in enumerate(chunks):
        chunk=struct.pack("I",len(data))+struct.pack("I",self.seq)+struct.pack("I",i)+struct.pack("I",len(chunks))+chunk
        self.socket.sendto(chunk, (address[0], address[1]))
      self.seq+=1
    except Exception as e:
      print(e)

class LOUS_Receiver(threading.Thread):
  def __init__(self,ip,port, compression=False, recvFrom=[]):
    threading.Thread.__init__(self)
    self.ip=ip
    self.port=port
    self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.compression=compression
    self.data=None
    self._stop = threading.Event()
    self.running=True
    self.whitelist=recvFrom

  def run(self):
    #TODO: We will have to handle large sequence numbers, exceeding the maximum positive of an int
    try:
      self.socket.bind((self.ip,self.port))
      chunkBucket={}
      while self.running:
        try:
          data, addr = self.socket.recvfrom(65535)
          length=int.from_bytes(data[:4],byteorder="little")
          #recv from limit
          if not self.whitelist or addr[0] in self.whitelist:
            seq=int.from_bytes(data[4:8],byteorder="little")
            chunk=int.from_bytes(data[8:12],byteorder="little")
            chunks=int.from_bytes(data[12:16],byteorder="little")
            payload=data[16:]
            if not seq in chunkBucket.keys():
              chunkBucket[seq]={chunk: payload, "len":chunks}
            else:
              chunkBucket[seq][chunk]=payload
            # Redundancy check
            if not "len" in chunkBucket[seq].keys():
              chunkBucket[seq]["len"]=chunks
            # Is bucket full?
            if len(chunkBucket[seq])==chunkBucket[seq]["len"]+1:
              chunkBucket[seq].pop("len")
              # Rearrange the chunks in order and reconstruct the data
              data=b''.join([chunkBucket[seq][j] for j in sorted(chunkBucket[seq])])
              # Remove all previous chunks from list
              leftover=sorted(chunkBucket)[sorted(chunkBucket).index(seq):]
              chunkBucket={i:chunkBucket[i] for i in leftover}
              # Decompress if needed
              if self.compression:
                try:
                  data = zlib.decompress(data)
                except:
                  pass
              self.data=data
        except Exception as e:
          print(e)
          pass
    except Exception as e:
      print(e)

  def last(self):
    return self.data

  def stop(self):
    self.running=False
    self._stop.set()

  def stopped(self):
    return self._stop.isSet()

def recvWrapper(sock):
  recv=sock.recv(4)
  recv=int.from_bytes(recv,byteorder="little")
  data=b''
  while(len(data)<recv):
    data+=sock.recv(recv)
  return data

def sendWrapper(sock, data):
  data=struct.pack("I",len(data))+data
  sock.sendall(data)
