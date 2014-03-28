from bge import logic
import time
	
def Game():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	message = cont.sensors['Message']
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['newLevel'] = 0
			obj['target'] = scene.objects['Tank']
			obj['depth'] = obj.position.y - obj['target'].position.y
			obj['end'] = False
			obj['time'] = 0.0
			obj['players'] = 0.0
			obj['enemies'] = 0.0
			#dict['level'] = 1
			scene.suspend()
			
	def Update():
		pass
		
	def Next():
		if obj['enemies'] < 1:
			if obj['time'] > 45:
				scene.suspend()
				logic.addScene('Next')
			obj['time'] += 1
			
	def Gameover():	
		if obj['players'] < 1:
			if obj['time'] > 45:	
				scene.suspend()
				logic.addScene('Gameover')
			obj['time'] += 1
	
	def Camera():
	
		tarPos = obj['target'].worldPosition
		pos = obj.worldPosition
		soft = 0.05
		obj.position.x += (tarPos.x - pos.x) * soft
		obj.position.y += (tarPos.y + obj['depth'] - pos.y) * soft
		logic.mouse.visible = False
		
	def Countdown():
		logic.addScene('Countdown',True)
		obj['newLevel'] += 1
		
	Init()
	Update()
	if not 'Tank' in scene.objects:
		pass
	else:
		Camera()
	Next()
	Gameover()
	if obj['newLevel'] == 0:
		Countdown()
	
def CountdownAction():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	action = cont.actuators['Action']
	scenes = logic.getSceneList()
	dict = logic.globalDict
	level = dict['level']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['time'] = 0.0
	
	def Update():
		cont.activate(action)
		if obj['time'] > 130.0:
			for i in scenes:
				if 'Level%s' % level in i.name:
					i.resume()
			for i in scenes:
				if 'Menu' in i.name:
					i.end()
			scene.end()
		obj['time'] += 1.0
			
	Init()
	Update()

def Level1():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 1
	
	def Update():
		pass
	
	Init()
	Update()
	
def Level2():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 2
	
	def Update():
		pass
	
	Init()
	Update()
	
def Level3():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 3
	
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
