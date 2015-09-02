import pyLOUS
import time
import os

sendData=bytearray(os.urandom(1000000))
s=pyLOUS.LOUS_Sender()
r=pyLOUS.LOUS_Receiver("0.0.0.0", 4321)
r.start()
s.send(sendData, ("localhost",4321))
time.sleep(0.5)
recvData=r.last()
r.stop()
if recvData:
  if sendData == recvData:
    print("Object sent & received successfully!")
  else:
    print("Failed to reconstruct the object!")
else:
  print("Failed to receive")
