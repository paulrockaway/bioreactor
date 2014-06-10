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

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

##Variables##
rct1threshold = "20.00"
rct1pwm = "33.3"

rct2threshold = "99.99"
rct2pwm = "100"

rct3threshold = "100.00"
rct3pwm = "0.13"

rct4threshold = "25."
rct4pwm = "35"

wastepwm = "1"

port = "/dev/ttyACM0"


##Functions for Serial Communication##

#may be useful if other serial ports are in existance
'''def serial_ports():
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

print list(serial_ports())'''




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



class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        self.port = 0
        self.initUI()
        
    def initUI(self):      

        btn1 = QtGui.QPushButton("Connect", self)
        btn1.move(10, 10)

        btn2 = QtGui.QPushButton("Send Values", self)
        btn2.move(10, 50)

	btn3 = QtGui.QPushButton("Start/Stop", self)
        btn3.move(10, 90)
            
        btn1.clicked.connect(self.buttonClicked)            
        btn2.clicked.connect(self.buttonClicked)
	btn3.clicked.connect(self.buttonClicked)
        
        self.statusBar()
        
        self.setGeometry(300, 300, 700, 500)
        self.setWindowTitle('Bioreactor Expiriment')
        self.show()
        
    def buttonClicked(self):
      
        sender = self.sender()
	if sender.text() == "Connect":
		self.port = connectserial()
		if port != False:
			self.statusBar().showMessage("Connection Made")
		else:
			self.statusBar().showMessage("Connection Failed")
	if sender.text() == "Send Values":
		if testserial(self.port,sendvalues()):
			self.statusBar().showMessage("Values Sent")
		else:
			self.statusBar().showMessage("Error: Values NOT Sent")
	if sender.text() == "Start/Stop":
		state = start(self.port)
		if state == True:
			self.statusBar().showMessage("Expiriment Started")
		elif state == False:
			self.statusBar().showMessage("Expiriment Stopped")
		else:
			self.statusBar().showMessage("Error, Please Retry 'Connect'")
        
        
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


