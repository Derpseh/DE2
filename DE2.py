#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
DE2. Hatemail goes to valkynora@gmail.com, as always.
"""

#imports and settings, as usual.
import sys
from PyQt4 import QtGui, QtCore
import urllib2
import xml.etree.ElementTree as ET
import time
import threading
global isRunning
global isUpdated
isRunning = False
isUpdated = False

#separating this and the other class to keep the threads more easily distinct.
class MainGUI(QtGui.QMainWindow):  
    def __init__(self):
        super(MainGUI, self).__init__()
        self.isRunning = False
#setting up timer thread in background. This should run every 1s, checking for an update.
        self.background = TimerThread(self)
        t = threading.Thread(target=self.background.check)
#daemon, so it actually closes properly after DE2 closes, rather than leaving dangling stuff that causes problems later >.>
        t.daemon = True
        t.start()
#if I get a signal from the timer thread, do the whole go notification thing.
        self.background.notify.connect(self.GoNotif)
        self.initUI()
        
#UI initialisation. Nothing too exciting here.        
    def initUI(self):
        a = 1
        global sometext
        self.setObjectName("MainWindow")
        self.setWindowTitle("DE2")
        self.resize(286, 55)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        btn = QtGui.QPushButton('Set',self.centralwidget)
        btn.setGeometry(QtCore.QRect(210, 0, 75, 20))
        btn.setObjectName("pushButton")
        self.inputbox = QtGui.QLineEdit(self.centralwidget)
        self.inputbox.setGeometry(QtCore.QRect(0, 0, 200, 20))
        self.inputbox.setObjectName("lineEdit")
        self.soundbox = QtGui.QCheckBox('Sound?', self)
        self.soundbox.toggle()
        self.soundbox.move(0, 15)
        self.showDialog()
        self.inputbox.setText(UAgent)
        sometext = self.inputbox.text
        self.setCentralWidget(self.centralwidget)
        self.gobar = self.statusBar()
        self.gobar.showMessage(' ')
#if the button is clicked, go do stuff
        btn.clicked.connect(self.checkRegion)

        self.show()

#initial dialog for grabbing a nation name to shove into the user agent. Setting headers while I'm at it.
    def showDialog(self):
        global UAgent
        global headers
        text, ok = QtGui.QInputDialog.getText(self, 'U-Agent input', 
            'Enter your nation name:')
        
        if ok:
            UAgent = str(text)
            headers = {'User-Agent' : 'DE2; currently in use by' + UAgent + '. Contact Devi at valkynora@gmail.com to yell at dev if needed.'}
            print UAgent




#checking if trigger region actually exists in the first place.
    def checkRegion(self):
        global CurrentLast
        global SanInput
        global isRunning
        try:
            self.gobar.showMessage(' ')
#delay, so even if someone tries to spam the button it won't make the modfolk mad.
            time.sleep(1)
            SanInput = str(self.inputbox.text()).replace(' ','_')
            req = urllib2.Request("http://www.nationstates.net/cgi-bin/api.cgi?region=" + SanInput + "&q=lastupdate", None, headers)
            html = urllib2.urlopen(req).read()
            trunk = ET.fromstring(html)
#dear gods, why does NS still use XML? This is just so dumb and awkward.
            for EVENT in trunk.iter('LASTUPDATE'):
                CurrentLast = EVENT.text
#resetting variables
            isRunning = True
            isUpdated = False
            self.gobar.showMessage('Waiting...')
#            print SanInput, CurrentLast
#if the input doesn't match an existing region, or something otherwise borks up, display.
        except:
            self.gobar.showMessage('Not a Region')
#triggers when it catches a thing from the other thread, as mentioned. Displays go; (TODO:optional sound cue here.)
    def GoNotif(self):
        self.gobar.showMessage('GO!')
#at least for windows, this should produce a beep. haven't tested for mac/linux.
        if self.soundbox.isChecked():
            print "\007"

#And here's the timer thread.
class TimerThread(QtCore.QObject):
#the signal that does things
    notify = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(TimerThread, self).__init__(parent)

#timerloop! I shunted the bulk of requests and stuff here as well, so it doesn't cause potential freezing in the main thread.
    def check(self):
        global isRunning
        while True:
            try:
#obligatory delays because rate limit violations are punishable by DEATh
                time.sleep(0.75)
#                print threading.active_count()
#I have it set up to only actually do the requests if it's supposed to be watching something. The timer loop runs throughout, but this section doesn't, for obviour reasons.
                if isRunning == True:
                    req = urllib2.Request("http://www.nationstates.net/cgi-bin/api.cgi?region=" + SanInput + "&q=lastupdate", None, headers)
                    html = urllib2.urlopen(req).read()
                    trunk = ET.fromstring(html)
                    for EVENT in trunk.iter('LASTUPDATE'):
                        CheckUpd = EVENT.text
#if the lastupdate shard is different from before, send the signal :>
                    if CheckUpd != CurrentLast:
                        isRunning = False
                        isUpdated = True
                        print "Not Waiting anymore"
                        self.notify.emit()
#if it isn't, just skip.
                    else:
                        print "Waiting... "

            except:
                time.sleep(1)
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainGUI()
    
    sys.exit(app.exec_())


main()
