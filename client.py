# Python TCP Client A
import socket 

from tkinter import *
import random
import pickle
import threading
 
window = Tk()
window.title("Divide and Conquer")
global rows
rows = 4
squareSize = 50
global canvasList 
global CurrentGameBoard
global AreaList
global countNumber
global newMove 

canvasList = []
CurrentGameBoard = []
AreaList = []
#to identify the canvas number widget
countNumber = 0
global SquareState
newMove =False

 
gameStateArray = []
 
global tcpClientA
global SquareState

RunningAsServer = False
timeout = False
print("IpAdress")

#specify your own servers Ip here
#use gethostname() for local host
#host = '192.168.0.12'
host = socket.gethostname()

print ("host is",host) 
port = 2008

BUFFER_SIZE = 2000 
tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClientA.connect((host, port))



class UpdateThread(threading.Thread): 
 
    def __init__(self,ip,port): 
        threading.Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        print ("[+] Sending To " + ip + ":" + str(port) )
 
    def run(self): 
        while True : 

        	data = tcpClientA.recv(BUFFER_SIZE)
        	CurrentGameBoard = pickle.loads(data)
        	#print (" Client2 received data:", newArrayState)
        	for i in range(len(CurrentGameBoard)):
        		canvasList[i-1].config(background = CurrentGameBoard[i-1].color)
           
            # send current game state every someodd seconds
            # each client has its own update thread 
            #time.sleep(0.3)
            
 

class GameStateObj:
        color = ""
        name = ""
        canvasNumber = 0
        percentageComplete = 0
        rowIndex = 0
        columnIndex = 0

SquareState = GameStateObj()

 

def xy(event):
        global lastx, lasty
        if event.widget.cget('state') != 'disabled':   
                lastx, lasty = event.x, event.y

 
                  
def addLine(event):
        global lastx, lasty
        if event.widget.cget('state') != 'disabled':   
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
                #DEBUG - Outputs Mouse Coordinates

                print( (lastx, lasty) )
                global AreaList
                AreaList.append(tuple((lastx, lasty)))
                AreaList = list(set(AreaList))



                #print( (event.x, event.y) )

def doneStroke(event):
        if event.widget.cget('state') != 'disabled':
                #DEBUG - Picks a random color to set the BG   

                #Clears all the drawing inside the Canvas
                 
                #Sets the background color and disables the canvas
                color = "grey"
                print ("canvas List:")
                global AreaList
                id = str(event.widget)

                if len(AreaList)>5:
                        color = random.choice(["green","blue"])

                        event.widget.config(bg=color, state="disabled")
                   
                        position =0
                        if(len(id)==9):
                                position = int(id[8])
                        if(len(id)==10):
                                position = int(id[8])*10 + int(id[9])
                        if(len(id)==8):
                                position = 1

                        print("position:", position)
                         
                        SquareState.color = color
                        SquareState.rowIndex = position//rows
                        SquareState.columnIndex = position%rows
                        SquareState.canvasNumber = position
                        print (SquareState.rowIndex,SquareState.columnIndex)
                        print("sending data")

                        data = pickle.dumps(SquareState)
                        tcpClientA.send(data) 


                print (len(AreaList))
                del AreaList[:]
                print("new Listlength")
                print(len(AreaList))

                print(id)
                event.widget.delete("all")
                

#Creates the Grid
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
                state.color = "grey"
                state.canvasNumber = countNumber
                CurrentGameBoard.append(state)
                

UpdateBoard = UpdateThread( host, port)
UpdateBoard.start()

print(window.grid_size())
window.mainloop()

 

        ##set the gameboard

tcpClientA.close() 
 






