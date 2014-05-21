from bge import logic
from bge import events
from bge import render
import math
import mathutils

def Scalar(vector1, vector2):
	x = vector1[0] * vector2[0]
	y = vector1[1] * vector2[1]
	z = vector1[2] * vector2[2]
	
	return mathutils.Vector((x, y, z))
	
def AbsVec(vector):
	x = abs(vector[0])
	y = abs(vector[1])
	z = abs(vector[2])
	
	return mathutils.Vector((x, y, z))

def Max(value, max, min):
	if value > max:
		return max
	elif value < min:
		return min
	else:
		return value

def Sign(value):
	if value > 0:
		return 1
	elif value < 0:
		return -1
	else:
		return 0

def AxisCheck(my, front = 1.0, left = 1.0, right = 1.0, prop = 'wall'):

	cont = logic.getCurrentController()
	obj = cont.owner
	
	pos = obj.position
	toPosFront = pos.copy()
	toPosLeft = pos.copy()
	toPosRight = pos.copy()
	
	toPosFront.y += front + my
	toPosLeft.y += front + my
	toPosLeft.x -= left + my
	toPosRight.y += front + my
	toPosRight.x += right + my
	
	#return obj.rayCast(To Position, From Position, Distance (0=infinity), With Property, 1, 1)
	return (obj.rayCast(toPosFront, pos, 0, prop, 1, 1)[0], obj.rayCast(toPosLeft, pos, 0, prop, 1, 1)[0], obj.rayCast(toPosRight, pos, 0, prop, 1, 1)[0])

class EnemyTemp(object):
	
	def __init__(self, hp, shot_cd):
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		dict = logic.globalDict
		level = dict['level']
		enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		obj['parent'] = scene.objects['Enemy%s%s' % (level, enemyID)]
		aim = scene.objects['EnemyAim%s%s' % (level, enemyID)]
		self.hp = hp
		self.shot_cd = shot_cd
		if 'Tank' in scene.objects:
			obj['target'] = scene.objects['Tank']
		obj['atk'] = 10
	
	def Pathing(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		messageL = cont.sensors['MessageL']
		messageR = cont.sensors['MessageR']
		steering = cont.actuators['Steering']
		dict = logic.globalDict
		level = dict['level']
		enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		#print(scene.objects)
		
		def Init():
			if not 'init1' in obj:
				obj['init1'] = 1
				obj['evadeTimer'] = 50
				scene.addObject('EvadeR', obj)
				scene.addObject('EvadeL', obj)
		Init()
		evadeR = scene.objects['EvadeR']
		evadeL = scene.objects['EvadeL']
		obj['evadeTimer'] += 1
		for i in range (0,361,30):
			i *= (math.pi/180)	
			if messageL.positive and obj['evadeTimer']:
				if 'Rocket' in scene.objects:
					evadeR.worldPosition = obj.worldPosition + Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
					evadeL.worldPosition = obj.worldPosition - Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
					steering.behavior = 2
					steering.distance = 1000
					cont.activate(steering)
					steering.target = scene.objects['EvadeR']
					obj['evadeTimer'] = 0
					#render.drawLine(obj.worldPosition, scene.objects['EvadeR'].worldPosition,(1.0,1.0,1.0))
					#print("L")
			elif messageR.positive and obj['evadeTimer']:
				if 'Rocket' in scene.objects:
					evadeR.worldPosition = obj.worldPosition + Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
					evadeL.worldPosition = obj.worldPosition - Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
					steering.behavior = 2
					steering.distance = 1000
					cont.activate(steering)
					steering.target = scene.objects['EvadeL']
					obj['evadeTimer'] = 0
					#render.drawLine(obj.worldPosition, scene.objects['EvadeL'].worldPosition,(1.0,1.0,1.0))
					#print("R")
			elif obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0] == None and obj['evadeTimer'] >= 50:
					steering.behavior = 3
					steering.distance = 1
					steering.target = scene.objects['Tank']
					cont.activate(steering)
					#render.drawLine(obj.worldPosition, steering.target.worldPosition, [1.0, 1.0, 1.0])
					#print("Tank")
			elif obj.rayCast(obj.worldPosition + mathutils.Vector((2.5*math.sin(i),2.5*math.cos(i),0)), obj, 2.5, "", 0, 0, 0)[0] != None and obj['evadeTimer'] >= 50:
					evadeObject = scene.addObject('Evade', obj, 50)
					evadeObject.worldPosition = obj.rayCast(obj.worldPosition + mathutils.Vector((2.5*math.sin(i),2.5*math.cos(i),0)), obj, 2.5, "", 0, 0, 0)[1]
					steering.behavior = 2
					steering.distance = 1000
					cont.activate(steering)
					steering.target = scene.objects['Evade']
					#render.drawLine(obj.worldPosition, obj.worldPosition + mathutils.Vector((5*math.sin(i),5*math.cos(i),0)), [1.0, 1.0, 1.0])
					#print("Wall")
			else:
				cont.deactivate(steering)
				
	def Health(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		dict = logic.globalDict
		level = dict['level']
		scene = logic.getCurrentScene()
		enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		hit = cont.sensors['Message2']
		if hit.positive:
			self.hp -= 10
		if self.hp < 1:
			if dict['level'] != 0:
				dict['levelScore'] += 100
				dict['tank_kills'] += 1
				scene.addObject('Plus_100', obj, 40)
				scene.objects['Plus_100'].alignAxisToVect([1.0,0,0],0,1.0)
				#print (dir(scene.objects['Plus_100']))
			scene.addObject('Explosion',obj)
			obj.endObject()
			scene.objects['EnemyGun%s%s' % (level, enemyID)].endObject()
			scene.objects['CamMain']['enemies'] -= 1
			logic.sendMessage('explosion', 'None')
			
	def Gun(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		obj.worldPosition = obj['parent'].worldPosition
		
	def Aim(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		
		if not 'my' in obj['target']:
			obj['target']['my'] = 0.0
		if not 'mx' in obj['target']:
			obj['target']['mx'] = 0.0
			
		ori = obj.orientation.to_euler()
		pos = obj.worldPosition
		corVec = mathutils.Vector((-1.0, 1.0, 1.0))
		tarSpeedVec = AbsVec(mathutils.Vector((obj['target']['mx'], obj['target']['my'], 0)))
		tarOri = obj['target'].orientation[1]
		tarPos = obj['target'].worldPosition
		time = (obj.getDistanceTo(obj['target']))/0.3
		corPos = tarPos + (Scalar(Scalar(tarOri, corVec), tarSpeedVec) * time)
		obj['dir'] = (-math.pi/2 + math.atan2((corPos.y - pos.y), (corPos.x - pos.x)))
		ori.z = obj['dir']
		obj.orientation = ori
		#render.drawLine(pos, corPos, [0.0, 1.0, 0.0])
		
	def RocketInit(self):
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		def Init():
			if not 'init' in obj:
				obj['init'] = 1
				obj['shottimer'] = self.shot_cd
		Init()
		
		obj['shottimer'] += 1.0
		if obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0] != None:
			if obj['shottimer'] >= self.shot_cd:
				obj['shottimer'] = 0.0
				rocket = scene.addObject('EnemyRocket',obj)
				rocket['speed'] = 0.25
				rocket['type'] = 'player'

def Level0():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	if not 'level' in dict:
		pass
	else:
		enemy = EnemyTemp(10,100)
		if 'enemy' in obj:
			if not 'init' in obj:
				obj['init'] = 1
				scene.objects['CamMain']['enemies'] += 1.0
			if 'Tank' in scene.objects:
				enemy.Pathing()
			enemy.Health()	
		elif 'gun' in obj:
			enemy.Gun()
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Aim()
		
def Level1():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	if not 'level' in dict:
		pass
	else:
		enemy = EnemyTemp(10, 120)
		if 'enemy' in obj:
			if not 'init' in obj:
				obj['init'] = 1
				scene.objects['CamMain']['enemies'] += 1.0
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Pathing()
			enemy.Health()	
		elif 'gun' in obj:
			enemy.Gun()
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Aim()
		else:
			enemy.RocketInit()
			
def Level2():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	if not 'level' in dict:
		pass
	else:
		enemy = EnemyTemp(10, 120)
		if 'enemy' in obj:
			if not 'init' in obj:
				obj['init'] = 1
				scene.objects['CamMain']['enemies'] += 1.0
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Pathing()
			enemy.Health()	
		elif 'gun' in obj:
			enemy.Gun()
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Aim()
		else:
			enemy.RocketInit()
			
def Level3():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level = dict['level']
	scene = logic.getCurrentScene()
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		
	if 'level' in dict:
		enemy = EnemyTemp(10, 120)
		if 'enemy' in obj:
			if not 'init' in obj:
				obj['init'] = 1
				scene.objects['CamMain']['enemies'] += 1.0
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Pathing()
			enemy.Health()	
		elif 'gun' in obj:
			enemy.Gun()
			if not 'Tank' in scene.objects:
				pass
			else:
				enemy.Aim()
		else:
			enemy.RocketInit()
				
	
def Rocket():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	motion = cont.actuators['Motion']
	collision = cont.sensors['Collision']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			if not 'speed' in obj:
				obj['speed'] = 0.0
			if not 'dir' in obj:
				obj['dir'] = 0.0
			obj['time'] = 0.0
			obj['rocket'] = True
	
	def Update():
		obj['dir'] = obj.linearVelocity
		
		obj.localPosition.z = 1.0
		
		scene.addObject('EffectRocket1',obj)
		scene.addObject('EffectRocket2',obj)
		
		motion.useLocalDLoc = True
		motion.useLocalDRot = True
		#motion.dRot = [0.0, obj['ry'], 0.0]
		motion.dLoc = [0.0, obj['speed'] ,0.0]
		#obj.applyForce([0.0, 0.0, 9.82], 0)
		cont.activate(motion)
		
		obj['time'] += 1
		if obj['time'] > 2:
			if collision.positive:
				enemy = collision.hitObject
				if not 'hp' in enemy:
					pass
				else:
					enemy['hp'] -= 10
				obj.endObject()
				explosion = scene.addObject('Explosion',obj)
				explosion['dir'] = obj['dir']
				logic.sendMessage('rocket_explosion', 'None')
	
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