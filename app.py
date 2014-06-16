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

def errormessage(error):
        err = QtGui.QMessageBox()
        err.setText(error)
        err.exec_()

def connectserial():
        '''
        Attempts to make a serial connection with the MSP430

        Input:
        None

        Output:
        If a connection is established, the pyserial communication class object
        If no connection is established, False is returned
        '''
                
        for testport in serial_ports():       
                print testport
                try:
                        sercom = serial.Serial(testport, 9600, timeout = 0)		#set the name, baud rate, and timout of the serial connection as well as the following settings
                except:
                        continue
                sercom.baudrate=9600
                sercom.parity = serial.PARITY_NONE
                sercom.bytesize = serial.EIGHTBITS
                sercom.stopbits = serial.STOPBITS_ONE
                sercom.write("test\n")					#send 'test\n' and go into a loop while waiting to see if it is returned
                print 'Attempting Connection'
                recieved = ""
                giveupcounter = 0 
                while True:
                    time.sleep(0.2)
                    recieved += sercom.readline()
                    giveupcounter += 1
                    if giveupcounter > 30:
                        #'Connection Failed')
                        break
                    if recieved == "test\n":
                        #'Connection Made'
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
                        errormessage("Connection did not Respond")
                        return False
                if testrecieved == str(sendstring):
                        #"correct"
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
                errormessage("Error, input percent not acceptable")
        return (num / 256, num % 256)
                
        
def decode(string):
        
        co2 = string[1]* 256 + string[2]
        pwr = string[3] *256 + string[4]
        return (string[0], co2, pwr)
        

def start(serial):
        serial.write('start\n')
        recieved = ""
        giveupcounter = 0 
        while True:
            time.sleep(1)
            recieved += serial.readline()
            giveupcounter += 1
            if giveupcounter > 30:
                errormessage('Connection Failed')
                return 'Error'
            if recieved == "start\n": 
                
                return True
            if recieved == "stop\n":
                
                return False
        


##Functions for GUI##


class mainWindow(QtGui.QWidget):
    
    def __init__(self, application):
        super(mainWindow, self).__init__()
        
        #### Reactor Results ####
        self.reactorAco2 = []
        self.reactorBco2 = []
        self.reactorCco2 = []
        self.reactorDco2 = []
        
        self.reactorApwr = []
        self.reactorBpwr = []
        self.reactorCpwr = []
        self.reactorDpwr = []
        
        self.reactorAtime = []
        self.reactorBtime = []
        self.reactorCtime = []
        self.reactorDtime = []
        
        self.wastepwr = []
        self.wastetime = []
        
        
        #### Other Stuff ####
        self.port = 0
        self.portopen = False
        self.started = False
        self.time = QtCore.QTime()
        self.timecounter = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start(1000)
        self.exapp = application
        self.initUI()
    
    def getTime(self):
        self.timecounter += self.time.elapsed()/1000
        self.time.restart()
        return self.timecounter
        
    def update(self):
        if self.started == True:
                if self.portopen == True:
                        if self.port.inWaiting() > 0:
                                label, co2, pwr = decode(self.port.readline())
                                if label == 'W':
                                        wastepwr.append(pwr)
                                        self.wastetime.append(self.getTime())
                                elif label == 'A':
                                        reactorAco2.append(co2)
                                        reactorApwr.append(pwr)
                                        self.reactorAtime.append(self.getTime())
                                        
                                        self.plotA.getPlotItem().clear()
                                        self.plotA.plot(list(x/60 for x in self.reactorAtime), self.reactorAco2, pen=(0,255,0))
                                        self.plotA.plot(ist(x/60 for x in self.reactorAtime),self.reactorApwr, pen=(255,0,0))
                                        self.plotA.setRange(None,(0,1),(0,1))
                                elif label == 'B':
                                        reactorBco2.append(co2)
                                        reactorBpwr.append(pwr)
                                        self.reactorBtime.append(self.getTime())
                                        
                                        self.plotB.getPlotItem().clear()
                                        self.plotB.plot(list(x/60 for x in self.reactorBtime), self.reactorBco2, pen=(0,255,0))
                                        self.plotB.plot(ist(x/60 for x in self.reactorBtime),self.reactorBpwr, pen=(255,0,0))
                                        self.plotB.setRange(None,(0,1),(0,1))
                                elif label == 'C':
                                        reactorCco2.append(co2)
                                        reactorCpwr.append(pwr)
                                        self.reactorCtime.append(self.getTime())
                                        
                                        self.plotC.getPlotItem().clear()
                                        self.plotC.plot(list(x/60 for x in self.reactorCtime), self.reactorCco2, pen=(0,255,0))
                                        self.plotC.plot(ist(x/60 for x in self.reactorCtime),self.reactorCpwr, pen=(255,0,0))
                                        self.plotC.setRange(None,(0,1),(0,1))
                                elif label == 'D':
                                        reactorDco2.append(co2)
                                        reactorDpwr.append(pwr)
                                        self.reactorDtime.append(self.getTime())
                                        
                                        self.plotD.getPlotItem().clear()
                                        self.plotD.plot(list(x/60 for x in self.reactorDtime), self.reactorDco2, pen=(0,255,0))
                                        self.plotD.plot(ist(x/60 for x in self.reactorDtime),self.reactorDpwr, pen=(255,0,0))
                                        self.plotD.setRange(None,(0,1),(0,1))
                                        
                
        
    
        
    def initUI(self):      
        
       
        grid = QtGui.QGridLayout()
        
        #####Plots######
        
        labelStyle = {'color': '#FFF', 'font-size': '8pt'}
        co2labelStyle = {'color': '#0F0', 'font-size': '8pt'}
        self.plotA = pg.PlotWidget()
        grid.addWidget(self.plotA ,5,0,10,10)
        self.plotA.getPlotItem().setTitle("Reactor A", **labelStyle)
        self.plotA.getPlotItem().setLabel('left', '<font color="#ffffff">%</font><font color="#ffffff"> </font><font color="#00ff00">CO2</font><font color="#00ff00"> </font><font color="#ff0000">Pump</font>', None, **co2labelStyle)
        self.plotA.getPlotItem().setLabel('bottom', "Time (Hr)", None, **labelStyle)
        self.plotA.setRange(None,(0,1),(0,0.2))
        
        self.plotB = pg.PlotWidget()
        grid.addWidget(self.plotB ,5,10,10,10)
        self.plotB.getPlotItem().setTitle("Reactor B", **labelStyle)
        self.plotB.getPlotItem().setLabel('left', '<font color="#ffffff">%</font><font color="#ffffff"> </font><font color="#00ff00">CO2</font><font color="#00ff00"> </font><font color="#ff0000">Pump</font>', None, **co2labelStyle)
        self.plotB.getPlotItem().setLabel('bottom', "Time (Hr)", None, **labelStyle)
        self.plotB.setRange(None,(0,1),(0,0.2))
        
        self.plotC = pg.PlotWidget()
        grid.addWidget(self.plotC ,15,0,10,10)
        self.plotC.getPlotItem().setTitle("Reactor C", **labelStyle)
        self.plotC.getPlotItem().setLabel('left', '<font color="#ffffff">%</font><font color="#ffffff"> </font><font color="#00ff00">CO2</font><font color="#00ff00"> </font><font color="#ff0000">Pump</font>', None, **co2labelStyle)
        self.plotC.getPlotItem().setLabel('bottom', "Time (Hr)", None, **labelStyle)
        self.plotC.setRange(None,(0,1),(0,0.2))
        
        self.plotD = pg.PlotWidget()
        grid.addWidget(self.plotD ,15,10,10,10)
        self.plotD.getPlotItem().setTitle("Reactor D", **labelStyle)
        self.plotD.getPlotItem().setLabel('left', '<font color="#ffffff">%</font><font color="#ffffff"> </font><font color="#00ff00">CO2</font><font color="#00ff00"> </font><font color="#ff0000">Pump</font>', None, **co2labelStyle)
        self.plotD.getPlotItem().setLabel('bottom', "Time (Hr)", None, **labelStyle)
        self.plotD.setRange(None,(0,1),(0,0.2))
        
        
        #####Buttons######
        
        connectbtn = QtGui.QPushButton("Connect", self)
        connectbtn.setGeometry(QtCore.QRect(10,10,80,25))
        
        exportbtn = QtGui.QPushButton("Export", self)
        exportbtn.setGeometry(QtCore.QRect(100,10,80,25))
        
        startbtn = QtGui.QPushButton("Start/Stop", self)
        startbtn.setGeometry(QtCore.QRect(10,80,80,25))
        
        sendbtn = QtGui.QPushButton("Send Values", self)
        sendbtn.setGeometry(QtCore.QRect(10,45,80,25))
           
        connectbtn.clicked.connect(self.buttonClicked)            
        exportbtn.clicked.connect(self.buttonClicked)
        startbtn.clicked.connect(self.buttonClicked)
        sendbtn.clicked.connect(self.buttonClicked)
        
        #####Grid Placeholders######
        
        self.spacelbl = QtGui.QLabel(' ')
        for x in range(5):
                for y in range(20):
                        grid.addWidget(self.spacelbl, x,y)
                        
        ######Labels########
        
        self.messagelbl = QtGui.QLabel('Initialized',self)
        grid.addWidget(self.messagelbl, 25,0,1,20)
        
        self.wastelbl = QtGui.QLabel('Waste', self)
        self.wastelbl.move(100, 35)

        self.wastepwrlbl = QtGui.QLabel('  Output(%):', self)
        self.wastepwrlbl.move(100, 50)
        
        ##############Reactor A######
        self.reactorAlbl = QtGui.QLabel('Reactor A:', self)
        self.reactorAlbl.move(190, -5)

        self.reactorAthreshlbl = QtGui.QLabel('Threashold(%):', self)
        self.reactorAthreshlbl.move(190, 10)
        
        self.reactorAonpwrlbl = QtGui.QLabel('On Output(%):', self)
        self.reactorAonpwrlbl.move(190, 45)
        
        self.reactorAoffpwrlbl = QtGui.QLabel('Off Output(%):', self)
        self.reactorAoffpwrlbl.move(190, 80)
        
        ###############Reactor B#######
        
        self.reactorBlbl = QtGui.QLabel('Reactor B:', self)
        self.reactorBlbl.move(375, -5)

        self.reactorBthreshlbl = QtGui.QLabel('Threashold(%):', self)
        self.reactorBthreshlbl.move(375, 10)
        
        self.reactorBonpwrlbl = QtGui.QLabel('On Output(%):', self)
        self.reactorBonpwrlbl.move(375, 45)
        
        self.reactorBoffpwrlbl = QtGui.QLabel('Off Output(%):', self)
        self.reactorBoffpwrlbl.move(375, 80)
        
        ###############Reactor C#######
        self.reactorClbl = QtGui.QLabel('Reactor C:', self)
        self.reactorClbl.move(560, -5)

        self.reactorCthreshlbl = QtGui.QLabel('Threashold(%):', self)
        self.reactorCthreshlbl.move(560, 10)
        
        self.reactorConpwrlbl = QtGui.QLabel('On Output(%):', self)
        self.reactorConpwrlbl.move(560, 45)
        
        self.reactorCoffpwrlbl = QtGui.QLabel('Off Output(%):', self)
        self.reactorCoffpwrlbl.move(560, 80)
        
        ################Reactor D#######
        
        self.reactorDlbl = QtGui.QLabel('Reactor D:', self)
        self.reactorDlbl.move(745, -5)

        self.reactorDthreshlbl = QtGui.QLabel('Threashold(%):', self)
        self.reactorDthreshlbl.move(745, 10)

        self.reactorDonpwrlbl = QtGui.QLabel('On Output(%):', self)
        self.reactorDonpwrlbl.move(745, 45)
        
        self.reactorDoffpwrlbl = QtGui.QLabel('Off Output(%):', self)
        self.reactorDoffpwrlbl.move(745, 80)

        ######Line Edits######

        self.wastele = QtGui.QLineEdit(self)
        self.wastele.setGeometry(QtCore.QRect(100,80,80,25))
        
        ##############Reactor A#######
        self.reactorAthreshle = QtGui.QLineEdit(self)
        self.reactorAthreshle.setGeometry(QtCore.QRect(285,10,80,25))

        self.reactorAonpwrle = QtGui.QLineEdit(self)
        self.reactorAonpwrle.setGeometry(QtCore.QRect(285,45,80,25))
        
        self.reactorAoffpwrle = QtGui.QLineEdit(self)
        self.reactorAoffpwrle.setGeometry(QtCore.QRect(285,80,80,25))
        
        ################Reactor B#######
        self.reactorBthreshle = QtGui.QLineEdit(self)
        self.reactorBthreshle.setGeometry(QtCore.QRect(470,10,80,25))

        self.reactorBonpwrle = QtGui.QLineEdit(self)
        self.reactorBonpwrle.setGeometry(QtCore.QRect(470,45,80,25))
        
        self.reactorBoffpwrle = QtGui.QLineEdit(self)
        self.reactorBoffpwrle.setGeometry(QtCore.QRect(470,80,80,25))
        
        ################Reactor C#######
        
        self.reactorCthreshle = QtGui.QLineEdit(self)
        self.reactorCthreshle.setGeometry(QtCore.QRect(655,10,80,25))

        self.reactorConpwrle = QtGui.QLineEdit(self)
        self.reactorConpwrle.setGeometry(QtCore.QRect(655,45,80,25))
        
        self.reactorCoffpwrle = QtGui.QLineEdit(self)
        self.reactorCoffpwrle.setGeometry(QtCore.QRect(655,80,80,25))
        
        ################Reactor D#######
        
        self.reactorDthreshle = QtGui.QLineEdit(self)
        self.reactorDthreshle.setGeometry(QtCore.QRect(840,10,80,25))
        
        self.reactorDonpwrle = QtGui.QLineEdit(self)
        self.reactorDonpwrle.setGeometry(QtCore.QRect(840,45,80,25))
        
        self.reactorDoffpwrle = QtGui.QLineEdit(self)
        self.reactorDoffpwrle.setGeometry(QtCore.QRect(840,80,80,25))
       
       
        ######Layout########
        self.setLayout(grid)
        
        self.setGeometry(50, 10, 930, 700)
        self.setWindowTitle('Bioreactor Expiriment')
        self.show()
    
    def showMessage(self, mesg):
        self.messagelbl.setText(mesg)
        
    def buttonClicked(self):
      
        sender = self.sender()
        if sender.text() == "Connect":
                self.port = connectserial()
                if self.port != False:
                        print "connection made"
                        
                        self.showMessage("Connection Made")
                        
                        
                        self.portopen = True
                else:
                        
                        errormessage("Connection Failed")
        
        if sender.text() == "Export":
                #export
                pass
        
        if sender.text() == "Send Values":
                
                compiledlist = []
                compiledlist.append(convertvalues(str(self.reactorAthreshle.text())))
                compiledlist.append(convertvalues(str(self.reactorAonpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorAoffpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorBthreshle.text())))
                compiledlist.append(convertvalues(str(self.reactorBonpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorBoffpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorCthreshle.text())))
                compiledlist.append(convertvalues(str(self.reactorConpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorCoffpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorDthreshle.text())))
                compiledlist.append(convertvalues(str(self.reactorDonpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.reactorDoffpwrle.text()) ))
                compiledlist.append(convertvalues(str(self.wastele.text())))
                sendstring = ""
                for tupleitem in compiledlist:
                        sendstring += str(tupleitem[0]) + ':' + str(tupleitem[1])+ ','
                sendstring = sendstring[:-1] + '\n'
                if testserial(self.port,sendstring):
                        self.showMessage("Values Sent")
                        
                else:
                        errormessage("Error: Values NOT Sent")
        
        if sender.text() == "Start/Stop":
                self.started = True
                self.time.start()
                state = start(self.port)
                if state == True:
                        
                        self.showMessage("Expiriment Started")
                elif state == False:
                        
                        self.showMessage("Expiriment Stopped")
                else:
                        errormessage("Error: Please Retry 'Connect'")
                        
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = mainWindow(app)
    sys.exit(app.exec_())
    


##run##	

if __name__ == '__main__':
    main()



