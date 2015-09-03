# pyLOUS
Large Object UDP Streaming Socket for Python

## What is pyLOUS?
In computer networking, our main protocols are UDP and TCP. UDP allows us to send real time data, that doesn't slow down
the pipe on a slow connection, while still guaranteeing that the received packet is not corrupted. This makes it ideal
for streaming video or audio. But what if you want to send objects larger then the maximum size of a UDP packet? <br />
pyLOUS is a simple wrapper around the normal UDP socket, that buffers packets and re-arranges them in the correct order,
allowing you to send data larger then 65kb. Due to the sequencing of frames, it keeps track of data chunks and order,
so you always have the most recent complete data.

pyLOUS:
 * **is non-blocking** - pyLOUS runs in a separate thread, allowing it to continue collecting data while you are processing the last received data
 * **guarantees complete data** - When it receives data, it is complete. When chunks get lost, the entire object is dropped
 * **is easy to implement** - pyLOUS takes care of socket creation and object handling. Look at the example code
 * **comes with a setup script** - This makes it easy to install and use in your projects
 
## Usage
### Sending data
    import pyLOUS
    import os
    data=bytearray(os.urandom(1000000))
    sender=pyLOUS.LOUS_Sender()
    sender.send(data, ("localhost",4321))

### Receiving data
    import pyLOUS
    receiver=pyLOUS.LOUS_Receiver("0.0.0.0", 4321)
    receiver.start()
    while True:
        # last data:
        data=receiver.last()
        # or
        # last data from IP:
        data=receiver.last("127.0.0.1")
        # check if any object has been received completely
        if data:
            # do stuff
