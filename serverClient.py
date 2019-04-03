
import socket 
from tkinter import *
import numpy as np
from PIL import Image
from PIL import ImageDraw
import _thread
import pickle
import threading
# Multithreaded Python server : TCP Server Socket Thread Pool
#
import time
from time import sleep

import random
import sys
 
global penWidth, filledThreshold, rows
squareSize = 50
penWidth = 0
img = Image.new('1', (squareSize, squareSize), 0)  
percentFilledChecker = ImageDraw.Draw(img)
filledThreshold = 0.5

mouseEventList = []
pixels = squareSize*squareSize


global connectionIsOK
connectionISOK = True

window = Tk()
window.title("Divide and Conquer")
global rows
rows = 10
squareSize = 50
global canvasList 
global CurrentGameBoard
global AreaList
global countNumber
global SquareState
global myUserID
global ConnectionList
global IPList
global tcpClientA
global firstConnection
global reconnectLock
global serverLock
global lock
global IPList
global startLock
global ReceiveQueue
global time
global rtt 
ReceiveQueue = []
notConnected = True

firstConnection = True
myUserID = ""
canvasList = []
CurrentGameBoard = []
AreaList = []
lock = threading.BoundedSemaphore(value=1)
IPList = []
socketUseList = []
colors = ["red","green","blue","black"]

#IPList.append ('192.168.0.17')
ConnectionList = []
serverLock = threading.BoundedSemaphore(value=1)
reconnectLock = threading.BoundedSemaphore(value=1)

syncLock = threading.BoundedSemaphore(value=1)
startLock = threading.BoundedSemaphore(value=1)
 
def getFastestUser(queue):
	fastest = 0
	for i in range(len(queue)):
		if(queue[i]["Time"]< queue[fastest]["Time"]):
			fastest = i
	return queue[fastest]

 



class GameStateObj:
	color = ""
	canvasNumber = 0
	state ="Normal"
	UserID = ""

  
SquareState = GameStateObj()
ServerSquareState =  GameStateObj()

def PriorityServerUpdate(gameStateDict):
	global ReceiveQueue,CurrentGameBoard
	if ("gameState" in gameStateDict):
		#message = GameStateObj()
		Message = gameStateDict["gameState"]
		print ("Server received data:",Message.color, Message.canvasNumber,Message.UserID)
		if(Message.color=="yellow" and Message.state == "disabled"):
			ReceiveQueue.append(gameStateDict)
			priorityValue = getFastestUser(ReceiveQueue)
			ReceiveQueue.remove(priorityValue)
			priorityState = priorityValue["gameState"]
			if(CurrentGameBoard[int(priorityState.canvasNumber)-1].state !="disabled"):
				#lock.acquire()
				print("priority queue processed Server:",priorityState.UserID)
				CurrentGameBoard[int(priorityState.canvasNumber)-1].color = priorityState.color
				CurrentGameBoard[int(priorityState.canvasNumber)-1].UserID = priorityState.UserID
				CurrentGameBoard[int(priorityState.canvasNumber)-1].state = priorityState.state
				#canvasList[int(priorityState.canvasNumber)-1].config(background = priorityState.color,state = priorityState.state)
				#lock.release()
		else:
			#lock.acquire()
			print("direct Updating value for Server",Message.UserID)
			CurrentGameBoard[int(Message.canvasNumber)-1].color = Message.color
			CurrentGameBoard[int(Message.canvasNumber)-1].UserID = Message.UserID
			CurrentGameBoard[int(Message.canvasNumber)-1].state = Message.state
			canvasList[int(Message.canvasNumber)-1].config(background = Message.color,state = Message.state)
			#lock.release()
		

 
	 
					


def HandleReconnectToAnotherServer():
	global tcpClientA
	global IPList
	global notConnected
	while (True):
		print("tryng to connect to ",IPList)
		reconnectLock.acquire()
	
		if(notConnected):
			if(IPList[0]!= (socket.gethostbyname(socket.gethostname()))):
				# check ip list vs your own ip
				try:
					print("checking for old socket")
					if(socketUseList):
						print("oldSocket found and pop")
						oldSocket = socketUseList.pop()
						oldSocket.shutdown(socket.SHUT_RDWR)
						oldSocket.close()

					time.sleep(4.0)
					print("tryng to connect to ",IPList)
					print("first value is ", IPList[0])
					host = IPList[0]
					IPList.remove(host)
					port = 2008
					print ("host is",host) 
					print("connecting to server")
					syncLock.acquire()
					print("inside syncLock creating socket")
					tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
					tcpClientA.settimeout(5)

					tcpClientA.connect((host, port))
					print("Connected. Establishing rtt")
					calculateRTT(tcpClientA)
					socketUseList.append(tcpClientA)
					syncLock.release()
					print("should be connect")
					notConnected = False
				
				except Exception as e:  
					print("unable to connect",e)
					notConnected = True
			else:
				print("starting new server session as Server")
				global isServer
				isServer= True
				print("isServer",isServer)
				#global serverLock
				serverLock.release()
				print("serverLock released, isServer set to true")
				#_thread.start_new_thread(TurnClientIntoServer,(isServer,))
		
				
	 

def sendConstantUpdatesToClient(conn,ip,port): 
		while True :
			global CurrentGameBoard
			gameStateMessage = {"gameBoard":CurrentGameBoard}
			#sleep the same as client send to send to all clients. 
			time.sleep(0.1)
			data = pickle.dumps(gameStateMessage)
			conn.send(data)
			#print("size of server data", str(sys.getsizeof(pickle.dumps(gameStateMessage))))
			
#def server insert
# 	insert into the queue with time stamp delay. 

 
def ReceiveUpdatesFromClient(conn,ip,port): 
	global ReceiveQueue
	while True : 
			try:
				data = conn.recv(20000) 
				#check that field other wise.
				data = pickle.loads(data)
				#print("serverRecievedData",data)
				if ("gameState" in data):
					#message = GameStateObj()
					Message = data["gameState"]
					print ("Server received data:",Message.color, Message.canvasNumber,Message.UserID)
					if(Message.color=="yellow" and Message.state == "disabled"):
						ReceiveQueue.append(data)
						priorityValue = getFastestUser(ReceiveQueue)
						ReceiveQueue.remove(priorityValue)
						priorityState = priorityValue["gameState"]
						if(CurrentGameBoard[int(priorityState.canvasNumber)-1].state !="disabled"):
							lock.acquire()# be careful of these locks!
							print("priority queue processed user:",priorityState.UserID)
							CurrentGameBoard[int(priorityState.canvasNumber)-1].color = priorityState.color
							CurrentGameBoard[int(priorityState.canvasNumber)-1].UserID = priorityState.UserID
							CurrentGameBoard[int(priorityState.canvasNumber)-1].state = priorityState.state
							canvasList[int(priorityState.canvasNumber)-1].config(background = priorityState.color,state = priorityState.state)
							lock.release()# seems like we don't need them
							# further testing required.

					#	get highest yellow item insert
					# 	current gaem board set 
					#else:
					#  if color not yellow and disabled.
					# set the color. 
					#add to queue
					# take out smallest time stamp. 
					##here have a sorted priority queue based on time. 
					# server has its own function to add to this queue
					# here we process the queue. and set the canvas board based on prioity
					# average send time. 
					#
					#get highest priority. 
					else:
						lock.acquire()
						print("direct Updating value for User",Message.UserID)
						CurrentGameBoard[int(Message.canvasNumber)-1].color = Message.color
						CurrentGameBoard[int(Message.canvasNumber)-1].UserID = Message.UserID
						CurrentGameBoard[int(Message.canvasNumber)-1].state = Message.state
						canvasList[int(Message.canvasNumber)-1].config(background = Message.color,state = Message.state)
						lock.release()
			
			except Exception as e: 
				print(e)

			
			
class UpdateClientFromServer(threading.Thread): 
 
	def __init__(self): 
		threading.Thread.__init__(self) 
	   
	
	def run(self): 
		
		global firstConnection 
		global tcpClientA
		global CurrentGameBoard
		global IPList,penWidth,rows,filledThreshold,myUserID

		while True :  
			try:
				if(firstConnection):
					sleep(5)
					print("firstConnection")
					firstConnection = False
				data = tcpClientA.recv(10000)
				data = pickle.loads(data)
			
				if("gameBoard" in data):
					CurrentGameBoard = data["gameBoard"]
					for i in range(len(CurrentGameBoard)):
						if (CurrentGameBoard[i-1].UserID == myUserID and CurrentGameBoard[i-1].color=="yellow" and CurrentGameBoard[i-1].state=="disabled"):
							continue
						else:
							#print(i,CurrentGameBoard[i-1].state)
							canvasList[i-1].config(background = CurrentGameBoard[i-1].color, state = CurrentGameBoard[i-1].state)#, state = CurrentGameBoard[i-1].state)
				
				#elif( "IPList" in data):
					#print("IpListRecieved",data["IPList"])
					#global IPList
					#IPList = data["IPList"]
					#print(IPList)

	
				elif( "initialise" in data):
					
					print("initialise", data)
					IPList = data["IPList"]
					print("IpListRecieved",IPList)

					penWidth = data["Penwidth"]
					print("penWidthreceived",penWidth)

					rows = data["rows"]
					print("rows received:",rows)

					filledThreshold = data["threshold"]
					print("Threshold received",filledThreshold)
					myUserID = data["UserID"]
					print("UserID received",myUserID)
					startLock.release()
				
			#TODO:change test general exception. 
			except socket.timeout:
			 
				global notConnected
				global reconnectLock
				reconnectLock.release()
				notConnected = True
				print("reconnecting to next Server")
				pass

			except Exception as e:
				#print(e)
				pass
					

			   

		

def TurnClientIntoServer():
	print("entering while loops")
	global isServer
	while(True):
		serverLock.acquire()
		print("in while lock aquired")
		print("isServer",isServer)
		if(isServer):
			print("isServer is true in if statement")
			print("checking for old socket")
			if(socketUseList):
				print("oldSocket found and pop")
				oldSocket = socketUseList.pop()
				oldSocket.shutdown(socket.SHUT_RDWR)
				oldSocket.close()

			TCP_IP = '0.0.0.0' 
			TCP_PORT = 2008
			BUFFER_SIZE = 20  # Usually 1024, but we need quick response 
			tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
			tcpServer.bind((socket.gethostname(), TCP_PORT))    
			print("binded waiting for players")
			global number
			players = 0 
			number = 2
			
			global firstConnection
			if (not firstConnection):
				print("not first connection")
				#len of the IP list now for that many clients. 
				number = number -1

			if(isServer):
				while players<number: 
					tcpServer.listen(4) 
					print ("Multithreaded Python server : Waiting for connections from TCP clients..." )
					(conn,(ip,port)) = tcpServer.accept() 
					try:
						calculateRTT(conn)
						_thread.start_new_thread(ReceiveUpdatesFromClient,(conn,ip,port,))
						_thread.start_new_thread(sendConstantUpdatesToClient,(conn,ip,port,))
						print("newConnection")
						IPList.append(ip)
						ConnectionList.append(conn)
					except:
						print ("Error: unable to start thread")
					players = players+1

		if(isServer):
			print("sending initiliaze data")
			global penWidth,rows,filledThreshold,myUserID
			ownIP = socket.gethostbyname(socket.gethostname())
			#inpput here
			#print("Enter Pen width(1-10)")
			#inPenwidth = input()

			#penWidth = 10

			#print("Enter ")
			
			#rows = 6
			#filledThreshold = 25
			
			myUserID =0

			toSend = {"initialise":1,"IPList":IPList,"Penwidth":penWidth,"rows":rows,"threshold":filledThreshold}

			print(rows)
			print(penWidth)
			print(filledThreshold)
	 
			for i in range (len(ConnectionList)):#len(IPList):
				toSend.update({"UserID":i+1})
				ConnectionList[i].send(pickle.dumps(toSend))
				del toSend["UserID"]
			startLock.release()
			break
'''
		if(isServer):
			ownIP = socket.gethostbyname(socket.gethostname())
			disctIpList = {"IPList":IPList}
			for i in range (len(ConnectionList)):#len(IPList):
				ConnectionList[i].send(pickle.dumps(disctIpList))
			break
'''
		 
	   
		#threads.append(newthread)
		
def calculateRTT(conn):
	global rtt
	global isServer
	if(isServer): 
		currentTime = time.time()
		#dictTime = {"RTT":currentTime}
		conn.send(str(currentTime))
	else:
		currTime = time.time()
		conn.recv(1024)
		afterTime = time.time()
		elapsedTime = afterTime - currTime
		rtt = elapsedTime / 2
		print("My RTT is : " + str(rtt))
		
def PositionIntoIndex(position):
	columnNumber = position %rows
	rowNumber = position//rows
	return (rowNumber,columnNumber)

def xy(event):
	global lastx, lasty  
	
	if event.widget.cget('state') != 'disabled': 
		lastx, lasty = event.x, event.y
		mouseEventList.extend([lastx, lasty])  
		id = str(event.widget)
		position =0
		if(len(id)==9):
			position = int(id[8])
		if(len(id)==10):
			position = int(id[8])*10 + int(id[9])
		if(len(id)==8):
			position = 1
		print("Position", position)
		if (isServer):
			#lock.acquire()
			#buffer system to check the times, then if that time is
			# smallest then set it, 
			# other wise, dont
			# server buffer time is added some delay. 
			ServerSquareState.color = "yellow"
			ServerSquareState.state = "disabled"
			ServerSquareState.canvasNumber = position
			ServerSquareState.UserID = myUserID
			currentTime = time.time()
			#add some delay time aswell. 
			message = {"gameState":ServerSquareState,"Time":currentTime}
			PriorityServerUpdate(message)
			
			#currentTime = time.time()
			#CurrentGameBoard[int(position)-1].color = "yellow" 
			#CurrentGameBoard[int(position)-1].state = "disabled"
			#CurrentGameBoard[int(position)-1].UserID = myUserID
			# add user
			#lock.release()

		elif (not isServer):
			SquareState.color = "yellow"
			SquareState.state = "disabled"
			SquareState.canvasNumber = position
			SquareState.UserID = myUserID
			currentTime = time.time()
			# time stamp for yellow
			message = {"gameState":SquareState,"Time":currentTime}
			data = pickle.dumps(message)
   
			tcpClientA.send(data) 

		  
def addLine(event):
	global lastx, lasty
	global isServer
	if event.widget.cget('state') != 'disabled':   
		
			 
		if event.x > squareSize:
			event.x = squareSize
		if event.x < 0:
			event.x = 0
		if event.y > squareSize:
			event.y = squareSize
		if event.y < 0:
			event.y = 0
		#Creates a line in the clicked on widget
		event.widget.create_line((lastx, lasty, event.x, event.y), width=penWidth)
		mouseEventList.extend([event.x, event.y])
		lastx, lasty = event.x, event.y

		#print( (lastx, lasty) )
		global AreaList
		AreaList.append(tuple((lastx, lasty)))
		AreaList = list(set(AreaList))





def doneStroke(event):
	if event.widget.cget('state') != 'disabled':
		

		#DEBUG - Picks a random color to set the BG   
		#Clears all the drawing inside the Canvas
		global SquareState
		global percentFilled, filledThreshold
		percentFilledChecker.line(mouseEventList, fill=1, width=penWidth)
		output = np.asarray(img)
		percentFilled = np.count_nonzero(output)/pixels
		percentFilledString = str(int(round(percentFilled*100, 0)))
		print("Percent Filled: " + percentFilledString)
		#percentFilledChecker.rectangle((0,0,squareSize,squareSize), fill=0)
		#mouseEventList.clear()

		#Clears the image for reuse, seems faster than remaking the image everytime
		#
		#Sets the background color and disables the canvas
		color = "grey"
		print ("canvas List:")
		
		position = 0
		id = str(event.widget)
		position =0

		if(len(id)==9):
			position = int(id[8])
		if(len(id)==10):
			position = int(id[8])*10 + int(id[9])
		if(len(id)==8):
			position = 1
	
		print("percent filled vs threashold",int(percentFilledString),int(filledThreshold))
		#print("Position", position)

		if (int(percentFilledString)> int(filledThreshold)):

			color = colors[int(myUserID)%4]
			#event.widget.config(bg=color, state="disabled")

			percentFilledChecker.rectangle((0,0,squareSize,squareSize), fill=0)
			mouseEventList.clear()

			if (isServer):
				ServerSquareState.color = color
				ServerSquareState.state = "disabled"
				ServerSquareState.canvasNumber = position
				ServerSquareState.UserID = myUserID
				message = {"gameState":ServerSquareState}
				PriorityServerUpdate(message)

				#lock.acquire()
				#CurrentGameBoard[int(position)-1].color = color
				#CurrentGameBoard[int(position)-1].state = "disabled"
				#CurrentGameBoard[int(position)-1].UserID = myUserID
				#lock.release()
				#clear list?
			elif (not isServer):
				SquareState.color = color
				SquareState.state = "disabled"
				SquareState.canvasNumber = position
				SquareState.UserID = myUserID
				
				message = {"gameState":SquareState}
				data = pickle.dumps(message)
				tcpClientA.send(data) 
				#clear list?

		   
		#add delay here to sync time
		else:
			#is this important what does it do?
			percentFilledChecker.rectangle((0,0,squareSize,squareSize), fill=0)
			mouseEventList.clear()
			print("not over 50")
			if(isServer):
				ServerSquareState.color = "grey"
				ServerSquareState.state = "normal"
				ServerSquareState.canvasNumber = position
				ServerSquareState.UserID = ""
				message = {"gameState":ServerSquareState}
				PriorityServerUpdate(message)
				#lock.acquire()
				#CurrentGameBoard[int(position)-1].color = "grey" 
				#CurrentGameBoard[int(position)-1].state = "normal"
				#CurrentGameBoard[int(position)-1].UserID = ""
				# call another function. that sets its game board. 
				#lock.release()
				 # disbale the color for all other users
				# that user though does not get diabled

			elif (not isServer):
				print("reset press")
				SquareState.color = "grey"
				SquareState.state = "normal"
				SquareState.UserID = ""
				SquareState.canvasNumber = position
				message = {"gameState":SquareState}
				data = pickle.dumps(message)
				tcpClientA.send(data) 
		

		print (len(AreaList))
		del AreaList[:]
		print("new Listlength")
		print(len(AreaList))

		event.widget.delete("all")
		
 
#print("EnterID")
#myUserID = input()

print("isServer?")
Server = input()



if(Server=="yes"):
	#global penWidth,rows,filledThreshold
	isServer = True
	startLock.acquire()
	print("Deny and conquer configuring settings")
 
	print("pen width")
	INpenWidth = input()
	print("rows:")
	InRows = input()
	print("filled percent")
	INfilledThreshold = input()

	penWidth = int(INpenWidth)
	rows = int(InRows)
	filledThreshold = int(INfilledThreshold)

	#set input settings here. 
	#set global settings here.
	
else:
	isServer = False

countNumber = 0

if (not isServer):
	#input Ip
	#
	print("enter Servers IP:")
	#IP = input()

	#IPList.append('192.168.0.10')
	IPList.append("192.168.137.237")
	_thread.start_new_thread(HandleReconnectToAnotherServer,())
	UpdateBoard = UpdateClientFromServer()
	UpdateBoard.start()
	startLock.acquire()

	#start thread here


_thread.start_new_thread(TurnClientIntoServer,())


startLock.acquire()
for r in range(rows):
	for c in range(rows):
		item = Canvas(window, bg="grey", height=squareSize, width=squareSize)
		item.grid(row=r, column=c)
		item.bind("<Button-1>", xy)
		item.bind("<B1-Motion>", addLine)
		item.bind("<B1-ButtonRelease>", doneStroke)
		canvasList.append(item)
		countNumber =countNumber+1
		state = GameStateObj()
		state.canvasNumber = countNumber
		state.color = "grey"
		state.state = "normal"
		CurrentGameBoard.append(state)
startLock.release()
					   


print(window.grid_size())
window.mainloop()
 
 
 








