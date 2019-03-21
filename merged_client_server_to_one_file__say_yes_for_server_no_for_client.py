import socket 

import _thread
import pickle
import threading
# Multithreaded Python server : TCP Server Socket Thread Pool
#
import time
from time import sleep

from tkinter import *
import random

global isServer


global connectionIsOK
connectionISOK = True

window = Tk()
window.title("Divide and Conquer")
global rows
rows = 4
squareSize = 50
global canvasList 
global CurrentGameBoard
global AreaList
global countNumber
global SquareState
global myUserID
myUserID = ""
canvasList = []
CurrentGameBoard = []
AreaList = []
lock = threading.BoundedSemaphore(value=1)
 

class GameStateObj:
    color = ""
    name = ""
    canvasNumber = 0
    percentageComplete = 0
    rowIndex = 0
    columnIndex = 0
    state ="Normal"
    UserID = ""


SquareState = GameStateObj()

def sendConstantUpdatesToClient(conn,ip,port): 
        while True :
            time.sleep(0.2)
            data = pickle.dumps(CurrentGameBoard)
            conn.send(data)


 
def ReceiveUpdatesFromClient(conn,ip,port): 
    while True : 
            data = conn.recv(4048) 
            message = GameStateObj()
            Message = pickle.loads(data)
            print ("Server received data:",Message.color, Message.rowIndex,Message.columnIndex, Message.canvasNumber)
            lock.acquire()
            CurrentGameBoard[int(Message.canvasNumber)-1].color = Message.color
            
            canvasList[int(Message.canvasNumber)-1].config(background = Message.color)

            # if not user update
            lock.release()
            
            

class CLientUpdatesFromServer(threading.Thread): 
 
    def __init__(self,ip,port): 
        threading.Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        print ("[+] Sending To " + ip + ":" + str(port) )
    
    def run(self): 
        while True : 
            
            data = tcpClientA.recv(BUFFER_SIZE)
            CurrentGameBoard = pickle.loads(data)
            for i in range(len(CurrentGameBoard)):
                canvasList[i-1].config(background = CurrentGameBoard[i-1].color)#, state = CurrentGameBoard[i-1].state)
                #if (CurrentGameBoard[i-1].UserID == myUserID):

                # if not your id lock it.

            # send current game state every someodd seconds
            # each client has its own update thread 
            #time.sleep(0.3)


def TurnClientIntoServer(isServer):
    #while(True):
        if(isServer):
            #tcpClientA.shutdown()
            #tcpClientA.close()
            TCP_IP = '0.0.0.0' 
            TCP_PORT = 2009
            BUFFER_SIZE = 20  # Usually 1024, but we need quick response 
            tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            tcpServer.bind((socket.gethostname(), TCP_PORT))    

            players = 0 
            if(isServer):
                while players<2: 
            
                    #print ("Multithreaded Python server : Waiting for connections from TCP clients..." )
                    tcpServer.listen(4) 
                    print ("Multithreaded Python server : Waiting for connections from TCP clients..." )
                    (conn,(ip,port)) = tcpServer.accept() 
                    try:
                        _thread.start_new_thread(ReceiveUpdatesFromClient,(conn,ip,port,))
                        _thread.start_new_thread(sendConstantUpdatesToClient,(conn,ip,port,))
                        print("newConnection")
                    except:
                        print ("Error: unable to start thread")
                    players = players+1
            #break
       
        #threads.append(newthread)
        
 
def PositionIntoIndex(position):
    columnNumber = position %rows
    rowNumber = position//rows
    return (rowNumber,columnNumber)

def xy(event):
    global lastx, lasty
    #if event.widget.cget('state') != 'disabled':   
    lastx, lasty = event.x, event.y

          
def addLine(event):
    global lastx, lasty
    #if event.widget.cget('state') != 'disabled':   
        #event.widget.config(bg="yellow", state="disabled")
        #Constraints so that when calculating pixesl (Not yet implemented) coloring off the square doesn't count
    if event.x > squareSize:
        event.x = squareSize
    if event.x < 0:
        event.x = 0
    if event.y > squareSize:
        event.y = squareSize
    if event.y < 0:
        event.y = 0
    #Creates a line in the clicked on widget
    event.widget.create_line((lastx, lasty, event.x, event.y), width=5)
    lastx, lasty = event.x, event.y

    print( (lastx, lasty) )
    global AreaList
    AreaList.append(tuple((lastx, lasty)))
    AreaList = list(set(AreaList))

def pressLock(event):
    if event.widget.cget('state') != 'disabled':
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
            lock.acquire()
            CurrentGameBoard[int(position)-1].color = "yellow" 
            #CurrentGameBoard[int(position)-1].state = "disabled"
            # add user
            lock.release()

        elif (not isServer):
            SquareState.color = "yellow"
            #SquareState.state = "disabled"
            # add user
            SquareState.canvasNumber = position
            data = pickle.dumps(SquareState)
            tcpClientA.send(data) 




def doneStroke(event):
    if event.widget.cget('state') != 'disabled':
        #DEBUG - Picks a random color to set the BG   
        #Clears all the drawing inside the Canvas
        
        #Sets the background color and disables the canvas
        color = "grey"
        print ("canvas List:")
        
        position = 0

        if len(AreaList)>5:
            color = random.choice(["green","blue"])
            event.widget.config(bg=color, state="disabled")
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
                lock.acquire()
                CurrentGameBoard[int(position)-1].color = color
                CurrentGameBoard[int(position)-1].state = "disabled"
                lock.release()
            elif (not isServer):
                SquareState.color = color
                SquareState.state = "disabled"
                SquareState.canvasNumber = position
                data = pickle.dumps(SquareState)
                tcpClientA.send(data) 

           
        #add delay here to sync time
        '''
        elif isServer:
                lock.acquire()
                CurrentGameBoard[int(position)-1].color = "grey" 
                CurrentGameBoard[int(position)-1].state = "normal"
                lock.release()

        elif (not isServer):
                SquareState.color = "grey"
                SquareState.state = "normal"
                data = pickle.dumps(SquareState)
                tcpClientA.send(data) 
        '''

        print (len(AreaList))
        del AreaList[:]
        print("new Listlength")
        print(len(AreaList))

        event.widget.delete("all")
        
 
print("EnterID")
myUserID = input()

print("isServer?")
Server = input()

if(Server=="yes"):
    isServer = True
else:
    isServer = False

countNumber = 0

if (not isServer):
    host = socket.gethostname()
    port = 2009
    print ("host is",host) 
    BUFFER_SIZE = 2000 
    tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #tcpClientA.settimeout(1.0)
    tcpClientA.connect((host, port))
    #start thread here


global gui
gui = True



for r in range(rows):
    for c in range(rows):
        item = Canvas(window, bg="grey", height=squareSize, width=squareSize)
        item.grid(row=r, column=c)
        item.bind("<Button-1>", xy)
        item.bind("<B1-Motion>", addLine)
        item.bind("<B1-ButtonRelease>", doneStroke)
        #item.bind("<Button-1>", pressLock)
        #add event click to lock the button
        canvasList.append(item)
        countNumber =countNumber+1
        state = GameStateObj()
        state.canvasNumber = countNumber
        state.color = "grey"
        state.state = "normal"
        CurrentGameBoard.append(state)


#Todo: add more players
#thread.start_new_thread ( function, args[, kwargs] )

        
if(not isServer):
    UpdateBoard = CLientUpdatesFromServer(host, port)
    UpdateBoard.start()


_thread.start_new_thread(TurnClientIntoServer,(isServer,))
                       
print(window.grid_size())
window.mainloop()
gui = False

 








