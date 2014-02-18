from bge import logic
from bge import events
from bge import render
import math
import mathutils
import time

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

def Bounce(my, front = 0.6, left = 0.2, right = 0.2, prop = 'wall'):

	cont = logic.getCurrentController()
	obj = cont.owner
	
	ori = obj.localOrientation[1].copy()
	ori.x *= -1
	angle = math.atan2(ori.y,ori.x) * 57.2958
	pos = obj.position
	toPosFront = (pos + ori)
	toPosLeft = (pos + ori)
	toPosRight = (pos + ori)
	
	toPosLeft.y = pos.y - (ori.x * left) + (ori.y * front)
	toPosLeft.x = pos.x - (ori.y * left) + (ori.x * front)
	toPosRight.y = pos.y + (ori.x * right) + (ori.y * front)
	toPosRight.x = pos.x + (ori.y * right) + (ori.x * front)
	
	colAngle = mathutils.Vector((0.0, 0.0, 0.0))
	
	if obj.rayCast(toPosFront, pos, 0, prop, 1, 1)[0] != None:
		colAngle = obj.rayCast(toPosFront, pos, 0, prop, 1, 1)[2]
	elif obj.rayCast(toPosLeft, pos, 0, prop, 1, 1)[0] != None:
		colAngle = obj.rayCast(toPosLeft, pos, 0, prop, 1, 1)[2]
	elif obj.rayCast(toPosRight, pos, 0, prop, 1, 1)[0] != None:
		colAngle = obj.rayCast(toPosRight, pos, 0, prop, 1, 1)[2]
	
	#render.drawLine(obj.position, toPosFront, [0.0, 0.0, 1.0])
	#render.drawLine(obj.position, toPosLeft, [0.0, 0.0, 1.0])
	#render.drawLine(obj.position, toPosRight, [0.0, 0.0, 1.0])
	
	return colAngle
		
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

def Player():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	motion = cont.actuators['Motion']
	
	#Keyboard movement events
	key = logic.keyboard.events
	kbleft = key[events.AKEY]
	kbright = key[events.DKEY]
	kbup = key[events.WKEY]
	kbdown = key[events.SKEY]
	
	#Init function. Runs once.
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['my'] = 0.0
			obj['mx'] = 0.0
			obj['maxspeed'] = .1
			obj['accel'] = .01
			obj['friction'] = 0.1
			obj['hp'] = 10
			scene.objects['CamMain']['players'] += 1.0
			obj['explode'] = True
			obj['dir'] = 0.0
			
	#Update function. Runs every logic frame when TRUE level triggering is active
	def Update():
		
		#left/right motion
		if kbleft > 0:
			obj['mx'] += -obj['accel']
		elif kbright > 0:
			obj['mx'] += obj['accel']
		else:
			obj['mx'] *= (1-obj['friction'])
		
		#up/down motion		
		if kbup > 0:
			obj['my'] += obj['accel']
		elif kbdown > 0:
			obj['my'] += -obj['accel']
		else:
			obj['my'] *= (1-obj['friction'])

		if AxisCheck(obj['my'], 1.0, 1.0, 1.0, 'wall')[0] != None:
			obj['my'] = 0

		#Max speed
		obj['mx'] = Max(obj['mx'], obj['maxspeed'],-obj['maxspeed'])
		obj['my'] = Max(obj['my'], obj['maxspeed'],-obj['maxspeed'])
		
		motion.useLocalDLoc = False
		motion.dLoc = [obj['mx'], obj['my'] ,0.0]
		cont.activate(motion)
		
	def Animate():
		ori = obj.orientation.to_euler()
		obj['dir'] = math.atan2(-obj['mx'], obj['my'])
		ori.z = obj['dir']
		obj.orientation = ori
	
	def Health():
		if obj['hp'] < 1:
			obj.endObject()
			scene.objects['TankGun'].endObject()
			scene.objects['CamMain']['players'] -= 1
	
	Init()
	Update()
	Animate()
	Health()

def Gun():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	motion = cont.actuators['Motion']
	obj['parent'] = scene.objects['Tank']
	aim = scene.objects['TankAim']
	rInit = scene.objects['RocketInit']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['scale'] = 0.001
			obj['time'] = 0
			
	def Update():
		
		obj.worldPosition = obj['parent'].worldPosition
		
		obj['time'] += 1
		
		def mousePos():
			x = int(render.getWindowWidth() / 2 - (logic.mouse.position[0] * render.getWindowWidth())) * obj['scale']
			return x
		
		if obj['time'] > 1:
			pos = mousePos()
			motion.useLocalDRot = False
			motion.dRot = (0.0, 0.0, pos)
			cont.activate(motion)

		render.setMousePosition(int(render.getWindowWidth() / 2), int(render.getWindowHeight() / 2))
		
	def Laser():
		ray = obj.rayCast(aim, rInit, 100, '', 1, 0)[1]
		hitPos = [ray[0],ray[1], ray[2]]
		render.drawLine(rInit.worldPosition, hitPos, [1.0, 0.0, 0.0])
	
	Init()
	Update()
	Laser()

def RocketEffect():
	
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
			
		if obj['time'] > 10.0:
			obj.endObject()
		obj['time'] += 1.0
		
		cont.activate(action)
	
	Init()
	Update()
	
def RocketInit():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	mouse = logic.mouse.events
	msshoot = mouse[events.LEFTMOUSE]
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['atk'] = 10
			obj['shottimer'] = 0.0
			obj['dir'] = 0.0
			
	def Update():
	
		obj['shottimer'] += 1.0
		if msshoot:
			if obj['shottimer'] >= 60.0:
				obj['shottimer'] = 0.0
				rocket = scene.addObject('Rocket',obj)
				rocket['speed'] = 0.25
				rocket['dir'] = obj['dir']
		
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
			obj['bounces'] = 0
			obj['maxBounces'] = 1
			obj['front'] = 0.62
			obj['side'] = 0.21
			obj['time'] = 0.0
	
	def Update():
		
		obj.localPosition.z = 1.0
		
		scene.addObject('EffectRocket1',obj)
		scene.addObject('EffectRocket2',obj)
		
		motion.useLocalDLoc = True
		motion.useLocalDRot = True
		motion.dLoc = [0.0, obj['speed'] ,0.0]
		obj.applyForce([0.0, 0.0, 9.82], 0)
		cont.activate(motion)
	
	def BounceAngle():
		if Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall') != mathutils.Vector((0.0, 0.0, 0.0)):
			if int(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[1]) == -1: #collision surface is on the X axis
				colAngle = math.atan2(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[0], Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[1])
				rocketAngle = math.atan2(obj.orientation[1][0], obj.orientation[1][1])
				newAngle = -(rocketAngle - colAngle)
				ori = obj.orientation.to_euler()
				ori.z = newAngle
				obj.orientation = ori
				obj['bounces'] += 1
				
			elif int(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[1]) == 1: #collision surface is on the X axis
				colAngle = math.atan2(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[0], Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[1])
				rocketAngle = math.atan2(obj.orientation[1][0], obj.orientation[1][1])
				newAngle = math.pi - rocketAngle
				ori = obj.orientation.to_euler()
				ori.z = newAngle
				obj.orientation = ori
				obj['bounces'] += 1

			elif int(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[0]) == 1: #collision surface is on the Y axis
				colAngle = math.atan2(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[0], Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[1])
				rocketAngle = math.atan2(obj.orientation[1][0], obj.orientation[1][1])
				newAngle = -(math.pi/2) - (rocketAngle - colAngle)
				ori = obj.orientation.to_euler()
				ori.z = newAngle
				obj.orientation = ori
				obj['bounces'] += 1
				
			elif int(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[0]) == -1: #collision surface is on the Y axis
				colAngle = math.atan2(Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[0], Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall')[1])
				rocketAngle = math.atan2(obj.orientation[1][0], obj.orientation[1][1])
				newAngle = (math.pi/2) - (rocketAngle - colAngle)
				ori = obj.orientation.to_euler()
				ori.z = newAngle
				obj.orientation = ori
				obj['bounces'] += 1
	def Death():	
		obj['time'] += 1.0
		
		if obj['bounces'] > obj['maxBounces']:
			obj.endObject()
			eff1 = scene.addObject('Effect1',obj)
			eff2 = scene.addObject('Effect2',obj)
		
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
		
		if obj['time'] > 600:
			obj.endObject()
			
	def Message():
		ori = obj.orientation[1].copy()
		ori.x *= -1
		pos = obj.position
		toPos = pos + ori
		
		ray = obj.rayCast(toPos, obj, 100, '', 1, 0)
		hitPos = [ray[1][0], ray[1][1], ray[1][2]]
		#render.drawLine(obj.position, hitPos, [0.0, 1.0, 0.0])
		if obj.rayCast(toPos, obj, 100, 'enemy', 1, 0)[0] != None:
			logic.sendMessage('hit', 'None', 'Enemy')
	
	Init()
	Update()
	Message()
	BounceAngle()
	Death()

	
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