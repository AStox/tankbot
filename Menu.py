from bge import logic
from bge import events
from bge import render

class Button(object):
		
	def getName(self):
		return self.name
	
	def mouseOver(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		mouse = cont.sensors['Mouse']
		
		if mouse.positive:
			if obj['var'] == 0:
				obj.playAction('PlayAction',1.0,5.0,1,1,1.0,0,0.0,1,1.0)
				obj['var'] += 1
		else:
			obj.playAction('PlayAction',5.0,1.0,1,1,1.0,0,0.0,1,1.0)
			obj['var'] -= 1
			
	def Play(self):
		cont = logic.getCurrentController()
		scene = logic.getCurrentScene()
		mouse = cont.sensors['Mouse']
		mouseEvents = logic.mouse.events
		click = mouseEvents[events.LEFTMOUSE]		
		if click:
			logic.addScene('Level1',True)
			scene.end()
			
	def Quit(self):
		cont = logic.getCurrentController()
		scene = logic.getCurrentScene()
		mouse = cont.sensors['Mouse']
		mouseEvents = logic.mouse.events
		click = mouseEvents[events.LEFTMOUSE]
		if click:
			logic.endGame()
			
	def Next(self):
		cont = logic.getCurrentController()
		scene = logic.getCurrentScene()
		mouse = cont.sensors['Mouse']
		mouseEvents = logic.mouse.events
		click = mouseEvents[events.LEFTMOUSE]
		nextLevel = logic.globalDict['level'] + 1
		if click:
			logic.addScene('Level%s' % nextLevel, True)
		
	
			
def Camera():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['level'] = 1
	
	def Update():
		logic.mouse.visible = True
	
	Init()
	Update()

def Play():
	
	def Init():
		cont = logic.getCurrentController()
		obj = cont.owner
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
	
	def Update():
		
		play = Button()
		play.mouseOver()
		play.Play()
	
	Init()
	Update()
	
def Quit():
	
	def Init():
		cont = logic.getCurrentController()
		obj = cont.owner
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
	
	def Update():
		
		quit = Button()
		quit.mouseOver()
		quit.Quit()
	
	Init()
	Update()	

def Next():
	
	def Init():
		cont = logic.getCurrentController()
		obj = cont.owner
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
	
	def Update():
		
		next = Button()
		next.mouseOver()
		next.Next()
	
	Init()
	Update()
	
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