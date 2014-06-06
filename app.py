from PyQt4 import QtGui  # (the example applies equally well to PySide)
import pyqtgraph as pg
import sys


def main():
	## Always start by initializing Qt (only once per application)
	app = QtGui.QApplication(sys.argv)

	## Variables



	## Define a top-level widget to hold everything
	w = QtGui.QWidget()
	#w.resize(20,20)

	## Create some widgets to be placed inside
	chkbtn = QtGui.QPushButton('Check Connection')
	sndbtn = QtGui.QPushButton('Update Values')
	strtbtn = QtGui.QPushButton('Start/Stop')

	rct1threasholdlbl = QtGui.QLabel('CO2 Threashold (%)')
	rct1percentlbl = QtGui.QLabel('Pump Output Level (%)')
	rct1lbl = QtGui.QLabel('Bioreactor 1:')
	rct1threshtext = QtGui.QLineEdit('')
	rct1outputtext = QtGui.QLineEdit('')

	rct2threasholdlbl = QtGui.QLabel('CO2 Threashold (%)')
	rct2percentlbl = QtGui.QLabel('Pump Output Level (%)')
	rct2lbl = QtGui.QLabel('Bioreactor 2:')
	rct2threshtext = QtGui.QLineEdit('')
	rct2outputtext = QtGui.QLineEdit('')

	rct3threasholdlbl = QtGui.QLabel('CO2 Threashold (%)')
	rct3percentlbl = QtGui.QLabel('Pump Output Level (%)')
	rct3lbl = QtGui.QLabel('Bioreactor 3:')
	rct3threshtext = QtGui.QLineEdit('')
	rct3outputtext = QtGui.QLineEdit('')

	rct4threasholdlbl = QtGui.QLabel('CO2 Threashold (%)')
	rct4percentlbl = QtGui.QLabel('Pump Output Level (%)')
	rct4lbl = QtGui.QLabel('Bioreactor 4:')
	rct4threshtext = QtGui.QLineEdit('')
	rct4outputtext = QtGui.QLineEdit('')

	listw = QtGui.QListWidget()
	plot = pg.PlotWidget()

	## Create a grid layout to manage the widgets size and position
	layout = QtGui.QGridLayout()
	w.setLayout(layout)

	## Add widgets to the layout in their proper positions
	layout.addWidget(chkbtn, 0, 0)   # button goes in upper-left
	layout.addWidget(sndbtn, 1, 0)   # button goes in upper-left
	layout.addWidget(strtbtn, 2, 0)   # button goes in upper-left

	layout.addWidget(rct1lbl,3,0)
	layout.addWidget(rct1threasholdlbl,4,0)
	layout.addWidget(rct1threshtext, 5, 0)   # text edit goes in middle-lef
	layout.addWidget(rct1percentlbl,6,0)
	layout.addWidget(rct1outputtext, 7, 0)

	layout.addWidget(rct2lbl,9,0)
	layout.addWidget(rct2threasholdlbl,10,0)
	layout.addWidget(rct2threshtext, 11, 0)   # text edit goes in middle-lef
	layout.addWidget(rct2percentlbl,12,0)
	layout.addWidget(rct2outputtext, 13, 0)  

	layout.addWidget(rct3lbl,14,0)
	layout.addWidget(rct3threasholdlbl,15,0)
	layout.addWidget(rct3threshtext, 16, 0)   # text edit goes in middle-lef
	layout.addWidget(rct3percentlbl,17,0)
	layout.addWidget(rct3outputtext, 18, 0) 

	layout.addWidget(rct4lbl,19,0)
	layout.addWidget(rct4threasholdlbl,20,0)
	layout.addWidget(rct4threshtext, 21, 0)   # text edit goes in middle-lef
	layout.addWidget(rct4percentlbl,22,0)
	layout.addWidget(rct4outputtext, 23, 0) 

	  

	#layout.addWidget(listw, 8, 0)  # list widget goes in bottom-left
	layout.addWidget(plot, 0, 1, 24, 3)  # plot goes on right side, spanning 3 rows

	## Display the widget as a new window
	w.show()

	## Start the Qt event loop
	sys.exit(app.exec_())
	#app.exec_()

if __name__ == '__main__':
    main()


