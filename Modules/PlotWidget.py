from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5 import QtCore,QtWidgets,QtGui
from PyQt5 import QtWebEngineWidgets
import Globals
import hashlib
import math
import locale


## @package PlotWidget
# Widget to Display gantt plot of measurement

class SniffPlot(QtWidgets.QWidget):
	##The constructor
	#  initialize attributes
	def __init__(self,sniffconfig):
		self.data={}
		self.rects=[]
		self.endTime=0
		self.endTime_=0
		self.startTime=0
		self.startTime_=0
		self.ntask=0
		self.plotStart=0
		self.plotEnd=0
		self.zoomfac=1
		self.offset=0
		self.overrideStyle=""
		self.snifferConfig=sniffconfig
		self.taskcols={}
		self.rangeslider=None
		self.plotWindowStart=None
		self.plotWindowEnd=None
		self.plotWindowStartLabel=None
		self.plotWindowEndLabel=None
		self.plotWindowDurationLabel=None
		self.qp = QtGui.QPainter()
		super(SniffPlot,self).__init__()
		self.setMouseTracking(True)
		self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
	
	## Override style for printing
	def setOverrideStyle(self,style):
		self.overrideStyle=style
	
	## Update start value of plot
	def updateStart(self,start):
		self.plotStart=start
		self.repaint()
	
	## Update end value of plot
	def updateEnd(self,end):
		self.plotEnd=end
		self.repaint()
	
	## Add a scrollbar
	def setScrollbar(self,rangeslider):
		self.rangeslider=rangeslider
		self.rangeslider.startValueChanged.connect(self.updateStart)
		self.rangeslider.endValueChanged.connect(self.updateEnd)
	
	## Add spinnners for start and end values
	def setWindowSpinner(self,plotWindowStart,plotWindowEnd):
		self.plotWindowStart=plotWindowStart
		self.plotWindowEnd=plotWindowEnd
		self.plotWindowStart.valueChanged.connect(self.updateWindow)
		self.plotWindowEnd.valueChanged.connect(self.updateWindow)
	
	## Add labels for start and end values
	# tis enables the widget to change text in the containing Tab
	# @param plotWindowStartLabel Label for Plot start time
	# @param plotWindowEndLabel Label for Plot end time
	# @param plotWindowDurationLabel Label for Plot duration
	def setRangeLabels(self,plotWindowStartLabel,plotWindowEndLabel,plotWindowDurationLabel):
		self.plotWindowStartLabel=plotWindowStartLabel
		self.plotWindowEndLabel=plotWindowEndLabel
		self.plotWindowDurationLabel=plotWindowDurationLabel
	
	## Reset start value to default
	def resetStart(self):
		self.plotWindowStart.setValue(self.startTime_)
	
	## Reset end value to default
	def resetEnd(self):
		self.plotWindowEnd.setValue(self.endTime_)
	
	## Update start/end value in plot and rangeslider
	def updateWindow(self):
		if self.plotWindowEnd and self.plotWindowStart and self.plotWindowDurationLabel:
			
			self.endTime=self.plotWindowEnd.value()
			self.startTime=self.plotWindowStart.value()
			
			if not self.endTime-self.startTime:
				if self.endTime+1<=self.endTime_:
					self.endTime+=1
				elif self.startTime-1>=self.startTime_:
					self.startTime-=1
				
				self.plotWindowStart.setValue(self.startTime)
				self.plotWindowEnd.setValue(self.endTime)
					
			self.endTime=self.plotWindowEnd.value()
			self.startTime=self.plotWindowStart.value()
			
			self.plotWindowDurationLabel.setText(self.scaledunit((self.endTime-self.startTime)/1000,"s"))
			self.updateRangeslider()
	
	## Update rangesliter on start/end value update
	def updateRangeslider(self):
		if self.rangeslider:
			self.rangeslider.setMin(self.startTime)
			self.rangeslider.setMax(self.endTime)
			self.rangeslider.setStart(self.startTime)
			self.rangeslider.setEnd(self.endTime)
			self.plotStart=self.startTime
			self.plotEnd=self.endTime
			self.rangeslider.repaint()
	
	## Apply values from rangeslider to plot
	def applyRange(self):
		start=self.rangeslider.start()
		end=self.rangeslider.end()
		self.plotWindowStart.setValue(start)
		self.plotWindowEnd.setValue(end)
	
	## Load new data from plottab into plotwidget
	# @param data dictionary of tasks and correspondig state changes
	# @param tmax end time of plot
	# @param tmin start time of plot
	def update_data(self,data,tmax,tmin):
		for t in data: #generate random color based on task-ID
			self.taskcols[t]=QtGui.QColor("#"+hashlib.md5(str(t).encode("ASCII")).hexdigest()[:6])
		self.data=data
		self.endTime_=tmax
		self.startTime_=tmin
		self.endTime=tmax
		self.startTime=tmin
		self.ntask=len(data)
		if self.plotWindowStart:
			self.plotWindowStart.setMinimum(tmin)
			self.plotWindowStart.setMaximum(tmax-1)
		if self.plotWindowEnd:
			self.plotWindowEnd.setMinimum(tmin+1)
			self.plotWindowEnd.setMaximum(tmax)
			self.plotWindowEnd.setValue(tmax)
		if self.plotWindowStartLabel:
			self.plotWindowStartLabel.setText("%.2f ms" % tmin)
		if self.plotWindowEndLabel:
			self.plotWindowEndLabel.setText("%.2f ms" % tmax)
		
		self.updateRangeslider()
	
	## Round tickdelta to match 1/2/5 pattern
	# @param tickdelta value to be rounded
	def roundTickdelta(self,tickdelta):
		try:
			fac=10**math.ceil(math.log(tickdelta,10))
		except ValueError:
			return tickdelta
		steps=[0.1,0.2,0.5,1,2,5,10,20,50,100]

		for idx in range(len(steps)-1):
			if tickdelta>=steps[idx]*fac\
			and tickdelta<=steps[idx+1]*fac: #tickdelta is in range
				tickdelta=fac*steps[idx]
				return tickdelta
		return tickdelta
		
	## Number + unit to scaled number, e.g. 0.001,s to 1 ms
	# @param value value to be scaled
	# @param unit unit to be appended
	def scaledunit(self,value,unit):
		prefix=" kMGTPEZYyzafpnµm"
		if value:
			def sign(x, value=1):  return -value if x < 0 else value
			l = int(math.floor(math.log10(abs(value))))
			if abs(l) > 24:
				l = sign(l, value=24)
			div, mod = divmod(l, 3)
			value=round(value*(10**(-l+mod)),3)
		else:
			div=0
		return locale.str(value)+" "+prefix[div]+unit

	## Return task name from ID
	def getTaskName(self,taskid):
		try:
			return " ("+Globals.objectDict['TASK'][str(taskid)]+")"
		except KeyError:
			return ""
	
	## Default function from Qt, used to display task information on hover
	# @param event to be handled
	def event(self,evt):
		if type(evt) is QtGui.QHelpEvent:
			for r,txt in self.rects:
				if r.contains(evt.pos()):
					QtWidgets.QToolTip.showText(evt.globalPos(),txt,self,r)
			return True
		QtWidgets.QToolTip.hideText()
		return super(SniffPlot,self).event(evt)
	
	## Paint the whole thing
	# @param e Qt-Internal event
	def paintEvent(self,e):
		self.rects=[]
		# in insufficient data is avaliable abort
		if not self.endTime and not self.ntask and not self.data:
			return
		# apply plotStart as offset (so this becomes our 0ms point)
		if self.plotStart:
			self.offset=self.plotStart
			# self.offset=self.roundTickdelta(self.offset)
		else:
			self.offset=0
		
		# calculate zoom factor from actual and selectd lenght
		if (self.endTime-self.startTime) and (self.plotEnd-self.plotStart):
			self.zoomfac=(self.endTime-self.startTime)/(self.plotEnd-self.plotStart)
		self.qp.begin(self)
		
		try:
			if not self.ntask: return
			# set up some values (measurements, colors)
			barHeight=(self.height()-20)/self.ntask
			timeWidth=(self.width()/(self.endTime-self.startTime))*self.zoomfac
			
			tickDelta=self.width()/(20*timeWidth)
			
			tickDelta=self.roundTickdelta(tickDelta)
			
			if (self.overrideStyle or self.snifferConfig.configCurrentTheme)=="Dark":
				textCol=QtGui.QColor(255,255,255,255)
				lineCol=QtGui.QColor(128,128,128,128)
			else:
				textCol=QtGui.QColor(0,0,0,255)
				lineCol=QtGui.QColor(128,128,128,128)
			
			t=0
			n=0
			# draw our vertival lines and add labels
			while t+self.offset<self.plotEnd and tickDelta>0:
				px=t*timeWidth
				self.qp.setPen(lineCol)
				self.qp.drawLine(px,0,px,self.height())
				self.qp.save()
				self.qp.translate(px+3,self.height())
				self.qp.rotate(-25)
				self.qp.setPen(textCol)
				if n==0:
					self.qp.drawText(0,0,self.scaledunit(self.offset/1000,"s"))
				else:
					self.qp.drawText(0,0,"+"+self.scaledunit(n*tickDelta/1000,"s"))
				self.qp.restore()
				t+=tickDelta
				n+=1
			
			ypos=0
			# for every task in our list draw a set of rectangles
			for taskid in sorted(self.data):
				self.qp.setPen(textCol)
				
				tasktext="TASK "+str(taskid)+self.getTaskName(taskid)
				if taskid == 99999:
					tasktext="EVENTS"
				self.qp.drawText(0,ypos+8,tasktext)
				taskCol=QtGui.QColor()
				# calculate height and width for each event rectangle
				for idx in range(len(self.data[taskid])-1):
					current=self.data[taskid][idx]
					next=self.data[taskid][idx+1]
					if taskid==99999:
						rect=QtCore.QRect((current["time"]-self.offset)*timeWidth,ypos+10,3,barHeight-20)
						self.qp.setPen(lineCol)
						brush=QtGui.QBrush(self.taskcols[taskid])
						self.qp.setBrush(brush)
						self.qp.drawRect(rect)
						self.rects.append([rect,"EVENT %s\ntime: %d ms"%(current["state"],current["time"])])
						continue
					if next["time"]<self.offset: continue
					if (current["time"]-self.offset)*timeWidth>self.width(): continue
					
					rect=QtCore.QRect((current["time"]-self.offset)*timeWidth,ypos+10,(next["time"]-current["time"])*timeWidth,barHeight-20)
					self.qp.setPen(lineCol)
					
					if current["state"]=="running":
						brush=QtGui.QBrush(self.taskcols[taskid])
					if current["state"]=="ready":
						brush=QtGui.QBrush(self.taskcols[taskid].lighter(200),5) #Qt::Dense4Pattern
					if current["state"]=="waiting":
						continue
					self.qp.setBrush(brush)
					
					self.qp.drawRect(rect)
					# remember the information correspondig to the rectangle
					# so we can use it do display info on hover
					self.rects.append([rect,tasktext+"\nstate: %s\nbegin: %d ms\nend: %d ms\nduration: %s ms"\
					%(current["state"],current["time"],next["time"],next["time"]-current["time"])])
					
				ypos+=barHeight
				
		except: raise
		finally:
			self.qp.end()