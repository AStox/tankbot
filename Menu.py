from bge import logic
from bge import events
from bge import render
import time

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
			logic.addScene('Level0')
			logic.addScene('Music')
			
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
		
	def Again(self):
		cont = logic.getCurrentController()
		scene = logic.getCurrentScene()
		scenes = logic.getSceneList()
		mouse = cont.sensors['Mouse']
		mouseEvents = logic.mouse.events
		click = mouseEvents[events.LEFTMOUSE]
		dict = logic.globalDict
		level = dict['level']

		if click:
			for i in scenes:
				if 'Level%s' % (level) in i.name:
					i.restart()
			scene.end()

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
	
def Again():
	
	def Init():
		cont = logic.getCurrentController()
		obj = cont.owner
		if not 'init' in obj:
			obj['init'] = 1
			obj['var'] = 0
	
	def Update():
		
		again = Button()
		again.mouseOver()
		again.Again()
	
	Init()
	Update()

def Score():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	levelScore = str(int(dict['levelScore']))
	score = str(int(dict['score']))
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		tankPoints = dict['tank_kills'] * 100
		rocketPoints = dict['rocket_kills'] * 10
		timeBonus = 50 - int(dict['levelClock'])
		if dict['level'] == 0:
			timePoints = 0
		elif timeBonus >= 1:
			timePoints = timeBonus
		else:
			timePoints = 0
			
		for i in range(1,5):
			if 'tank%s' % i in obj and tankPoints >= 10**(4-i):
				scene.addObject('Num_%s' % (str(tankPoints)[len(str(tankPoints))-(5-i)]),obj)	
			if tankPoints == 0:
				if 'tank4' in obj:
					scene.addObject('Num_0', obj)
			if 'time%s' % i in obj and timePoints >= 10**(4-i):
				scene.addObject('Num_%s' % (str(timePoints)[len(str(timePoints))-(5-i)]),obj)
			elif timePoints == 0:
				if 'time4' in obj:
					scene.addObject('Num_0', obj)
			if 'rocket%s' % i in obj and rocketPoints >= 10**(4-i):
					scene.addObject('Num_%s' % (str(rocketPoints)[len(str(rocketPoints))-(5-i)]),obj)
			elif rocketPoints == 0:
				if 'rocket4' in obj:
					scene.addObject('Num_0', obj)
			
			if 'digit%s' % i in obj and dict['score'] >= 10**(4-i):
				scene.addObject('Num_%s' % (score[len(score)-(5-i)]),obj)
			if dict['score'] == 0:
				if 'digit4' in obj:
					scene.addObject('Num_0', obj)
					
			"""if 'digit%s' % i in obj and dict['levelScore'] >= 10**(4-i):			####CODE FOR THE SCORE FROM A SINGLE LEVEL###
				scene.addObject('Num_%s' % (score[len(levelScore)-(5-i)]),obj)
			if dict['levelScore'] == 0:
				if 'digit4' in obj:
					scene.addObject('Num_0', obj)"""

	Init()
	Update()
	
def Paused():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	pause = cont.sensors['Keyboard']
	dict = logic.globalDict
	level = dict['level']
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		for i in scenes:
			if 'Score' in i.name:
				i.suspend()
		if pause.positive:
			dict['paused'] = False
			for i in scenes:
					if 'Score' in i.name:
						i.resume()
					if 'Level%s' % level in i.name:
						i.resume()
			scene.end()
	
	Init()
	Update()	
	
def ScoreCounter():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['score'] += dict['levelScore']
			
	
	def Update():
		pass
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