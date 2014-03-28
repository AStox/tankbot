tankbot
=======
An attempt to teach myself the python scripting language by making a simple game on the Blender Game Engine. The game is a top down, tank game similar to the tank game featured on Wii Play. The game currently only features a few simple test level.

A .Blend is included in this repository along with all the code I've written so far.

Suggestions and tips are appreciated and can be sent to Adamstox@gmail.com.


Controls:
WASD to move the tank, mouse to aim, left mouse button to fire. Your rockets will bounce off walls once. One hit kills.

About the Code:
(NOTE: I'm using Blender 3D's game engine to create this game so many of the functions and syntax used is exclusive to Blender)
Player.py is where all of the logic for the player is stored. Likewise, Enemy.py is where all logic for the enemy tanks is stored. This includes pathfinding, which I've accomplished using navigation meshes and simple follow/flee behaviors. Game.py contains the main logic for the game, or the main game structure. This is where I handle switching levels, game overs, camera motion, etc. The majority of the code here is attached to the camera objects of each scene. Finally, Menu.py is where the button class is kept, along with all of its different button functions. 

About the Game:
I'm learning python as I go so the first bit of code I wrote, the player's code, is more primitive than the latest code (although not by much). I've noticed I tend to rely on if/then statments for almost everything and I'm afraid this might limit myself or the game in the future. I've turned all of the code for the menu buttons in the game into one "Button" class with different functions for each button. It might not have been to most practical use of classes I could have done for this project, but it did teach me about them, which is the ultimate goal. As I add different enemy tanks, I plan to create an 'Enemy' class to easily create and customize new enemies.
