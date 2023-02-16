import time

from PIL import Image

import cv2
# from livestreamer import Livestreamer

# # change to a stream that is actually online
# livestreamer = Livestreamer()
# plugin = livestreamer.resolve_url("http://twitch.tv/NieDaRadek")
# streams = plugin.get_streams()
# stream = streams['mobile_High']

# # download enough data to make sure the first frame is there
# fd = stream.open()
# data = ''
# while len(data) < 3e5:
#     data += fd.read()
#     time.sleep(0.1)
# fd.close()

fname = 'test.bin'
open(fname, 'wb')
capture = cv2.VideoCapture(fname)
imgdata = capture.read()[1]
imgdata = imgdata[...,::-1] # BGR -> RGB
img = Image.fromarray(imgdata)
img.save('frame.png')
# img.show()