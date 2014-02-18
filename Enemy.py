from bge import logic
from bge import events
import math
import mathutils

def Scalar(vector1, vector2):
	x = vector1[0] * vector2[0]
	y = vector1[1] * vector2[1]
	z = vector1[2] * vector2[2]
	
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

def Enemy():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	message = cont.sensors['Message']
	steering = cont.actuators['Steering']
	navmesh = scene.objects['Navmesh']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['target'] = scene.objects['Tank']
			obj['node'] = 0
			obj['rz'] = 0.0
			obj['my'] = 0.0
			obj['maxspeed'] = 0.05
			obj['accel'] = 0.005
			obj['friction'] = 0.3
			obj['hp'] = 10
			obj['dir'] = 0.0
			obj['enemy'] = True
			scene.objects['CamMain']['enemies'] += 1.0
			
	def Update():
		pass
	
	def Pathing():
		if message.positive:
			steering.behavior = 2
			steering.distance = 1000
			if not 'Rocket' in scene.objects:
				pass
			else:
				steering.target = scene.objects['EvadeR']
			cont.activate(steering)
		else:
			steering.behavior = 3
			if (obj.rayCast('Tank', obj, 0, 'rocket', 0, 0)[0]) != None:
				cont.deactivate(steering)
			elif (obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0]) == None: #if player is not detected:
				steering.distance = 1
				steering.target = scene.objects['Tank']
				cont.activate(steering)
			else:
				cont.deactivate(steering)
				
	def Health():
		if obj['hp'] < 1:
			obj.endObject()
			scene.objects['EnemyGun'].endObject()
			scene.objects['CamMain']['enemies'] -= 1
	
	Init()
	Update()
	if not 'Tank' in scene.objects:
		pass
	else:
		Pathing()
	Health()

def Gun():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['dir'] = 0.0
			obj['target'] = scene.objects['Tank']
			obj['parent'] = scene.objects['Enemy']
	
	def Update():
		
		obj.worldPosition = obj['parent'].worldPosition
			
	def Aim():
		if not 'my' in obj['target']:
			obj['target']['my'] = 0.0
			
		ori = obj.orientation.to_euler()
		pos = obj.worldPosition
		corVec = mathutils.Vector((-1.0, 1.0, 1.0))
		tarSpeed = obj['target']['my']
		tarSpeedVec = mathutils.Vector((tarSpeed, tarSpeed, tarSpeed))
		tarOri = obj['target'].orientation[1]
		tarPos = obj['target'].worldPosition
		time = (obj.getDistanceTo(obj['target']))/0.35
		corPos = tarPos + (Scalar(Scalar(tarOri, corVec), tarSpeedVec) * time)
		obj['dir'] = (-math.pi/2 + math.atan2((corPos.y - pos.y), (corPos.x - pos.x)))
		ori.z = obj['dir']
		obj.orientation = ori
		"""print('my: ', obj['target']['my'])
		print('Tank Position: ', tarPos)
		print('Tank Orientation: ', tarOri)
		print('Correcting Vector: ', corVec)
		print('tarSpeedVec: ', tarSpeedVec)
		print('Time to Target: ', time)
		print('Product: ',Scalar(tarOri, corVec))
		print('Corrected Position: ', corPos)
		"""
		
	Init()
	Update()
	if not 'Tank' in scene.objects:
		pass
	else:
		Aim()
	
def RocketInit():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	aim = scene.objects['EnemyAim']
	
	
	def Init():
		
		if not 'init' in obj:
			obj['init'] = 1
			obj['atk'] = 10
			obj['shottimer'] = 60.0
			obj['dir'] = 0.0
			obj['target'] = scene.objects['Tank']
			
	def Update():
		
		obj['shottimer'] += 1.0
		if obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0] != None:
			if obj['shottimer'] >= 60.0:
				obj['shottimer'] = 0.0
				rocket = scene.addObject('EnemyRocket',obj)
				rocket['speed'] = 0.25
				rocket['dir'] = obj['dir']
				rocket['type'] = 'player'
		
	Init()
	Update()
	
def Rocket():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
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
		
		obj.localPosition.z = 1.0
		
		scene.addObject('EffectRocket1',obj)
		scene.addObject('EffectRocket2',obj)
		
		motion.useLocalDLoc = True
		motion.useLocalDRot = True
		#motion.dRot = [0.0, obj['ry'], 0.0]
		motion.dLoc = [0.0, obj['speed'] ,0.0]
		obj.applyForce([0.0, 0.0, 9.82], 0)
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
				eff1 = scene.addObject('Effect1',obj)
				eff2 = scene.addObject('Effect2',obj)
	
	Init()
	Update()

def RocketOutline():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	obj['parent'] = scene.objects['EnemyRocket']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
	
	def Update():
		obj.worldPosition = obj['parent'].worldPosition
	
	Init()
	Update()
	
def Explosion():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	action = cont.actuators['Action']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['time'] = 0.0
			if not 'type' in obj:
				obj['type'] = None
	
	def Update():
			
		if obj['time'] > 37.0:
			obj.endObject()
		obj['time'] += 1.0
		
		cont.activate(action)
	
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