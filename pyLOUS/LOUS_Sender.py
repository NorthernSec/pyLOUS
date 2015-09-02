#!/usr/bin/env python3.3
# -*- coding: utf8 -*-
#
# Large Object UDP Streaming Sender Socket
#
# Copyright (c) 2015	NorthernSec
# Copyright (c) 2015	Pieter-Jan Moreels

# Imports
import socket
import struct
from .Exceptions import TooManyFramesException

class LOUS_Sender():
  def __init__(self, chunkSize=8192):
    self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.chunkSize=chunkSize
    self.seq=0
    self.max4Bytes=4294967296-1

  def send(self, data, address):
    chunks = [data[i:i+self.chunkSize] for i in range(0, len(data), self.chunkSize)]
    if len(chunks) > self.max4Bytes:
      raise TooManyFramesException()
    if self.seq > self.max4Bytes:
      pass # TODO: We will have to figure something out here. Probably overflow to 0000
    for i, chunk in enumerate(chunks):
      chunk=struct.pack("I",len(data))+struct.pack("I",self.seq)+struct.pack("I",i)+struct.pack("I",len(chunks))+chunk
      self.socket.sendto(chunk, (address[0], address[1]))
    self.seq+=1
