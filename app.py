'''
Serial Communication Protocol:
Outgoing:
        String of former lilst of tuples of values
Incoming:
        String of 'T's and 'F's to represent which pumps are on
        String of values that indicate CO2 percentages in bioreactors
'''

import os
import serial
from serial.tools import list_ports
import time
import numpy as np
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import pyqtgraph as pg

##Variables##

xtest = np.array([0,1,3,4.5,7,10])
ytest = np.array([1,2,3,4,5,6])

port = "/dev/ttyACM0"


##Functions for Serial Communication##

#may be useful if other serial ports are in existance
def serial_ports():
    """
    Returns a generator for all available serial ports
    """
    if os.name == 'nt':
        # windows
        for i in range(256):
            try:
                s = serial.Serial(i)
                s.close()
                yield 'COM' + str(i + 1)
            except serial.SerialException:
                pass
    else:
        # unix
        for port in list_ports.comports():
            yield port[0]

#print list(serial_ports())




def connectserial():
        '''
        Attempts to make a serial connection with the MSP430

        Input:
        None

        Output:
        If a connection is established, the pyserial communication class object
        If no connection is established, False is returned
        '''
        sercom = serial.Serial(port, 9600, timeout = 0)		#set the name, baud rate, and timout of the serial connection as well as the following settings
        sercom.baudrate=9600
        sercom.parity = serial.PARITY_NONE
        sercom.bytesize = serial.EIGHTBITS
        sercom.stopbits = serial.STOPBITS_ONE
        sercom.write("test\n")					#send 'test\n' and go into a loop while waiting to see if it is returned
        print 'Attempting Connection'
        recieved = ""
        giveupcounter = 0 
        while True:
            time.sleep(1)
            recieved += sercom.readline()
            giveupcounter += 1
            if giveupcounter > 30:
                print 'Connection Failed'
                return False
            if recieved == "test\n":
                print 'Connection Made'
                return sercom

def testserial(sercom,sendstring):
        print "Writing: '" + str(sendstring)+ "'"
        sercom.write(str(sendstring))
        testrecieved = ""
        donecounter = 0
        while True:
                time.sleep(1)
                testrecieved += sercom.readline()
                print testrecieved
                donecounter +=1
                if donecounter > 30:
                        print "error"
                        return False
                if testrecieved == str(sendstring):
                        print "correct"
                        return True


def convertvalues(string):	
        '''
        Converts a percent string with two digits after the decimal (max) and makes it into two 8 bit words for sending via serial

        Input:
        String of percent

        Output:
        Returns a tuple of two integers that fit within 8 bits
        '''
        decimalflag = False
        for character in string:					#check for decimal place
                if character == '.':
                        decimalflag = True
                        break
        if decimalflag:	
                stringlist = string.split('.')				#split string at the decimal place
                if len(stringlist[1]) == 1:
                        stringlist[1] += '0'
                        string = stringlist[0]+stringlist[1]
                else:
                        string= string.replace('.','')
        else:
                string += '00'
        num = int(string)
        if num > 10000 or num < 0:
                print "Error, input percent not acceptable"
                #error
        return (num / 256, num % 256)
                
def sendvalues():
        '''
        Converts all the values that need to be sent

        Input:
        None

        Output:
        List of tuples of 8 bit numbers
        '''
        compiledlist = []
        compiledlist.append(convertvalues(rct1threshold))
        compiledlist.append(convertvalues(rct1pwm ))
        compiledlist.append(convertvalues(rct2threshold))
        compiledlist.append(convertvalues(rct2pwm ))
        compiledlist.append(convertvalues(rct3threshold))
        compiledlist.append(convertvalues(rct3pwm ))
        compiledlist.append(convertvalues(rct4threshold))
        compiledlist.append(convertvalues(rct4pwm ))
        compiledlist.append(convertvalues(wastepwm))
        return compiledlist
        
def readinput(serial):
        data = serial.readline()
        #parse data here

def start(serial):
        serial.write('start\n')
        recieved = ""
        giveupcounter = 0 
        while True:
            time.sleep(1)
            recieved += serial.readline()
            giveupcounter += 1
            if giveupcounter > 30:
                print 'Connection Failed'
                return 'Error'
            if recieved == "start\n": 
                print 'Started'
                return True
            if recieved == "stop\n":
                print 'Stopped'
                return False
        

##Functions for GUI##



class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.port = 0
        self.initUI()
        
        
        
    def initUI(self):      
        ###########################################################################################
       
        grid = QtGui.QGridLayout()
        
        
        self.graph = pg.PlotDataItem(xtest,ytest)
        self.gwidget = pg.PlotWidget()
        self.gwidget.addItem(self.graph)
        self.gwidget.move(100,100)
        
        grid.addWidget(self.gwidget, 0,2,10,10)
        grid.addWidget(QtGui.QLabel('  '),0,1)
        
        ##########################################################################################
        
        btn1 = QtGui.QPushButton("Connect", self)
        grid.addWidget(btn1,0,0)

        btn2 = QtGui.QPushButton("Send Values", self)
        grid.addWidget(btn2,1,0)

        btn3 = QtGui.QPushButton("Start/Stop", self)
        grid.addWidget(btn3,2,0)
            
        btn1.clicked.connect(self.buttonClicked)            
        btn2.clicked.connect(self.buttonClicked)
        btn3.clicked.connect(self.buttonClicked)
        
        self.lbl1 = QtGui.QLabel('Reactor A:', self)
        self.lbl1.move(10, 100)

        self.lbl2 = QtGui.QLabel('  Threashold(%):', self)
        self.lbl2.move(10, 115)
        
        self.le1 = QtGui.QLineEdit(self)
        self.le1.move(10, 140)

        self.lbl3 = QtGui.QLabel('  Output(%):', self)
        self.lbl3.move(10, 165)

        self.le2 = QtGui.QLineEdit(self)
        self.le2.move(10, 190)

        self.lbl4 = QtGui.QLabel('Reactor B:', self)
        self.lbl4.move(10, 215)

        self.lbl5 = QtGui.QLabel('  Threashold(%):', self)
        self.lbl5.move(10, 230)

        self.le3 = QtGui.QLineEdit(self)
        self.le3.move(10, 255)

        self.lbl6 = QtGui.QLabel('  Output(%):', self)
        self.lbl6.move(10, 280)

        self.le4 = QtGui.QLineEdit(self)
        self.le4.move(10, 305)

        self.lbl7 = QtGui.QLabel('Reactor C:', self)
        self.lbl7.move(10, 330)

        self.lbl8 = QtGui.QLabel('  Threashold(%):', self)
        self.lbl8.move(10, 345)

        self.le5 = QtGui.QLineEdit(self)
        self.le5.move(10, 370)

        self.lbl9 = QtGui.QLabel('  Output(%):', self)
        self.lbl9.move(10, 395)

        self.le6 = QtGui.QLineEdit(self)
        self.le6.move(10, 420)

        self.lbl10 = QtGui.QLabel('Reactor B:', self)
        self.lbl10.move(10, 445)

        self.lbl11 = QtGui.QLabel('  Threashold(%):', self)
        self.lbl11.move(10, 460)

        self.le7 = QtGui.QLineEdit(self)
        self.le7.move(10, 485)

        self.lbl12 = QtGui.QLabel('  Output(%):', self)
        self.lbl12.move(10, 510)

        self.le8 = QtGui.QLineEdit(self)
        self.le8.move(10, 535)

        self.lbl13 = QtGui.QLabel('Waste:', self)
        self.lbl13.move(10, 560)

        self.lbl14 = QtGui.QLabel('  Output(%):', self)
        self.lbl14.move(10, 575)

        self.le9 = QtGui.QLineEdit(self)
        self.le9.move(10, 600)

        ########################################################## 
        self.setLayout(grid)
        #########################################################
        
        self.setGeometry(150, 10, 700, 650)
        self.setWindowTitle('Bioreactor Expiriment')
        self.show()
        
    def buttonClicked(self):
      
        sender = self.sender()
        if sender.text() == "Connect":
                self.port = connectserial()
                if port != False:
                        print "connection made"
                else:
                        print "connection failed"
        
        if sender.text() == "Send Values":
                
                compiledlist = []
                compiledlist.append(convertvalues(str(self.le1.text())))
                compiledlist.append(convertvalues(str(self.le2.text()) ))
                compiledlist.append(convertvalues(str(self.le3.text())))
                compiledlist.append(convertvalues(str(self.le4.text()) ))
                compiledlist.append(convertvalues(str(self.le5.text())))
                compiledlist.append(convertvalues(str(self.le6.text()) ))
                compiledlist.append(convertvalues(str(self.le7.text())))
                compiledlist.append(convertvalues(str(self.le8.text()) ))
                compiledlist.append(convertvalues(str(self.le9.text())))
                if testserial(self.port,compiledlist):
                        print "Values Sent"
                else:
                        print "Error: Values NOT Sent"
        
        if sender.text() == "Start/Stop":
                state = start(self.port)
                if state == True:
                        print "Expiriment Started"
                elif state == False:
                        print "Expiriment Stopped"
                else:
                        print "Error, Please Retry 'Connect'"
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    
    






if __name__ == '__main__':
    main()
    

##run##	

'''
port = connectserial()
testserial(port, sendvalues())
'''

