from tkinter import *
import numpy as np
from PIL import Image
from PIL import ImageDraw
import random
import socket

class MainApplication:
    def __init__(self, window):
        self.window = window
        self.rows = None
        self.squareSize = 30
        self.penWidth = None
        self.img = Image.new('1', (self.squareSize, self.squareSize), 0)  
        self.percentFilledChecker = ImageDraw.Draw(self.img)
        self.filledThreshold = None
        self.canvasList = []
        self.mouseEventList = []
        self.pixels = self.squareSize*self.squareSize

        
    def client(self):
        button1 = Button(self.window, text="Server", command=self.makeSettings)
        button1.pack(anchor=CENTER)
        button2 = Button(self.window, text="Client", command=self.clientInput)
        button2.pack(anchor=CENTER)

    def clientInput(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        enterLabel = Label(self.window, text="\nEnter the ip of your server below")
        enterLabel.pack()
        self.ipEnter = Entry(self.window)
        self.ipEnter.pack()
        button1 = Button(self.window, text="Go", command=self.connect)
        button1.pack(anchor=CENTER)
        
    def connect(self):
        connectionIP = self.ipEnter.get()
        print(connectionIP)
        for widget in self.window.winfo_children():
            widget.destroy()
        button = Button(self.window, text="Start Game", command=self.makeBoard)
        button.pack(anchor=CENTER) 

        
    def makeSettings(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        hostIP = str(socket.gethostbyname(socket.gethostname()) )
        titleLabel = Label(self.window, text="Divide and Conquer - Server Settings")
        titleLabel.pack()
        ipLabel = Label(self.window, text="Server IP: "+hostIP)
        ipLabel.pack()
        rowLabel = Label(self.window, text="\n\n# of Rows")
        rowLabel.pack()
        self.rowScale = Scale(self.window, from_=1, to=10, orient=HORIZONTAL)
        self.rowScale.pack()
        penLabel = Label(self.window, text="\nPen Width")
        penLabel.pack()
        self.penScale = Scale(self.window, from_=1, to=10, orient=HORIZONTAL)
        self.penScale.pack()
        threshLabel = Label(self.window, text="\nFilled Threshold %")
        threshLabel.pack()
        self.filledThresholdScale = Scale(self.window, from_=1, to=100, orient=HORIZONTAL)
        self.filledThresholdScale.pack()

        button = Button(self.window, text="Submit Settings", command=self.getSettings)
        button.pack(anchor=CENTER)

    def makeBoard(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        for r in range(self.rows):
            for c in range(self.rows):
                item = Canvas(window, bg="grey", height=self.squareSize, width=self.squareSize)
                item.grid(row=r, column=c)
                item.bind("<Button-1>", self.xy)
                item.bind("<B1-Motion>", self.addLine)
                item.bind("<B1-ButtonRelease>", self.doneStroke)
                self.canvasList.append(item)

    def getSettings(self):
        self.rows = self.rowScale.get()
        self.penWidth= self.penScale.get()
        self.filledThreshold = self.filledThresholdScale.get()
        for widget in self.window.winfo_children():
            widget.destroy()
        button = Button(self.window, text="Start Game", command=self.makeBoard)
        button.pack(anchor=CENTER) 
        

    def xy(self, event):
        global lastx, lasty
        if event.widget.cget('state') != 'disabled':   
            lastx, lasty = event.x, event.y
            self.mouseEventList.extend([lastx, lasty])

    def addLine(self, event):
        global lastx, lasty
        if event.widget.cget('state') != 'disabled':   
            #Constraints so that when calculating pixesl (Not yet implemented) coloring off the square doesn't count
            if event.x > self.squareSize:
                event.x = self.squareSize
            if event.x < 0:
                event.x = 0
            if event.y > self.squareSize:
                event.y = self.squareSize
            if event.y < 0:
                event.y = 0
            #Creates a line in the clicked on widget
            event.widget.create_line((lastx, lasty, event.x, event.y), width=self.penWidth)
            self.mouseEventList.extend([event.x, event.y])
            lastx, lasty = event.x, event.y
            #DEBUG - Outputs Mouse Coordinates
            #print( (lastx, lasty) )
            #print( (event.x, event.y) )

    def doneStroke(self, event):
        if event.widget.cget('state') != 'disabled':
            #DEBUG - Picks a random color to set the BG   
            color = random.choice(["red","blue"])
            #Clears all the drawing inside the Canvas
            event.widget.delete("all")
            #Checks % filled
            self.percentFilledChecker.line(self.mouseEventList, fill=1, width=self.penWidth)
            output = np.asarray(self.img)
            percentFilled = np.count_nonzero(output)/self.pixels
            percentFilledString = str(int(round(percentFilled*100, 0)))
            print("Percent Filled: " + percentFilledString)
            #Clears the image for reuse, seems faster than remaking the image everytime
            self.percentFilledChecker.rectangle((0,0,self.squareSize,self.squareSize), fill=0)
            #Clears the mouse event list
            self.mouseEventList.clear()
            event.widget.create_text(self.squareSize/2,self.squareSize/2, text=percentFilledString, fill=color )
            
            #Sets the background color and disables the canvas
            #if percentFilled > filledThreshold:
                #event.widget.config(bg=color, state="disabled")

if __name__ == '__main__':
    window = Tk()
    window.title("Divide and Conquer")
    MainApplication(window).client()
    window.mainloop()
