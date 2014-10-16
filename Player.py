'''
Copyright 2014 Adam Stockermans

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from bge import logic
from bge import events
from bge import render
import math
import mathutils
import time

def Dist(vector1,vector2): #Distance function. Used below
	x = vector1[0] - vector2[0]
	y = vector1[1] - vector2[1]
	z = vector1[2] - vector2[2]
	return math.sqrt(math.sqrt(x**2+y**2)+z**2)

def Scalar(vector1, vector2): #Scalar Multiplication of vectors. Used below
	x = vector1[0] * vector2[0]
	y = vector1[1] * vector2[1]
	z = vector1[2] * vector2[2]
	
	return mathutils.Vector((x, y, z))

def Max(value, max, min): #Determines if a value is larger or smaller than a specified Max/Min.
	if value > max:
		return max
	elif value < min:
		return min
	else:
		return value

def Sign(value): #Determines if a number is + or -.
	if value > 0:
		return 1
	elif value < 0:
		return -1
	else:
		return 0

def Bounce(my, front = 0.6, left = 0.2, right = 0.2, prop = 'wall'): 
# A function used to determine the angle of the collision between a projectile and a wall.
# Front, Left, Right arguments are the collision box dimensions of the projectile.

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
	return colAngle
		
def AxisCheck(my, front = 1.0, left = 1.0, right = 1.0, prop = 'wall'): #Function used to double check collisions.

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
	
	return (obj.rayCast(toPosFront, pos, 0, prop, 1, 1)[0], obj.rayCast(toPosLeft, pos, 0, prop, 1, 1)[0], obj.rayCast(toPosRight, pos, 0, prop, 1, 1)[0])

def Player(): #Main player function. Run by "Tank" object in Blender.
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	motion = cont.actuators['Motion']
	key = logic.keyboard.events
	kbleft = key[events.AKEY]
	kbright = key[events.DKEY]
	kbup = key[events.WKEY]
	kbdown = key[events.SKEY]
	
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
			obj['trailTime'] = 0
			
	def Update():
		
		obj['trailTime'] += 1 #Timer used for Tank's trail graphic
		
		if kbleft > 0: #left/right motion
			obj['mx'] += -obj['accel']
			if obj['trailTime'] > 2:
				obj['trailTime'] = 0
				scene.addObject('Trail', obj, 1000)
		elif kbright > 0:
			obj['mx'] += obj['accel']
			if obj['trailTime'] > 2:
				obj['trailTime'] = 0
				scene.addObject('Trail', obj, 1000)
		else:
			obj['mx'] *= (1-obj['friction'])
		
		if kbup > 0: #up/down motion
			obj['my'] += obj['accel']
			if obj['trailTime'] > 2:
				obj['trailTime'] = 0
				scene.addObject('Trail', obj, 1000)
		elif kbdown > 0:
			obj['my'] += -obj['accel']
			if obj['trailTime'] > 2:
				obj['trailTime'] = 0
				scene.addObject('Trail', obj, 1000)
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
		
	def Animate(): #This function translates up/down/left/right inputs into smooth rotations.
		ori = obj.orientation.to_euler()
		obj['dir'] = math.atan2(-obj['mx'], obj['my'])
		ori.z = obj['dir']
		obj.orientation = ori
	
	def Death(): #This function handles the Tank's death :(
		if obj['hp'] < 1:
			scene.addObject('Explosion',obj)
			logic.sendMessage('explosion', 'None')
			obj.endObject()
			scene.objects['TankGun'].endObject()
			scene.objects['CamMain']['players'] -= 1
		
	Init()
	Update()
	Animate()
	Death()

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
			obj['scale'] = 1
			obj['time'] = 0
			scene.addObject('LaserPoint',obj)
			
	def Update():
		
		obj.worldPosition = obj['parent'].worldPosition #Making sure the Tank's gun goes where it should.
		
		def MousePos(): #This function handles the gun's rotation, making it follow the cursor's position.
			x = int(render.getWindowWidth() / 2 - (logic.mouse.position[0] * render.getWindowWidth())) * obj['scale']
			y = int(render.getWindowHeight() / 2 - (logic.mouse.position[1] * render.getWindowHeight())) * obj['scale']
			return mathutils.Vector((-x, y, 0.6520))
		
		toVect = MousePos() - obj.worldPosition
		obj.alignAxisToVect(toVect, 1, 1)
		obj.alignAxisToVect([0.0, 0.0, 1.0], 2, 1)
		
	def Laser(): #Draws the aiming laser from the gun.
		ray = obj.rayCast(aim, rInit, 500, '', 1, 0)[1]
		hitPos = [ray[0], ray[1], ray[2]]
		render.drawLine(rInit.worldPosition, hitPos, [1.0, 0.0, 0.0])
		scene.objects['LaserPoint'].worldPosition = (mathutils.Vector((hitPos[0], hitPos[1], hitPos[2])) + (obj.rayCast(aim, rInit, 500, '', 1, 0)[2]*.25))
	
	Init()
	Update()
	Laser()

def RocketEffect(): #Simple function controlling the fire effect on the back of rockets.
	
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
	
def RocketInit(): #Function controlling instantiation of rockets. Run by the RocketInit object in Blender.
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	
	mouse = logic.mouse.events
	msshoot = mouse[events.LEFTMOUSE]
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['atk'] = 10
			obj['shottimer'] = 50.0
			obj['dir'] = 0.0
			
	def Update():
	
		obj['shottimer'] += 1.0
		if msshoot:
			if obj['shottimer'] >= 60.0:
				obj['shottimer'] = 0.0
				rocket = scene.addObject('Rocket', obj)
				rocket['speed'] = 0.25
				rocket['dir'] = obj['dir']
		
	Init()
	Update()
	
def Rocket(): #Function controlling general rocket behaviour, including bounce angle, and death. 
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	motion = cont.actuators['Motion']
	collision = cont.sensors['Collision']
	dict = logic.globalDict
	level = dict['level']
	rocket_collision = cont.sensors['Collision2']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['hp'] = 1
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
		obj.worldPosition.z = 1
		scene.addObject('EffectRocket1',obj)
		scene.addObject('EffectRocket2',obj)		
		motion.useLocalDLoc = True
		motion.useLocalDRot = True
		motion.dLoc = [0.0, obj['speed'] ,0.0]
		obj.applyForce([0.0, 0.0, 9.82], 0)
		cont.activate(motion)
		
	def BounceAngle(): # A function used to determine the new angle of motion of a projectile after bouncing off a wall. 
		if Bounce(obj['speed'], obj['front'], obj['side'], obj['side'], 'wall') != mathutils.Vector((0.0, 0.0, 0.0)):
			cont.activate(cont.actuators['Bounce'])
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
		if obj['bounces'] > obj['maxBounces']:
			obj.endObject()
			explosion = scene.addObject('Explosion',obj)
			logic.sendMessage('rocket_explosion', 'None')
		
		if rocket_collision.positive and obj['time'] < 30:
			dict['levelScore'] += 10
			dict['rocket_kills'] += 1
			scene.addObject('Plus_10',obj,40)
			scene.objects['Plus_10'].alignAxisToVect([1.0,0,0],0,1.0)
		if collision.positive:
			enemy = collision.hitObject
			if 'player' in enemy and obj['time'] < 5.0:
				pass
			else:
				if 'enemy' in enemy:
					logic.sendMessage('hit', 'None', str(enemy))
				if 'hp' in enemy:
					enemy['hp'] -= 10
				obj.endObject()
				explosion = scene.addObject('Explosion',obj)
		if obj['hp'] < 1:
			obj.endObject()
		if obj['time'] > 600:
			obj.endObject()
		
		obj['time'] += 1.0
			
	def Message(): #This function alerts enemy tanks when a rocket is going to collide with them.
		ori = obj.orientation[1].copy()
		ori.x *= -1
		pos = obj.position
		toPos = pos + ori
		posL = obj.worldPosition + Scalar(obj.orientation[0], mathutils.Vector((-1,1,1)))*.5
		posR = obj.worldPosition - Scalar(obj.orientation[0], mathutils.Vector((-1,1,1)))*.5
		
		ray = obj.rayCast(toPos, obj, 10000, '', 1, 0)
		rayL = obj.rayCast(posL + Scalar(obj.orientation[1], mathutils.Vector((-1,1,1))), posL, 10000, '', 1, 0)
		rayR = obj.rayCast(posR + Scalar(obj.orientation[1], mathutils.Vector((-1,1,1))), posR, 10000, '', 1, 0)
		
		if ray[1] != None or rayL[1] != None or rayR[1] != None:
			hitPos = [ray[1][0], ray[1][1], ray[1][2]]
			hitPosL = [rayL[1][0], rayL[1][1], rayL[1][2]]
			hitPosR = [rayR[1][0], rayR[1][1], rayR[1][2]]
		if ray != None or rayL != None or rayR != None:
			if ray[0] != None:
				if Dist(ray[1], scene.objects['EvadeL'].worldPosition) > Dist(ray[1], scene.objects['EvadeR'].worldPosition):
					logic.sendMessage('hit_L', 'None', str(ray[0]))
				else:
					logic.sendMessage('hit_R', 'None', str(ray[0]))
			elif rayL[0] != None:
				if Dist(rayL[1], scene.objects['EvadeL'].worldPosition) > Dist(rayL[1], scene.objects['EvadeR'].worldPosition):
					logic.sendMessage('hit_L', 'None', str(rayL[0]))
				else:
					logic.sendMessage('hit_R', 'None', str(rayL[0]))
			elif rayR[0] != None:
				if Dist(rayR[1], scene.objects['EvadeL'].worldPosition) > Dist(rayR[1], scene.objects['EvadeR'].worldPosition):
					logic.sendMessage('hit_L', 'None', str(rayR[0]))
				else:
					logic.sendMessage('hit_R', 'None', str(rayR[0]))
	
	Init()
	Update()
	Message()
	BounceAngle()
	Death()	
	
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