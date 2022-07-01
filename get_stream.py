# get stream ,
# 1 snapshot
# 2 video, using cv2
# 3 metadata, using http avstream.cgi

from math import ceil, floor
import os, time, sys
import cv2 as cv
import numpy as np
import requests
import base64, re, json
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

import xmltodict
#import threading


# import xml.etree.ElementTree as ET
# from xml.dom import minidom
# from xml.etree import ElementTree
#import xml.etree.ElementTree as elemTree
#import socket
#import sqlite3

path = ''
device_ip = '192.168.132.6'
userid = 'root'
userpw = 'Rootpass12345~'

class RingBuffer:
	def __init__(self, size):
		self.data = [None for i in range(size)]

	def append(self, x):
		self.data.pop(0)
		self.data.append(x)

	def get(self):
		return self.data
	def close(self):
		del self.data

mBuffer = RingBuffer(3)


def checkAuthMode(url, id, pw):
	r = requests.get('http://'+url+'/cgi-bin/admin/network.cgi?msubmenu=ip&action=view', auth=HTTPDigestAuth(id, pw))
	if r.text.find('Unauthorized') < 0:
		return HTTPDigestAuth(id, pw)
	
	r = requests.get('http://'+url+'/cgi-bin/admin/network.cgi?msubmenu=ip&action=view', auth=HTTPBasicAuth(id, pw))
	if r.text.find('Unauthorized') <0:
		return HTTPBasicAuth(id, pw)
	
	return False

def getSnapshot(url, authkey):
	cgi_str ="/cgi-bin/video.cgi"
	r = requests.get('http://'+ url + cgi_str, auth=authkey)
	if r:
		return r.content
	return False

def viewSnapshot(stream, waitsec=0):
	bytes_as_np_array = np.frombuffer(stream, dtype=np.uint8)
	img = cv.imdecode(bytes_as_np_array, cv.IMREAD_ANYCOLOR)
	w = len(img)
	h = floor(len(bytes_as_np_array)/w)
	w_name = 'Image ' + str(w) +'x' + str(h)
	cv.imshow(w_name, img)
	cv.waitKey(waitsec)
	cv.destroyWindow(w_name)

def showVideo(url, channel='ufirststream'):
	url = 'rtsp://' + url + '/' + channel
	cap = cv.VideoCapture(url)
	if cap.isOpened():
		size =  (cap.get(cv.CAP_PROP_FRAME_WIDTH), cap.get(cv.CAP_PROP_FRAME_HEIGHT))
		Running = True
	else :
		Running = False
	
	cap.set(cv.CAP_PROP_BUFFERSIZE,3)
	w_name = url + "  " + str(size)
	while Running :
		t = time.time()
		# ret, img = cap.read()
		ret = cap.grab()
		ret = cap.grab()
		ret, img = cap.retrieve()

		# cv.putText(img, str(time.time()), (40,100), font, fontsize, (32,32,32), 4, cv.LINE_AA)
		# cv.putText(img, str(cap.get(cv.CAP_PROP_POS_MSEC)), (50,200), font, fontsize, (32,32,32), 4, cv.LINE_AA)
		if ret:
			cv.imshow(w_name, img)
		
		ch =  cv.waitKey(1)
		if ch == 27 or ch == ord('Q') or ch == ord('q'):
			Running = False
		
	cap.release()
	cv.destroyWindow(w_name)

def getMetadataStream(url):
	regex = re.compile(b"<vca>(.*)</vca>", re.IGNORECASE)
	cgi_str ="/nvc-cgi/admin/avstream.cgi?streamno=first&streamreq=meta&format=xml"
	r = requests.get('http://'+ url + cgi_str, auth=authkey, timeout=1, stream=True)

	for chunk in r. iter_content(chunk_size=1024):
		t = regex.search(chunk.replace(b"\n", b""))
		if t:
			try :
				p = t.group().decode()
			except UnicodeDecodeError as e:
				print(e)
				continue
			# print (t.group())
			json_str = json.dumps(xmltodict.parse(p))
			mBuffer.append(json_str)

			print(mBuffer.get()[0])

	return False

def getMetadata(url):
	regex = re.compile(b"<vca>(.*)</vca>", re.IGNORECASE)
	cgi_str ="/nvc-cgi/admin/avstream.cgi?streamno=second&streamreq=meta&format=xml"
	r = requests.get('http://'+ url + cgi_str, auth=authkey, timeout=1, stream=True)

	for chunk in r. iter_content(chunk_size=1024):
		t = regex.search(chunk.replace(b"\n", b""))
		if t:
			try :
				p = t.group().decode()
			except UnicodeDecodeError as e:
				print(e)
				continue
			json_str = json.dumps(xmltodict.parse(p))
			return json.loads(json_str)['vca']
	return False


if __name__ == "__main__":
	authkey = checkAuthMode(device_ip, userid, userpw)

	if not authkey:
		print ("Authkey fail, id or pw may be wrong")
		sys.exit()

	# body = getSnapshot(device_ip, authkey)
	# viewSnapshot(body)
	
	# showVideo(device_ip, 'channel1')

	m = getMetadata(device_ip)

	print(m)
	mBuffer.close()

sys.exit()



def getStream(url, stream='video'):
		global authkey
		err = 0

		server = (url, 80)
		conn = HTTPConnection(*server)

		conn.putrequest("GET","/nvc-cgi/admin/avstream.cgi?streamno=first&streamreq=" + stream +"&format=xml")
		conn.putheader("Authorization", authkey)
		conn.endheaders()

		rs = conn.getresponse()
		print (rs)

		# fname = "F"+ str(int(time.time()))+ ".avi"
		# f = open(fname, "wb")
		flag = 0
		body = b""
		for i in range(1000):
				# data = rs.read(4096)
				data = rs.readline()
				if not data:
						break
				if data.find(b'<vca>') >=0:
					flag = 1
				if flag:
					# f.write(data)
					body +=data
				if data.find(b'</vca>') >=0:
					flag = 0
					break
				print (i)
				
		# f.close()

		conn.close()
		return body

bdy = getStream("192.168.132.6", "meta")    

print (bdy)
tree = ET.fromstring(bdy)
x = tree.findall('counts/count')
for item in x:
	print ('id', item.find('id').text)
	print ('name', item.find('name').text)
	print ('value', item.find('val').text)

print (x)
sys.exit()

def digestpacket(st):
#   print (st)
#   return st

	""" This routine takes a UDP packet, i.e. a string of bytes and ..
	(a) strips off the RTP header
	(b) adds NAL "stamps" to the packets, so that they are recognized as NAL's
	(c) Concantenates frames
	(d) Returns a packet that can be written to disk as such and that is recognized by stock media players as h264 stream
	"""
	startbytes=b"\x00\x00\x00\x01" # this is the sequence of four bytes that identifies a NAL packet.. must be in front of every NAL packet.

	bt=bitstring.BitArray(bytes=st) # turn the whole string-of-bytes packet into a string of bits.  Very unefficient, but hey, this is only for demoing.
	lc=12 # bytecounter
	bc=12*8 # bitcounter

	version=bt[0:2].uint # version
	p=bt[3] # P
	x=bt[4] # X
	cc=bt[4:8].uint # CC
	m=bt[9] # M
	pt=bt[9:16].uint # PT
	sn=bt[16:32].uint # sequence number
	timestamp=bt[32:64].uint # timestamp
	ssrc=bt[64:96].uint # ssrc identifier
	# The header format can be found from:
	# https://en.wikipedia.org/wiki/Real-time_Transport_Protocol

	lc=12 # so, we have red twelve bytes
	bc=12*8 # .. and that many bits

#   print ("version, p, x, cc, m, pt",version,p,x,cc,m,pt)
#   print ("sequence number, timestamp",sn,timestamp)
#   print ("sync. source identifier",ssrc)

	# st=f.read(4*cc) # csrc identifiers, 32 bits (4 bytes) each
	cids=[]
	for i in range(cc):
		cids.append(bt[bc:bc+32].uint)
		bc+=32; lc+=4;
#   print ("csrc identifiers:",cids)

	if (x):
		# this section haven't been tested.. might fail
		hid=bt[bc:bc+16].uint
		bc+=16; lc+=2;

		hlen=bt[bc:bc+16].uint
		bc+=16; lc+=2;

		# print ("ext. header id, header len",hid,hlen)

		hst=bt[bc:bc+32*hlen]
		bc+=32*hlen; lc+=4*hlen;


	# OK, now we enter the NAL packet, as described here:
	# 
	# https://tools.ietf.org/html/rfc6184#section-1.3
	#
	# Some quotes from that document:
	#
	"""
	5.3. NAL Unit Header Usage


	The structure and semantics of the NAL unit header were introduced in
	Section 1.3.  For convenience, the format of the NAL unit header is
	reprinted below:

			+---------------+
			|0|1|2|3|4|5|6|7|
			+-+-+-+-+-+-+-+-+
			|F|NRI|  Type   |
			+---------------+

	This section specifies the semantics of F and NRI according to this
	specification.

	"""
	"""
	Table 3.  Summary of allowed NAL unit types for each packetization
								mode (yes = allowed, no = disallowed, ig = ignore)

			Payload Packet    Single NAL    Non-Interleaved    Interleaved
			Type    Type      Unit Mode           Mode             Mode
			-------------------------------------------------------------
			0      reserved      ig               ig               ig
			1-23   NAL unit     yes              yes               no
			24     STAP-A        no              yes               no
			25     STAP-B        no               no              yes
			26     MTAP16        no               no              yes
			27     MTAP24        no               no              yes
			28     FU-A          no              yes              yes
			29     FU-B          no               no              yes
			30-31  reserved      ig               ig               ig
	"""
	# This was also very usefull:
	# http://stackoverflow.com/questions/7665217/how-to-process-raw-udp-packets-so-that-they-can-be-decoded-by-a-decoder-filter-i
	# A quote from that:
	"""
	First byte:  [ 3 NAL UNIT BITS | 5 FRAGMENT TYPE BITS] 
	Second byte: [ START BIT | RESERVED BIT | END BIT | 5 NAL UNIT BITS] 
	Other bytes: [... VIDEO FRAGMENT DATA...]
	"""

	fb=bt[bc] # i.e. "F"
	nri=bt[bc+1:bc+3].uint # "NRI"
	nlu0=bt[bc:bc+3] # "3 NAL UNIT BITS" (i.e. [F | NRI])
	typ=bt[bc+3:bc+8].uint # "Type"
#   print ("F, NRI, Type :", fb, nri, typ)
#   print ("first three bits together :",bt[bc:bc+3])

	if (typ==7 or typ==8):
		# this means we have either an SPS or a PPS packet
		# they have the meta-info about resolution, etc.
		# more reading for example here:
		# http://www.cardinalpeak.com/blog/the-h-264-sequence-parameter-set/
		if (typ==7):
			print (">>>>> SPS packet")
		else:
			print (">>>>> PPS packet")
		return startbytes+st[lc:]
		# .. notice here that we include the NAL starting sequence "startbytes" and the "First byte"

	bc+=8; lc+=1; # let's go to "Second byte"
	# ********* WE ARE AT THE "Second byte" ************
	# The "Type" here is most likely 28, i.e. "FU-A"
	start=bt[bc] # start bit
	end=bt[bc+2] # end bit
	nlu1=bt[bc+3:bc+8] # 5 nal unit bits

	if (start): # OK, this is a first fragment in a movie frame
		# print (">>> first fragment found")
		nlu=nlu0+nlu1 # Create "[3 NAL UNIT BITS | 5 NAL UNIT BITS]"
		head= startbytes+nlu.bytes # .. add the NAL starting sequence
		lc+=1 # We skip the "Second byte"
	if (start==False and end==False): # intermediate fragment in a sequence, just dump "VIDEO FRAGMENT DATA"
		head=b""
		lc+=1 # We skip the "Second byte"
	elif (end==True): # last fragment in a sequence, just dump "VIDEO FRAGMENT DATA"
		head=b""
		# print ("<<<< last fragment found")
		lc+=1 # We skip the "Second byte"

	if (typ==28): # This code only handles "Type" = 28, i.e. "FU-A"
		return head+st[lc:]
	else:
		raise(Exception,"unknown frame type for this piece of s***")

# class VideoCapture:
#     def __init__(self, name):
#         self.cap = cv.VideoCapture(name)
#         self.t = threading.Thread(target=self._reader)
#         self.t.daemon = True
#         self.t.start()

#     # grab frames as soon as they are available
#     def _reader(self):
#         while True:
#             ret = self.cap.grab()
#             if not ret:
#                 break

#     # retrieve latest frame
#     def show(self):
#         ret, frame = self.cap.retrieve()
#         cv.imshow('a', frame)
#         # return frame

def throw(cap):
		while True:
				ret = cap.grab()
				if not ret :
						break

Running =  True
# url = "rtsp://192.168.132.6:554/channel2"
# url = "http://root:Rootpass12345~@192.168.132.6/nvc-cgi/admin/avstream.cgi?streamno=second&streamreq=video,metadata"
# url = "D:\\BACKUP\\Downloads\\Unconfirmed 811234.mp4"
url = "D:\\BACKUP\\Downloads\\Unconfirmed 992416.mp4"
url = "D:\\BACKUP\\Downloads\\Unconfirmed 96137.mp4"
# url = "D:\\BACKUP\\Downloads\\Unconfirmed 189758 - Copy.crdownload"

# f = open(url, "rb")
# body = f.read(4096)
# st=digestpacket(body)

# f.close()

cap = cv.VideoCapture(url)

font = cv.FONT_HERSHEY_PLAIN
fontsize = 3.0

# t = threading.Thread(target=throw, args=(cap,))
# t.start()

if cap.isOpened():
		# aperture=  cap.get(cv.CAP_PROP_APERTURE)
		# aravis =  cap.get(cv.CAP_PROP_ARAVIS_AUTOTRIGGER)
		# exposure =  cap.get(cv.CAP_PROP_AUTO_EXPOSURE)
		for i in range(30):
				a = cap.get(i)

				print (i, a)
		Running = True

		# print(aperture, aravis, exposure)

# cap.set(cv.CAP_PROP_BUFFERSIZE,3)
i =0
while Running :
		t = time.time()
		ret, img = cap.read()
		# ret = cap.grab()
		# ret, img = cap.retrieve()

		# cv.putText(img, str(time.time()), (40,100), font, fontsize, (32,32,32), 4, cv.LINE_AA)
		# cv.putText(img, str(cap.get(cv.CAP_PROP_POS_MSEC)), (50,200), font, fontsize, (32,32,32), 4, cv.LINE_AA)
		if ret:
				cv.imshow(url, img)
				# print (i)
		
		
		ch =  cv.waitKey(1)
		if ch == 27 or ch == ord('Q') or ch == ord('q'):
				Running = False
		
		i+=1
		
		
cap.release()
cv.destroyAllWindows()