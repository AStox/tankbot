from bge import logic
from bge import events
from bge import render

#test

class Button(object):
		
	def __init__(self, name, action):
		self.name = name
		self.action = action
		
	def getName(self):
		return self.name
	
	def mouseOver(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		mouse = cont.sensors['Mouse']
		
		if mouse.positive:
			if obj['var'] == 0:
				obj.playAction(self.action,1.0,5.0,1,1,1.0,0,0.0,1,1.0)
				obj['var'] += 1
		else:
			obj.playAction(self.action,5.0,10.0,1,1,1.0,0,0.0,1,1.0)
			obj['var'] -= 1
			
def Camera():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		logic.mouse.visible = True
	
	Init()
	Update()

def Play():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	mouse = cont.sensors['Mouse']
	mouseEvents = logic.mouse.events
	click = mouseEvents[events.LEFTMOUSE]
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
	
	def Update():
		
		play = Button('play','PlayAction')
		play.mouseOver()
		
		"""
		if mouse.positive:
			if obj['var'] == 0:
				obj.playAction('PlayAction',1.0,5.0,1,1,1.0,0,0.0,1,1.0)
				obj['var'] += 1
		else:
			obj.playAction('PlayAction',5.0,10.0,1,1,1.0,0,0.0,1,1.0)
			obj['var'] -= 1
		"""
		
	def Click():
		if click:
			logic.addScene('Level1',True)
			scene.end()
	
	Init()
	Update()
	Click()
	
	
def Quit():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	mouse = cont.sensors['Mouse']
	mouseEvents = logic.mouse.events
	click = mouseEvents[events.LEFTMOUSE]
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
	
	def Update():
		if mouse.positive:
			if obj['var'] == 0:
				obj.playAction('QuitAction',1.0,5.0,1,1,1.0,0,0.0,1,1.0)
				obj['var'] += 1
		else:
			obj.playAction('QuitAction',5.0,10.0,1,1,1.0,0,0.0,1,1.0)
			obj['var'] -= 1
	
	def Click():
		if click:
			logic.endGame()
	
	Init()
	Update()
	Click()
	
def Template():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		pass
	
	Init()
	Update()