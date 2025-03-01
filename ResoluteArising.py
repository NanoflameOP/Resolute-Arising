####################
# Resolute Arising #
####################
# Bugs:
# Enemies clipping with border
# Boss3 ability enemy spawns screen scaling (goes back to original 51x51 sprite when screen size changed)
#########################################################################################################


# Imports
import pygame as pg
from pygame.locals import *
from pygame import mixer
import sys
import math
import time
import random
import os
import copy


# Initialise display - we'll work the code from a 800x450 window that scales size and coords appropriately
pg.init()
global initial_display
global current_display
initial_display = (800, 450)
current_display = initial_display
screen = pg.display.set_mode(initial_display, HWSURFACE | DOUBLEBUF | RESIZABLE)
current_display = pg.display.get_surface().get_size()   # keeps a record of screen size whenever we change it
pg.display.set_caption("Resolute Arising")
pg.display.set_icon(pg.image.load('resolute_arising_icon.png'))
# Set number of mixer channels we want
mixer.set_num_channels(20)


# Set key info
powers = ["energy barrier","minigun","timestop","grenade launcher","energy absorber"]
item_images = {
    "energy barrier" : "energy_barrier_item.png",
    "minigun" : "minigun_item.png",
    "timestop" : "timestop_item.png",
    "grenade launcher" : "grenade_launcher_item.png",
    "energy absorber" : "energy_absorber_item.png"
    }
enemy_types = ["classic","ninja","pirate","boss1","boss2","boss3","boss4","final_boss"]
# Specify enemy types and stats for each endless mode
# Key: [rate of being picked, enemy parameters(given as ranges)]
# Enemy parameters we define here: health,item,speed,time_until_spawn,movement_type,item_rate,ability_rate,sensor_radius,fawn_timer
endless_fight_enemies = {
        "classic" : [12,[2,10],[None],[2,3],[1,2],["random","to_player"],[10,30],[0,0],[100,100],[0,0]],
        "classic" : [8,[2,10],["minigun","grenade launcher"],[2,3],[1,2],["random","to_player"],[10,30],[0,0],[100,100],[0,0]],
        "ninja" : [5,[5,15],["energy barrier","energy absorber"],[4,6],[1,2],["random"],[0,20],[0,0],[100,100],[0,0]],
        "ninja" : [4,[5,15],["energy barrier","energy absorber"],[3,4],[1,2],["to_player"],[0,20],[0,0],[100,100],[0,0]],
        "pirate" : [3,[10,20],[None,"minigun"],[3,5],[1,2],["away_player","to_player"],[10,20],[0,0],[100,100],[0,0]],
        "boss1" : [2,[50,100],[None],[3,4],[1,2],["random"],[10,30],[300,450],[100,100],[0,0]]
    }
endless_flight_enemies = {
        "classic" : [12,[2,10],[None],[3,6],[1,2],["random","to_player","predictable"],[10,30],[0,0],[100,100],[0,0]],
        "ninja" : [4,[5,15],["timestop"],[4,7],[1,2],["random"],[0,20],[0,0],[100,100],[0,0]],
        "boss2" : [2,[30,75],[None],[3,6],[1,2],["to_player"],[10,30],[100,150],[100,100],[0,0]]
    }
endless_freeze_enemies = {
        "classic" : [12,[2,10],[None],[4,6],[1,2],["random","predictable"],[40,60],[0,0],[50,150],[0,0]],
        "ninja" : [4,[5,15],[None,"minigun"],[5,8],[1,2],["random"],[40,60],[0,0],[50,150],[0,0]],
        "boss3" : [2,[50,75],[None],[4,5],[1,2],["predictable"],[40,60],[350,450],[100,150],[0,0]]
    }
endless_fawn_enemies = {
        "classic" : [12,[2,10],[None],[2,4],[1,2],["random","to_player"],[10,30],[0,0],[100,100],[200,800]],
        "classic" : [3,[2,10],["minigun"],[2,5],[1,2],["predictable"],[40,60],[0,0],[100,100],[200,800]],
        "ninja" : [5,[5,15],["energy barrier"],[3,6],[1,2],["random"],[0,20],[0,0],[100,100],[200,800]],
        "boss4" : [2,[30,50],[None],[3,6],[1,2],["random"],[0,20],[50,100],[100,100],[800,1600]]
    }
# Specify availible items for each endless mode as well as rates at which they spawn (stats are defined elsewhere)
endless_fight_items = {
        "minigun" : 4,
        "grenade launcher" : 2,
        "energy barrier" : 3,
        "energy absorber" : 1
    }
endless_flight_items = {
        "energy barrier" : 2,
        "timestop" : 6
    }
endless_freeze_items = {
        "timestop" : 6,
        "energy barrier" : 1
    }
endless_fawn_items = {
        "timestop" : 1
    }
global current_level_unlock
global music_on
global sfx_on
global endless_fight_high_score
global endless_flight_high_score
global endless_freeze_high_score
global endless_fawn_high_score
global current_music
current_music = None
# Open save file to set following variables
# These are the default values for no save file
current_level_unlock = 1
music_on = True
sfx_on = True
endless_fight_high_score = 0
endless_flight_high_score = 0
endless_freeze_high_score = 0
endless_fawn_high_score = 0
# Access and read save file here
# (values read line by line and copies whatever is written after a space)
try:
    with open("save_file.txt") as f:
        all_data = []
        for line in f:
            data = ""
            add = False
            for character in line:
                if character == " ":
                    add = True
                elif add == True:
                    data += character
            all_data.append(data[:-1])
        # Now overwrite default values with our saved ones
        try:
            current_level_unlock = int(all_data[0])
            music_on = bool(int(all_data[1]))
            sfx_on = bool(int(all_data[2]))
            endless_fight_high_score = int(all_data[3])
            endless_flight_high_score = int(all_data[4])
            endless_freeze_high_score = int(all_data[5])
            endless_fawn_high_score = int(all_data[6])
        except ValueError:
            print("Save file not formatted correctly")
    f.close()
except FileNotFoundError:
    print("Save file not found")
    

# Set dictionary for enemy icons
# Each enemy type can be peaceful, hostile or targeted
enemy_icons = {
    'endless_peaceful' : 'empty.png',
    'endless_hostile' : 'empty.png',
    'endless_targeted' : 'empty.png',
    'classic_peaceful' : 'enemy3.png',
    'classic_hostile' : 'enemy2.png',
    'classic_targeted' : 'enemy1.png',
    'ninja_peaceful' : 'enemy4.png',
    'ninja_hostile' : 'enemy4.png',
    'ninja_targeted' : 'enemy5.png',
    'pirate_peaceful' : 'enemy9.png',
    'pirate_hostile' : 'enemy9.png',
    'pirate_targeted' : 'enemy10.png',
    'boss1_peaceful' : 'boss1.png',
    'boss1_hostile' : 'boss1.png',
    'boss1_targeted' : 'boss1.png',
    'boss2_peaceful' : 'boss2.png',
    'boss2_hostile' : 'boss2.png',
    'boss2_targeted' : 'boss2.png',
    'boss3_peaceful' : 'boss3.png',
    'boss3_hostile' : 'boss3.png',
    'boss3_targeted' : 'boss3_aggro.png',
    'boss4_peaceful' : 'boss4.png',
    'boss4_hostile' : 'boss4.png',
    'boss4_targeted' : 'boss4.png',
    'final_boss_peaceful' : 'final_boss_hurt.png',
    'final_boss_hostile' : 'final_boss.png',
    'final_boss_targeted' : 'final_boss.png'
    }


# Create classes
class player():
    def __init__(self,image,health,item,x,y,speed):
        self.original_image = pg.image.load(image)
        self.image = pg.image.load(image)
        self.original_image_name = image
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use current x/y for timestop and freeze
        self.currentx = self.initialx
        self.currenty = self.initialy
        self.health = health
        self.max_health = copy.copy(health)
        self.item = item
        self.speed = speed
        self.initial_speed = copy.copy(speed)
        self.energy_item = None

    def move_left(self):
        if hitsBorder(self,self.speed,[-1,0]) == False:
            self.selfrect.move_ip(self.speed[0]*-1,0)

    def move_right(self):
        if hitsBorder(self,self.speed,[1,0]) == False:
            self.selfrect.move_ip(self.speed[0]*1,0)

    def move_up(self):
        if hitsBorder(self,self.speed,[0,-1]) == False:
            self.selfrect.move_ip(0,self.speed[1]*-1)

    def move_down(self):
        if hitsBorder(self,self.speed,[0,1]) == False:
            self.selfrect.move_ip(0,self.speed[1]*1)


class enemy():
    def __init__(self,enemy_type,health,item,x,y,speed,direction,time_until_spawn,movement_type,item_rate=0,ability_rate=0,sensor_radius=100,fawn_timer=0):
        self.type = enemy_type
        # movement_type either "to_player", "away_player", "random", "predictable", "", "at_player"
        self.movement_type = movement_type
        # Set image attributes to none and immediately call change_icon()
        self.original_image = None
        self.image = None
        self.original_image_name = None
        self.change_icon()
        self.image = pg.transform.scale(self.original_image, ((current_display[0]/initial_display[0])*self.original_image.get_width(),(current_display[1]/initial_display[1])*self.original_image.get_height()))
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use current x/y for timestop
        self.currentx = self.initialx
        self.currenty = self.initialy
        self.initial_health = health
        self.health = health
        self.item = item
        self.energy_item = None
        self.speed = speed
        self.initial_speed = copy.copy(speed)
        self.direction = direction
        self.commited_direction = False
        self.time_until_spawn = time_until_spawn
        self.item_rate = item_rate
        self.ability_rate = ability_rate
        # Sensor attributes
        self.sensor_obj = None
        self.sensor_radius = sensor_radius
        # Timer for enemy to despawn. We naturally set it to infinity unless told otherwise
        self.timer = math.inf
        # Timer for fawn
        self.fawn_timer = fawn_timer


    def move_to_or_away_player(self,player_object,to_player):
        direction_to_player = [player_object.selfrect.x-self.selfrect.x, player_object.selfrect.y-self.selfrect.y]
        normalise_vector_multiplier = 1
        try:
            normalise_vector_multiplier = 1/math.sqrt((direction_to_player[0]**2)+(direction_to_player[1]**2))
        except ZeroDivisionError:
            pass
        if to_player == False:
            normalise_vector_multiplier *= -1
        direction_to_player[0] *= normalise_vector_multiplier
        direction_to_player[1] *= normalise_vector_multiplier
        # Move randomly if will hit border and moving away from player else apply calculated vector
        if (hitsBorder(self,self.speed,direction_to_player)) and (to_player == False):
            self.move_randomly()
        else:
            self.direction = direction_to_player

            
    def move_randomly(self):
        rand_direction = [math.inf,math.inf]
        # Get random direction until find one that won't hit border
        attempts = 0
        while hitsBorder(self,self.speed,rand_direction):
            x = random.uniform(-1,1)
            y = random.uniform(-1,1)
            normalise_vector_multiplier = 1
            try:
                normalise_vector_multiplier = 1/math.sqrt((x**2)+(y**2))
            except ZeroDivisionError:
                pass
            rand_direction = [x*normalise_vector_multiplier,y*normalise_vector_multiplier]
            # If something goes wrong. i.e. enemy stuck outside border when called, we can use attempts to break out of loop so game does not crash
            attempts+=1
            if attempts > 20:
                rand_direction = [0,0]
                break
        # Move in random direction
        self.direction = rand_direction

    def move_predictable(self):
        # Just rebound off of border by inverting direction
        if (self.selfrect.left <= 0) or (self.selfrect.right >= current_display[0]):
            self.direction[0] *= -1
        elif (self.selfrect.top <= 0) or (self.selfrect.bottom >= current_display[1]):
            self.direction[1] *= -1
        else:
            pass

    def move_at_player(self,player_object):
        # Move to player's initial position when called (not intended to be called by same object more than once)
        if self.commited_direction == False:
            if self.timer > 300:
                # Set max 5 second (60fps) timer on all enemies with this movement to reduce lag
                self.timer = 300
            self.direction = [player_object.selfrect.x-self.selfrect.x, player_object.selfrect.y-self.selfrect.y]
            normalise_vector_multiplier = 1
            try:
                normalise_vector_multiplier = 1/math.sqrt((self.direction[0]**2)+(self.direction[1]**2))
            except ZeroDivisionError:
                pass
            self.direction[0] *= normalise_vector_multiplier
            self.direction[1] *= normalise_vector_multiplier
            self.commited_direction = True
        else:
            # Already been called for this object so pass
            pass

    def change_icon(self):
        # We change the icons for enemies here as appropriate
        # We do this with self.type. We need to re-apply original_image, image and original_image_name as well     
        try:
            new_image = None
            if (self.movement_type == "to_player") or (self.movement_type == "at_player"):
                new_image = enemy_icons[self.type+"_targeted"]
            elif self.movement_type == "away_player":
                new_image = enemy_icons[self.type+"_peaceful"]
            else:
                new_image = enemy_icons[self.type+"_hostile"]
            # Now update attributes
            if self.image != None:
                old_w = self.image.get_width()
                old_h = self.image.get_height()
                self.original_image = pg.image.load(new_image)
                self.original_image_name = new_image
                # Current image needs scaling immediately to same size as previous one
                self.image = pg.transform.scale(self.original_image, (old_w,old_h))
            else:
                # Needed as when instatiated it won't have a previous image to scale to
                self.original_image = pg.image.load(new_image)
                self.original_image_name = new_image
        except ValueError:
            print("Cannot find enemy sprite for", self)

    def ability(self,all_objects,active_objects,mouse,player_object,level,current_time,indicator):  
        # Define abilities for each enemy type
        dice_roll = random.randint(0,int(self.ability_rate))
        if dice_roll == 0:
            # If we use ability, check which one we have
            
            # Endless - Used to spawn infinite enemies
            if self.type == 'endless':
                # Fetch the correct enemy dictionary for the gamemode, item spawn rate, and max enemy count before this enemy stops spawning
                supplied_dict = {}
                item_dict = {}
                max_enemy_count = 0
                # Spawn rate is chance of spawning item each time this ability is called
                item_spawn_rate = 0
                if level == "endless_fight":
                    supplied_dict = endless_fight_enemies
                    item_dict = endless_fight_items
                    max_enemy_count = 3
                    item_spawn_rate = 10
                elif level == "endless_flight":
                    supplied_dict = endless_flight_enemies
                    item_dict = endless_flight_items
                    max_enemy_count = max(3,2+(current_time//30))
                    item_spawn_rate = 20
                elif level == "endless_freeze":
                    supplied_dict = endless_freeze_enemies
                    item_dict = endless_freeze_items
                    max_enemy_count = max(3,2+(current_time//30))
                    item_spawn_rate = 20
                elif level == "endless_fawn":
                    supplied_dict = endless_fawn_enemies
                    item_dict = endless_fawn_items
                    max_enemy_count = max(3,2+(current_time//30))
                    item_spawn_rate = 60
                # Now that we have the correct dictionary, pick which enemy to spawn based on rate index (first index)
                total_rate = 0
                for enemy_type in supplied_dict:
                    total_rate += supplied_dict[enemy_type][0]
                p = random.randint(0,total_rate)
                running_rate = 0
                chosen_enemy_type = None
                for enemy_type in supplied_dict:
                    running_rate += supplied_dict[enemy_type][0]
                    if running_rate >= p:
                        chosen_enemy_type = enemy_type
                        break
                # Now we've picked which one to spawn, just need to unpack info and take values in their random ranges
                # Info to unpack: health,item,speed,time_until_spawn,movement_type,item_rate,ability_rate,sensor_radius,fawn_timer
                # Enemy parameters: enemy_type,health,item,x,y,speed,direction,time_until_spawn,movement_type,item_rate,ability_rate,sensor_radius,fawn_timer
                new_x = random.randint(0,740)*(current_display[0]/initial_display[0])
                new_y = random.randint(0,390)*(current_display[1]/initial_display[1])
                new_health = random.randint(supplied_dict[chosen_enemy_type][1][0],supplied_dict[chosen_enemy_type][1][1])
                new_item = random.choice(supplied_dict[chosen_enemy_type][2])
                new_speed = random.randint(supplied_dict[chosen_enemy_type][3][0],supplied_dict[chosen_enemy_type][3][1])
                new_speed = [new_speed,new_speed]
                new_time_until_spawn = current_time + random.randint(supplied_dict[chosen_enemy_type][4][0],supplied_dict[chosen_enemy_type][4][1])
                new_movement_type = random.choice(supplied_dict[chosen_enemy_type][5])
                new_item_rate = random.randint(supplied_dict[chosen_enemy_type][6][0],supplied_dict[chosen_enemy_type][6][1])
                new_ability_rate = random.randint(supplied_dict[chosen_enemy_type][7][0],supplied_dict[chosen_enemy_type][7][1])
                new_sensor_radius = random.randint(supplied_dict[chosen_enemy_type][8][0],supplied_dict[chosen_enemy_type][8][1])
                new_fawn_timer = random.randint(supplied_dict[chosen_enemy_type][9][0],supplied_dict[chosen_enemy_type][9][1])
                # Create instance of enemy
                new_enemy = enemy(chosen_enemy_type,new_health,new_item,new_x,new_y,new_speed,[0,0],new_time_until_spawn,new_movement_type,new_item_rate,new_ability_rate,new_sensor_radius,new_fawn_timer)
                # Move randomly just to set initial direction vector
                new_enemy.move_randomly()
                # Give enemy timer until removed if playing flight or freeze
                if (level == "endless_flight") or (level == "endless_freeze"):
                    # Frames x Seconds
                    new_enemy.timer = 60*random.randint(20,30)
                # Get current enemy count
                enemy_count = 0
                for item in all_objects:
                    if isinstance(item,enemy):
                        enemy_count += 1
                # Now check to spawn enemy
                if (not isNear(player_object.selfrect.left,new_enemy.selfrect.left,player_object.selfrect.top,new_enemy.selfrect.top,200)) and (enemy_count < max_enemy_count+1):
                    # Only adds enemy if won't spawn too close to player object
                    all_objects.append(new_enemy)
                # Finally check to see if we spawn item
                p = random.randint(0,item_spawn_rate)
                if p == 0:
                    # Select item from given list using rates
                    total_rate = 0
                    for item_type in item_dict:
                        total_rate += item_dict[item_type]
                    q = random.randint(0,total_rate)
                    running_rate = 0
                    chosen_item_type = None
                    for item_type in item_dict:
                        running_rate += item_dict[item_type]
                        if running_rate >= q:
                            chosen_item_type = item_type
                            break
                    # And spawn it (we assume universal timer of 300 frames/5 seconds for collectable item)
                    new_x = random.randint(0,760)
                    new_y = random.randint(0,410)
                    new_item = collectable_item(chosen_item_type,new_x,new_y,300,0)
                    # Scale item image
                    new_item.image = pg.transform.scale(new_item.original_image, ((current_display[0]/initial_display[0])*new_item.original_image.get_width(),(current_display[1]/initial_display[1])*new_item.original_image.get_height()))
                    new_item.selfrect = new_item.image.get_rect(topleft=((current_display[0]/initial_display[0])*new_item.initialx,(current_display[1]/initial_display[1])*new_item.initialy))
                    all_objects.append(new_item)
                    
            # Boss 1
            elif self.type == 'boss1':
                # Boss1 ability is to summon enemies, apply energy barriers automatically and change movement pattern
                # Add enemy
                new_enemy = enemy('classic',3,None,random.randint(0,740),random.randint(0,390),[2,2],[-1,1],current_time+1,"to_player",10,0,0,math.inf)
                # Rescale enemy
                new_enemy.image = pg.transform.scale(new_enemy.original_image, ((current_display[0]/initial_display[0])*new_enemy.original_image.get_width(),(current_display[1]/initial_display[1])*new_enemy.original_image.get_height()))
                new_enemy.selfrect = new_enemy.image.get_rect(topleft=((current_display[0]/initial_display[0])*new_enemy.initialx,(current_display[1]/initial_display[1])*new_enemy.initialy))
                new_enemy.speed[0] = new_enemy.initial_speed[0]*(current_display[0]/initial_display[0])
                new_enemy.speed[1] = new_enemy.initial_speed[1]*(current_display[1]/initial_display[1])
                if not isNear(new_enemy.selfrect.left,player_object.selfrect.left,new_enemy.selfrect.top,player_object.selfrect.top,150):
                    # Only adds enemy if won't spawn near player object
                    all_objects.append(new_enemy)
                # Apply energy barrier
                current_item = self.item
                self.item = "energy barrier"
                all_objects = use_item(self,all_objects,mouse,player_object,level,current_time)
                self.item = current_item
                # Change movement - charge player if health below 25%
                if self.health <= self.initial_health/4:
                    self.movement_type = "to_player"
                elif self.movement_type == "away_player":
                    self.movement_type = "random"
                elif self.movement_type == "random":
                    self.movement_type = "away_player"
                    
            # Boss 2
            elif self.type == 'boss2':
                # Teleport randomly to somewhere on screen
                new_x = random.randint(0,740)*(current_display[0]/initial_display[0])
                new_y = random.randint(0,390)*(current_display[1]/initial_display[1])
                # Not too close to player though
                if not isNear(new_x,player_object.selfrect.left,new_y,player_object.selfrect.top,150):
                    self.selfrect.left = new_x
                    self.selfrect.top = new_y
                # And fire a bullet
                current_item = self.item
                self.item = minigun(self,1,0,5,[0.025,0.025])
                all_objects = use_item(self,all_objects,mouse,player_object,level,current_time)
                self.item = current_item

            # Boss 3
            elif self.type == 'boss3':
                # Fire small enemy object in direction of player
                # Add enemy and change timer to 2 seconds (120 frames) so it despawns sooner
                new_enemy = enemy('classic',3,None,self.selfrect.centerx,self.selfrect.centery,[8,8],[0,0],0,"at_player",0,0,random.randint(50,125),math.inf)
                new_enemy.timer = current_time+120
                # Rescale enemy
                new_size = random.randint(15,35)
                new_enemy.original_image = pg.transform.scale(new_enemy.original_image, ((current_display[0]/initial_display[0])*new_size,(current_display[1]/initial_display[1])*new_size))
                new_enemy.image = pg.transform.scale(new_enemy.original_image, ((current_display[0]/initial_display[0])*new_size,(current_display[1]/initial_display[1])*new_size))
                new_enemy.selfrect = new_enemy.image.get_rect(topleft=(self.selfrect.centerx,self.selfrect.centery))
                new_enemy.speed[0] = new_enemy.initial_speed[0]*(current_display[0]/initial_display[0])
                new_enemy.speed[1] = new_enemy.initial_speed[1]*(current_display[1]/initial_display[1])
                all_objects.append(new_enemy)

            # Boss 4
            elif self.type == 'boss4':
                # Eratic movement pattern. If player is too far away it summons enemies to move at player
                # First take a random number to decide movement
                # Note that this doesn't change movement_type just direction vector
                movement_roll = random.randint(0,100)
                if movement_roll <= 35:
                    # Retain Movement
                    pass
                elif movement_roll <= 40:
                    # Move away from player
                    self.move_to_or_away_player(player_object,False)
                elif movement_roll <= 60:
                    # Move to player
                    self.move_to_or_away_player(player_object,True)
                else:
                    # Move random
                    self.move_randomly()
                # Now check to see if player in range of self
                # We have random integer roll here to reduce the amount of spawns so to not overwhelm processing
                if (not isNear(self.selfrect.left,player_object.selfrect.left,self.selfrect.top,player_object.selfrect.top,230)) and (random.randint(1,2)==1):
                    # If out of range spawn enemies to charge at player
                    new_enemy = enemy('classic',4,None,random.randint(0,740),random.randint(0,390),[8,8],[-1,1],current_time+1,"at_player",0,0,0,math.inf)
                    new_enemy.timer = 120
                    # Rescale enemy
                    new_enemy.image = pg.transform.scale(new_enemy.original_image, ((current_display[0]/initial_display[0])*new_enemy.original_image.get_width(),(current_display[1]/initial_display[1])*new_enemy.original_image.get_height()))
                    new_enemy.selfrect = new_enemy.image.get_rect(topleft=((current_display[0]/initial_display[0])*new_enemy.initialx,(current_display[1]/initial_display[1])*new_enemy.initialy))
                    new_enemy.speed[0] = new_enemy.initial_speed[0]*(current_display[0]/initial_display[0])
                    new_enemy.speed[1] = new_enemy.initial_speed[1]*(current_display[1]/initial_display[1])
                    all_objects.append(new_enemy)
                    
            # Final boss
            elif self.type == 'final_boss':
                # Changes indicator at different health levels
                changed_mode = False
                if self.health <= self.initial_health*0.1:
                    # Less than 10% health
                    if indicator != "fawn":
                        indicator = "fawn"
                        # Give player minigun
                        player_object.item = "minigun"
                        play_sfx('item_pickup.mp3')
                        changed_mode = True
                    # Move away from player. Give option to fawn or kill
                    self.movement_type = "away_player"
                elif self.health <= self.initial_health*0.3:
                    # Less than 30% health
                    if indicator != "freeze":
                        indicator = "freeze"
                        # Make boss use timestop and change movement to predictable (invert direction vector first)
                        # That way player will have time to react to sensor
                        self.item = timestop(self,90)
                        all_objects = use_item(self,all_objects,mouse,player_object,level,current_time)
                        self.direction[0] *= -1
                        self.direction[1] *= -1
                        self.movement_type = "predictable"
                        changed_mode = True
                    # Sacrifice some health over time (3 per second)
                    self.health -= 1/20
                    # Summon enemies to move to player
                    dice_roll = random.randint(0,80)
                    if dice_roll == 0:
                        # Summon enemy
                        new_enemy = enemy('pirate',4,None,random.randint(0,740),random.randint(0,390),[2,2],[-1,1],current_time+1,"to_player",0,0,0,math.inf)
                        new_enemy.timer = 180
                        # Rescale enemy
                        new_enemy.image = pg.transform.scale(new_enemy.original_image, ((current_display[0]/initial_display[0])*new_enemy.original_image.get_width(),(current_display[1]/initial_display[1])*new_enemy.original_image.get_height()))
                        new_enemy.selfrect = new_enemy.image.get_rect(topleft=((current_display[0]/initial_display[0])*new_enemy.initialx,(current_display[1]/initial_display[1])*new_enemy.initialy))
                        new_enemy.speed[0] = new_enemy.initial_speed[0]*(current_display[0]/initial_display[0])
                        new_enemy.speed[1] = new_enemy.initial_speed[1]*(current_display[1]/initial_display[1])
                        all_objects.append(new_enemy)
                elif self.health <= self.initial_health*0.65:
                    # Less than 65% health
                    if indicator != "flight":
                        indicator = "flight"
                        # Remove player's current item
                        player_object.item = None
                        # Give boss a special grenade launcher
                        self.item = grenade_launcher(self,math.inf,30,6,[0.02,0.02],80,75)
                        changed_mode = True
                    # Sacrifice some health over time (3 per second)
                    self.health -= 1/20
                    # Summon enemies to move at player
                    dice_roll = random.randint(0,120)
                    if dice_roll == 0:
                        # Summon enemy
                        new_enemy = enemy('ninja',4,None,random.randint(0,740),random.randint(0,390),[8,8],[-1,1],current_time+1,"at_player",0,0,0,math.inf)
                        new_enemy.timer = 120
                        # Rescale enemy
                        new_enemy.image = pg.transform.scale(new_enemy.original_image, ((current_display[0]/initial_display[0])*new_enemy.original_image.get_width(),(current_display[1]/initial_display[1])*new_enemy.original_image.get_height()))
                        new_enemy.selfrect = new_enemy.image.get_rect(topleft=((current_display[0]/initial_display[0])*new_enemy.initialx,(current_display[1]/initial_display[1])*new_enemy.initialy))
                        new_enemy.speed[0] = new_enemy.initial_speed[0]*(current_display[0]/initial_display[0])
                        new_enemy.speed[1] = new_enemy.initial_speed[1]*(current_display[1]/initial_display[1])
                        all_objects.append(new_enemy)
                    # Change movement when below 35% health to to_player
                    if self.health <= self.initial_health*0.35:
                        self.movement_type = "to_player"
                else:
                    # Less than 100% health (assumes indicator is already set to fight)
                    # Roll to change player and boss item to a random one
                    item_roll = random.randint(0,300)
                    if item_roll == 0:
                        # Player can have any item except energy absorber and barrier
                        player_object.item = random.choice(["minigun","timestop","grenade launcher"])
                        play_sfx('item_pickup.mp3')
                        # Boss can have any item
                        self.item = random.choice(powers)
                    # Change movement when below 90% health to random
                    if self.health <= self.initial_health*0.9:
                        self.movement_type = "random"
                        
                # If changed to different indicator value, re-prints display text
                if changed_mode == True:
                    indicator_text = text(indicator+"_text.png",275,100,0,current_time+1,True)
                    # Rescale text
                    indicator_text.image = pg.transform.scale(indicator_text.original_image, ((current_display[0]/initial_display[0])*indicator_text.original_image.get_width(),(current_display[1]/initial_display[1])*indicator_text.original_image.get_height()))
                    indicator_text.selfrect = indicator_text.image.get_rect(topleft=((current_display[0]/initial_display[0])*indicator_text.initialx,(current_display[1]/initial_display[1])*indicator_text.initialy))
                    # Append it to all_objects
                    all_objects.append(indicator_text)
                
            # For ability-less enemies we just pass
            else:
                pass
        return all_objects, indicator
            


class energy_barrier():
    def __init__(self,user,x,y,health=math.inf):
        self.user = user
        if type(self.user) == enemy:
            self.original_image = pg.image.load('energy_barrier_dark.png')
            self.image = pg.image.load('energy_barrier_dark.png')
            self.original_image_name = 'energy_barrier_dark.png'
        else:
            self.original_image = pg.image.load('energy_barrier_light.png')
            self.image = pg.image.load('energy_barrier_light.png')
            self.original_image_name = 'energy_barrier_light.png'
        self.image = pg.transform.scale(self.original_image, ((current_display[0]/initial_display[0])*self.original_image.get_width(),(current_display[1]/initial_display[1])*self.original_image.get_height()))
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use current x/y for timestop
        self.currentx = self.initialx
        self.currenty = self.initialy
        self.max_health = health
        self.health = health
        play_sfx('energy_barrier_spawn.mp3')

class energy_absorber():
    def __init__(self,user,x,y,timer,health=math.inf):
        self.user = user
        if type(self.user) == enemy:
            self.original_image = pg.image.load('energy_absorber_dark.png')
            self.image = pg.image.load('energy_absorber_dark.png')
            self.original_image_name = 'energy_absorber_dark.png'
        else:
            self.original_image = pg.image.load('energy_absorber_light.png')
            self.image = pg.image.load('energy_absorber_light.png')
            self.original_image_name = 'energy_absorber_light.png'
        self.image = pg.transform.scale(self.original_image, ((current_display[0]/initial_display[0])*self.original_image.get_width(),(current_display[1]/initial_display[1])*self.original_image.get_height()))
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use current x/y for timestop
        self.currentx = self.initialx
        self.currenty = self.initialy
        self.absorbed_health = 0
        self.max_health = health
        self.health = health
        # Timer should be at least 4 seconds long (240 frames) for best performance
        self.timer = max(240,timer)

    def get_explosion_values(self):
        # Calculates the damage and radius of explosion once timer runs out
        health = self.absorbed_health*4
        radius = 50*math.sqrt(self.absorbed_health/10)
        return health, radius

class bullet():
    def __init__(self,user,x,y,health,speed,direction):
        self.user = user # user in this instance just gives them immunity to the shot etc.
        if type(self.user) == enemy:
            self.original_image = pg.image.load('bullet_dark.png')
            self.image = pg.image.load('bullet_dark.png')
            self.original_image_name = 'bullet_dark.png'
        else:
            self.original_image = pg.image.load('bullet_light.png')
            self.image = pg.image.load('bullet_light.png')
            self.original_image_name = 'bullet_light.png'
        self.image = pg.transform.scale(self.original_image, ((current_display[0]/initial_display[0])*self.original_image.get_width(),(current_display[1]/initial_display[1])*self.original_image.get_height()))
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use current x/y for timestop
        self.currentx = self.initialx
        self.currenty = self.initialy
        self.health = health
        self.speed = speed
        self.direction = direction
        play_sfx('bullet_sfx.mp3')

class grenade():
    def __init__(self,user,x,y,health,speed,direction,timer,radius):
        self.user = user # user in this instance just gives them immunity to the shot etc.
        if type(self.user) == enemy:
            self.original_image = pg.image.load('grenade_dark.png')
            self.image = pg.image.load('grenade_dark.png')
            self.original_image_name = 'grenade_dark.png'
        else:
            self.original_image = pg.image.load('grenade_light.png')
            self.image = pg.image.load('grenade_light.png')
            self.original_image_name = 'grenade_light.png'
        self.image = pg.transform.scale(self.original_image, ((current_display[0]/initial_display[0])*self.original_image.get_width(),(current_display[1]/initial_display[1])*self.original_image.get_height()))
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use current x/y for timestop
        self.currentx = self.initialx
        self.currenty = self.initialy
        self.health = health
        self.speed = speed
        self.direction = direction
        self.timer = timer
        self.radius = radius
        play_sfx('grenade_sfx.mp3')


class explosion():
    def __init__(self,user,x,y,health,radius,timer,center_image,indicator=None):
        self.user = user
        # We make radius 2d so can change x and y radius independently due to screen size not neccesarily being square
        # Scale radius to screen size
        self.radius = [radius,radius]
        self.radius[0] = self.radius[0]*(current_display[0]/initial_display[0])
        self.radius[1] = self.radius[1]*(current_display[1]/initial_display[1])
        if type(self.user) == enemy:
            self.original_image = pg.image.load('explosion_dark.png')
            self.image = pg.image.load('explosion_dark.png')
            self.original_image_name = 'explosion_dark.png'
        else:
            self.original_image = pg.image.load('explosion_light.png')
            self.image = pg.image.load('explosion_light.png')
            self.original_image_name = 'explosion_light.png'
        # Scale image and original image to radius (and hence screen size)
        self.original_image = pg.transform.scale(self.original_image, (self.radius[0]*2, self.radius[1]*2))
        self.image = pg.transform.scale(self.image, (self.radius[0]*2, self.radius[1]*2))
        # Set selfrect for explosion
        # We use center_image here (the image of object explosion is centered around)
        self.selfrect = self.image.get_rect(topleft=((x-(self.radius[0]-(center_image.get_width()/2))),(y-(self.radius[1]-(center_image.get_height()/2)))))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # 'health' is in reality the max damage it can deal
        self.health = health
        self.timer = timer
        # Indicator use for energy absorber or grenade launcher
        self.indicator = indicator
        play_sfx('explosion_sfx.mp3')
        

class minigun():
    # Works differently to other classes
    # Has no image or rect. Is just used to store data about user, ammunition, cooldown between shots, bullet health and speed, etc.
    def __init__(self,user,ammo,cooldown,health,speed):
        self.user = user
        self.max_ammo = ammo
        self.ammo = ammo
        self.cooldown = cooldown
        self.initial_cooldown = cooldown
        self.health = health
        self.speed = speed
        self.initial_speed = copy.copy(speed)
        # Scale speed to current screen size immediately
        self.speed[0] = self.initial_speed[0]*(current_display[0]/initial_display[0])
        self.speed[1] = self.initial_speed[1]*(current_display[1]/initial_display[1])
        play_sfx('minigun_sfx.mp3')
        

class grenade_launcher():
    # Works simiarly to minigun class
    def __init__(self,user,ammo,cooldown,health,speed,timer,radius):
        self.user = user
        self.max_ammo = ammo
        self.ammo = ammo
        self.cooldown = cooldown
        self.initial_cooldown = cooldown
        # 'health' will be the max damage explosion deals
        self.health = health
        # Radius for explosion as well
        self.radius = radius
        self.speed = speed
        self.initial_speed = copy.copy(speed)
        # Scale speed to current screen size immediately
        self.speed[0] = self.initial_speed[0]*(current_display[0]/initial_display[0])
        self.speed[1] = self.initial_speed[1]*(current_display[1]/initial_display[1])
        # Timer until explosion goes off
        self.timer = timer
        play_sfx('grenade_launcher_sfx.mp3')

class timestop():
    # Works simiarly to minigun class
    def __init__(self,user,duration):
        self.user = user
        self.max_duration = duration
        self.duration = duration
        # Immediatly active once called
        self.active = True
        play_sfx('timestop_sfx.mp3')

    def stop_time(self,active_objects):
        # Function to stop time on objects by setting their coords to what they were before moving (currentx/currenty)
        self.duration -= 1
        if isinstance(self.user,player):
            for item in active_objects:
                if isinstance(item,enemy):
                    item.selfrect = item.image.get_rect(topleft=(item.currentx,item.currenty))
                    if isinstance(item.energy_item,energy_barrier) or isinstance(item.energy_item,energy_absorber):
                        item.energy_item.selfrect = item.energy_item.image.get_rect(topleft=(item.energy_item.currentx,item.energy_item.currenty))
                if isinstance(item,bullet) or isinstance(item,grenade):
                    if isinstance(item.user,enemy):
                        item.selfrect = item.image.get_rect(topleft=(item.currentx,item.currenty))
        else:
            for item in active_objects:
                if isinstance(item,player):
                    item.selfrect = item.image.get_rect(topleft=(item.currentx,item.currenty))
                    if isinstance(item.energy_item,energy_barrier) or isinstance(item.energy_item,energy_absorber):
                        item.energy_item.selfrect = item.energy_item.image.get_rect(topleft=(item.energy_item.currentx,item.energy_item.currenty))
                if isinstance(item,bullet) or isinstance(item,grenade):
                    if isinstance(item.user,player):
                        item.selfrect = item.image.get_rect(topleft=(item.currentx,item.currenty))
        if self.duration <= 0:
            # Remove self if duration expires
            self.active = False
            self.user.item = None


class collectable_item():
    def __init__(self,item_type,x,y,timer,time_until_spawn):
        self.item_type = item_type
        self.original_image = pg.image.load(item_images[item_type])
        self.image = pg.image.load(item_images[item_type])
        self.original_image_name = item_images[item_type]
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Timer in total frames; time_until_spawn in seconds
        self.timer = timer
        self.time_until_spawn = time_until_spawn


class sensor():
    def __init__(self,user,x,y,radius,detection=False,active=True):
        self.user = user
        # Set users sensor object to this one
        self.user.sensor_obj = self
        self.detection = detection
        self.active = active
        # We make radius 2d so can change x and y radius independently due to screen size not neccesarily being square
        # Scale radius to screen size
        self.radius = [radius,radius]
        self.radius[0] = self.radius[0]*(current_display[0]/initial_display[0])
        self.radius[1] = self.radius[1]*(current_display[1]/initial_display[1])
        self.original_image = pg.image.load('detection_circle.png')
        self.image = pg.image.load('detection_circle.png')
        self.original_image_name = 'detection_circle.png'
        # Scale image and original image to radius (and hence screen size)
        self.original_image = pg.transform.scale(self.original_image, (self.radius[0]*2, self.radius[1]*2))
        self.image = pg.transform.scale(self.image, (self.radius[0]*2, self.radius[1]*2))
        # Set selfrect for sensor around user
        self.selfrect = self.image.get_rect(topleft=((x-(self.radius[0]-(user.image.get_width()/2))),(y-(self.radius[1]-(user.image.get_height()/2)))))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top


class fawn_collectable():
    def __init__(self,user,x,y):
        self.user = user
        self.original_image = pg.image.load('fawn_ball.png')
        self.image = pg.image.load('fawn_ball.png')
        self.original_image_name = 'fawn_ball.png'
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
            

class button():
    def __init__(self,image,x,y,function=None,overlay=False):
        self.original_image = pg.image.load(image)
        self.image = pg.image.load(image)
        self.original_image_name = image
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        self.function = function
        self.overlay = overlay

    def pressed(self,mouse):
        # Determines if mouse is over button (use in tandem with MOUSEBUTTONDOWN)
        if mouse[0] > self.selfrect.topleft[0]:
            if mouse[1] > self.selfrect.topleft[1]:
                if mouse[0] < self.selfrect.bottomright[0]:
                    if mouse[1] < self.selfrect.bottomright[1]:
                        return True
        return False

    def perform_function(self):
        if self.function == None:
            pass
        elif self.function == "go_to_campaign_menu":
            campaign_menu()
        elif self.function == "go_to_endless_menu":
            endless_menu()
        elif self.function == "go_to_controls_menu":
            controls_menu()
        elif self.function == "toggle_music":
            global music_on
            if music_on == True:
                music_on = False
                self.original_image = pg.image.load('music_off.png')
                self.original_image_name = 'music_off.png'
            else:
                music_on = True
                self.original_image = pg.image.load('music_on.png')
                self.original_image_name = 'music_on.png'
        elif self.function == "toggle_sfx":
            global sfx_on
            if sfx_on == True:
                sfx_on = False
                self.original_image = pg.image.load('sfx_off.png')
                self.original_image_name = 'sfx_off.png'
            else:
                sfx_on = True
                self.original_image = pg.image.load('sfx_on.png')
                self.original_image_name = 'sfx_on.png'
        elif self.function == "quit_program":
            save_game()
            pg.quit()
            sys.exit()
        elif self.function[:11] == "play_level_":
            # String slice to find level number we want to play
            print("play level:", self.function[11:])
            level_type = levels[self.function[11:]][0]
            
            # Need to get all game objects into a single list. Will be [background,player,enemies,collectable items,other]
            level_objects = [background(levels[self.function[11:]][4]),levels[self.function[11:]][1]]
            for enemy_obj in levels[self.function[11:]][2]:
                level_objects.append(enemy_obj)
            for new_item in levels[self.function[11:]][6]:
                level_objects.append(new_item)
            # We also add pause button
            level_objects.append(button('pause_button.png',769,1,"go_to_pause_screen"))
            # And item box
            level_objects.append(text('current_item_box.png',150,400))
            # And health box
            level_objects.append(text('health_box.png',0,400))
            # Finally we copy the list and pass the copy through
            # Manually copy level_objects otherwise it messes with dictionary
            level_objects_copy = deepcopy_level(level_objects)
            
            # Now simply run game
            win = play_game(level_objects_copy,levels[self.function[11:]][3],levels[self.function[11:]][5],self.function[11:],copy.copy(level_type))
            # If we played a level we haven't beat yet, increase level unlock
            global current_level_unlock
            if (win == True) and (int(self.function[11:]) == current_level_unlock):
                current_level_unlock += 1
            # Once game run play either victory or game over screen before returning to main
            if win == None:
                pass
            elif win == True:
                victory_screen()
            else:
                game_over_screen()
        elif self.function[:8] == "endless_":
            print("play endless:", self.function[8:])
            level_type = self.function[8:]
            # Need endless objects as [background,player,enemies,other]
            level_objects = [background('endless_background.png'),player('player.png',20,None,350,225,[5,5])]
            # To keep game infinite, we create enemy far outside border that has ability to spawn all enemies continuously
            endless_enemy = enemy('endless',math.inf,None,99999,99999,[0,0],[1,1],0,None,0,20,0,math.inf)
            level_objects.append(endless_enemy)
            # We also add pause button
            level_objects.append(button('pause_button.png',769,1,"go_to_pause_screen"))
            # And item box
            level_objects.append(text('current_item_box.png',150,400))
            # And health box
            level_objects.append(text('health_box.png',0,400))
            # Finally we copy the list and pass the copy through
            level_objects_copy = deepcopy_level(level_objects)

            # Now play endless
            win = play_game(level_objects_copy,math.inf,'endless_music.mp3',self.function,copy.copy(level_type))
            # Unwinable so game over screen after end
            if win != None:
                game_over_screen()
            
            
class background():
    # Dummy class so it can iterate in other functions
    def __init__(self,image):
        self.original_image = pg.image.load(image)
        self.image = pg.image.load(image)
        self.original_image_name = image
        self.selfrect = self.image.get_rect(topleft=(0,0))
        self.initialx = 0
        self.initialy = 0

class text():
    # Dummy class so it can iterate in other functions
    def __init__(self,image,x,y,time_to_add=0,time_to_remove=math.inf,overlay=False):
        self.original_image = pg.image.load(image)
        self.image = pg.image.load(image)
        self.original_image_name = image
        self.selfrect = self.image.get_rect(topleft=(x,y))
        self.initialx = self.selfrect.left
        self.initialy = self.selfrect.top
        # Use these values if we want temporary text
        self.time_to_add = time_to_add
        self.time_to_remove = time_to_remove
        self.overlay = overlay
        

# Create minor functions
def isNear(x1,x2,y1,y2,dist):
    # Returns true if coords near each other given distance (scaled to initial display (approx))
    distance = math.sqrt(math.pow(x1-x2,2) + (math.pow(y1-y2,2)))
    if distance <= (dist*(math.sqrt(current_display[0]**2+current_display[1]**2)/math.sqrt(initial_display[0]**2+initial_display[1]**2))):
        return True
    else:
        return False

    
def save_game():
    # Save game by overwriting save file with current values of global variables (creates one if none present as well)
    f = open("save_file.txt", "w")
    f.write("current_level_unlock= "+str(current_level_unlock)+"\n")
    # Boolean values read as 0 or 1
    if music_on:
        f.write("music_on= 1\n")
    else:
        f.write("music_on= 0\n")
    if sfx_on:
        f.write("sfx_on= 1\n")
    else:
        f.write("sfx_on= 0\n")
    f.write("endless_fight_high_score= "+str(endless_fight_high_score)+"\n")
    f.write("endless_flight_high_score= "+str(endless_flight_high_score)+"\n")
    f.write("endless_freeze_high_score= "+str(endless_freeze_high_score)+"\n")
    f.write("endless_fawn_high_score= "+str(endless_fawn_high_score)+"\n")
    f.close()


def deepcopy_level(list_objects):
    copy_list = []
    for item in list_objects:
        if isinstance(item,background) or isinstance(item,button) or isinstance(item,text):
            # Don't need to copy if background, button or text (as we won't modify them)
            copy_list.append(item)
        else:
            # Primarily need to deepcopy anything else that either changes coords or is removed etc.
            copy_list.append(deepcopy_object(item))
    return copy_list


def deepcopy_object(obj):
    # We deepcopy an object by just making a new instance of it
    if isinstance(obj,player):
        # Player parameters are image,health,item,x,y,speed
        return player(obj.original_image_name,obj.health,obj.item,obj.initialx,obj.initialy,copy.copy(obj.initial_speed))
    elif isinstance(obj,enemy):
        # Enemy parameters are type,health,item,x,y,speed,direction,time_until_spawn,movement_type,item_rate,ability_rate,sensor_radius
        return enemy(obj.type,obj.health,obj.item,obj.initialx,obj.initialy,copy.copy(obj.initial_speed),obj.direction,obj.time_until_spawn,obj.movement_type,obj.item_rate,obj.ability_rate,obj.sensor_radius,obj.fawn_timer)
    elif isinstance(obj,collectable_item):
        # Collectable_item parameters are item_type,x,y,timer,time_until_spawn
        return collectable_item(obj.item_type,obj.initialx,obj.initialy,obj.timer,obj.time_until_spawn)
    else:
        print("Error while trying to replicate copy of:", obj)
        return None


def do_enemy_movement(active_objects,player_object,all_objects,mouse,level,current_time,score,indicator):
    # First we get a list of enemies to move
    enemies = []
    for item in active_objects:
        if isinstance(item,enemy):
            enemies.append(item)
    # Now move them depending on their movement/direction/speed (we change their icons here as well)
    # Also have a chance of using their item
    # Also check for ability usage
    for enemy_obj in enemies:
        enemy_obj.change_icon()
        if (hitsBorder(enemy_obj,enemy_obj.speed,enemy_obj.direction) and (enemy_obj.movement_type == "random")):
            enemy_obj.move_randomly()
        elif enemy_obj.movement_type == "to_player":
            enemy_obj.move_to_or_away_player(player_object,True)
        elif enemy_obj.movement_type == "away_player":
            enemy_obj.move_to_or_away_player(player_object,False)
        elif enemy_obj.movement_type == "at_player":
            enemy_obj.move_at_player(player_object)
        elif enemy_obj.movement_type == "predictable":
            enemy_obj.move_predictable()
        else:
            pass
        # Move object
        enemy_obj.selfrect.move_ip(enemy_obj.speed[0]*enemy_obj.direction[0],enemy_obj.speed[1]*enemy_obj.direction[1])
        # Check to see if we will use their item
        dice_roll = random.randint(0,int(enemy_obj.item_rate))
        if dice_roll == 0:
            all_objects = use_item(enemy_obj,all_objects,mouse,player_object,level,current_time)
        # And run ability method for each object
        all_objects, indicator = enemy_obj.ability(all_objects,active_objects,mouse,player_object,level,current_time,indicator)
        # Decrease fawn_timer by 1
        enemy_obj.fawn_timer -= 1
        # And spawn fawn collectable if playing fawn
        if (enemy_obj.fawn_timer <= 0) and ((indicator == "fawn") or (level == "endless_fawn")):
            all_objects = spawn_fawn(all_objects,enemy_obj,player_object)
            # Once spawned we set timer to infinity so we only spawn 1 collectable
            enemy_obj.fawn_timer = math.inf
        # Finally decrease timer by 1 (almost all enemies have it set to infinity so only really used in endless)
        enemy_obj.timer -= 1
        if enemy_obj.timer <= 0:
            # Remove enemy if timer expires and increase score if not fawn (fawn can only have score increase if fawn collectable is touched or killed enemy)
            all_objects.remove(enemy_obj)
            if indicator != "fawn":
                score += 1
    return all_objects, score, indicator
        

def do_item_movement(all_objects,active_objects):
    # Move items in given list
    to_remove = []
    for item in active_objects:
        if isinstance(item,energy_barrier) or isinstance(item,energy_absorber):
            item.selfrect.move_ip(item.user.selfrect.left-item.selfrect.left-(item.user.image.get_width()/4),item.user.selfrect.top-item.selfrect.top-(item.user.image.get_height()/4))
            # Also reduce energy absorber timer
            if isinstance(item,energy_absorber):
                if item.timer == 240:
                    play_sfx('absorber_4_sec_countdown.mp3')
                item.timer -= 1
                if item.timer <= 0:
                    # If timer runs out, remove absorber object but spawn explosion
                    exp_health, exp_radius = item.get_explosion_values()
                    to_remove.append(item)
                    new_exp = explosion(item.user,copy.copy(item.user.selfrect.left),copy.copy(item.user.selfrect.top),exp_health,exp_radius,60,item.user.image,"energy absorber")
                    all_objects.append(new_exp)                   
        elif isinstance(item,bullet):
            # Bullet speed needs to be really slow as direction vector isn't normalised
            item.selfrect.move_ip(item.speed[0]*item.direction[0],item.speed[1]*item.direction[1])
            # Remove bullets way outside of border to reduce lag
            if (item.selfrect.left > current_display[0]+100) or (item.selfrect.left < -100) or (item.selfrect.top > current_display[1]+100) or (item.selfrect.top < -100):
                to_remove.append(item)
        elif isinstance(item,grenade):
            # Reduce timer until explosion
            item.timer -= 1
            if (item.timer <= 0) or hitsBorder(item,item.speed,item.direction):
                # Replace grenade with explosion if timer goes off or hits the border
                to_remove.append(item)
                # We assume explosion lasts 1 second (60 frames) for now
                new_exp = explosion(item.user,copy.copy(item.selfrect.left),copy.copy(item.selfrect.top),item.health,item.radius,60,item.image)
                all_objects.append(new_exp)
            else:
                # Grenade speed also needs to be low as direction vector isn't normalised
                item.selfrect.move_ip(item.speed[0]*item.direction[0],item.speed[1]*item.direction[1])
        elif isinstance(item,explosion):
            if item.indicator == None:
                pass
            elif item.indicator == "energy absorber":
                # We move explosion with user if energy absorber indicator
                item.selfrect.move_ip(item.user.selfrect.left-item.selfrect.left-(item.radius[0]-item.user.image.get_width()/2),item.user.selfrect.top-item.selfrect.top-(item.radius[1]-item.user.image.get_height()/2))
            # Remove explosion after given duration frames
            item.timer -= 1
            if item.timer <= 0:
                to_remove.append(item)
        elif isinstance(item,collectable_item):
            # Remove collectable items once their timer expires
            item.timer -= 1
            if item.timer <= 0:
                to_remove.append(item)
    # Remove any items that require removal from all_objects
    for rubbish in to_remove:
        all_objects.remove(rubbish)
    # Return all objects                        
    return all_objects
        

def do_collisions(all_objects,active_objects,score):
    # Check for collisions between list of active objects and return updated list of all objects
    to_remove = []
    for item in active_objects:
        # Get a double for loop going on active objects
        for other_item in active_objects:
            # Pass if either item is already on removal list
            if (other_item in to_remove) or (item in to_remove):
                pass
            # Pass if object variables are the same
            elif other_item == item:
                pass
            # Or if either object is the background, text or buttons
            elif isinstance(other_item,background) or isinstance(item,background) or isinstance(other_item,button) or isinstance(item,button) or isinstance(other_item,text) or isinstance(item,text):
                pass
            # Otherwise if objects collide check for interactions
            elif isCollision(item,other_item):
                # Fawn collectable interactions
                if isinstance(item,fawn_collectable):
                    # With player
                    if isinstance(other_item,player):
                        # Remove enemy user and collectable
                        item.user.health = 0
                        to_remove.append(item.user)
                        to_remove.append(item)
                        play_sfx('fawned_sfx.mp3')
                # Collectable item interactions
                if isinstance(item,collectable_item):
                    # With player or enemy; collects the item
                    if isinstance(other_item,player) or isinstance(other_item,enemy):
                        other_item.item = item.item_type
                        item.timer = 0
                        # Remove item immediately once collected (so doesn't accidently apply multiple times)
                        to_remove.append(item)
                        play_sfx('item_pickup.mp3')
                # Grenade interactions
                if isinstance(item,grenade):
                    # Collision with member of other team
                    if isinstance(other_item,player) or isinstance(other_item,enemy):
                        if (type(item.user) != type(other_item)):                          
                            item.timer = 0
                    # Collision with energy barrier
                    if isinstance(other_item,energy_barrier):
                        if (type(item.user) != type(other_item.user)):
                            item.timer = 0
                            play_sfx('energy_barrier_hit.mp3')
                    # Collision with explosion from other team
                    if isinstance(other_item,explosion):
                        if (type(item.user) != type(other_item.user)):
                            item.timer = 0
                # Explosion interactions
                if isinstance(item,explosion):
                    # Collision with member of other team
                    if isinstance(other_item,player) or isinstance(other_item,enemy):
                        if (type(item.user) != type(other_item)):                          
                            original_target_health = other_item.health
                            other_item.health -= item.health
                            item.health -= original_target_health
                    # Collision with bullet
                    if isinstance(other_item,bullet):
                        if (type(item.user) != type(other_item.user)):
                            original_target_health = other_item.health
                            other_item.health -= item.health
                            item.health -= original_target_health
                # Energy absorber interactions
                if isinstance(item,energy_absorber):
                    # Collision with member of other team
                    if isinstance(other_item,player) or isinstance(other_item,enemy):
                        if (type(item.user) != type(other_item)):                          
                            item.absorbed_health += other_item.health
                            item.health -= other_item.health
                            # Absorber insta-kills on contact
                            other_item.health = 0
                            play_sfx('absorbed_sfx.mp3')
                            # If absorber exceeds limit, insta-kills user
                            if item.health <= 0:
                                item.user.health = 0
                                # Append them to removal list immediately
                                to_remove.append(item.user)
                                play_sfx('energy_absorber_break_sfx.mp3')
                    # Collision with opposing bullet,grenade or explosion
                    if isinstance(other_item,bullet) or isinstance(other_item,grenade) or isinstance(other_item,explosion):
                        if (type(item.user) != type(other_item.user)):  
                            item.absorbed_health += other_item.health
                            item.health -= other_item.health
                            # Absorber insta-kills on contact
                            other_item.health = 0
                            play_sfx('absorbed_sfx.mp3')
                            # If absorber exceeds limit, insta-kills user
                            if item.health <= 0:
                                item.user.health = 0
                                # Append them to removal list immediately
                                to_remove.append(item.user)
                                play_sfx('energy_absorber_break_sfx.mp3')
                # Energy barrier interactions
                if isinstance(item,energy_barrier):
                    # Collision with player from enemy user
                    if isinstance(other_item,player) and (type(item.user) == enemy):
                        original_target_health = other_item.health
                        other_item.health -= item.health
                        item.health -= original_target_health
                        play_sfx('energy_barrier_hit.mp3')
                    # Collision with enemy from player user
                    if isinstance(other_item,enemy) and (type(item.user) == player):
                        original_target_health = other_item.health
                        other_item.health -= item.health
                        item.health -= original_target_health
                        play_sfx('energy_barrier_hit.mp3')
                    # Collision between barriers
                    if isinstance(other_item,energy_barrier):
                        # If a barrier belongs to different teams
                        if type(item.user) != type(other_item.user):
                            # Drains health from each barrier
                            item.health -= 1
                            other_item.health -= 1
                            play_sfx('energy_barrier_hit.mp3')
                # Enemy interactions
                if isinstance(item,enemy):
                    # Change player and enemy health if they collide
                    if isinstance(other_item,player):
                        other_item.health -= 1
                        item.health -= 1         
                # Bullet interactions
                if isinstance(item,bullet):
                    # Damage player if bullet type is enemy
                    if isinstance(other_item,player) and (type(item.user) == enemy):
                        original_target_health = other_item.health
                        other_item.health -= item.health
                        item.health -= original_target_health
                    # Damage enemy if bullet type is player
                    if isinstance(other_item,enemy) and (type(item.user) == player):
                        original_target_health = other_item.health
                        other_item.health -= item.health
                        item.health -= original_target_health
                    # Damage energy barrier if hit barrier that isn't your own team
                    if isinstance(other_item,energy_barrier):
                        if type(item.user) != type(other_item.user):
                            original_target_health = other_item.health
                            other_item.health -= item.health
                            item.health -= original_target_health
                            play_sfx('energy_barrier_hit.mp3')
                    
                # Add item to removal list if no health left
                if isinstance(item,player) or isinstance(item,enemy) or isinstance(item,bullet) or isinstance(item,energy_barrier) or isinstance(item,energy_absorber) or isinstance(item,explosion) or isinstance(item,grenade):
                    if item.health <= 0:
                        to_remove.append(item)
                        if isinstance(item,player):
                            play_sfx('player_death_sfx.mp3')
                # Same for other item
                if isinstance(other_item,player) or isinstance(other_item,enemy) or isinstance(other_item,bullet) or isinstance(other_item,energy_barrier) or isinstance(other_item,energy_absorber) or isinstance(other_item,explosion) or isinstance(other_item,grenade):
                    if other_item.health <= 0:
                        to_remove.append(other_item)
                        if isinstance(other_item,player):
                            play_sfx('player_death_sfx.mp3')
                # For energy barrier and absorber and fawn collectables, remove if user has no health left or being/already removed
                if isinstance(item,energy_barrier) or isinstance(item,energy_absorber) or isinstance(item,fawn_collectable):
                    if (item.user.health <= 0) or (item.user in to_remove) or (item.user not in all_objects):
                        to_remove.append(item)
                if isinstance(other_item,energy_barrier) or isinstance(other_item,energy_absorber) or isinstance(other_item,fawn_collectable):
                    if (other_item.user.health <= 0) or (other_item.user in to_remove) or (other_item.user not in all_objects):
                        to_remove.append(other_item)
                        
    # Clear dead objects
    for rubbish in to_remove:
        try:
            # May have removed object earlier on so use try/except
            all_objects.remove(rubbish)
            # Increment score if enemy removed
            if isinstance(rubbish,enemy):
                score += 1
        except(ValueError):
            pass

    # Return new list of all objects and new score
    return all_objects, score

    
def use_item(user,list_objects,mouse,player_object,level,current_time):
    # Energy barrier
    if user.item == "energy barrier":
        new_barrier = energy_barrier(user,copy.copy(user.selfrect.left-(user.original_image.get_width()/4)),copy.copy(user.selfrect.top-(user.original_image.get_height()/4)),copy.copy(level_item_stats[level][0][0]))
        list_objects.append(new_barrier)
        old_barrier = user.energy_item
        try:
            list_objects.remove(old_barrier)
        except ValueError:
            pass
        user.energy_item = new_barrier
        user.item = None

    # Minigun
    elif user.item == "minigun":
        # Replace item with instance of minigun
        user.item = minigun(user,copy.copy(level_item_stats[level][1][0]),copy.copy(level_item_stats[level][1][1]),copy.copy(level_item_stats[level][1][2]),copy.copy(level_item_stats[level][1][3]))
    elif type(user.item) == minigun:
        if user.item.cooldown > 0:
            user.item.cooldown -= 1
        elif user.item.ammo > 0:
            # Take a shot
            shot = None
            if type(user) == player:
                # Toward mouse if player user
                # Note that for any direction to mouse or player, we scale by inverse of screen size change (true for all objects like this)
                shot = bullet(user,user.selfrect.centerx,user.selfrect.centery,user.item.health,user.item.speed,[(mouse[0]-user.selfrect.centerx)*(initial_display[0]/current_display[0]),(mouse[1]-user.selfrect.centery)*(initial_display[1]/current_display[1])])
            else:
                # Toward player if enemy user
                shot = bullet(user,user.selfrect.centerx,user.selfrect.centery,user.item.health,user.item.speed,[(player_object.selfrect.centerx-user.selfrect.centerx)*(initial_display[0]/current_display[0]),(player_object.selfrect.centery-user.selfrect.centery)*(initial_display[1]/current_display[1])])
            list_objects.append(shot)
            # And reset cooldown 
            user.item.ammo -= 1
            user.item.cooldown = user.item.initial_cooldown
        else:
            user.item = None

    # Timestop
    elif user.item == "timestop":
        # Replace item with instance of timestop
        # Timestop is one and done operation
        user.item = timestop(user,copy.copy(level_item_stats[level][2][0]))
        # Spawns this brief graphic to indicate it
        new_graphic = text('timestop_graphic.png',user.selfrect.left,user.selfrect.top,0,current_time+0.1,True)
        list_objects.append(new_graphic)
        # Scale graphic to screen size
        new_graphic.image = pg.transform.scale(new_graphic.original_image, ((current_display[0]/initial_display[0])*new_graphic.original_image.get_width(),(current_display[1]/initial_display[1])*new_graphic.original_image.get_height()))

    # Grenade Launcher
    elif user.item == "grenade launcher":
        # Replace item with instance of grenade_launcher
        user.item = grenade_launcher(user,copy.copy(level_item_stats[level][3][0]),copy.copy(level_item_stats[level][3][1]),copy.copy(level_item_stats[level][3][2]),copy.copy(level_item_stats[level][3][3]),copy.copy(level_item_stats[level][3][4]),copy.copy(level_item_stats[level][3][5]))
    elif type(user.item) == grenade_launcher:
        if user.item.cooldown > 0:
            user.item.cooldown -= 1
        elif user.item.ammo > 0:
            # Take a shot
            shot = None
            if type(user) == player:
                # Toward mouse if player user
                shot = grenade(user,user.selfrect.centerx,user.selfrect.centery,user.item.health,user.item.speed,[(mouse[0]-user.selfrect.centerx)*(initial_display[0]/current_display[0]),(mouse[1]-user.selfrect.centery)*(initial_display[1]/current_display[1])],user.item.timer,user.item.radius)
            else:
                # Toward player if enemy user
                shot = grenade(user,user.selfrect.centerx,user.selfrect.centery,user.item.health,user.item.speed,[(player_object.selfrect.centerx-user.selfrect.centerx)*(initial_display[0]/current_display[0]),(player_object.selfrect.centery-user.selfrect.centery)*(initial_display[1]/current_display[1])],user.item.timer,user.item.radius)
            list_objects.append(shot)        
            # And reset cooldown 
            user.item.ammo -= 1
            user.item.cooldown = user.item.initial_cooldown
        else:
            user.item = None

    # Energy absorber
    elif user.item == "energy absorber":
        new_absorber = energy_absorber(user,copy.copy(user.selfrect.left-(user.original_image.get_width()/4)),copy.copy(user.selfrect.top-(user.original_image.get_height()/4)),copy.copy(level_item_stats[level][4][0]),copy.copy(level_item_stats[level][4][1]))
        list_objects.append(new_absorber)
        old_absorber = user.energy_item
        try:
            list_objects.remove(old_absorber)
        except ValueError:
            pass
        user.energy_item = new_absorber
        user.item = None
        
    else:
        pass
    return list_objects


def check_timestop(active_objects):
    # Timestop needs to check for players/enemies with active timestops (as timestop not in active objects)
    for item in active_objects:
        if isinstance(item,player) or isinstance(item,enemy):
            if isinstance(item.item,timestop):
                if item.item.active:
                    item.item.stop_time(active_objects)

def update_current_position(active_objects):
    # Function needed for timestop to work smoothly
    for item in active_objects:
        if isinstance(item,bullet) or isinstance(item,grenade) or isinstance(item,enemy) or isinstance(item,player) or isinstance(item,energy_barrier) or isinstance(item,energy_absorber):
            # Update current x/y for selected classes
            item.currentx = item.selfrect.left
            item.currenty = item.selfrect.top
    

def isCollision(x,y):
    if not(isinstance(x,explosion) or isinstance(y,explosion) or isinstance(x,sensor) or isinstance(y,sensor)):
        return pg.Rect.colliderect(x.selfrect,y.selfrect)
    else:
        # If explosion or sensor do collision based on smaller side of each object
        # We compare distance between centers against the sum of their smaller length
        # It's not perfect but the most accurate I can get it without being overly complicated
        if math.hypot(x.selfrect.centerx-y.selfrect.centerx,x.selfrect.centery-y.selfrect.centery) <= (min((x.image.get_width()/2),(x.image.get_height()/2))+min((y.image.get_width()/2),(y.image.get_height()/2))):
            return True
        else:
            return False


def hitsBorder(given_object,speed,direction):
    # Returns true if given_object will hit border at given speed/direction
    # Get border dimensions
    border_width = pg.display.get_surface().get_width()
    border_height = pg.display.get_surface().get_height()
    # Get dimensions of object in its new location
    future_left = given_object.selfrect.left + speed[0]*direction[0]
    future_right = given_object.selfrect.right + speed[0]*direction[0]
    future_top = given_object.selfrect.top + speed[1]*direction[1]
    future_bottom = given_object.selfrect.bottom + speed[1]*direction[1]
    # If in boundary return false (i.e. won't go outside border)
    if future_left >= 0:
        if future_right <= border_width:
            if future_top >= 0:
                if future_bottom <= border_height:
                    return False
    return True

def update_objects_display(list_objects,indicator=""):
    # Updates display of objects by iterating through given list and pasting image onto their rects
    # Will sort given list first into order specified (use dict so we can specify text to data type)
    # Note that overlayed text and buttons are pasted after all other objects
    order_wanted = {
        "background" : background,
        "sensor" : sensor,
        "button" : button,
        "text" : text,
        "collectable item" : collectable_item,
        "player" : player,
        "enemy" : enemy,
        "energy barrier" : energy_barrier,
        "energy absorber" : energy_absorber,
        "bullet" : bullet,
        "grenade" : grenade,
        "explosion" : explosion,
        "fawn collectable" : fawn_collectable
        }
    sorted_list_objects = []
    # Uses a double for loop so slow af but easy to program/reorder to the order we want to blit
    for each_type in order_wanted:
        for item in list_objects:
            if isinstance(item,order_wanted[each_type]):
                if each_type == "sensor":
                    # Only blit sensor if set to active and indicator is freeze
                    if (item.active == True) and (indicator == "freeze"):
                        sorted_list_objects.append(item)
                elif (each_type == "text") or (each_type == "button"):
                    # Only add text and buttons now if overlay is false
                    if item.overlay == False:
                        sorted_list_objects.append(item)
                # There's a glitch with energy shields/fawns with no living user being blited so this remedies it
                elif (each_type == "energy barrier") or (each_type == "energy absorber") or (each_type == "fawn collectable"):
                    if item.user in list_objects:
                        sorted_list_objects.append(item)
                else: 
                    sorted_list_objects.append(item)
    # Check for any overlay text and buttons (they get added last)
    for item in list_objects:
        if isinstance(item,text) or isinstance(item,button):
            if item.overlay == True:
                sorted_list_objects.append(item)
    
    # Now blit objects
    # Call pg.display.update() outside of function in case of other display functions
    for sprite in sorted_list_objects:
        screen.blit(sprite.image,sprite.selfrect)

def update_screen_scaling(size,w,h,all_sprites,initial=True):
    # Function to update scaling of sprites/background etc. if screen size changed
    # Uses initial coordinates/sprite size
    global current_display
    screen = pg.display.set_mode(size, HWSURFACE | DOUBLEBUF | RESIZABLE)
    for item in all_sprites:
        # Update image proportions
        if isinstance(item,explosion) or isinstance(item,sensor):
            # Objects that work with a radius need updating differently
            item.radius[0] = item.radius[0]*(w/current_display[0])
            item.radius[1] = item.radius[1]*(h/current_display[1])
            item.original_image = pg.transform.scale(item.original_image, (item.radius[0]*2, item.radius[1]*2))
            item.image = pg.transform.scale(item.image, (item.radius[0]*2, item.radius[1]*2))
        else:
            item.image = pg.transform.scale(item.original_image, ((w/initial_display[0])*item.original_image.get_width(),(h/initial_display[1])*item.original_image.get_height()))
        # Update coordinates
        if (not (isinstance(item,fawn_collectable) or isinstance(item,sensor) or isinstance(item,collectable_item) or isinstance(item,player) or isinstance(item,enemy) or isinstance(item,energy_barrier) or isinstance(item,grenade) or isinstance(item,bullet) or isinstance(item,energy_absorber) or isinstance(item,explosion))) or initial:
            # This works for stationary objects
            # Moving objects need the initial_display movement first and then current display one (use initial parameter to control this)
            item.selfrect = item.image.get_rect(topleft=((w/initial_display[0])*item.initialx,(h/initial_display[1])*item.initialy))
        else:
            # This works for moving objects
            item.selfrect = item.image.get_rect(topleft=((w/current_display[0])*item.selfrect.left,(h/current_display[1])*item.selfrect.top))
        # Update current position for each item as well (incase screensize changed during timestop)
        update_current_position([item])
        # We also update speed of moving objects
        if isinstance(item,player) or isinstance(item,enemy):
            item.speed[0] = item.initial_speed[0]*(w/initial_display[0])
            item.speed[1] = item.initial_speed[1]*(h/initial_display[1])
            # Update mingun and grenade_launcher as well if held and active
            if isinstance(item.item,minigun) or isinstance(item.item,grenade_launcher):
                item.item.speed[0] = item.item.initial_speed[0]*(w/initial_display[0])
                item.item.speed[1] = item.item.initial_speed[1]*(h/initial_display[1])
    # Finally replace current_display with new one
    current_display = (pg.display.get_surface().get_width(),pg.display.get_surface().get_height())


def check_key_press(event,held_keys):
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_a:
            held_keys.append('left')
        elif event.key == pg.K_d:
            held_keys.append('right')
        elif event.key == pg.K_s:
            held_keys.append('down')
        elif event.key == pg.K_w:
            held_keys.append('up')
        elif event.key == pg.K_SPACE:
            held_keys.append('item')
    if event.type == pg.KEYUP:
        if (event.key == pg.K_a) and ('left' in held_keys):
            held_keys.remove('left')
        elif (event.key == pg.K_d) and ('right' in held_keys):
            held_keys.remove('right')
        elif (event.key == pg.K_s) and ('down' in held_keys):
            held_keys.remove('down')
        elif (event.key == pg.K_w) and ('up' in held_keys):
            held_keys.remove('up')
        elif (event.key == pg.K_SPACE) and ('item' in held_keys):
            held_keys.remove('item')
    return held_keys


def check_player_movement(this_player,held_keys,all_objects,mouse,level,current_time):
    # Player movement
    if isinstance(this_player,player):
        if 'left' in held_keys:
            this_player.move_left()
        if 'right' in held_keys:
            this_player.move_right()
        if 'down' in held_keys:
            this_player.move_down()
        if 'up' in held_keys:
            this_player.move_up()
        if 'item' in held_keys:
            all_objects = use_item(this_player,all_objects,mouse,this_player,level,current_time)
    return all_objects


def get_active_objects(all_objects,elapsed_time):
    # If something dies etc. remove it from complete list of objects. Active just shows what objects should be considered at that immediate time
    active = []
    for item in all_objects:
        if isinstance(item,enemy) or isinstance(item,collectable_item):
            if elapsed_time >= item.time_until_spawn:
                # Active when timer exceeds variable
                active.append(item)
        elif isinstance(item,text):
            if elapsed_time > item.time_to_add and item.time_to_remove > elapsed_time:
                # Add temporary text if in given time frame
                active.append(item)
        else:
            active.append(item)
        # Also check for incoming enemies within the next second so we can indicate with red circle
        if isinstance(item,enemy):
            # (int(elapsed_time*15))%2==0 gives flashing effect of circle
            if (elapsed_time + 1 > item.time_until_spawn > elapsed_time) and ((int(elapsed_time*15))%2==0):
                red_circle = text('red_circle.png',item.selfrect.left,item.selfrect.top,0,elapsed_time+0.1)
                active.append(red_circle)
                # Scale image to fit enemy size
                red_circle.original_image = pg.transform.scale(red_circle.original_image, (item.image.get_width(),item.image.get_height()))
                red_circle.image = pg.transform.scale(red_circle.image, (item.image.get_width(),item.image.get_height()))
    return active


def fight_end_conditions(current_time,time_limit,active_objects,fight_objects):
    # Check end conditions for fight game mode. Return win and run as boolean
    win = False
    run = True

    # Check if a player object is active - if not then lose
    # Also check if no enemies left - then win
    is_player = False
    is_enemy = False
    for item in fight_objects:
        if isinstance(item,player):
            is_player = True
        if isinstance(item,enemy):
            is_enemy = True
    if is_player == False:
        run = False
    elif is_enemy == False:
        run = False
        win = True 

    # Check clock - lose condition
    if time_limit <= current_time:
        run = False

    return win, run

def flight_end_conditions(current_time,time_limit,active_objects,flight_objects):
    # Check end conditions for flight game mode. Return win and run as boolean
    win = False
    run = True

    # Check if a player object is active - if not then lose
    # Also check if no enemies left - then win
    is_player = False
    is_enemy = False
    for item in flight_objects:
        if isinstance(item,player):
            is_player = True
        if isinstance(item,enemy):
            is_enemy = True
    if is_player == False:
        run = False
    elif is_enemy == False:
        run = False
        win = True

    # Check clock - win condition
    if time_limit <= current_time:
        run = False
        win = True

    return win, run

def freeze_end_conditions(current_time,time_limit,active_objects,freeze_objects):
    # Check end conditions for freeze game mode. Return win and run as boolean
    win = False
    run = True

    # Check if a player object is active - if not then lose
    # Also check if no enemies left - then win
    is_player = False
    is_enemy = False
    for item in freeze_objects:
        if isinstance(item,player):
            is_player = True
        if isinstance(item,enemy):
            is_enemy = True
    if is_player == False:
        run = False
    elif is_enemy == False:
        run = False
        win = True

    # Check clock - win condition
    if time_limit <= current_time:
        run = False
        win = True

    return win, run

def fawn_end_conditions(current_time,time_limit,active_objects,fawn_objects):
    # Check end conditions for fawn game mode. Return win and run as boolean
    win = False
    run = True

    # Check if a player object is active - if not then lose
    # Also check if no enemies left - then win
    is_player = False
    is_enemy = False
    for item in fawn_objects:
        if isinstance(item,player):
            is_player = True
        if isinstance(item,enemy):
            is_enemy = True
    if is_player == False:
        run = False
    elif is_enemy == False:
        run = False
        win = True

    # Check clock - lose condition if not all enemies fawned
    if time_limit <= current_time:
        run = False

    return win, run


def play_music(given_track):
    global current_music
    if not music_on:
        mixer.music.unload()
    elif (given_track != current_music) or (mixer.music.get_busy()==False):
        mixer.music.unload()
        if given_track != None:
            mixer.music.load(given_track)
            if music_on == True:
                mixer.music.play(-1)  # -1 puts background music on loop
    current_music = given_track


def play_sfx(given_sound):
    if sfx_on:
        # Finds an empty or over-used channel to play given sfx on
        mixer.find_channel(True).play(mixer.Sound(given_sound))

def get_sensors(all_objects,active_objects):
    # Get sensors for enemies without one and move existing ones
    # Sensor parameters: user,x,y,radius,detection=False
    to_remove = []
    for item in active_objects:
        if isinstance(item,enemy):
            if item.sensor_obj == None:
                # Create sensor for enemy if doesn't have one
                all_objects.append(sensor(item,copy.copy(item.selfrect.left),copy.copy(item.selfrect.top),copy.copy(item.sensor_radius)))
            else:
                # Otherwise move existing one
                item.sensor_obj.selfrect.move_ip(item.selfrect.left-item.sensor_obj.selfrect.left-(item.sensor_obj.radius[0]-item.image.get_width()/2),item.selfrect.top-item.sensor_obj.selfrect.top-(item.sensor_obj.radius[1]-item.image.get_height()/2))
            if item.sensor_obj.detection == True:
                # Set active to false if already detected
                item.sensor_obj.active = False
        if isinstance(item,sensor):
            if item.user not in all_objects:
                # Remove sensor if user has died
                to_remove.append(item)
    # Clear rubbish
    for rubbish in to_remove:
        all_objects.remove(rubbish)
    return all_objects

def check_sensor_movement(active_objects,player_object):
    # Check if active sensor collides with player and player has moved this turn
    for item in active_objects:
        if isinstance(item,sensor):
            if item.active == True:
                if (isCollision(item,player_object)) and ((player_object.selfrect.left != player_object.currentx) or (player_object.selfrect.top != player_object.currenty)):
                    # If detection, set to true and change enemy attributes like so
                    play_sfx('detection_sfx.mp3')
                    item.detection = True
                    item.user.movement_type = "to_player"
                    if (item.user.speed[0] > 1) and (item.user.speed[1] > 1):
                        # For enemies that move around at high speed, normalised direction
                        item.user.speed[0] *= 2
                        item.user.speed[1] *= 2
                        item.user.initial_speed[0] *= 2
                        item.user.initial_speed[1] *= 2
                    else:
                        # For enemies that move at low speed/zero speed
                        item.user.speed[0] = 10
                        item.user.speed[1] = 10
                        item.user.initial_speed[0] = 10
                        item.user.initial_speed[1] = 10
                    item.user.item_rate *= 0.5
                    item.user.ability_rate *= 0.5


def spawn_fawn(all_objects,enemy_obj,player_obj):
    # Spawn a fawn collectable for the given enemy not too close to player
    new_x = random.randint(0,760)
    new_y = random.randint(0,410)
    while isNear(player_obj.selfrect.left,new_x*(current_display[0]/initial_display[0]),player_obj.selfrect.top,new_y*(current_display[0]/initial_display[0]),200):
        new_x = random.randint(0,760)
        new_y = random.randint(0,410)
    new_fawn = fawn_collectable(enemy_obj,new_x,new_y)
    # Scale image/rect
    new_fawn.image = pg.transform.scale(new_fawn.original_image, ((current_display[0]/initial_display[0])*new_fawn.original_image.get_width(),(current_display[1]/initial_display[1])*new_fawn.original_image.get_height()))
    new_fawn.selfrect = new_fawn.image.get_rect(topleft=((current_display[0]/initial_display[0])*new_fawn.initialx,(current_display[1]/initial_display[1])*new_fawn.initialy))
    # And add it to all_objects
    all_objects.append(new_fawn)
    return all_objects
                    

# Create main functions
def menu_loop(menu_objects,menu_music=None,indicator=None):
    # Main loop for menu screens. Just pass through menu objects (including background) and music
    play_music(menu_music)
    # Adjust screen display initially
    if indicator != "pause":
        update_screen_scaling(pg.display.get_surface().get_size(),pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),menu_objects)
    else:
        # Pause menu can reset game objects if initial is true
        update_screen_scaling(pg.display.get_surface().get_size(),pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),menu_objects,False)
    clock = pg.time.Clock()
    run = True
    while run:
        mouse = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == VIDEORESIZE:
                update_screen_scaling(event.dict['size'],event.dict['w'],event.dict['h'],menu_objects,False)
            if event.type == pg.QUIT:
                save_game()
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                for this_object in menu_objects:
                    if isinstance(this_object,button):
                        if this_object.pressed(mouse):
                            play_sfx('button_click.mp3')
                            if this_object.function == "go_back":
                                # Break loop if button's function was go_back
                                run = False
                            elif (this_object.function == "go_double_back") and (indicator=="pause"):
                                # Return false if select campaign screen button on pause menu (returns false to game function which returns None there)
                                return False
                            else:
                                # Otherwise perform function and update screen after
                                this_object.perform_function()
                                if indicator == "campaign":
                                    # Need to update display if campaign so levels update automatically
                                    menu_objects = update_campaign_menu()
                                if indicator == "main_menu":
                                    # Need to update music button display if changed during a game
                                    if music_on == True:
                                        menu_objects[-2].original_image_name = "music_on.png"
                                        menu_objects[-2].original_image = pg.image.load('music_on.png')
                                    else:
                                        menu_objects[-2].original_image_name = "music_off.png"
                                        menu_objects[-2].original_image = pg.image.load('music_off.png')
                                    if sfx_on == True:
                                        menu_objects[-1].original_image_name = "sfx_on.png"
                                        menu_objects[-1].original_image = pg.image.load('sfx_on.png')
                                    else:
                                        menu_objects[-1].original_image_name = "sfx_off.png"
                                        menu_objects[-1].original_image = pg.image.load('sfx_off.png')
                                        
                                update_screen_scaling(pg.display.get_surface().get_size(),pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),menu_objects,False)
        # Update display
        update_objects_display(menu_objects)
        pg.display.update()
        # And music
        play_music(menu_music)
        # And clock tick
        clock.tick(60)

        
def play_game(all_objects,time_limit,given_music,level,indicator=""):
    global endless_fight_high_score
    global endless_flight_high_score
    global endless_freeze_high_score
    global endless_fawn_high_score
    play_music(given_music)
    # Add temporary indicator text to all_objects
    indicator_text = text(indicator+"_text.png",275,100,0,1,True)
    all_objects.append(indicator_text)
    # Adjust screen display initially
    active_objects = get_active_objects(all_objects,0)
    update_screen_scaling(pg.display.get_surface().get_size(),pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),all_objects)
    # Set starting values
    held_keys = []
    start_time = time.time()
    paused_time = 0
    score = 0
    clock = pg.time.Clock()
    run = True
    win = False
    while run:
        # Main loop here
        mouse = pg.mouse.get_pos()
        current_time = time.time()-start_time-paused_time
        active_objects = get_active_objects(all_objects,current_time)                
        update_current_position(active_objects)
        
        # We add timer, score and highscore manually as simple static text. It won't be included with screenscaling so we reassign text size etc. each time and put it at (0,0)
        ui_font = pg.font.Font('freesansbold.ttf',int(24*(math.sqrt((pg.display.get_surface().get_width()**2)+(pg.display.get_surface().get_height()**2))/math.sqrt((initial_display[0]**2)+(initial_display[1]**2)))))
        timer = ui_font.render("Timer: " + str("%.2f" % max(0,(time_limit-current_time))),True,(255,255,255))
        score_text = ui_font.render("Score: " + str(score),True,(255,255,255))
        highscore = ui_font.render("",True,(255,255,255))
        if level == "endless_fight":
            highscore = ui_font.render("Highscore: " + str(endless_fight_high_score),True,(255,255,255))
        elif level == "endless_flight":
            highscore = ui_font.render("Highscore: " + str(endless_flight_high_score),True,(255,255,255))
        elif level == "endless_freeze":
            highscore = ui_font.render("Highscore: " + str(endless_freeze_high_score),True,(255,255,255))
        elif level == "endless_fawn":
            highscore = ui_font.render("Highscore: " + str(endless_fawn_high_score),True,(255,255,255))
        if len(level) >= 8:
            if level[:8] == "endless_":
                # Change timer to incrementing one if endless mode
                timer = ui_font.render("Timer: " + str("%.2f" % (current_time)),True,(255,255,255))
        # We also add current item and info to item box and update current health box
        # Player stored in index 1
        item_image = None
        item_font = pg.font.Font('freesansbold.ttf',int(8*(math.sqrt((pg.display.get_surface().get_width()**2)+(pg.display.get_surface().get_height()**2))/math.sqrt((initial_display[0]**2)+(initial_display[1]**2)))))
        health_font = pg.font.Font('freesansbold.ttf',int(28*(math.sqrt((pg.display.get_surface().get_width()**2)+(pg.display.get_surface().get_height()**2))/math.sqrt((initial_display[0]**2)+(initial_display[1]**2)))))
        # First get health info
        health_info = health_font.render(str(all_objects[1].health)+"/"+str(all_objects[1].max_health),True,(255,255,255))       
        # Now get item info
        item_info = item_font.render("",True,(255,255,255))
        # First check for instance of barrier or absorber around player
        for item in active_objects:
            if isinstance(item,energy_absorber):
                if isinstance(item.user,player):
                    item_image = pg.image.load('energy_absorber_item.png')
                    item_info = ui_font.render(str(item.absorbed_health)+"/"+str(item.max_health),True,(255,255,255))
            if isinstance(item,energy_barrier):
                if isinstance(item.user,player):
                    item_image = pg.image.load('energy_barrier_item.png')
                    item_info = ui_font.render(str(item.health)+"/"+str(item.max_health),True,(255,255,255))
        # Then either pass if no item or overwrite with new one
        if all_objects[1].item == None:
            pass
        elif isinstance(all_objects[1].item,minigun):
            item_image = pg.image.load('minigun_item.png')
            item_info = ui_font.render(str(all_objects[1].item.ammo)+"/"+str(all_objects[1].item.max_ammo),True,(255,255,255))
        elif (all_objects[1].item == "minigun"):
            item_image = pg.image.load('minigun_item.png')
            item_info = ui_font.render(str(level_item_stats[level][1][0])+"/"+str(level_item_stats[level][1][0]),True,(255,255,255))
        elif isinstance(all_objects[1].item,grenade_launcher):
            item_image = pg.image.load('grenade_launcher_item.png')
            item_info = ui_font.render(str(all_objects[1].item.ammo)+"/"+str(all_objects[1].item.max_ammo),True,(255,255,255))
        elif (all_objects[1].item == "grenade launcher"):
            item_image = pg.image.load('grenade_launcher_item.png')
            item_info = ui_font.render(str(level_item_stats[level][3][0])+"/"+str(level_item_stats[level][3][0]),True,(255,255,255))
        elif isinstance(all_objects[1].item,timestop):
            item_image = pg.image.load('timestop_item.png')
            item_info = ui_font.render(str(all_objects[1].item.duration)+"/"+str(all_objects[1].item.max_duration),True,(255,255,255))
        elif (all_objects[1].item == "timestop"):
            item_image = pg.image.load('timestop_item.png')
            item_info = ui_font.render(str(level_item_stats[level][2][0])+"/"+str(level_item_stats[level][2][0]),True,(255,255,255))
        elif (all_objects[1].item == "energy barrier"):
            item_image = pg.image.load('energy_barrier_item.png')
            item_info = ui_font.render(str(level_item_stats[level][0][0])+"/"+str(level_item_stats[level][0][0]),True,(255,255,255))
        elif (all_objects[1].item == "energy absorber"):
            item_image = pg.image.load('energy_absorber_item.png')
            item_info = ui_font.render("0/"+str(level_item_stats[level][4][1]),True,(255,255,255))
            
        # Check events
        for event in pg.event.get():
            if event.type == VIDEORESIZE:
                update_screen_scaling(event.dict['size'],event.dict['w'],event.dict['h'],all_objects,False)
                held_keys = []
            if event.type == pg.QUIT:
                save_game()
                pg.quit()
                sys.exit()
            # Keeping track of pressed keys
            held_keys = check_key_press(event,held_keys)
            if event.type == pg.MOUSEBUTTONDOWN:
                for this_object in active_objects:
                    # Check for button click
                    if isinstance(this_object,button):
                        if this_object.pressed(mouse):
                            play_sfx('button_click.mp3')
                            if this_object.function == "go_back":
                                # Break loop if button's function was go_back
                                run = False
                            elif this_object.function == "go_to_pause_screen":
                                # Pause screen messes with clock so we return how long we're on the screen
                                # Pass through active objects as pause screen will be mini screen (not full on menu)
                                cont, dur = pause_screen(active_objects,given_music)
                                paused_time += dur
                                if cont == False:
                                    # If false is returned, player pressed campaign screen button so immediately terminate game 
                                    return None
                            else:
                                # Otherwise perform function and update screen after
                                this_object.perform_function()
                                update_screen_scaling(pg.display.get_surface().get_size(),pg.display.get_surface().get_width(),pg.display.get_surface().get_height(),all_objects,False)
                            held_keys = []

        # Player stored in index 1
        all_objects = check_player_movement(all_objects[1],held_keys,all_objects,mouse,level,current_time)

        # Do enemy movement (from active list)
        all_objects, score, indicator = do_enemy_movement(active_objects,all_objects[1],all_objects,mouse,level,current_time,score,indicator)

        # Do item movement (from active list)
        all_objects = do_item_movement(all_objects,active_objects)

        # Check for timestop to overwrite any changes where needed
        check_timestop(active_objects)

        # Check for collisions
        all_objects, score = do_collisions(all_objects,active_objects,score)

        # Check for end condition and gamemode specific functions
        if indicator == "":
            pass
        elif indicator == "fight":
            win, run = fight_end_conditions(current_time,time_limit,active_objects,all_objects)
        elif indicator == "flight":
            win, run = flight_end_conditions(current_time,time_limit,active_objects,all_objects)
        elif indicator == "freeze":
            all_objects = get_sensors(all_objects,active_objects)
            if isinstance(all_objects[1],player):
                # Player may be removed prior to calling this so check for isinstance first
                check_sensor_movement(active_objects,all_objects[1])
            win, run = freeze_end_conditions(current_time,time_limit,active_objects,all_objects)
        elif indicator == "fawn":
            # Fawn collectable is dealt with in enemy_movement()
            win, run = fawn_end_conditions(current_time,time_limit,active_objects,all_objects)

        # Output objects display
        update_objects_display(active_objects,indicator)
        # Output scores/timer
        screen.blit(timer,(0,0))
        screen.blit(score_text,(260*(current_display[0]/initial_display[0]),0))
        screen.blit(highscore,(520*(current_display[0]/initial_display[0]),0))
        # Output item box data
        if item_image != None:
            item_image = pg.transform.scale(item_image, ((current_display[0]/initial_display[0])*item_image.get_width(),(current_display[1]/initial_display[1])*item_image.get_height()))
            screen.blit(item_image,(158*(current_display[0]/initial_display[0]),415*(current_display[1]/initial_display[1])))
        screen.blit(item_info,(200*(current_display[0]/initial_display[0]),420*(current_display[1]/initial_display[1])))
        screen.blit(health_info,(30*(current_display[0]/initial_display[0]),420*(current_display[1]/initial_display[1])))
        # Update display
        pg.display.update()
        # And music
        play_music(given_music)
        # And deal with clock
        clock.tick(60)
    # If new record, change global variable
    if (level == "endless_fight") and (score > endless_fight_high_score):
        endless_fight_high_score = score
    elif (level == "endless_flight") and (score > endless_flight_high_score):
        endless_flight_high_score = score
    elif (level == "endless_freeze") and (score > endless_freeze_high_score):
        endless_freeze_high_score = score
    elif (level == "endless_fawn") and (score > endless_fawn_high_score):
        endless_fawn_high_score = score
    # Return outcome
    return win
                


def main_menu():
    # Define objects for main menu (append in order we wish to include them on screen)
    main_menu_objects = []
    main_menu_objects.append(background('menu_background.png'))
    main_menu_objects.append(text('main_title.png',250,90))
    main_menu_objects.append(button('campaign_button.png',20,30,"go_to_campaign_menu"))
    main_menu_objects.append(button('endless_button.png',20,135,"go_to_endless_menu"))
    main_menu_objects.append(button('controls_button.png',20,240,"go_to_controls_menu"))
    main_menu_objects.append(button('quit_button.png',20,345,"quit_program"))
    music_image = 'music_on.png'
    sfx_image = 'sfx_on.png'
    if music_on == False:
        music_image = 'music_off.png'
    if sfx_on == False:
        sfx_image = 'sfx_off.png'
    main_menu_objects.append(button(music_image,650,0,"toggle_music"))
    main_menu_objects.append(button(sfx_image,725,0,"toggle_sfx"))

    # Start loop for the menu
    menu_loop(main_menu_objects,'main_theme.mp3',"main_menu")


def campaign_menu():
    # Define objects for campaign menu (append in order we wish to include them on screen)
    campaign_menu_objects = update_campaign_menu()
    # Start loop for the menu
    menu_loop(campaign_menu_objects,'main_theme.mp3',"campaign")


def get_main_campaign_display():
    # Gets all objects that are not level buttons for campaign menu
    campaign_menu_objects = []
    campaign_menu_objects.append(background('menu_background.png'))
    campaign_menu_objects.append(text('campaign_text.png',20,10))
    campaign_menu_objects.append(button('back_button.png',720,20,"go_back"))
    return campaign_menu_objects


def get_level_buttons():
    # Get layout for campaign level buttons
    level_buttons = []
    level_counter = 1
    for i in range(0,5):
        newy = 105+(60*i)
        for j in range(0,10):
            newx = 35+(50*j)
            if j == 9:
                # Boss levels are moved slightly further along
                newx = 585
            if level_counter < current_level_unlock:
                level_buttons.append(button('level_complete_button.png',newx,newy,"play_level_"+str(level_counter)))
            elif level_counter == current_level_unlock:
                level_buttons.append(button('active_level_button.png',newx,newy,"play_level_"+str(level_counter)))
            else:
                level_buttons.append(button('level_locked_button.png',newx,newy,None))
            level_counter += 1
    return level_buttons


def update_campaign_menu():
    campaign_menu_objects = get_main_campaign_display()
    # Use loop to add level select buttons at the end
    level_buttons = get_level_buttons()
    for item in level_buttons:
        campaign_menu_objects.append(item)
    return campaign_menu_objects
    

    
def controls_menu():
    # Define objects for controls menu (append in order we wish to include them on screen)
    controls_menu_objects = []
    controls_menu_objects.append(background('menu_background.png'))
    controls_menu_objects.append(text('controls_text.png',20,10))
    controls_menu_objects.append(button('back_button.png',720,20,"go_back"))
    controls_menu_objects.append(text('wasd.png',20,120))
    controls_menu_objects.append(text('move_text.png',200,120))
    controls_menu_objects.append(text('mouse.png',450,120))
    controls_menu_objects.append(text('aim_text.png',540,125))
    controls_menu_objects.append(text('spacebar.png',200,280))
    controls_menu_objects.append(text('use_item_text.png',350,255))
    
    # Start loop for the menu
    menu_loop(controls_menu_objects,'main_theme.mp3')

    
def endless_menu():
    # Define objects for endless menu (append in order we wish to include them on screen)
    endless_menu_objects = []
    endless_menu_objects.append(background('menu_background.png'))
    endless_menu_objects.append(text('endless_text.png',15,10))
    endless_menu_objects.append(button('back_button.png',720,20,"go_back"))
    endless_menu_objects.append(button('fight_button.png',100,100,"endless_fight"))
    endless_menu_objects.append(button('flight_button.png',500,100,"endless_flight"))
    endless_menu_objects.append(button('freeze_button.png',100,300,"endless_freeze"))
    endless_menu_objects.append(button('fawn_button.png',500,300,"endless_fawn"))
    
    # Start loop for the menu
    menu_loop(endless_menu_objects,'main_theme.mp3')

    
def victory_screen():
    # Define objects for victory screen (append in order we wish to include them on screen)
    victory_objects = []
    victory_objects.append(background('victory_background.png'))
    victory_objects.append(text('victory_text.png',100,10))
    victory_objects.append(button('back_to_menu.png',300,280,"go_back"))

    # Start loop for the menu
    menu_loop(victory_objects,'victory_music.mp3')

    
def game_over_screen():
    # Define objects for game over screen (append in order we wish to include them on screen)
    game_over_objects = []
    game_over_objects.append(background('game_over_background.png'))
    game_over_objects.append(text('game_over_text.png',100,10))
    game_over_objects.append(button('back_to_menu.png',300,280,"go_back"))


    # Start loop for the menu
    menu_loop(game_over_objects,'game_over_music.mp3')


def pause_screen(background_objects,given_music):
    starting_time = time.time()
    # We render background objects and on top of it the pause menu
    pause_objects = background_objects
    pause_objects.append(text('pause_menu.png',150,50,0,math.inf,True))
    pause_objects.append(text('paused_text.png',200,10,0,math.inf,True))
    pause_objects.append(button('resume.png',170,250,"go_back",True))
    pause_objects.append(button('back_to_menu.png',430,250,"go_double_back",True))
    music_image = 'music_on.png'
    sfx_image = 'sfx_on.png'
    if music_on == False:
        music_image = 'music_off.png'
    if sfx_on == False:
        sfx_image = 'sfx_off.png'
    pause_objects.append(button(music_image,325,180,"toggle_music",True))
    pause_objects.append(button(sfx_image,400,180,"toggle_sfx",True))

    # Start loop for pause menu
    run = menu_loop(pause_objects,given_music,"pause")

    # Return time spent paused once done and if we need to go double_back
    return run, time.time() - starting_time



# Create dictionary to map level number to parameters
# Key: Level number to [game_type,player,[list of enemy objects],time_limit,background,music,[list of collectable items]]
# Enemy parameters: enemy_type,health,item,x,y,speed,direction,time_until_spawn,movement_type,item_rate,ability_rate,sensor_radius,fawn_timer
global levels
levels = {
    "1" : ["flight",player('player.png',1,None,350,225,[5,5]),[enemy('classic',1,None,100,100,[4,4],[-1,1],2,"random"),enemy('classic',1,None,100,100,[3,3],[1,1],15,"to_player")],20,'world1_background.png','intro_level_music.mp3',[]],
    "2" : ["fight",player('player.png',1,"energy barrier",350,225,[5,5]),[enemy('classic',1,None,50,100,[6,6],[-1,1],0,"away_player"),enemy('classic',1,None,700,300,[6,6],[1,1],0,"away_player"),enemy('classic',1,None,450,200,[4,4],[-1,1],10,"to_player")],20,'world1_background.png','intro_level_music.mp3',[]],
    "3" : ["fight",player('player.png',1,"minigun",350,225,[5,5]),[enemy('classic',1,"energy barrier",50,300,[3,3],[0,1],0,"random"),enemy('classic',1,None,650,100,[3,3],[-1,1],0,"to_player")],15,'world1_background.png','intro_level_music.mp3',[]],
    "4" : ["flight",player('player.png',1,None,350,225,[5,5]),[enemy('classic',1,"minigun",50,100,[6,6],[-1,1],0,"random",5)],10,'world1_background.png','intro_level_music.mp3',[]],
    "5" : ["fight",player('player.png',1,"minigun",350,225,[5,5]),[enemy('classic',1,"energy absorber",50,100,[4,4],[-1,1],0,"to_player",0)],15,'world1_background.png','intro_level_music.mp3',[]],
    "6" : ["fight",player('player.png',1,"energy absorber",350,225,[5,5]),[enemy('classic',1,"minigun",i*30,100,[8,8],[-1,1],i/2,"to_player",0) for i in range(1,23)],15,'world1_background.png','intro_level_music.mp3',[]],
    "7" : ["flight",player('player.png',1,"timestop",350,380,[5,5]),[enemy('ninja',2,None,i*50,100,[5,5],[-1,1],0,"to_player",0) for i in range(1,15)],3,'world1_background.png','intro_level_music.mp3',[]],
    "8" : ["flight",player('player.png',1,None,50,225,[5,5]),[enemy('classic',2,"timestop",700,i*75,[3,3],[-1,1],0,"to_player",1000) for i in range(1,5)],15,'world1_background.png','intro_level_music.mp3',[collectable_item("timestop",370,200,300,10)]],
    "9" : ["fight",player('player.png',1,"energy absorber",350,225,[5,5]),[enemy('classic',10,"grenade launcher",700,100,[8,8],[-1,1],0,"away_player",0),enemy('ninja',200,None,50,100,[8,8],[-1,1],10,"to_player",0)],15,'world1_background.png','intro_level_music.mp3',[]],
    "10" : ["fight",player('player.png',10,"minigun",700,225,[5,5]),[enemy('boss1',150,"grenade launcher",50,225,[6,6],[-1,1],0,"away_player",10,100)],60,'boss1_background.png','boss1_music.mp3',[]],
    "11" : ["freeze",player('player.png',1,None,200,225,[5,5]),[enemy('classic',1,None,600,100,[4,4],[-1,1],0,"random"),enemy('classic',1,None,100,100,[5,5],[1,1],6,"random")],15,'world2_background.png','world2_music.mp3',[]],
    "12" : ["freeze",player('player.png',10,"timestop",200,225,[5,5]),[enemy('ninja',20,"minigun",400,100,[5,5],[1,1],0,"random",2,0,150),enemy('ninja',20,"timestop",700,300,[6,6],[1,-1],0,"random",400,0,75)],20,'world2_background.png','world2_music.mp3',[]],
    "13" : ["freeze",player('player.png',10,None,200,225,[5,5]),[enemy('classic',20,"grenade launcher",500,100,[4,4],[1,1],0,"predictable",3,0,275)],math.inf,'world2_background.png','world2_music.mp3',[collectable_item("minigun",100,200,math.inf,15),collectable_item("minigun",670,200,math.inf,15)]],
    "14" : ["fight",player('player.png',10,"minigun",350,225,[5,5]),[enemy('classic',10,None,550,225,[4,4],[1,1],0,"predictable",3,0,275),enemy('classic',10,None,350,325,[4,4],[1,-1],0,"predictable",3,0,275),enemy('classic',10,None,350,125,[4,4],[-1,1],0,"predictable",3,0,275),enemy('classic',10,None,150,225,[4,4],[-1,-1],0,"predictable",3,0,275)],5,'world2_background.png','world2_music.mp3',[]],
    "15" : ["flight",player('player.png',10,None,350,225,[5,5]),[enemy('classic',10,None,10,10,[2,2],[1,1],0,"to_player",3,0,275),enemy('classic',10,None,10,390,[2,2],[1,-1],0,"to_player",3,0,275),enemy('classic',10,None,740,10,[2,2],[-1,1],0,"to_player",3,0,275),enemy('classic',10,None,740,390,[2,2],[-1,-1],0,"to_player",3,0,275),enemy('classic',10,None,550,225,[3,3],[1,1],0,"to_player",3,0,275),enemy('classic',10,None,350,375,[3,3],[1,-1],0,"to_player",3,0,275),enemy('classic',10,None,350,75,[3,3],[-1,1],0,"to_player",3,0,275),enemy('classic',10,None,150,225,[3,3],[-1,-1],0,"to_player",3,0,275)],5,'world2_background.png','world2_music.mp3',[]],
    "16" : ["fight",player('player.png',10,"minigun",350,225,[5,5]),[enemy('classic',7,"minigun",random.randint(0,740),random.randint(0,390),[i,i],[-1,1],i*2,"random",4) for i in range(1,12)],30,'world2_background.png','world2_music.mp3',[]],
    "17" : ["flight",player('player.png',10,None,350,225,[5,5]),[enemy('ninja',10,None,random.randint(0,740),random.randint(0,390),[8+i,8+i],[-1,1],i*2,"at_player",4) for i in range(1,12)],25,'world2_background.png','world2_music.mp3',[]],
    "18" : ["freeze",player('player.png',10,None,350,225,[5,5]),[enemy('classic',10,"energy absorber",random.randint(0,740),random.randint(0,390),[4,4],[-1,1],i*3,"predictable",0) for i in range(1,4)],20,'world2_background.png','world2_music.mp3',[]],
    "19" : ["fight",player('player.png',10,"energy barrier",350,225,[5,5]),[enemy('classic',8,None,random.randint(0,740),random.randint(0,390),[i,i],[-1,1],i,"predictable",5) for i in range(1,19)],20,'world2_background.png','world2_music.mp3',[]],
    "20" : ["flight",player('player.png',15,None,350,350,[5,5]),[enemy('boss2',500,None,350,10,[3,3],[-1,1],0,"to_player",0,100)],60,'boss2_background.png','boss2_music.mp3',[collectable_item("timestop",370,200,300,i*10) for i in range(1,6)]],
    "21" : ["fawn",player('player.png',15,None,350,350,[5,5]),[enemy('classic',20,None,10,10,[4,4],[-1,1],0,"to_player",0,100,0,300),enemy('classic',20,None,740,10,[5,5],[-1,1],5,"to_player",0,100,0,300)],15,'world3_background.png','world3_music.mp3',[]],
    "22" : ["fight",player('player.png',5,"minigun",350,225,[5,5]),[enemy('classic',5,None,random.randint(0,740),random.randint(0,390),[i+1,i+1],[-1,1],i,"to_player",4) for i in range(1,20)],25,'world3_background.png','world3_music.mp3',[]],
    "23" : ["fawn",player('player.png',15,None,350,350,[5,5]),[enemy('classic',5,None,random.randint(0,740),random.randint(0,390),[6,6],[-1,1],i,"random",0,0,0,180) for i in range(1,14)],20,'world3_background.png','world3_music.mp3',[]],
    "24" : ["flight",player('player.png',15,"timestop",350,225,[5,5]),[enemy('classic',20,"minigun",5,5,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"minigun",5,395,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"minigun",745,5,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"minigun",745,395,[0,0],[0,0],0,"",10,0,0,0)],30,'world3_background.png','world3_music.mp3',[]],
    "25" : ["freeze",player('player.png',15,None,100,225,[5,5]),[enemy('ninja',20,None,700,225,[6,6],[1,1],i**2,"predictable",0,220,150) for i in range(1,4)],15,'world3_background.png','world3_music.mp3',[]],
    "26" : ["fawn",player('player.png',15,None,350,225,[5,5]),[enemy('ninja',20,"minigun",5,5,[0,0],[0,0],0,"",5,0,0,240),enemy('ninja',20,"minigun",745,5,[0,0],[0,0],3,"",5,0,0,240),enemy('ninja',20,"minigun",5,395,[0,0],[0,0],6,"",5,0,0,240),enemy('ninja',20,"minigun",745,395,[0,0],[0,0],9,"",5,0,0,240)],16,'world3_background.png','world3_music.mp3',[]],
    "27" : ["fight",player('player.png',15,"energy absorber",350,225,[1,1]),[enemy('ninja',100,None,350,390,[6,6],[-1,1],5,"random",0,220,150),enemy('ninja',100,None,350,10,[6,6],[-1,1],5,"random",0,220,150),enemy('classic',20,"minigun",5,5,[0,0],[0,0],0,"",3,0,0,0),enemy('classic',20,"minigun",5,395,[0,0],[0,0],0,"",3,0,0,0),enemy('classic',20,"minigun",745,5,[0,0],[0,0],0,"",3,0,0,0),enemy('classic',20,"minigun",745,395,[0,0],[0,0],0,"",3,0,0,0)],15,'world3_background.png','world3_music.mp3',[]],
    "28" : ["flight",player('player.png',15,None,350,225,[5,5]),[enemy('classic',4,None,random.randint(0,740),random.randint(0,390),[6,6],[-1,1],1+(i/4),"at_player",0) for i in range(1,60)],15,'world3_background.png','world3_music.mp3',[]],
    "29" : ["freeze",player('player.png',15,"minigun",350,395,[2,2]),[enemy('classic',20,None,350,5,[6,6],[-1,1],i,"random",0,220,75) for i in range(1,8)],20,'world3_background.png','world3_music.mp3',[]],
    "30" : ["freeze",player('player.png',15,None,350,350,[5,5]),[enemy('boss3',500,None,350,10,[4,4],[-1,1],0,"predictable",0,220,150)],60,'boss3_background.png','boss3_music.mp3',[]],
    "31" : ["fight",player('player.png',15,None,350,350,[5,5]),[enemy('pirate',20,"energy barrier",350,5,[3,3],[-1,1],0,"to_player",0,220,75)],5,'world4_background.png','world4_music.mp3',[collectable_item("minigun",100,300,150,0),collectable_item("grenade launcher",670,300,150,0)]],
    "32" : ["fawn",player('player.png',15,None,350,350,[5,5]),[enemy('classic',5,None,random.randint(0,740),random.randint(0,390),[3,3],[-1,1],(2*i)/3,random.choice(["to_player","away_player","random"]),0,220,75,90) for i in range(2,19)],20,'world4_background.png','world4_music.mp3',[]],
    "33" : ["flight",player('player.png',15,None,350,225,[5,5]),[enemy('classic',20,"minigun",5,5,[0,0],[0,0],1.5,"",2,0,0,0),enemy('classic',20,"minigun",5,395,[0,0],[0,0],1.5,"",2,0,0,0),enemy('classic',20,"minigun",745,5,[0,0],[0,0],1.5,"",2,0,0,0),enemy('classic',20,"minigun",745,395,[0,0],[0,0],1.5,"",2,0,0,0)],14.5,'world4_background.png','world4_music.mp3',[collectable_item("energy barrier",50,225,90,0),collectable_item("timestop",650,225,90,0),collectable_item("minigun",350,25,90,0),collectable_item("grenade launcher",350,395,90,0)]],
    "34" : ["fawn",player('player.png',1,None,25,25,[5,5]),[enemy('pirate',20,"minigun",375,210,[0,0],[0,0],1,"",0,0,0,900),enemy('pirate',20,None,random.randint(0,740),random.randint(0,390),[0,0],[0,0],8,"",0,220,75,0),enemy('pirate',20,None,random.randint(0,740),random.randint(0,390),[0,0],[0,0],8,"",0,220,75,0),enemy('pirate',20,None,random.randint(0,740),random.randint(0,390),[0,0],[0,0],8,"",0,220,75,0),enemy('pirate',20,None,random.randint(0,740),random.randint(0,390),[0,0],[0,0],12,"",0,220,75,0),enemy('pirate',20,None,random.randint(0,740),random.randint(0,390),[0,0],[0,0],12,"",0,220,75,0)],20,'world4_background.png','world4_music.mp3',[]],
    "35" : ["fight",player('player.png',15,"grenade launcher",25,25,[5,5]),[enemy('ninja',5,random.choice([None,"energy absorber"]),random.randint(0,740),random.randint(0,390),[4,4],[-1,1],random.randint(1,15),random.choice(["to_player","predictable","random"]),120,220,75,90) for i in range(2,20)],20,'world4_background.png','world4_music.mp3',[]],
    "36" : ["freeze",player('player.png',15,None,25,200,[5,5]),[enemy('pirate',20,None,700,200,[6,6],[0,0],16,"at_player",0,0,0),enemy('pirate',20,None,25,200,[6,6],[0,0],16,"at_player",0,0,0),enemy('pirate',20,None,375,395,[4,4],[0,0],12,"to_player",0,0,0),enemy('pirate',20,None,375,25,[6,6],[0,0],10,"at_player",0,0,0),enemy('pirate',20,None,375,395,[6,6],[0,0],10,"at_player",0,0,0),enemy('pirate',20,None,375,25,[4,4],[0,0],5,"to_player",0,0,0),enemy('pirate',20,None,375,200,[0,0],[0,0],0,"",0,0,150),enemy('pirate',20,None,5,5,[0,0],[0,0],0,"",0,0,100),enemy('pirate',20,None,5,395,[0,0],[0,0],0,"",0,0,100),enemy('pirate',20,None,745,395,[0,0],[0,0],0,"",0,0,100),enemy('pirate',20,None,745,5,[0,0],[0,0],0,"",0,0,100)],20,'world4_background.png','world4_music.mp3',[]],
    "37" : ["flight",player('player.png',15,None,350,225,[5,5]),[enemy('classic',20,"grenade launcher",5,5,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"grenade launcher",5,395,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"grenade launcher",745,5,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"grenade launcher",745,395,[0,0],[0,0],0,"",10,0,0,0)],30,'world4_background.png','world4_music.mp3',[]],
    "38" : ["fight",player('player.png',15,"minigun",350,225,[5,5]),[enemy('ninja',20,None,random.randint(0,740),random.randint(0,390),[3,3],[-1,1],i,random.choice(["predictable","random"]),0,0) for i in range(1,11)],15,'world4_background.png','world4_music.mp3',[]],
    "39" : ["fight",player('player.png',1,"minigun",375,210,[0,0]),[enemy('ninja',5,None,random.choice([random.randint(5,250),random.randint(500,740)]),random.choice([random.randint(5,95),random.randint(300,390)]),[2,2],[-1,1],random.randint(1,25),"to_player",0,220,75,90) for i in range(1,100)],30,'world4_background.png','world4_music.mp3',[]],
    "40" : ["fawn",player('player.png',15,None,350,350,[5,5]),[enemy('boss4',500,None,350,10,[4,4],[-1,1],0,"predictable",0,10,150,60*50)],60,'boss4_background.png','boss4_music.mp3',[]],
    "41" : ["freeze",player('player.png',15,None,25,25,[5,5]),[enemy('pirate',20,None,375,random.choice([60,370]),[0,0],[0,0],12,"",0,0,70),enemy('pirate',20,None,random.choice([710,40]),200,[0,0],[0,0],8,"",0,0,70),enemy('pirate',20,"minigun",375,210,[0,0],[0,0],1,"",3,0,70),enemy('pirate',20,None,600,255,[0,0],[0,0],0,"",0,0,70),enemy('pirate',20,None,150,255,[0,0],[0,0],0,"",0,0,70),enemy('pirate',20,None,600,125,[0,0],[0,0],0,"",0,0,70),enemy('pirate',20,None,150,125,[0,0],[0,0],0,"",0,0,70)],22,'world5_background.png','world5_music.mp3',[]],
    "42" : ["fawn",player('player.png',15,None,350,350,[5,5]),[enemy('ninja',20,None,5+(i*100),5+(i*55),[random.randint(2,8),0],[random.choice([-1,1]),0],1,"predictable",10,0,0,random.randint(800,1000)) for i in range(0,8)],25,'world5_background.png','world5_music.mp3',[]],
    "43" : ["freeze",player('player.png',15,"grenade launcher",25,25,[5,5]),[enemy('pirate',5,random.choice([None,"energy absorber"]),random.randint(0,740),random.randint(0,390),[4,4],[-1,1],random.randint(1,20),random.choice(["predictable","random"]),120,220,80,90) for i in range(2,28)],20,'world5_background.png','world5_music.mp3',[]],
    "44" : ["flight",player('player.png',15,None,25,25,[10,10]),[enemy('pirate',20,"grenade launcher",375,210,[0,0],[0,0],1,"",0,0)],10,'world5_background.png','world5_music.mp3',[]],
    "45" : ["fight",player('player.png',15,"minigun",350,225,[5,5]),[enemy('pirate',8,None,random.randint(0,740),random.randint(0,390),[i/2,i/2],[-1,1],i/2,"to_player",4) for i in range(8,26)],15,'world5_background.png','world5_music.mp3',[]],
    "46" : ["fight",player('player.png',25,"minigun",5,200,[0,0]),[enemy('pirate',10,None,200+(i*51),random.randint(5,390),[0,random.randint(2,5)],[0,random.choice([-1,1])],1,"predictable",0) for i in range(0,10)],20,'world5_background.png','world5_music.mp3',[]],
    "47" : ["flight",player('player.png',25,"timestop",5,200,[0,5]),[enemy('classic',20,"grenade launcher",745,100,[0,0],[0,0],16,"",10,0,0,0),enemy('classic',20,"grenade launcher",745,300,[0,0],[0,0],16,"",10,0,0,0),enemy('classic',20,"grenade launcher",745,200,[0,0],[0,0],12,"",10,0,0,0),enemy('classic',20,"grenade launcher",745,395,[0,0],[0,0],0,"",10,0,0,0),enemy('classic',20,"grenade launcher",745,5,[0,0],[0,0],0,"",10,0,0,0)],25,'world5_background.png','world5_music.mp3',[]],
    "48" : ["freeze",player('player.png',25,None,5,200,[0,5]),[enemy('pirate',25,None,random.randint(300,740),20+(i*60),[random.randint(2,4),0],[random.choice([-1,1]),0],1,"predictable",0,0,100) for i in range(0,7)],40,'world5_background.png','world5_music.mp3',[]],
    "49" : ["fawn",player('player.png',25,"minigun",350,225,[5,5]),[enemy('boss1',120,"grenade launcher",5,5,[6,6],[-1,1],1,"away_player",40,250,0,900),enemy('boss2',140,None,745,5,[3,3],[-1,1],1,"to_player",0,300,0,900),enemy('boss3',120,None,5,395,[4,4],[-1,1],1,"predictable",0,80,150,900),enemy('boss4',80,None,745,395,[4,4],[-1,1],1,"predictable",0,30,150,900)],math.inf,'penultimate_background.png','penultimate_music.mp3',[]],
    "50" : ["fight",player('player.png',50,None,350,350,[5,5]),[enemy('final_boss',500,None,350,10,[4,4],[-1,1],0,"predictable",2,0,150)],math.inf,'final_boss_background.png','final_boss_music.mp3',[]]
    }


# Stats for items corresponding to the level (including endless)
# Key: [energy barrier,minigun,timestop,grenade launcher,energy absorber]
# Parameters:
# Barrier: health
# Minigun: ammo,cooldown,health,speed
# Timestop: duration
# Grenade Launcher: ammo,cooldown,health,speed,timer,radius
# Energy Absorber: timer,health
# Other parameters are user specific
global level_item_stats
level_item_stats = {
    "1" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "2" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "3" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "4" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "5" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "6" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "7" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "8" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "9" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,100]],
    "10" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "11" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "12" : [[10],[math.inf,60,3,[0.03,0.03]],[90],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "13" : [[10],[math.inf,5,2,[0.03,0.03]],[90],[math.inf,100,5,[0.01,0.01],120,50],[600,500]],
    "14" : [[10],[math.inf,5,2,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "15" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "16" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "17" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "18" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[1800,500]],
    "19" : [[math.inf],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[1800,500]],
    "20" : [[10],[math.inf,5,2,[0.03,0.03]],[120],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "21" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "22" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "23" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "24" : [[10],[math.inf,5,2,[0.02,0.02]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "25" : [[10],[math.inf,5,2,[0.02,0.02]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "26" : [[10],[math.inf,2,2,[0.02,0.02]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "27" : [[10],[math.inf,9,10,[0.02,0.02]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,math.inf]],
    "28" : [[10],[math.inf,9,10,[0.02,0.02]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,math.inf]],
    "29" : [[10],[5,10,20,[0.03,0.03]],[60],[math.inf,10,5,[0.01,0.01],120,50],[600,math.inf]],
    "30" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "31" : [[math.inf],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,15,5,[0.01,0.01],120,50],[600,500]],
    "32" : [[math.inf],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,15,5,[0.01,0.01],120,50],[600,500]],
    "33" : [[50],[math.inf,4,2,[0.03,0.03]],[480],[math.inf,12,5,[0.02,0.02],120,50],[600,500]],
    "34" : [[50],[math.inf,5,2,[0.05,0.05]],[480],[math.inf,12,5,[0.02,0.02],120,50],[600,500]],
    "35" : [[50],[math.inf,5,2,[0.05,0.05]],[480],[math.inf,40,10,[0.05,0.05],120,70],[240,20]],
    "36" : [[50],[math.inf,5,2,[0.05,0.05]],[480],[math.inf,40,10,[0.05,0.05],120,70],[240,20]],
    "37" : [[10],[math.inf,5,2,[0.02,0.02]],[60],[math.inf,8,4,[0.018,0.018],100,50],[600,500]],
    "38" : [[10],[10,15,20,[0.06,0.06]],[60],[math.inf,8,4,[0.018,0.018],100,50],[600,500]],
    "39" : [[50],[math.inf,5,5,[0.02,0.02]],[480],[math.inf,40,10,[0.05,0.05],120,70],[240,20]],
    "40" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "41" : [[10],[math.inf,3,5,[0.03,0.03]],[60],[math.inf,8,4,[0.018,0.018],100,50],[600,500]],
    "42" : [[10],[math.inf,5,2,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "43" : [[50],[math.inf,5,2,[0.05,0.05]],[480],[math.inf,40,10,[0.05,0.05],120,70],[240,20]],
    "44" : [[50],[math.inf,5,2,[0.05,0.05]],[480],[math.inf,5,20,[0.1,0.1],120,100],[240,20]],
    "45" : [[10],[math.inf,5,3,[0.03,0.03]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "46" : [[10],[5,10,math.inf,[0.05,0]],[30],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "47" : [[10],[math.inf,5,3,[0.03,0.03]],[90],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "48" : [[10],[math.inf,5,3,[0.03,0.03]],[90],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "49" : [[10],[math.inf,5,3,[0.03,0.03]],[90],[math.inf,10,5,[0.01,0.01],120,50],[600,500]],
    "50" : [[50],[math.inf,5,3,[0.03,0.03]],[120],[math.inf,20,8,[0.01,0.01],120,50],[600,math.inf]],
    "endless_fight" : [[15],[100,5,2,[0.03,0.03]],[60],[20,30,5,[0.01,0.01],120,40],[240,80]],
    "endless_flight" : [[15],[25,5,2,[0.03,0.03]],[90],[20,30,5,[0.01,0.01],120,40],[240,100]],
    "endless_freeze" : [[15],[100,5,2,[0.03,0.03]],[60],[20,30,5,[0.01,0.01],120,40],[240,100]],
    "endless_fawn" : [[15],[100,5,2,[0.03,0.03]],[60],[20,30,5,[0.01,0.01],120,40],[240,100]]
    }


# Main loop
while True:
    main_menu()
