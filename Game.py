from bge import logic
from bge import render
import mathutils
import time
import random
	
def Game():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	scenes = logic.getSceneList()
	message = cont.sensors['Message']
	message1 = cont.sensors['Message1']
	dict = logic.globalDict
	pause = cont.sensors['Keyboard']
	
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
			obj['actionTime'] = 0.0
			dict['paused'] = False
			for i in scenes:
				if 'Score' in i.name:
					i.objects['Digit1']['digit'] = 0
					i.objects['Digit2']['digit'] = 0
			scene.suspend()
			
	def Update():
		if message1.positive:
			obj.playAction("CamMainAction",1.0,11.0,1,1,0.0,1,0.0,0,1.0)
		if obj.getActionFrame(1) > 10.5:
			obj.stopAction(1)
			obj.setActionFrame(0,1)
			
		if pause.positive and dict['paused'] == False:
			dict['paused'] = True
			logic.addScene('Pause')
			scene.suspend()
		"""elif pause.positive and dict['paused'] == True:
			dict['paused'] = False
			for i in scenes:
					if 'Pause' in i.name:
						i.end()"""
		
		#while dict['paused'] == True:
			#scene.suspend()
		
		
	def Next():
		if obj['enemies'] < 1:
			for i in scenes:
					if 'Score' in i.name:
						i.suspend()
			if obj['time'] > 45: #delay between when the last tank is killed and the 'next' menu appears
				if dict['level'] == 0:
					dict['score'] = 0
				else:
					timeBonus = 50 - (int(dict['levelClock']))
					if timeBonus >= 1:
						dict['levelScore'] += timeBonus
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
	if not 'Next' in scenes:
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
		for i in scenes:
			if 'Score' in i.name:
				i.suspend()
		if obj['time'] > 130.0:
			for i in scenes:
				if 'Level%s' % level in i.name:
					i.resume()
			for i in scenes:
				if 'Score' in i.name:
					i.resume()
			for i in scenes:
				if 'Menu' in i.name:
					i.end()
			scene.end()
		obj['time'] += 1.0
			
	Init()
	Update()

def Level0():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 0
			if not 'Score' in scenes:
				logic.addScene('Score')
			logic.addScene('Controls')
			if not 'score' in dict:
				dict['score'] = 0
			if not 'score' in dict:
				dict['levelScore'] = 0
			if not 'levelClock' in dict:
				dict['levelClock']= 0
			if not 'tank_kills' in dict:
				dict['tank_kills'] = 0
			if not 'rocket_kills' in dict:
				dict['rocket_kills'] = 0
	
	def Update():
		pass
	
	Init()
	Update()	
	
def Level1():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 1
			dict['score'] = 0
			for i in scenes:
				if 'Controls' in i.name:
					i.end()
			if not 'Score' in scenes:
				logic.addScene('Score')
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
	
	def Update():
		pass
	
	Init()
	Update()
	
def Level2():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 2
			if not 'Score' in scenes:
				logic.addScene('Score')
			if not 'score' in dict:
				dict['score'] = 0
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
	
	def Update():
		pass
	
	Init()
	Update()
	
def Level3():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 3
			if not 'Score' in scenes:
				logic.addScene('Score')
			if not 'score' in dict:
				dict['score'] = 0
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
	
	def Update():
		pass
	
	Init()
	Update()	

def Explosion():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	tank_explosion = cont.sensors['Message1']
	rocket_explosion = cont.sensors['Message2']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['time'] = 0.0
			#for i in range(1,26):
				#bit = scene.addObject('Bit', obj, 100)
	
	def Update():
		if obj['time'] > 37.0:
			obj.endObject()
			#scene.objects['Effect1'].endObject()
			#scene.objects['Effect2'].endObject()
		obj['time'] += 1.0
		if tank_explosion.positive:
			cont.activate(cont.actuators['Tank'])
		if rocket_explosion.positive:
			cont.activate(cont.actuators['Rocket'])
		
	
	Init()
	Update()
	
def Bit():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj.mass = .1
	
	def Update():
		fac = 2
		obj.applyForce([0.0, 0.0, -10], 0)
		obj.enableRigidBody()
		obj.linearVelocity = [random.randint(-10, 10)*fac, random.randint(-10, 10)*fac, random.randint(1, 5)*fac]
		scale = random.randint(1,4)/2
		obj.worldScale = [scale, scale, scale]
	
	Init()
	Update()
	
def Grid():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	collision = cont.sensors['Collision']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		if collision.positive:
				enemy = collision.hitObject
				if 'hp' in enemy:
					enemy['hp'] -= 1000
				logic.sendMessage('hit', 'None', str(enemy))
	
	Init()
	Update()

def Timer():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['levelClock'] = 0
			dict['score'] = 0
			obj['digit']= 0.0
			
	
	def Update():
		if dict['paused'] == True:
			scene.suspend()
		
		for i in range(1,4):
			if 'Digit%s' % i in obj and dict['levelClock'] >= 10**(3-i):
				scene.addObject('Num_%s' % (str(int(dict['levelClock']))[len(str(int(dict['levelClock'])))-(4-i)]),obj,1)
			if int(dict['levelClock']) == 0:
				if 'Digit3' in obj:
					scene.addObject('Num_0', obj,1)
		dict['levelClock'] += 1.0/(10*logic.getLogicTicRate())
	Init()
	Update()

def Switch():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	collision = cont.sensors['Collision']
	dict = logic.globalDict
	level = dict['level']
	switchID = str(obj)[len(str(obj))-4:len(str(obj))]
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		if collision.positive:
			logic.sendMessage('switch%s%s' % (level, switchID), 'None')
	
	Init()
	Update()

def Breakable():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['hp'] = 10
	
	def Update():
		if obj['hp'] <= 0:
			obj.endObject()
	
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