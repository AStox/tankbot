from bge import logic
import time
	
def Game():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	message = cont.sensors['Message']
	
	def Init():
		if not 'init' in obj:
			scene.suspend()
			obj['init'] = 1
			obj['newLevel'] = 0
			obj['target'] = scene.objects['Tank']
			obj['depth'] = obj.position.y - obj['target'].position.y
			obj['end'] = False
			obj['time'] = 0.0
			obj['players'] = 0.0
			obj['enemies'] = 0.0
			logic.globalDict['level'] = 1
			stats = { 'rocketsFired' : 0, 'rocketsIntercepted' : 0, 'bounceHits' : 0, 'level' : 0, 'score' : 0}
			logic.globalDict['stats'] = stats
			
	def Update():
		pass
		# if all tanks are destroyed, level += 1
		# OR
		# if all tanks are destroyed a menu pops up with stats and asking to continue to next level or stop.
	
	def Score():
		if obj['enemies'] < 1:
			if obj['time'] > 45:
				scene.suspend()
				logic.addScene('Score')
			obj['time'] += 1
		if obj['players'] < 1:
			if obj['time'] > 45:	
				scene.suspend()
				logic.addScene('Score')
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
	if obj['newLevel'] == 0:
		Countdown()
	Score()
	
def CountdownAction():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	action = cont.actuators['Action']
	scenes = logic.getSceneList()

	for i in scenes:
		if i.name == "Level1":
			level1 = i
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['time'] = 0.0
	
	def Update():
		cont.activate(action)
		if obj['time'] > 130.0:
			level1.resume()
			scene.end()
		obj['time'] += 1.0
			
	Init()
	Update()
	
def Score():
	
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