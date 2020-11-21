GlowScript 3.0 VPython

RATE = 100                # The number of times the while loop runs each second
dt = .1/RATE            # The time step each time through the while loop
scene.bind('keydown', keydown_fun)     # Function for key presses
scene.background = 0.8*vec(0, .9, 1)    # Light gray (0.8 out of 1.0)
scene.lights = []

class Block:
    scale = 1
    texture_map = {"dirt": texture = "https://lh3.googleusercontent.com/DpmqnZGty6vns7713z1kTAp3AwBqrZ5ZYz_jf-x04p3lFfQ3Q9j5KruZ-v81846PtM1A9HMHvxQkPpoOqViuvA=s400", 
                 "stone": texture = "https://art.pixilart.com/df108d01cd72892.png",
                 "lava": texture = "https://qph.fs.quoracdn.net/main-qimg-5691a6bcf4bd21df68e741ee1d9d4e0f",
                 "water": texture = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcR-ErVpce1X6Y7Z4bYIK9PJfLL4hh_R9nvbFg&usqp=CAU",
                 "wood": texture = "https://i.imgur.com/n6J1Jhz.jpg",
                 "leaf": texture = "https://i.imgur.com/E4ycyzv.jpg",
                 "grass_top": texture = {'file': "https://lh3.googleusercontent.com/0Xh1P9-7QIXw2j-TM5lGIo5Vvtkq3UIwynD04RgngIOU-4KOy06ZONL93Ht4YyCXEVXojj5Xn-H1m6NHC4rmW-g=s400", 'place':['sides']},
                 "grass": texture = {'file':"https://lh3.googleusercontent.com/2ZdPa8KBDybnUudpc9yRmaCU3DYHH4SL7gxRTPwyk1oCn_1xCzntDLkb02MChMipFu-N3BzNAtXP2BCiwOl9WgM", 'place':['sides']}}
                 
    def __init__(self, pos, type):
        self.pos = vec(1, 1, 0)
        self.pos.x = floor(pos.x) * Block.scale
        self.pos.y = floor(pos.y) * Block.scale
        self.pos.z = floor(pos.z) * Block.scale
        self.type = type
        
        if type == "grass":
            self.pos.x = self.pos.x
            self.pos.y = self.pos.y
            self.pos.z = self.pos.z
            
            self.b1 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x,self.pos.y,self.pos.z -Block.scale*.5), axis = vec(1,0,0), texture = Block.texture_map["grass"], emissive = True)
            self.b2 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x,self.pos.y,self.pos.z+ Block.scale -Block.scale*.5), axis = vec(1,0,0), texture = Block.texture_map["grass"], emissive = True)
            self.b3 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x + Block.scale*(-.5),self.pos.y,self.pos.z + Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["grass"], emissive = True)
            self.b4 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x+ Block.scale*(.5),self.pos.y,self.pos.z+Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["grass"], emissive = True)
            self.bottom = box(size = vec(Block.scale, .001, Block.scale), pos = vec(self.pos.x,self.pos.y+ Block.scale*(-.5),self.pos.z+Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["dirt"], emissive = True)
            self.grass_top = box(size = vec(Block.scale, .001, Block.scale), pos = vec(self.pos.x,self.pos.y+Block.scale*(.5),self.pos.z+Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["grass_top"], emissive = True)
            self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, opacity = 0.1, emissive = True)    
            self.model.visible = False
        else:
            self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, texture = Block.texture_map[type], emissive = True)

class Player:
    scale = .5
    
    def __init__(self, pos):
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Player.scale 
        self.pos.y = floor(pos.y) * Player.scale - .5*Player.scale
        self.pos.z = floor(pos.z) * Player.scale
        self.emissive = True
        
        #head
        self.face = box(size = vec(Player.scale,Player.scale,.001), axis = vec(0,0,0), pos = vec(self.pos.x,self.pos.y,self.pos.z), texture= "https://i.imgur.com/xGBPM4r.png", emissive = True)
        self.left_face = box(size = vec(Player.scale,Player.scale,.001), axis = vec(0,0,1), pos = vec(.5*Player.scale + self.pos.x,self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/0MweIHN.png", emissive = True)
        self.right_face = box(size = vec(Player.scale,Player.scale,.001), axis = vec(0,0,1), pos = vec(-.5*Player.scale + self.pos.x,self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/KBu05a4.png", emissive = True)
        self.forehead = box(size = vec(Player.scale,.001,Player.scale), axis = vec(0,0,0), pos = vec(self.pos.x,.5*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/5zchhnC.png", emissive = True)
        self.bottom = box(size = vec(Player.scale,.001,Player.scale), axis = vec(0,0,0), pos = vec(self.pos.x,-.5*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/5zchhnC.png", emissive = True)
        self.back_head = box(size = vec(Player.scale,Player.scale,.001), axis = vec(0,0,0), pos = vec(self.pos.x,self.pos.y,-1*Player.scale + self.pos.z), texture= "https://i.imgur.com/GM3mhsQ.jpg", emissive = True)
        
        #body
        self.front_body = box(size = vec(Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(self.pos.x,-1.25*Player.scale + self.pos.y,-.25*Player.scale + self.pos.z), texture= "https://i.imgur.com/VPh0BcH.png", emissive = True)
        self.back_body = box(size = vec(Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(self.pos.x,-1.25*Player.scale + self.pos.y,-.75*Player.scale + self.pos.z), texture= "https://i.imgur.com/g5SiySx.png", emissive = True)
        self.left_innerbody = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(.5*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/yUUrBWl.png", emissive = True)
        self.right_innerbody = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(-.5*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/yUUrBWl.png", emissive = True)
        
        #arms
        self.left_arm_front = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(.75*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.25*Player.scale + self.pos.z), texture= "https://i.imgur.com/RGQfD6E.png", emissive = True)
        self.right_arm_front = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(-.75*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.25*Player.scale + self.pos.z), texture= "https://i.imgur.com/RGQfD6E.png", emissive = True)
        self.left_arm_back = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(.75*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.75*Player.scale + self.pos.z), texture= "https://i.imgur.com/joEQh9C.png", emissive = True)
        self.right_arm_back = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(-.75*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.75*Player.scale + self.pos.z), texture= "https://i.imgur.com/joEQh9C.png", emissive = True)
        self.left_arm_side = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(1*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/hasbIck.png", emissive = True)
        self.right_arm_side = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(-1*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/YCj05N3.png", emissive = True)
        self.left_arm_inner = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(.5*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/hasbIck.png", emissive = True)
        self.right_arm_inner = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(-.5*Player.scale + self.pos.x,-1.25*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/hasbIck.png", emissive = True)
        
        #legs
        self.left_leg_front = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(.25*Player.scale + self.pos.x,-2.75*Player.scale + self.pos.y,-.25*Player.scale + self.pos.z), texture= "https://i.imgur.com/raDULwo.png", emissive = True)
        self.left_leg_back = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(.25*Player.scale + self.pos.x,-2.75*Player.scale + self.pos.y,-.75*Player.scale + self.pos.z), texture= "https://i.imgur.com/RVFoPxR.png", emissive = True)
        self.left_leg_side = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(.5*Player.scale + self.pos.x,-2.75*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/zwFnZgN.png", emissive = True)
        self.right_leg_front = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(-.25*Player.scale + self.pos.x,-2.75*Player.scale + self.pos.y,-.25*Player.scale + self.pos.z), texture= "https://i.imgur.com/raDULwo.png", emissive = True)
        self.right_leg_back = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,0), pos = vec(-.25*Player.scale + self.pos.x,-2.75*Player.scale + self.pos.y,-.75*Player.scale + self.pos.z), texture= "https://i.imgur.com/RVFoPxR.png", emissive = True)
        self.right_leg_side = box(size = vec(.5*Player.scale,1.5*Player.scale,.001), axis = vec(0,0,1), pos = vec(-.5*Player.scale + self.pos.x,-2.75*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/zwFnZgN.png", emissive = True)
        
        #shoulders
        self.shoulders = box(size = vec(2*Player.scale,.001,.5*Player.scale), axis = vec(0,0,0), pos = vec(self.pos.x,-.5*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/4Sl9Hde.png", emissive = True)
        #hands
        self.left_hand = box(size = vec(.5*Player.scale,.001,.5*Player.scale), axis = vec(0,0,0), pos = vec(.75*Player.scale + self.pos.x,-2*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/DtRDWLo.png", emissive = True)
        self.right_hand = box(size = vec(.5*Player.scale,.001,.5*Player.scale), axis = vec(0,0,0), pos = vec(-.75*Player.scale + self.pos.x,-2*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/DtRDWLo.png", emissive = True)
        #feet
        self.left_foot = box(size = vec(.5*Player.scale,.001,.5*Player.scale), axis = vec(0,0,0), pos = vec(.25*Player.scale + self.pos.x,-3.5*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/gNBY1QG.png", emissive = True)
        self.right_foot = box(size = vec(.5*Player.scale,.001,.5*Player.scale), axis = vec(0,0,0), pos = vec(-.25*Player.scale + self.pos.x,-3.5*Player.scale + self.pos.y,-.5*Player.scale + self.pos.z), texture= "https://i.imgur.com/gNBY1QG.png", emissive = True)
        
        self.pos.y = self.pos.y - .5*Player.scale
        
        self.h_0 = box(pos = vec(self.pos.x+Block.scale, self.pos.y+Block.scale, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_1 = box(pos = vec(self.pos.x+Block.scale, self.pos.y, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_2 = box(pos = vec(self.pos.x+Block.scale, self.pos.y-Block.scale, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_3 = box(pos = vec(self.pos.x+Block.scale, self.pos.y-2*Block.scale, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        self.h_4 = box(pos = vec(self.pos.x, self.pos.y-2, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        self.h_5 = box(pos = vec(self.pos.x, self.pos.y+Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_6 = box(pos = vec(self.pos.x, self.pos.y, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_7 = box(pos = vec(self.pos.x, self.pos.y-Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_8 = box(pos = vec(self.pos.x, self.pos.y-2*Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        self.h_9 = box(pos = vec(self.pos.x, self.pos.y+1, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        self.h_10 = box(pos = vec(self.pos.x-Block.scale, self.pos.y+Block.scale, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_11 = box(pos = vec(self.pos.x-Block.scale, self.pos.y, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_12 = box(pos = vec(self.pos.x-Block.scale, self.pos.y-Block.scale, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_13 = box(pos = vec(self.pos.x-Block.scale, self.pos.y-2*Block.scale, self.pos.z), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        self.h_14 = box(pos = vec(self.pos.x-Block.scale, self.pos.y+Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_15 = box(pos = vec(self.pos.x-Block.scale, self.pos.y, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_16 = box(pos = vec(self.pos.x-Block.scale, self.pos.y-Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_17 = box(pos = vec(self.pos.x-Block.scale, self.pos.y-2*Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        self.h_18 = box(pos = vec(self.pos.x+Block.scale, self.pos.y+Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_19 = box(pos = vec(self.pos.x+Block.scale, self.pos.y, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_20 = box(pos = vec(self.pos.x+Block.scale, self.pos.y-Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        self.h_21 = box(pos = vec(self.pos.x+Block.scale, self.pos.y-2*Block.scale, self.pos.z+Block.scale), axis = vec(1, 0, 0), size = vec(Block.scale, Block.scale, Block.scale), opacity=0.1, color = color.yellow)
        
        print(Block.scale)

d = {}
hitbox = []
count = 0
player = Player(vec(0,5,0))
print(player.h_2.pos)
cube = box(pos = vec(1, 3, 0), axis = vec(1, 0, 0), size = vec(1, 1, 1), opacity=0.5, color = color.yellow)
animate = 0
x = 0
i = 0

#island
for x in range(7):
    d[vec(x,0,0)] = Block(vec(x, 0, 0), "grass")
for x in range(7):
    d[vec(x,0,1)] = Block(vec(x, 0, 1), "grass")
for x in range(7):
    d[vec(x,0,2)] = Block(vec(x, 0, 2), "grass")
for x in range(3):
    d[vec(x,0,-1)] = Block(vec(x, 0, -1), "grass")
for x in range(3):
    d[vec(x,0,-2)] = Block(vec(x, 0, -2), "grass")
for x in range(3):
    d[vec(x,0,-3)] = Block(vec(x, 0, -3), "grass")

for x in range(7):
    for y in range(1,3):
        for z in range(3):
            d[vec(x,-y,z)] = Block(vec(x, -y, z), "dirt")

for x in range(3):
    for y in range(1,3):
        for z in range(1,4):
            d[vec(x,-y,-z)] = Block(vec(x, -y, -z), "dirt")

#tree
for y in range(1,5):
    d[vec(1,y,-2)] = Block(vec(1, y, -2), "wood")
for x in range(0,3):
    for y in range(3,5):
        for z in range(-3,0):
            d[vec(x,y,z)] = Block(vec(x, y, z), "leaf")
d[vec(1,5,-2)] = Block(vec(1, 5, -2), "leaf")

while True:
    
    rate(RATE)
    hitbox = [player.h_0.pos, player.h_1.pos, player.h_2.pos, player.h_3.pos, player.h_4.pos, player.h_5.pos, player.h_6.pos, player.h_7.pos, player.h_8.pos, player.h_9.pos,
                player.h_10.pos, player.h_11.pos, player.h_12.pos, player.h_13.pos, player.h_14.pos, player.h_15.pos, player.h_16.pos, player.h_17.pos, player.h_18.pos, player.h_19.pos,
                player.h_20.pos, player.h_21.pos]
    if cube.pos not in hitbox:
        print("You cannot move there")
        cube.pos = player.h_6.pos
        

def keydown_fun(event):
    """This function is called each time a key is pressed."""
    # ball.color = randcolor()  # this turns out to be very distracting!
    key = event.key
    print("key:", key)  # Prints the key pressed -- caps only...
    print(Player.pos)
    
    #controls for the player
    if key == 'up':
        player_move(player, vec(-1, 0, 0))
        cube.pos = cube.pos + vec(-1, 0, 0)
    elif key == 'left':
        player_move(player, vec(0, 0, 1))
        cube.pos = cube.pos + vec(0, 0, 1)
    elif key == 'down':
        player_move(player, vec(1, 0, 0))
        cube.pos = cube.pos + vec(1, 0, 0)
    elif key == 'right':
        player_move(player, vec(0, 0, -1))
        cube.pos = cube.pos + vec(0, 0, -1)
    elif key in 'Ww':
        player_move(player, vec(0, 1, 0))
        cube.pos = cube.pos + vec(0, 1, 0)
    elif key in 'Ss':
        player_move(player, vec(0, -1, 0))
        cube.pos = cube.pos + vec(0, -1, 0)
        
    #controls for cube(mining/placing --> in the future)
    elif key in 'Ii':
        cube.pos = cube.pos + vec(-1, 0, 0)
    elif key in 'Jj':
        cube.pos = cube.pos + vec(0, 0, 1)
    elif key in 'Kk':
        cube.pos = cube.pos + vec(1, 0, 0)
    elif key in 'Ll':
        cube.pos = cube.pos + vec(0, 0, -1)
    elif key in 'Oo':
        cube.pos = cube.pos + vec(0, 1, 0)
    elif key in 'Nn':
        cube.pos = cube.pos + vec(0, -1, 0)
    elif key in 'Mm':        
        mine(cube)
    elif key in 'Pp':
        water(cube)
    elif key in 'Rr':
        lava(cube)

def mine(cube):
    if cube.pos not in d:
        print("Cannot mine")
    elif d[cube.pos].type == "stone":
        count += 1
        d[cube.pos].model.visible = False
        #time-delay?!?!?!?!?
        #d[cube.pos] = Block(cube.pos,"stone")
    elif d[cube.pos].type == "grass":
        print(cube.pos)
        d[cube.pos].b1.visible = False
        d[cube.pos].b2.visible = False
        d[cube.pos].b3.visible = False
        d[cube.pos].b4.visible = False
        d[cube.pos].bottom.visible = False
        d[cube.pos].grass_top.visible = False
        d[cube.pos].model.visible = False
    else:
        d[cube.pos].model.visible = False

#places water and flows
def water(cube):
    print(d[cube.pos].type)
    #checks if the block exists and if it is "mineable"
    if cube.pos not in d or d[cube.pos].model.visible == True:
        print("You cannot place water here")
        return 0
        
    cubeW = Block(cube.pos, "water")
    
    x = cube.pos.x
    y = cube.pos.y
    z = cube.pos.z
 
    #checks the surrounding blocks
    for i in range(20):
        if d[vec(x, y-1,z)].model.visible == False:
            d[vec(x,y-1,z)] = Block(vec(x,y-1,z), "water")
            y = y - 1
        elif d[vec((x+1), y, z)].model.visible == False:
            d[vec(x+1,y,z)] = Block(vec(x+1,y,z), "water")
            x = x + 1
            print(x)
        elif d[vec(x-1, y, z)].model.visible == False:
            d[vec(x-1,y,z)] = Block(vec(x-1,y,z), "water")
            x = x - 1
        elif d[vec(x, y,(z+1))].model.visible == False:
            d[vec(x,y,z+1)] = Block(vec(x,y,z+1), "water")
            z = z + 1
            print(z)
        elif d[vec(x, y, z-1)].model.visible == False:
            d[vec(x,y,z-1)] = Block(vec(x,y,z-1), "water")
            z = z - 1
        else:
            break

#placement of lava and making stone
def lava(cube):
    if cube.pos not in d or d[cube.pos].model.visible == True:
        print("You cannot place lava here")
        return 0
    
    cubeW = Block(cube.pos, "lava")
    x = cube.pos.x
    y = cube.pos.y
    z = cube.pos.z
    
    blocksAround(cube,"water","stone")
    

#checks the blocks around cube.pos and creates a specified block type
def blocksAround(cube,detect,create):
    x = cube.pos.x
    y = cube.pos.y
    z = cube.pos.z
    
    if d[vec(x, y-1,z)].type == detect:
        d[vec(x,y-1,z)].model.visible = False
        d[vec(x,y-1,z)] = Block(vec(x, y-1,z), create)
    elif d[vec((x+1), y, z)].type == detect:
        d[vec(x+1,y,z)].model.visible = False
        d[vec(x+1,y,z)] = Block(vec(x+1, y,z), create)        
    elif d[vec(x-1, y, z)].type == detect:
        d[vec(x-1,y,z)].model.visible = False
        d[vec(x-1,y,z)] = Block(vec(x-1, y,z), create)
    elif d[vec(x, y,(z+1))].type == detect:
        d[vec(x,y,z+1)].model.visible = False
        d[vec(x,y,z+1)] = Block(vec(x, y,z+1), create)
    elif d[vec(x, y, z-1)].type == detect:
        d[vec(x,y,z-1)].model.visible = False
        d[vec(x,y,z-1)] = Block(vec(x, y,z-1), create)

#don't look at this: it just moves all elements of the player and the hitbox around
def player_move(player, key_vec):
    player.pos = player.pos + key_vec
    player.face.pos = player.face.pos + key_vec
    player.left_face.pos = player.left_face.pos + key_vec
    player.right_face.pos = player.right_face.pos + key_vec
    player.forehead.pos = player.forehead.pos + key_vec
    player.bottom.pos = player.bottom.pos + key_vec
    player.back_head.pos = player.back_head.pos + key_vec
    
    player.front_body.pos = player.front_body.pos + key_vec
    player.back_body.pos = player.back_body.pos + key_vec
    player.left_innerbody.pos = player.left_innerbody.pos + key_vec
    player.right_innerbody.pos = player.right_innerbody.pos + key_vec
    
    player.left_arm_front.pos = player.left_arm_front.pos + key_vec
    player.right_arm_front.pos = player.right_arm_front.pos + key_vec
    player.left_arm_back.pos = player.left_arm_back.pos + key_vec
    player.right_arm_back.pos = player.right_arm_back.pos + key_vec
    player.left_arm_side.pos = player.left_arm_side.pos + key_vec
    player.right_arm_side.pos = player.right_arm_side.pos + key_vec
    player.left_arm_inner.pos = player.left_arm_inner.pos + key_vec
    player.right_arm_inner.pos = player.right_arm_inner.pos + key_vec
    
    player.left_leg_front.pos = player.left_leg_front.pos + key_vec
    player.right_leg_front.pos = player.right_leg_front.pos + key_vec
    player.left_leg_back.pos = player.left_leg_back.pos + key_vec
    player.right_leg_back.pos = player.right_leg_back.pos + key_vec
    player.left_leg_side.pos = player.left_leg_side.pos + key_vec
    player.right_leg_side.pos = player.right_leg_side.pos + key_vec
    
    player.shoulders.pos = player.shoulders.pos + key_vec
    player.left_hand.pos = player.left_hand.pos + key_vec
    player.right_hand.pos = player.right_hand.pos + key_vec
    player.left_foot.pos = player.left_foot.pos + key_vec
    player.right_foot.pos = player.right_foot.pos + key_vec