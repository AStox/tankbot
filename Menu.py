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
			logic.addScene('Level1')
			
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
		scenes = logic.getSceneList()
		mouse = cont.sensors['Mouse']
		mouseEvents = logic.mouse.events
		click = mouseEvents[events.LEFTMOUSE]
		dict = logic.globalDict
		nextLevel = dict['level'] + 1
		
		if click:
			for i in scenes:
				if 'Level%s' % (nextLevel - 1) in i.name:
					i.replace('Level%s' % nextLevel)
			scene.end()
	
	def Gameover(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		mouse = cont.sensors['Mouse']
		mouseEvents = logic.mouse.events
		click = mouseEvents[events.LEFTMOUSE]
		if obj['time'] > 3:
			if click:
				logic.restartGame()
		obj['time'] += 1

def CameraMain():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		logic.mouse.visible = True
	
	Init()
	Update()
		
def Camera():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			logic.mouse.visible = True
	def Update():
		pass
	
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
	
def Gameover():
	
	def Init():
		cont = logic.getCurrentController()
		obj = cont.owner
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
			obj['time'] = 0
	
	def Update():
		
		gameover = Button()
		gameover.mouseOver()
		gameover.Gameover()
	
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
