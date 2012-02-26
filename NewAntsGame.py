#dfining a new ants game

import threading, time

from Tkinter import *

from math import radians

from vec import *

import random


random.seed(5554500)

#things to do:
#	add the attack defence
#	add the colors for the ants
#	add the trails


def intersect_circle(obj1, obj2):
	#the function takes two objects that has defined a position and a size
	#return true if obj1 is inside the obj2
	d = obj1.position.distance(obj2.position)
	if d < obj2.size: return True
	else: return False

def intersect_p_r(self, p1, p2, r):
	d = p1.distance(p2)
	if d < r: return True
	else: return False

class TimerClass(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.event = threading.Event()
		self.eventClass = None
	
	def run(self):
		while not self.event.is_set():
			self.eventClass.action()
			self.event.wait(0.1)
	
	def stop(self):
		print "timer stopped"
		self.event.set()
		
#le formiche devono lasciare una traccia
#la traccia deve avere un intensita
#le formiche devono avere uno stato e una funzione goto


		

class States:
	def __init__(self):
		self.search = 1
		self.harvest = 2
		self.bring_food_nest = 3
		self.attack = 4
		self.goto_food = 5
		self.discharge = 6
	
	def get_moving_states(self):
		return [self.search, self.bring_food_nest, self.goto_food]
	
	def get_static_states(self):
		return [self.harvest, self.attack, self.discharge]


ant_state = States()

class Trail:
	def __init__(self):
		self.position = V2(0,0)
		self.name = "trail"
		self.size = 1
		self.last_move = time.time()
		self.color = "black"
		self.intensity = 5
		self.state = ant_state.search
	

class Ant:
	def __init__(self, pos = V2(0,0)):
		self.name = "ant"
		self.attack = 10
		self.defense = 20
		self.position = pos
		self.direction = V2(1,0)
		self.speed = 5
		self.size = 3
		self.cost = 100
		self.move_time = 0.5 #second
		self.last_move = time.time()
		self.sight_r = 50
		self.state = ant_state.search
		self.harvest_rate = 0.1 #in ten seconds take 1
		self.reservoir = 0
		self.reservoir_limit = 50
		self.color = "yellow"
		self.player = None
		self.nest = None
	
	def reservoir_full(self):
		return self.reservoir >= self.reservoir_limit
		
	def is_reservoir_empty(self):
		return self.reservoir == 0
	
	def harvest(self,food):
		if not self.reservoir_full():
			if (time.time() - self.last_move) > self.harvest_rate:
				self.reservoir += 1
				food.resources -= 1
				self.last_move = time.time()
		else:
			self.state = ant_state.bring_food_nest
	
	def look(self, objects):
		object_list = []
		for obj in objects:
			if id(self) == id(obj):
				continue
			if self.position.distance(obj.position) < self.sight_r:
				object_list.append(obj)
		return object_list
	
	def make_move(self, objects):
		objs_seen = self.look(objects)
		
		index = 0
		for i, obj in enumerate(objs_seen):
			if intersect_circle(self,obj):
				if obj.name == "ant":
					self.state = ant_state.search
					break
				elif obj.name == "food" and not (self.state == ant_state.bring_food_nest):
					if obj.resources > 0:
						self.state = ant_state.harvest
						index = i
					else:
						self.state = ant_state.search
					break
				elif obj.name == "nest" and not (self.is_reservoir_empty()):
					self.state = ant_state.discharge
					break
				elif obj.name == "nest" and self.is_reservoir_empty():
					self.state = ant_state.search
			else:
				if obj.name == "food" and self.is_reservoir_empty():
					self.state = ant_state.goto_food
				elif not self.is_reservoir_empty():
					self.state = ant_state.bring_food_nest
				else:
					self.sate = ant_state.search
					

		if self.state == ant_state.goto_food:
			#print "I'm going toward the food"
			self.go_to_food(objs_seen[index])
		elif self.state == ant_state.harvest:
			#print "I'm harvesting..."
			if len(objs_seen) > 0 and objs_seen[index].name == "food":
				self.harvest(objs_seen[index])
			else:
				self.move_random()
		elif self.state == ant_state.bring_food_nest:
			#print "I'm going to the nest"
			self.go_to(self.nest.position)
		elif self.state == ant_state.search:
			original_pos = self.position
			self.move_random()
			counter = 0
			if len(objs_seen) > 0:
				while intersect_circle(self,objs_seen[index]):
					if counter > 10:
						self.position += V2(5,0)
					else:
						self.position = original_pos
						self.move_random()
					counter += 1
			
		elif self.state == ant_state.discharge:
			#print "I'm discharging"
			self.nest.resources += self.reservoir
			self.reservoir = 0
			self.state = ant_state.search
			
		else:
			self.move_random()

						
	def go_to_food(self,food):
		self.go_to(food.position)
	
	def rotate_dir(self,alpha):
		radalpha = radians(alpha)
		self.direction.rotate(radalpha)
	
	def move_dir(self):
		self.position += self.direction*self.speed
	
	def move_random(self):
		if (time.time() - self.last_move) > self.move_time:
			randdir = random.randrange(0,360)
			self.rotate_dir(randdir)
			self.position += self.direction*self.speed
	
	def go_to(self, v2):
		v2traspose = v2-self.position
		v2traspose.normalize()
		v2polar = v2traspose.convert_in_polar()
		dirpolar = self.direction.convert_in_polar()
		dirpolar.c[1] = v2polar.y()
		self.direction = dirpolar.convert_in_cartesian()
		self.move_dir()

class Nest:
	def __init__(self):
		self.name = "nest"
		self.position = V2(random.randrange(0,500),random.randrange(0,500))
		self.player = None
		self.size = 10
		self.ants = []
		self.resources = 1000
		self.spawn_time = 3 #seconds
		self.last_spawn = time.time() #seconds
		self.spawning_point = self.position+V2(50,0)
	
	def set_position(self,newcenter):
		self.position = newcenter
		self.spawning_point = newcenter+V2(50,0)
	
	def spawn_ant(self):
		if (time.time() - self.last_spawn) > self.spawn_time:
			spawned_ant = Ant((self.spawning_point))
			spawned_ant.nest = self
			spawned_ant.player = self.player
			self.ants.append(spawned_ant)
			self.resources -= spawned_ant.cost
			self.last_spawn = time.time()
	
	
class BBox:
	def __init__(self):
		self.position = V2(250,250)
		self.size = 250

class Player:
	def __init__(self, name):
		self.name = name
		self.color = "green"
		self.nest = Nest()
		self.nest.player = self


#Food should have a position, an ammount, size

class Food:
	def __init__(self):
		self.name = "food"
		self.position = V2()
		self.size = 6
		self.resources = 150

class GameEngine:
	def __init__(self):
		self.Players = [Player("Eric"), Player("Giovanni"), Player("Erug")]
		self.Players[1].color = "red"
		self.Players[2].color = "cyan"
		
		
		self.bbox = BBox()
		for player in self.Players:
			while not intersect_circle(player.nest,self.bbox):
				player.nest.set_position(V2(random.randrange(0,500),random.randrange(0,500)))

		self.food_n = 10
		self.food_list = [self.spawn_food() for n in range(self.food_n)]
		
		self.obj_list = []
	
	def spawn_food(self):
		food = Food()
		while not intersect_circle(food,self.bbox):
			food.position = V2(random.randrange(0,500),random.randrange(0,500))
		return food
		
	def check_food(self):
		for food in self.food_list:
			if food.resources <= 0:
				print "food exhausted: ", id(food)
				self.food_list.remove(food)
				self.food_list.append(self.spawn_food())
		self.update_obj_list()
		
	def update_obj_list(self):
		self.obj_list = []
		for player in self.Players:
			self.obj_list.append(player.nest)
			for ant in player.nest.ants:
				self.obj_list.append(ant)
		for food in self.food_list:
			self.obj_list.append(food)
		
	
	def action(self):		
		#player dependent action
		self.check_food()
		self.update_obj_list()
		for player in self.Players:
			print "Player name:", player.name, player.color
			
			#state dependent action

			if player.nest.resources >= Ant().cost:
				player.nest.spawn_ant()

			#time dependent actions
			for ant in player.nest.ants:
				#if ant in the bounding box
				original_pos = ant.position
				ant.make_move(self.obj_list)
							
				if not intersect_circle(ant, self.bbox):
					ant.position = original_pos
					#print "I'm outside the bounding sphere" #ant.position = original_pos
						
		

class GameCanvas:
	def __init__(self, parent_frame):
		self.frame = Frame(parent_frame)
		
		self.canvasH = 500
		self.canvas = Canvas(self.frame, height = self.canvasH, width = 500)
		self.canvas.pack()
		
		self.gEngine = GameEngine()
		
		self.frameCounter = 0

	def transform_coords(self,point):
		x1 = point.c[0]
		y1 = self.canvasH-point.c[1]
		return V2(x1,y1)
	
	def create_line(self,v1,v2, color):
		v1 = self.transform_coords(v1)
		v2 = self.transform_coords(v2)
		
		self.canvas.create_line(v1.x(),v1.y(),v2.x(),v2.y(), fill = color)
	
	def create_rectangle(self,center, size, color):
		x1 = center.x() - size
		y1 = self.canvasH - center.y() - size
		x2 = center.x() + size
		y2 = self.canvasH - center.y() + size
		self.canvas.create_rectangle(x1,y1,x2,y2, fill = color)
	
	def action(self):
		#frame dependent actions
		self.canvas.delete(ALL)
		
		self.gEngine.action()
		
		for food in self.gEngine.food_list:
			self.create_rectangle(food.position, food.size, "blue")
		for player in self.gEngine.Players:
			#draw nest
			print player.nest.resources, "ants: ", len(player.nest.ants)
			self.create_rectangle(player.nest.position, player.nest.size, player.color)
			#draw ants
			for ant in player.nest.ants:
				self.create_rectangle(ant.position, ant.size, player.color)
					
			
			
tmr = TimerClass()


root = Tk()

gCanv = GameCanvas(root)
gCanv.frame.pack()


tmr.eventClass = gCanv
tmr.start()


root.mainloop()

tmr.stop()