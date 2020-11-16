GlowScript 3.0 VPython

#Bugs?!? Why can't I use the '+' sign?!? bruhhhhhh

scene.bind('keydown', keydown_fun)     # Function for key presses
scene.background = 0.8*vec(0, .9, 1)    # Light gray (0.8 out of 1.0)
scene.lights = []

class Block:
    scale = 1
    texture_map = {"dirt": texture = "https://lh3.googleusercontent.com/DpmqnZGty6vns7713z1kTAp3AwBqrZ5ZYz_jf-x04p3lFfQ3Q9j5KruZ-v81846PtM1A9HMHvxQkPpoOqViuvA=s400", 
                 "stone": texture = "https://art.pixilart.com/df108d01cd72892.png",
                 "lava": texture = "https://qph.fs.quoracdn.net/main-qimg-5691a6bcf4bd21df68e741ee1d9d4e0f",
                 "water": texture = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcR-ErVpce1X6Y7Z4bYIK9PJfLL4hh_R9nvbFg&usqp=CAU",
                 "wood": texture = "https://lh3.googleusercontent.com/Sm5RI4dsQZxXHNQfpEBZZwbnuv_nUqNeSXMlpLSfdJC8mGb7REfYBLUNxiyZYTeXmOo-YkdWAGLBnuUj6-iHCA=s400",
                 "leaf": texture = "https://lh3.googleusercontent.com/proxy/L6-lYfQf-eINxjeFyohQ85kBX61qetzYPdU9NmXHuvC5y7SLeW1KDd6ccUB5G8iuBc55hYQe5O3nRNqoVWL4FGNayWhgvsT9",
                 "grass": texture = "https://lh3.googleusercontent.com/0Xh1P9-7QIXw2j-TM5lGIo5Vvtkq3UIwynD04RgngIOU-4KOy06ZONL93Ht4YyCXEVXojj5Xn-H1m6NHC4rmW-g=s400"}
                 
    def __init__(self, pos, type):
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Block.scale
        self.pos.y = floor(pos.y) * Block.scale
        self.pos.z = floor(pos.z) * Block.scale
        self.type = type
        self.emissive = True
        
        #Because we can't compound objects with textures, blocks specifically for grass, but not sure if we want this
        if type == "grass":
            self.pos.y = self.pos.y + (Block.scale*(4/10))
            self.model = box(size = vec(Block.scale, Block.scale*(1/5), Block.scale), pos = self.pos, texture = Block.texture_map["grass"], emissive = True)
            self.pos.y = self.pos.y - (Block.scale*(4/10)) - (Block.scale*(1/10))
            self.model = box(size = vec(Block.scale, Block.scale*(4/5), Block.scale), pos = self.pos, texture = Block.texture_map["dirt"], emissive = True)
        else:
            self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, texture = Block.texture_map[type], emissive = True)
        

cube = box(pos = vec(0, 0, 0), axis = vec(1, 0, 0), size = vec(1, 1, 1), opacity=0.5, color = color.yellow)
d = {}
count = 0



#island
for x in range(7):
    for y in range(3):
        for z in range(3):
            d[vec(x,-y,z)] = Block(vec(x, -y, z), "dirt")
for x in range(3):
    for y in range(3):
        for z in range(1,4):
            d[vec(x,-y,-z)] = Block(vec(x, -y, -z), "dirt")
#tree
for y in range(1,5):
    d[vec(1,y,-2)] = Block(vec(1, y, -2), "wood")
for x in range(3):
    for y in range(3,6):
        for z in range(-3,0):
            print(x,y,z)
            d[vec(x,y,z)] = Block(vec(x, y, z), "leaf")



def keydown_fun(event):
    """This function is called each time a key is pressed."""
    # ball.color = randcolor()  # this turns out to be very distracting!
    key = event.key
    print("key:", key)  # Prints the key pressed -- caps only...
    
    if key == 'up':
        cube.pos = cube.pos + vec(-1, 0, 0)
    elif key == 'left':
        cube.pos = cube.pos + vec(0, 0, 1)
    elif key == 'down':
        cube.pos = cube.pos + vec(1, 0, 0)
    elif key == 'right':
        cube.pos = cube.pos + vec(0, 0, -1)
    elif key in 'Ww':
        cube.pos = cube.pos + vec(0, 1, 0)
    elif key in 'Ss':
        cube.pos = cube.pos + vec(0, -1, 0)
    elif key in 'Mm':
        print(d[cube.pos].type)
        mine(cube)
    elif key in 'Pp':
        water(cube)
    elif key in 'Ll':
        lava(cube)

def mine(cube):
    if cube.pos not in d:
        print("Cannot mine")
    if d[cube.pos].type == "stone":
        count = 1
        d[cube.pos].model.visible = False
        #time-delay?!?!?!?!?
        d[cube.pos] = Block(cube.pos,"stone")
    else:
        d[cube.pos].model.visible = False

#places water and flows
def water(cube):
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
            d[vec(x,y-1,z)] = Block(vec(x, y-1,z), "water")
            y = y - 1
        elif d[vec((x+1), y, z)].model.visible == False:
            d[vec(x+1,y,z)] = Block(vec(x+1, y,z), "water")
            x += 1
            print(x)
        elif d[vec(x-1, y, z)].model.visible == False:
            d[vec(x-1,y,z)] = Block(vec(x-1, y,z), "water")
            x = x - 1
        elif d[vec(x, y,(z+1))].model.visible == False:
            d[vec(x,y,z+1)] = Block(vec(x, y,z+1), "water")
            z += 1
            print(z)
        elif d[vec(x, y, z-1)].model.visible == False:
            d[vec(x,y,z-1)] = Block(vec(x, y,z-1), "water")
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
    
    
"""
island with aesthetics?
for x in range(7):
    for y in range(1,3):
        for z in range(3):
            d[vec(x,0,z)] = Block(vec(x, 0, z), "grass")
            d[vec(x,-y,z)] = Block(vec(x, -y, z), "dirt")
for x in range(3):
    for y in range(1,3):
        for z in range(1,4):
            d[vec(x,0,-z)] = Block(vec(x, 0, -z), "grass")
            d[vec(x,-y,-z)] = Block(vec(x, -y, -z), "dirt")
"""
        

        
        
        