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
import copy
import random

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
	
def AbsVec(vector): #Converts a vector to the absolute values of its parts.
	x = abs(vector[0])
	y = abs(vector[1])
	z = abs(vector[2])
	
	return mathutils.Vector((x, y, z))

def VectorMagnitude(vector): #returns the magnitude of a vector
	return math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
	
def Angle(vector1, vector2): #returns the angle between two vectors
	return (180/math.pi)	* math.acos((Scalar(vector1, vector2)[0] + Scalar(vector1, vector2)[1] + Scalar(vector1, vector2)[2])/(VectorMagnitude(vector1)*VectorMagnitude(vector2)))
	
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

class EnemyTemp(object): #General enemy class
	
	def __init__(self, hp, shot_cd, type):
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		self.hp = hp
		self.shot_cd = shot_cd
		self.type = type
		dict = logic.globalDict
		level = dict['level']
		enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		obj['parent'] = scene.objects['Enemy%s%s' % (level, enemyID)]	
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
		
		def Init():
			if not 'init1' in obj:
				obj['init1'] = 1
				obj['evadeTimer'] = 50
				scene.addObject('EvadeR', obj)
				scene.addObject('EvadeL', obj)
				obj['trailTime'] = 0
				obj['trail'] = False
				if self.type == 'kamikaze':
					obj['following'] = False
	
		Init()
			
		evadeR = scene.objects['EvadeR']
		evadeL = scene.objects['EvadeL']
		obj['evadeTimer'] += 1
		
		if self.type == 'kamikaze' and obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0] != None:
			obj['following'] = True
		
		if obj['trail'] == True and obj['trailTime'] > 2:
			scene.addObject('Trail', obj, 1000)
			obj['trailTime'] = 0
		
		if self.type != 'artillery': #Lines 138 to 195 deal with pathing, follow and evade behaviours.
			obj['trail'] = False
			obj['trailTime'] += 1
			for i in range (0,361,30):
				i *= (math.pi/180)	
				
				#Evading to the left
				if self.type == 'regular' and messageL.positive and obj['evadeTimer']:
					if 'Rocket' in scene.objects:
						evadeR.worldPosition = obj.worldPosition + Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
						evadeL.worldPosition = obj.worldPosition - Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
						steering.behavior = 2
						steering.distance = 1000
						cont.activate(steering)
						steering.target = scene.objects['EvadeR']
						obj['evadeTimer'] = 0
						
				#Evading to the right
				elif self.type == 'regular' and messageR.positive and obj['evadeTimer']:
					if 'Rocket' in scene.objects:
						evadeR.worldPosition = obj.worldPosition + Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
						evadeL.worldPosition = obj.worldPosition - Scalar(scene.objects['Rocket'].orientation[0], mathutils.Vector((-1,1,1)))*3
						steering.behavior = 2
						steering.distance = 1000
						cont.activate(steering)
						steering.target = scene.objects['EvadeL']
						obj['evadeTimer'] = 0
						
				#Following Player
				elif self.type == 'regular' and obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0] == None and obj['evadeTimer'] >= 50:
					steering.behavior = 3
					steering.distance = 1
					steering.target = scene.objects['Tank']
					cont.activate(steering)
					
				#Keeping distance from obstacles
				elif obj.rayCast(obj.worldPosition + mathutils.Vector((2.5*math.sin(i),2.5*math.cos(i),0)), obj, 2.5, "", 0, 0, 0)[0] != None and obj['evadeTimer'] >= 50:
					evadeObject = scene.addObject('Evade', obj, 50)
					evadeObject.worldPosition = obj.rayCast(obj.worldPosition + mathutils.Vector((2.5*math.sin(i),2.5*math.cos(i),0)), obj, 2.5, "", 0, 0, 0)[1]
					steering.behavior = 2
					steering.distance = 1000
					cont.activate(steering)
					steering.target = scene.objects['Evade']

				#kamikaze type enemy following player
				elif self.type == 'kamikaze' and obj['following'] == True:
					steering.behavior = 3
					steering.distance = 0
					steering.target = scene.objects['Tank']
					cont.activate(steering)
					
				else:
					obj['trail'] = False
					cont.deactivate(steering)
					
	def Health(self): #Controls the death of enemies
	
		cont = logic.getCurrentController()
		obj = cont.owner
		dict = logic.globalDict
		level = dict['level']
		scene = logic.getCurrentScene()
		enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		hit = cont.sensors['Message2']
		if self.type == 'kamikaze':
			col = cont.sensors['Collision']
			if col.positive:
				self.hp -= 10
				enemy = col.hitObject
				if 'enemy' in enemy:
					logic.sendMessage('hit', 'None', str(enemy))
				if 'hp' in enemy:
					enemy['hp'] -= 10
		if hit.positive:
			self.hp -= 10
		if self.hp < 1:
			if dict['level'] != 0:
				dict['levelScore'] += 100
				dict['tank_kills'] += 1
				scene.addObject('Plus_100', obj, 40)
				scene.objects['Plus_100'].alignAxisToVect([1.0,0,0],0,1.0)
			scene.addObject('Explosion',obj)
			scene.objects['EnemyGun%s%s' % (level, enemyID)].endObject()
			scene.objects['CamMain']['enemies'] -= 1
			logic.sendMessage('explosion', 'None')
			obj.endObject()
			
	def Gun(self): #Controls gun position
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		obj.worldPosition = obj['parent'].worldPosition
		if self.type == 'miner':
			obj.orientation = obj['parent'].orientation
	
	def Aim(self): #Controls gun rotation. Is programmed to take into account the player's speed and direction for more accurate shots.
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		if self.type == 'miner':
			pass
		else:
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
			
			if self.type == 'artillery': #Artillery type enemies do not take into account Player's speed and direction.
				obj['vectNum'] = 10
				enemy = obj
				if 'Tank' in scene.objects:
					tarLoc= scene.objects['Tank'].worldPosition
				endVert = (tarLoc[0] - enemy.worldPosition[0], tarLoc[1] - enemy.worldPosition[1], tarLoc[2] - enemy.worldPosition[2])
				vertX = Scalar(endVert, mathutils.Vector((1/obj['vectNum'],1/obj['vectNum'],1/obj['vectNum'])))
				vertZ = -1*(1**2) + 1*obj['vectNum']
				vect = mathutils.Vector((vertX[0], vertX[1], vertZ))
				obj.alignAxisToVect(vect, 1, 1)
		
	def RocketInit(self): #Function controlling instantiation of rockets. Run by the RocketInit object in Blender.
		cont = logic.getCurrentController()
		obj = cont.owner
		scene = logic.getCurrentScene()
		dict = logic.globalDict
		level = dict['level']
		enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
		parent = scene.objects['Enemy%s%s' % (level, enemyID)]
		
		if self.type == 'regular':
			obj.worldPosition.z = 1
		elif self.type == 'miner':
			obj.worldPosition.z = .45
		
		def Init():
			if not 'init' in obj:
				obj['init'] = 1
				obj['shottimer'] = 0
				if self.type == 'artillery':
					obj['shottimer'] = random.randint(1, self.shot_cd)
				obj['total'] = 0
		Init()
		
		obj['shottimer'] += 1.0
		
		if self.type == 'regular':
			if obj.rayCast('Tank', obj, 0, 'player', 0, 0)[0] != None:
				if obj['shottimer'] >= self.shot_cd:
					obj['shottimer'] = 0.0
					rocket = scene.addObject('EnemyRocket',obj)
					rocket['speed'] = 0.25
					rocket['type'] = 'player'
		
		elif self.type == 'artillery':
			if 'Tank' in scene.objects and obj['shottimer'] >= self.shot_cd and obj.getDistanceTo(scene.objects['Tank']) < 35:
				obj['shottimer'] = 0.0
				rocket = scene.addObject('ArtilleryRocket',obj)
				rocket['speed'] = 0.25
				rocket['type'] = 'player'
				rocket['id'] = enemyID

				
#The level functions control what enemies are present in each level and their behaviours.
#For example, Level0, the "Controls" level at the start of the game has a regular enemy that does not attack.
				
def Level0(): 

	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	if not 'Evade' in scene.objects:
		scene.addObject('Evade', obj)
	if 'level' in dict:
		level = dict['level']
	
	if 'level' in dict:
		enemy = EnemyTemp(10, 120, 'regular')
		if 'enemy' in obj:
			if not 'init' in obj:
				obj['init'] = 1
				scene.objects['CamMain']['enemies'] += 1.0
			if 'Tank' in scene.objects:
				enemy.Pathing()
			enemy.Health()	
		elif 'gun' in obj:
			enemy.Gun()
			if 'Tank' in scene.objects:
				enemy.Aim()
		
def Level1():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	if not 'Evade' in scene.objects:
		scene.addObject('Evade', obj)
	if 'level' in dict:
		level = dict['level']
	
	if 'level' in dict:
		enemy = EnemyTemp(10, 120, 'regular')
		if 'enemy' in obj:
			if not 'init' in obj:
				obj['init'] = 1
				scene.objects['CamMain']['enemies'] += 1.0
			if 'Tank' in scene.objects:
				enemy.Pathing()
			enemy.Health()	
		elif 'gun' in obj:
			enemy.Gun()
			if 'Tank' in scene.objects:
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
		enemy = EnemyTemp(10, 120, 'regular')
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
		enemy = EnemyTemp(10, 120, 'regular')
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
			
def Level4():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level = dict['level']
	scene = logic.getCurrentScene()
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	
	if 'level' in dict:
		regular = EnemyTemp(10, 120, 'regular')
		miner = EnemyTemp(10, 120, 'miner')
		artillery = EnemyTemp(10,120, 'artillery')
		if obj['type'] == 'regular':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if 'Tank' in scene.objects:
					regular.Pathing()
				regular.Health()	
			elif 'gun' in obj:
				regular.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Aim()
			else:
				regular.RocketInit()
		elif obj['type'] == 'miner':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					miner.Pathing()
				miner.Health()	
			elif 'gun' in obj:
				miner.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					miner.Aim()
			else:
				miner.RocketInit()
		elif obj['type'] == 'artillery':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if 'Tank' in scene.objects:
					artillery.Pathing()
				artillery.Health()	
			elif 'gun' in obj:
				artillery.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Aim()
			else:
				artillery.RocketInit()
				
def Level5():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level = dict['level']
	scene = logic.getCurrentScene()
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	
	if 'level' in dict:
		regular = EnemyTemp(10, 120, 'regular')
		kamikaze = EnemyTemp(10, 520, 'kamikaze')
		artillery = EnemyTemp(10,120, 'artillery')
		if obj['type'] == 'regular':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Pathing()
				regular.Health()	
			elif 'gun' in obj:
				regular.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Aim()
			else:
				regular.RocketInit()
		elif obj['type'] == 'kamikaze':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if 'Tank' in scene.objects:
					kamikaze.Pathing()
				kamikaze.Health()	
			elif 'gun' in obj:
				kamikaze.Gun()	
		elif obj['type'] == 'artillery':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Pathing()
				artillery.Health()	
			elif 'gun' in obj:
				artillery.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Aim()
			else:
				artillery.RocketInit()

def Level6():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level = dict['level']
	scene = logic.getCurrentScene()
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	
	if 'level' in dict:
		regular = EnemyTemp(10, 120, 'regular')
		kamikaze = EnemyTemp(10, 520, 'kamikaze')
		artillery = EnemyTemp(10,120, 'artillery')
		if obj['type'] == 'regular':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Pathing()
				regular.Health()	
			elif 'gun' in obj:
				regular.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Aim()
			else:
				regular.RocketInit()
		elif obj['type'] == 'kamikaze':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if 'Tank' in scene.objects:
					kamikaze.Pathing()
				kamikaze.Health()	
			elif 'gun' in obj:
				kamikaze.Gun()	
		elif obj['type'] == 'artillery':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Pathing()
				artillery.Health()	
			elif 'gun' in obj:
				artillery.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Aim()
			else:
				artillery.RocketInit()

def Level7():
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level = dict['level']
	scene = logic.getCurrentScene()
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	
	if 'level' in dict:
		regular = EnemyTemp(10, 120, 'regular')
		kamikaze = EnemyTemp(10, 520, 'kamikaze')
		artillery = EnemyTemp(10,120, 'artillery')
		if obj['type'] == 'regular':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Pathing()
				regular.Health()	
			elif 'gun' in obj:
				regular.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					regular.Aim()
			else:
				regular.RocketInit()
		elif obj['type'] == 'kamikaze':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if 'Tank' in scene.objects:
					kamikaze.Pathing()
				kamikaze.Health()	
			elif 'gun' in obj:
				kamikaze.Gun()	
		elif obj['type'] == 'artillery':
			if 'enemy' in obj:
				if not 'init' in obj:
					obj['init'] = 1
					scene.objects['CamMain']['enemies'] += 1.0
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Pathing()
				artillery.Health()	
			elif 'gun' in obj:
				artillery.Gun()
				if not 'Tank' in scene.objects:
					pass
				else:
					artillery.Aim()
			else:
				artillery.RocketInit()
				
def Rocket(): #Function controlling general rocket behaviour and death.
	
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
			obj['hp'] = 1
	
	def Update():
		
		scene.addObject('EffectRocket1',obj)
		scene.addObject('EffectRocket2',obj)
		
		motion.useLocalDLoc = True
		motion.useLocalDRot = True
		motion.dLoc = [0.0, obj['speed'] ,0.0]
		obj.applyForce([0.0, 0.0, 9.82], 0)
		cont.activate(motion)
		
		obj['time'] += 1
		if obj['time'] > 2:
			if collision.positive:
				enemy = collision.hitObject
				if 'enemy' in enemy:
					logic.sendMessage('hit', 'None', str(enemy))
				if 'hp' in enemy:
					enemy['hp'] -= 10
				obj.endObject()
				explosion = scene.addObject('Explosion',obj)
				logic.sendMessage('rocket_explosion', 'None')
		
		if obj['hp'] < 1:
			obj.endObject()
			explosion = scene.addObject('Explosion',obj)
			logic.sendMessage('rocket_explosion', 'None')
		
	Init()
	Update()

def ArtilleryRocket(): #This function controls rocket behaviour and death for Artillery rockets, as well as their trajectory and shadow.
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level= dict['level']
	if 'Enemy%s%s' % (level,obj['id']) in scene.objects:
		enemy = scene.objects['EnemyRocketInit%s%s' % (level,obj['id'])]
	if 'Tank' in scene.objects:
		tarLoc = copy.copy(scene.objects['Tank'].worldPosition)
	motion = cont.actuators['Motion']
	collision = cont.sensors['Collision']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['shadowInit'] = False
			if not 'speed' in obj:
				obj['speed'] = 0.0
			if not 'dir' in obj:
				obj['dir'] = 0.0
			obj['time'] = 0.0
			obj['vectTime'] = 11
			obj['rocket'] = True
			obj['hp'] = 1
			obj['vect'] = 0
			obj['vectNum'] = 10
			obj['rocketInitLoc'] = copy.copy(scene.objects['EnemyRocketInit%s%s' % (level,obj['id'])].worldPosition)
			vertList = []
			for i in range(0,obj['vectNum'] + 1):
				endVert = (tarLoc[0] - enemy.worldPosition[0], tarLoc[1] - enemy.worldPosition[1], tarLoc[2] - enemy.worldPosition[2])
				vertX = Scalar(endVert, mathutils.Vector((i/obj['vectNum'],i/obj['vectNum'],i/obj['vectNum'])))
				vertZ = -1*(i**2) + i*obj['vectNum']
				vertX[2] = vertZ
				vert = (enemy.worldPosition[0] + vertX[0], enemy.worldPosition[1] + vertX[1],enemy.worldPosition[2] +vertZ)
				vertList.append(vert)
			obj['vertList'] = copy.copy(vertList)
			obj['shadow'] = scene.addObject('Shadow', scene.objects['Tank'])
			obj['shadow'].setVisible(False)
	def Update():
		
		rocketDist = .05 + Dist((obj.worldPosition[0], obj.worldPosition[1], 0.0), (obj['rocketInitLoc'][0], obj['rocketInitLoc'][1], 0.0))
		enemyDist = Dist((obj['rocketInitLoc'][0], obj['rocketInitLoc'][1], 0.0), (obj['vertList'][obj['vect']][0], obj['vertList'][obj['vect']][1], 0.0))
		if obj['vect'] <= (obj['vectNum'] - 1) and rocketDist >= enemyDist:
			obj.alignAxisToVect(mathutils.Vector((obj['vertList'][obj['vect'] + 1][0] - obj['vertList'][obj['vect']][0], obj['vertList'][obj['vect'] + 1][1] - obj['vertList'][obj['vect']][1], obj['vertList'][obj['vect'] + 1][2] - obj['vertList'][obj['vect']][2])), 1, 1.0)
			verticalDist = (Dist((0.0, 0.0, obj['vertList'][obj['vect']][2]), (0.0, 0.0, obj['vertList'][obj['vect']+1][2])))
			obj['speed'] = (obj['vertList'][int(obj['vectNum']/2)][2] - obj.worldPosition[2])/25 + verticalDist/20 + .1
			obj['vect'] += 1
		if rocketDist > 0.7*(Dist(obj['rocketInitLoc'], obj['vertList'][len(obj['vertList'])-1])) and obj['shadowInit'] == False:
			obj['shadow'].setVisible(True)
			obj['shadow'].worldScale = [(1-(obj.worldPosition[2]/27.5)), (1-(obj.worldPosition[2]/27.5)), 1]
		
		scene.addObject('EffectRocket1',obj)
		scene.addObject('EffectRocket2',obj)
		
		motion.useLocalDLoc = True
		motion.useLocalDRot = True
		motion.dLoc = [0.0, obj['speed'] ,0.0]
		obj.applyForce([0.0, 0.0, 9.82], 0)
		cont.activate(motion)
		
		obj['time'] += 1
		if obj['time'] > 2:
			if obj.worldPosition[2] < 1:
				obj['hp'] -= 10
			if collision.positive:
				enemy = collision.hitObject
				if 'enemy' in enemy:
					logic.sendMessage('hit', 'None', str(enemy))
				if 'hp' in enemy:
					enemy['hp'] -= 10
				obj.endObject()
				scene.objects['Shadow'].endObject()
				explosion = scene.addObject('Explosion',obj)
				logic.sendMessage('rocket_explosion', 'None')
		
		if obj['hp'] < 1:
			obj.endObject()
			scene.objects['Shadow'].endObject()
			explosion = scene.addObject('Explosion',obj)
			logic.sendMessage('rocket_explosion', 'None')
		
	Init()
	Update()
	
def Mine(): #Mines were removed from the game, but I figured I would leave this in here as inspiration if I ever decide to bring them back.
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	level = dict['level']
	enemyID = str(obj)[len(str(obj))-4:len(str(obj))]
	collision = cont.sensors['Collision']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['rocket'] = True
			obj['dist'] = 6
			obj['dist_evade'] = 1.5
			obj['time'] = 0

	def Update():
		for i in range (0,361,10):
				i *= (math.pi/180)
				#detects if the enemy is far enough away to be allowed to lay another mine
				ray = obj.rayCast(obj.worldPosition + mathutils.Vector((obj['dist']*math.sin(i),obj['dist']*math.cos(i),0)), obj, obj['dist'], "miner", 0, 0, 0)
				if ray[0] != None:
					logic.sendMessage('mine_near','',str('EnemyRocketInit%s%s' % (level, str(ray[0])[len(str(ray[0]))-4:len(str(ray[0]))])))
		if collision.positive and obj['time'] > 10:
			enemy = collision.hitObject
			scene.addObject('Explosion',enemy)
			if 'enemy' in enemy:
				logic.sendMessage('hit', 'None', str(enemy))
			if 'hp' in enemy:
				enemy['hp'] -= 10
			obj.endObject()
			obj.parent.endObject()
			explosion = scene.addObject('Explosion',obj)
			logic.sendMessage('rocket_explosion', 'None')
		obj['time'] += 1
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