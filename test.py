from pyLOUS import pyLOUS
import time
import os

def testRecv(sent, recveived):
  if recveived:
    if sent == recveived:
      print("Object sent & received successfully!")
    else:
      print("Failed to reconstruct the object!")
  else:
    print("Failed to receive")

sendData=bytearray(os.urandom(1000000))
s=pyLOUS.LOUS_Sender()
r=pyLOUS.LOUS_Receiver("0.0.0.0", 4321)
r.start()
s.send(sendData, ("localhost",4321))
time.sleep(0.5)
testRecv(sendData, r.last())
testRecv(sendData, r.last("127.0.0.1"))
r.stop()
print("Please press CTRL+C, we're still working on this bug :)")
