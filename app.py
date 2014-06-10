import os
import serial
from serial.tools import list_ports
import time

##Variables
rct1threshold = 0
rct1pwm = 0

rct2threshold = 0
rct2pwm = 0

rct3threshold = 0
rct3pwm = 0

rct4threshold = 0
rct4pwm = 0

wastepwm = 0

port = "/dev/ttyACM0"


##Initialize Serial

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
	sercom = serial.Serial(port, 9600, timeout = 0)
	sercom.baudrate=9600
	sercom.parity = serial.PARITY_NONE
	sercom.bytesize = serial.EIGHTBITS
	sercom.stopbits = serial.STOPBITS_ONE
	sercom.write("test\n")	
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
		return True


'''
	print 'waiting:'
	for character in 'test\n':
		print 'writing character '+ character
		sercom.write(character)
		print 'sleeping 1s'		
		time.sleep(1)
		print 'waking..'
	print sercom.inWaiting()
	
	if sercom.read(4) == "test":
		#update gui with 'connected'
	else:
		#update gui with 'not connected
	sercom.close()'''



def convertvalues(string):
	string = string.replace('.','')
	num = int(string)
	if num > 10000 or num < 0:
		pass
		#error
	return (num / 256, num % 256)
		
'''def sendvalues():
	compiledlist = []
	compiledlist.append(convertvalues(rct1threshold))
	compiledlist.append(convertvalues(rct1pwm ))
	compiledlist.append(convertvalues(rct2threshold))
	compiledlist.append(convertvalues(rct2pwm ))
	compiledlist.append(convertvalues(rct3threshold))
	compiledlist.append(convertvalues(rct3pwm ))
	compiledlist.append(convertvalues(rct4threshold))
	compiledlist.append(convertvalues(rct4pwm ))

	compiledlist.append(wastepwm)'''
	
	
		
connectserial()

