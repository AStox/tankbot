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
from bge import render
import mathutils
import time
import random
	
def Game(): #The main Game function is run from the camera object and controls camera movement, level switching, countdowns, gameovers, etc...
	
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
			dict['newLevel'] = 0
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
			if obj['time'] > 45:	#delay between when the last tank is killed and the 'gameover' menu appears
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
		dict['newLevel'] += 1
		
	Init()
	Update()
	if not 'Tank' in scene.objects:
		pass
	else:
		Camera()
	if not 'Gameover' in scenes:
		Next()
	if not 'Next' in scenes:
		Gameover()
	if dict['newLevel'] == 0:
		Countdown()
	
def CountdownAction(): #A function to pause the game when countdown is happening and resume when it's over.
	
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
#These level functions are mainly for debugging purposes, giving default values to to score and stuff so the game doesn't throw up errors if I start the game at level 3 instead of at the start.
#They also keep track of the  current level for the rest of the code. These are run by the ground objects of each level.
	
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
			if not 'levelscore' in dict:
				dict['levelScore'] = 0
			if not 'levelClock' in dict:
				dict['levelClock']= 0
			if not 'tank_kills' in dict:
				dict['tank_kills'] = 0
			if not 'rocket_kills' in dict:
				dict['rocket_kills'] = 0
			dict['breakable'] = False
	
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
			dict['breakable'] = False
	
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
			dict['breakable'] = False
			
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
			dict['breakable'] = False
	
	def Update():
		pass
	
	Init()
	Update()	

def Level4():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 4
			if not 'Score' in scenes:
				logic.addScene('Score')
			if not 'score' in dict:
				dict['score'] = 0
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
			scene.objects['CamMain']['enemies'] = 1
	
	def Update():
		pass
	
	Init()
	Update()		

def Level5():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 5
			if not 'Score' in scenes:
				logic.addScene('Score')
			if not 'score' in dict:
				dict['score'] = 0
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
			scene.objects['CamMain']['enemies'] = 1
			dict['breakable'] = False
	
	def Update():
		pass
	
	Init()
	Update()	

def Level6():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 6
			if not 'Score' in scenes:
				logic.addScene('Score')
			if not 'score' in dict:
				dict['score'] = 0
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
			scene.objects['CamMain']['enemies'] = 1
			dict['breakable'] = False
	
	def Update():
		pass
	
	Init()
	Update()		

def Level7():
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	scenes = logic.getSceneList()
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			dict['level'] = 7
			if not 'Score' in scenes:
				logic.addScene('Score')
			if not 'score' in dict:
				dict['score'] = 0
			dict['levelScore'] = 0
			dict['levelClock']= 0
			dict['tank_kills'] = 0
			dict['rocket_kills'] = 0
			scene.objects['CamMain']['enemies'] = 1
			dict['breakable'] = False
	
	def Update():
		pass
	
	Init()
	Update()		
	
def Explosion(): #This function controls the explosion animation and makes sure it's destroyed when the animation is over.
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	tank_explosion = cont.sensors['Message1']
	rocket_explosion = cont.sensors['Message2']
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['time'] = 0.0
	
	def Update():
		if obj['time'] > 37.0:
			obj.endObject()
		obj['time'] += 1.0
		if tank_explosion.positive:
			cont.activate(cont.actuators['Tank'])
		if rocket_explosion.positive:
			cont.activate(cont.actuators['Rocket'])
		
	
	Init()
	Update()
	
def Grid(): #kills any tank that touches the "water".
	
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

def Timer(): #Instantiates the timer in the corner of the screen.
	
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
	
def Level(): #Instantiates the level number in the other corner of the screen.
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			
	def Update():
		scene.addObject('Num_%s' % dict['level'], obj, 1)
	Init()
	Update()

def Breakable(): #Controls breakable blocks
	
	cont = logic.getCurrentController()
	obj = cont.owner
	scene = logic.getCurrentScene()
	dict = logic.globalDict
	
	def Init():
		if not 'init' in obj:
			obj['init'] = 1
			obj['hp'] = 10
			dict['breakable'] = False
	
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