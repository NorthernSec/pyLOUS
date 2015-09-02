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

# Constants
max4Bytes=4294967296-1

class LOUS_Sender():
  def __init__(self, chunkSize=8192):
    self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.chunkSize=chunkSize
    self.seq=0

  def send(self, data, address):
    chunks = [data[i:i+self.chunkSize] for i in range(0, len(data), self.chunkSize)]
    if len(chunks) > max4Bytes:
      raise TooManyFramesException()
    if self.seq > max4Bytes:
      pass # TODO: We will have to figure something out here. Probably overflow to 0000
    for i, chunk in enumerate(chunks):
      chunk=struct.pack("I",len(data))+struct.pack("I",self.seq)+struct.pack("I",i)+struct.pack("I",len(chunks))+chunk
      self.socket.sendto(chunk, (address[0], address[1]))
    self.seq+=1

class LOUS_Receiver(threading.Thread):
  def __init__(self,ip,port, recvFrom=[], buffer=10):
    threading.Thread.__init__(self)
    self.ip=ip
    self.port=port
    self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.data=None
    self.dataPerIP={}
    self._stop = threading.Event()
    self.running=True
    self.whitelist=recvFrom
    self.buffer=buffer

  def run(self):
    #TODO: We will have to handle large sequence numbers, exceeding the maximum positive of an int            (Potential bug)
    #TODO: We will need a time-based scraper to remove old data                                               (Potential DoS)
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
            # Create bucket if not exists
            if not addr in chunkBucket.keys():
              chunkBucket[addr]={}
            # Load bucket for ease of use
            bucket=chunkBucket[addr]
            # Store sequence number if not exist
            if "seq" not in bucket:
              bucket["seq"]=seq
            # Check if packet falls outside of our buffer
            if seq < bucket["seq"]-self.buffer:
              # TODO: Check if the seq might be an integer overflow
              # Assuming we send 50 objects/second, the socket can still receive for over 994 days

              # Discard packet
              continue
            # Chuck chunk in the right bucket
            if not seq in bucket.keys():
              bucket[seq]={chunk: payload, "len":chunks}
            else:
              bucket[seq][chunk]=payload
            # Redundancy check
            if not "len" in bucket[seq].keys():
              bucket[seq]["len"]=chunks
            # Is bucket full?
            if len(bucket[seq])==bucket[seq]["len"]+1:
              bucket[seq].pop("len")
              # Rearrange the chunks in order and reconstruct the data
              data=b''.join([bucket[seq][j] for j in sorted(bucket[seq])])
              # Remove all previous chunks from buffer TODO change
              # Remove from buffer instead of all
              tempSeq=bucket.pop("seq")
              leftover=sorted(bucket)[sorted(bucket).index(seq):]
              bucket={i:bucket[i] for i in leftover}
              bucket["seq"]=tempSeq
              # Save last known good
              self.data=data
              self.dataPerIP[addr[0]]=data
        except Exception as e:
          print("Exception")
          print(e)
          pass
    except Exception as e:
      print(e)

  def last(self, IP=None):
    if IP:
      if IP in self.dataPerIP:
        return self.dataPerIP[IP]
      else:
        return None
    else:
      return self.data

  def stop(self):
    self.running=False
    self._stop.set()

  def stopped(self):
    return self._stop.isSet()

class TooManyFramesException(Exception):
  pass
