GlowScript 3.0 VPython

scene.background = color.cyan
scene.width = 640                      # Make the 3D canvas larger
scene.height = 480
scene.resizable = True
scene.bind('keydown', keydown_fun)     # Function for key presses
scene.bind('keyup', keyup_fun)     # Function for key presses
scene.bind('mousedown', mousedown_fun)
scene.bind('mousemove', mousemove_fun)
scene.bind('mouseup', mouseup_fun)
scene.bind('mouseenter', mouseenter_fun)
scene.bind('mouseleave', mouseleave_fun)
scene.wrapper.css('height', '100%')
scene.wrapper.css('min-height', '100%')
scene.wrapper.css('margin', '0')

# +++ Start of object creation -- Create the blocks making up the world and the player

class Hitbox:
    ''' Wrapper class to hold information about axis aligned hitboxes. Used for collision detection instead of the 
        box class in VPython, since the hitboxes don't need to be displayed or have as many options.
    '''
    def __init__(self, pos, size, velocity = vec(0, 0, 0)):
        self.pos = pos
        self.velocity = velocity
        self.size = size

    def get_vertices(self):
        return (vec(self.pos.x - self.size.x / 2, self.pos.y - self.size.y / 2, self.pos.z - self.size.z / 2), vec(self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2, self.pos.z + self.size.z / 2))

    def copy(self):
        return Hitbox(vec(self.pos), vec(self.size), vec(self.velocity))

class Face:
    '''Wrapper class for a quad which allows it to be easily moved'''
    def __init__(self, pos, size, normal, axis, texture = None, color = vec(1, 1, 1)):
        width, height = (size.x, size.y)
        axis = (axis - axis.proj(normal)).norm()
        orthogonal = rotate(axis, angle = pi / 2, axis = normal)
        v0 = vertex(pos = axis * -width / 2 + orthogonal * -height / 2 + pos, texpos = vec(0, 0, 0), emissive = False, shininess = 0, color = color)
        v1 = vertex(pos = axis * width / 2 + orthogonal * -height / 2 + pos, texpos = vec(1, 0, 0), emissive = False, shininess = 0, color = color)
        v2 = vertex(pos = axis * width / 2 + orthogonal * height / 2 + pos, texpos = vec(1, 1, 0), emissive = False, shininess = 0, color = color)
        v3 = vertex(pos = axis * -width / 2 + orthogonal * height / 2 + pos, texpos = vec(0, 1, 0), emissive = False, shininess = 0, color = color)
        self.vertices = [v0, v1, v2, v3]
        self.quad = quad(v0 = v0, v1 = v1, v2 = v2, v3 = v3, texture = texture)
        self.pos = pos

    def new_pos(self, new_pos):
        for vertex in self.vertices:
            vertex.pos = vertex.pos - self.pos + new_pos
        self.pos = vec(new_pos)

    def rotate(self, angle, axis, origin):
        for vertex in self.vertices:
            vertex.rotate(angle = angle, axis = axis, origin = origin)

    def hide(self):
        self.quad.visible = False

    def show(self):
        self.quad.visible = True

# Represents the blocks that makeup the world
class Block:
    scale = 1
    color_map = {'dirt': vec(127 / 255, 92 / 255, 7 / 255), 'leaf': vec(12 / 255, 179 / 255, 26 / 255), 'stone': 0.5 * vec(1, 1, 1)}
    texture_map = {'dirt': texture = 'https://lh3.googleusercontent.com/DpmqnZGty6vns7713z1kTAp3AwBqrZ5ZYz_jf-x04p3lFfQ3Q9j5KruZ-v81846PtM1A9HMHvxQkPpoOqViuvA=s400', 
                'stone': texture = 'https://art.pixilart.com/df108d01cd72892.png',
                'lava': texture = 'https://qph.fs.quoracdn.net/main-qimg-5691a6bcf4bd21df68e741ee1d9d4e0f',
                'water': texture = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcR-ErVpce1X6Y7Z4bYIK9PJfLL4hh_R9nvbFg&usqp=CAU',
                'wood': texture = 'https://i.imgur.com/n6J1Jhz.jpg',
                'leaf': texture = 'https://i.imgur.com/E4ycyzv.jpg',
                'grass_top': texture = {'file': 'https://lh3.googleusercontent.com/0Xh1P9-7QIXw2j-TM5lGIo5Vvtkq3UIwynD04RgngIOU-4KOy06ZONL93Ht4YyCXEVXojj5Xn-H1m6NHC4rmW-g=s400', 'place':['sides']},
                'grass': texture = {'file':'https://lh3.googleusercontent.com/2ZdPa8KBDybnUudpc9yRmaCU3DYHH4SL7gxRTPwyk1oCn_1xCzntDLkb02MChMipFu-N3BzNAtXP2BCiwOl9WgM', 'place':['sides']}}
    blocks = {}
    def __init__(self, pos, block_type):
        # Align the block to a grid
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Block.scale + Block.scale / 2
        self.pos.y = floor(pos.y) * Block.scale + Block.scale / 2
        self.pos.z = floor(pos.z) * Block.scale + Block.scale / 2

        self.model = []
        self.hitbox = Hitbox(self.pos, vec(Block.scale, Block.scale, Block.scale))

        self.block_type = block_type
        if block_type != 'air':
            # Create block model
            block_north = block_east = block_south = block_west = block_top = block_bottom = None
            block_color = color.magenta
            if block_type in Block.texture_map:
                block_north = block_east = block_south = block_west = block_top = block_bottom = Block.texture_map[block_type]
                block_color = vec(1, 1, 1)
                if block_type == 'grass':
                    block_north = block_east = block_south = block_west = Block.texture_map['grass']
                    block_top = Block.texture_map['grass_top']
                    block_bottom = Block.texture_map['dirt']
            elif block_type in Block.color_map:
                block_color = Block.color_map[block_type]
            self.west = Face(pos = vec(self.pos.x, self.pos.y, self.pos.z - Block.scale / 2), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 0, -1), axis = vec(-1, 0, 0), texture = block_west, color = block_color)
            self.east = Face(pos = vec(self.pos.x, self.pos.y, self.pos.z + Block.scale / 2), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 0, 1), axis = vec(1, 0, 0), texture = block_east, color = block_color)
            self.south = Face(pos = vec(self.pos.x - Block.scale / 2, self.pos.y, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(-1, 0, 0), axis = vec(0, 0, 1), texture = block_south, color = block_color)
            self.north = Face(pos = vec(self.pos.x + Block.scale / 2, self.pos.y, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(1, 0, 0), axis = vec(0, 0, -1), texture = block_north, color = block_color)
            self.top = Face(pos = vec(self.pos.x, self.pos.y + Block.scale / 2, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 1, 0), axis = vec(0, 0, 1), texture = block_top, color = block_color)
            self.bottom = Face(pos = vec(self.pos.x, self.pos.y - Block.scale / 2, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 1, 0), axis = vec(0, 0, -1), texture = block_bottom, color = block_color)
            # self.model = [box(pos = self.pos, size = Block.scale * vec(1, 1, 1), color = color.magenta)]
            self.model = [self.north, self.east, self.west, self.south, self.bottom, self.top]

        # Add the block to the map, or if its an air block, just remove the previous block
        key = (floor(pos.x), floor(pos.y), floor(pos.z))
        if key in Block.blocks:
            oldBlock = Block.blocks[key]
            for side in oldBlock.model:
                side.hide()
                # side.visible = False
            del Block.blocks[key]
        if block_type != 'air':
            Block.blocks[key] = self

    def __repr__(self):
        return self.block_type + 'block'

    def remove(self):
        '''Remove the block by replacing it with an air block'''
        Block(self.pos, 'air')

class Player:
    scale = 0.93 * Block.scale / 2
    
    def __init__(self, pos):
        self.hitbox = Hitbox(pos, vec(Block.scale * 0.6, Block.scale * 1.8, Block.scale * 0.6))
        self.hitbox.vel = vec(0, 0, 0)
        self.hitbox.last_pos = vec(self.hitbox.pos)
        
        self.model = []

        #head
        self.face = box(size = vec(Player.scale, Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, self.hitbox.pos.y, self.hitbox.pos.z), texture= 'https://i.imgur.com/xGBPM4r.png', emissive = True)
        # self.face = Face(pos = vec(self.hitbox.pos.x, self.hitbox.pos.y, self.hitbox.pos.z), size = vec(Player.scale, Player.scale, 0), normal = vec(0, 0, 1), axis = vec(1, 0, 0), texture = 'https://i.imgur.com/xGBPM4r.png')
        self.left_face = box(size = vec(Player.scale, Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(0.5 * Player.scale + self.hitbox.pos.x, self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/0MweIHN.png', emissive = True)
        self.right_face = box(size = vec(Player.scale, Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(-0.5 * Player.scale + self.hitbox.pos.x, self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/KBu05a4.png', emissive = True)
        self.forehead = box(size = vec(Player.scale, 0.001, Player.scale), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, 0.5 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/5zchhnC.png', emissive = True)
        self.bottom = box(size = vec(Player.scale, 0.001, Player.scale), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, -0.5 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/5zchhnC.png', emissive = True)
        self.back_head = box(size = vec(Player.scale, Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, self.hitbox.pos.y, -1 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/GM3mhsQ.jpg', emissive = True)
        
        #body
        self.front_body = box(size = vec(Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.25 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/VPh0BcH.png', emissive = True)
        self.back_body = box(size = vec(Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.75 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/g5SiySx.png', emissive = True)
        self.left_innerbody = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(0.5 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/yUUrBWl.png', emissive = True)
        self.right_innerbody = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(-0.5 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/yUUrBWl.png', emissive = True)
        
        #arms
        self.left_arm_front = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(0.75 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.25 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/RGQfD6E.png', emissive = True)
        self.right_arm_front = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(-0.75 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.25 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/RGQfD6E.png', emissive = True)
        self.left_arm_back = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(0.75 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.75 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/joEQh9C.png', emissive = True)
        self.right_arm_back = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(-0.75 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.75 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/joEQh9C.png', emissive = True)
        self.left_arm_side = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(1 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/hasbIck.png', emissive = True)
        self.right_arm_side = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(-1 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/YCj05N3.png', emissive = True)
        self.left_arm_inner = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(0.5 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/hasbIck.png', emissive = True)
        self.right_arm_inner = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(-0.5 * Player.scale + self.hitbox.pos.x, -1.25 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/hasbIck.png', emissive = True)
        
        #legs
        self.left_leg_front = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(0.25 * Player.scale + self.hitbox.pos.x, -2.75 * Player.scale + self.hitbox.pos.y, -0.25 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/raDULwo.png', emissive = True)
        self.left_leg_back = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(0.25 * Player.scale + self.hitbox.pos.x, -2.75 * Player.scale + self.hitbox.pos.y, -0.75 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/RVFoPxR.png', emissive = True)
        self.left_leg_side = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(0.5 * Player.scale + self.hitbox.pos.x, -2.75 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/zwFnZgN.png', emissive = True)
        self.right_leg_front = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(-0.25 * Player.scale + self.hitbox.pos.x, -2.75 * Player.scale + self.hitbox.pos.y, -0.25 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/raDULwo.png', emissive = True)
        self.right_leg_back = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(-0.25 * Player.scale + self.hitbox.pos.x, -2.75 * Player.scale + self.hitbox.pos.y, -0.75 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/RVFoPxR.png', emissive = True)
        self.right_leg_side = box(size = vec(0.5 * Player.scale, 1.5 * Player.scale, 0.001), axis = vec(0, 0, 1), pos = vec(-0.5 * Player.scale + self.hitbox.pos.x, -2.75 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/zwFnZgN.png', emissive = True)
        
        #shoulders
        self.shoulders = box(size = vec(2 * Player.scale, 0.001, 0.5 * Player.scale), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, -0.5 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/4Sl9Hde.png', emissive = True)
        #hands
        self.left_hand = box(size = vec(0.5 * Player.scale, 0.001, 0.5 * Player.scale), axis = vec(0, 0, 0), pos = vec(0.75 * Player.scale + self.hitbox.pos.x, -2 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/DtRDWLo.png', emissive = True)
        self.right_hand = box(size = vec(0.5 * Player.scale, 0.001, 0.5 * Player.scale), axis = vec(0, 0, 0), pos = vec(-0.75 * Player.scale + self.hitbox.pos.x, -2 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/DtRDWLo.png', emissive = True)
        #feet
        self.left_foot = box(size = vec(0.5 * Player.scale, 0.001, 0.5 * Player.scale), axis = vec(0, 0, 0), pos = vec(0.25 * Player.scale + self.hitbox.pos.x, -3.5 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/gNBY1QG.png', emissive = True)
        self.right_foot = box(size = vec(0.5 * Player.scale, 0.001, 0.5 * Player.scale), axis = vec(0, 0, 0), pos = vec(-0.25 * Player.scale + self.hitbox.pos.x, -3.5 * Player.scale + self.hitbox.pos.y, -0.5 * Player.scale + self.hitbox.pos.z), texture= 'https://i.imgur.com/gNBY1QG.png', emissive = True)

        # Add all the boxes in the player model to an array
        self.model += [self.face, self.left_face, self.right_face, self.forehead, self.bottom, self.back_head, self.front_body, self.back_body, self.left_innerbody, self.right_innerbody,
                    self.left_arm_front, self.right_arm_front, self.left_arm_back, self.right_arm_back, self.left_arm_side, self.right_arm_side, self.left_arm_inner, self.right_arm_inner,
                    self.left_leg_front, self.right_leg_front, self.left_leg_back, self.right_leg_back, self.left_leg_side, self.right_leg_side, self.shoulders, self.left_hand,
                    self.right_hand, self.left_foot, self.right_foot]

        self.model_angle = 0
        self.rotate_model(-pi / 2)
        self.model_angle = 0

        for part in self.model:
            part.pos.y += 0.93 * Block.scale - Player.scale / 2
            part.pos.x += Player.scale / 2

        # Display hitbox
        # self.model += [box(pos = self.hitbox.pos, size = self.hitbox.size, color = color.white, opacity = 0.3)]
    
    def sync_model(self):
        '''Move all the boxes which make up the player model the same amount that the player's hitbox has moved'''
        displacement = self.hitbox.pos - self.hitbox.last_pos
        for box in self.model:
            box.pos += displacement
        self.hitbox.last_pos = vec(self.hitbox.pos)

    def rotate_model(self, delta_angle):
        '''Rotate the player's model by the give angle around the y axis'''
        self.model_angle += delta_angle
        for part in self.model:
            part.rotate(angle = -delta_angle, axis = scene.up, origin = self.hitbox.pos)
    
    def hide_model(self):
        for part in self.model:
            part.visible = False

    def show_model(self):
        for part in self.model:
            part.visible = True

player = Player(vec(0, Block.scale, 0))
tp_player(vec(1, 1, 1))

#island
for x in range(7):
    for y in range(3):
        for z in range(3):
            if y == 0:
                Block(vec(x, -y, z), 'grass')
            else:
                Block(vec(x, -y, z), 'dirt')
for x in range(3):
    for y in range(3):
        for z in range(1, 4):
            if y == 0:
                Block(vec(x, -y, -z), 'grass')
            else:
                Block(vec(x, -y, -z), 'dirt')
#tree
for x in range(3):
    for y in range(3, 6):
        for z in range(-3, 0):
                Block(vec(x, y, z), 'leaf')
for y in range(1, 5):
    Block(vec(1, y, -2), 'wood')

Block(vec(3,0,4), 'stone')
Block(vec(3,0,6), 'stone')
Block(vec(4,0,6), 'stone')
Block(vec(4,0,7), 'stone')
Block(vec(4,0,9), 'stone')
Block(vec(2,0,9), 'stone')
Block(vec(2,0,10), 'stone')
Block(vec(2,0,11), 'stone')

#wall
for y in range(-1,4):
    for z in range(11,16):
        Block(vec(3,y,z), 'water')

Block(vec(3,0,18), 'stone')
Block(vec(3,-6,20), 'stone')

#stairs
Block(vec(3,-6,22), 'water')
Block(vec(3,-6,23), 'water')
Block(vec(3,-5,23), 'water')
Block(vec(3,-5,24), 'water')
Block(vec(3,-4,24), 'water')
Block(vec(3,-4,25), 'water')
Block(vec(3,-3,25), 'water')
Block(vec(3,-3,26), 'water')
Block(vec(3,-2,26), 'water')
Block(vec(3,-2,27), 'water')
Block(vec(3,-1,27), 'water')
Block(vec(3,-1,28), 'water')
Block(vec(3,-0,28), 'water')

for x in range(1,4):
    for y in range(1,3):
        for z in range(30,33):
            Block(vec(x, 0, z), 'grass')
            Block(vec(x, -y, z), 'dirt')

# +++ Start of game loop section -- update the position of the player and other entities continuously

# Other constants
RATE = 30                                   # The number of times the while loop runs each second
dt = 1.0 / (1.0 * RATE)                     # The time step each time through the while loop
player.on_ground = False                    # False initially. Keeps track of whether the player is touching the ground
scene.autoscale = False                     # Avoids changing the view automatically
scene.userpan = False                       # Disables the default panning controls
scene.range = 3
scene.forward = vec(1, 0, 0)                # Initialize forward as a unit vector in the x direction. Rotates with the camera
scene.mouse.ray = vec(1, 0, 0)              # Initialize mouse.ray as a unit vector in the x direction. Rotates with the camera
scene.camera.up = vec(0, 1, 0)              # Initialize camera.up as a unit vector in the y direction. Rotates with the camera, unlike scene.up
scene.camera.orthogonal = vec(0, 0, 1)      # Initialize camera.orthogonal as a unit vector in the z direction. Rotates with the camera
friction_coef = 0.3                         # Friction coefficient applied when the player is not walking
max_vel = 5 * Block.scale * vec(1, 14, 1)   # Maximum value for the x and z components of the player's velocity
accel = 1 * Block.scale                     # Acceleration used in the x and z directions while walking
gravity = -9.8 * Block.scale * 5            # Acceleration used in the y direction while falling
scene.fov = pi / 3                          # Set field of view
userspin_rate = 8 * pi / 180                # Set the rate at which the camera rotates when the mouse is dragged near the edge of the screen
userspin_threshold = 0.3                    # Set the threshold for the mouse position on the screen before the camera starts rotating
dragging = False                            # Keeps track of whether the player is dragging to rotate the camers
mouse_onscreen = False                      # Keeps track of whether the mouse is on the screen
mouse_spinning = True                       # Keeps track of whether rotating the camera using the mouse's position is enabled
first_person = False
paused = False
flying = False                              # Keeps track of whether the player is flying
inventory = {1: ['water', 1], 2: ['lava', 1]}
current_slot = 1
if first_person:
    scene.userzoom = False
    scene.userspin = False
    player.hide_model()
else:
    scene.userzoom = True
    scene.userspin = True
    player.show_model()


cursor = box(size = vec(0.01, 0.01, 0.01), color = color.black, emissive = True)

# Dictionary mapping a control to whether it is active. Updated by keyboard events
controls = {control: False for control in ['up', 'down', 'left', 'right', 'jump', 'descend', 'camera_up', 'camera_down', 'camera_left', 'camera_right', 'mine', 'place', 'toggle_view', 'print_inventory', 'slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8', 'slot9', 'slot_inc', 'slot_dec', 'toggle_pause', 'grutor_mode', 'instructor_mode']}
last_controls = {key: controls[key] for key in controls}

# This is the 'event loop' or 'animation loop'
# Each pass through the loop will animate one step in time, dt
while True:
    rate(RATE)                             # maximum number of times per second the while loop runs

    # Unpause control
    if paused:
        if controls['toggle_pause'] and not last_controls['toggle_pause']:
            print('The game is running')
            paused = False
        last_controls = {key: controls[key] for key in controls}
        continue

    # +++ Start of PHYSICS UPDATES -- update all velocities and positions here, every time step
    
    # Calculate camera angle to figure out which direction to update the player's velocity in
    camera_angle_xz = atan2(scene.forward.z, scene.forward.x)
    if camera_angle_xz < 0:
        camera_angle_xz += 2 * pi

    # Rotate player's velocity by the camera angle to make updating it simple
    player.hitbox.vel = rotate(player.hitbox.vel, angle = camera_angle_xz, axis = scene.up)

    # Apply velocity updates in the x and z directions based on the current controls
    if controls['forward']:
        player.hitbox.vel.x += accel
    elif controls['backward']:
        player.hitbox.vel.x -= accel
    else:
        player.hitbox.vel.x *= friction_coef

    if controls['right']:
        player.hitbox.vel.z += accel
    elif controls['left']:
        player.hitbox.vel.z -= accel
    else:
        player.hitbox.vel.z *= friction_coef

    # Set velocity when the player jumps
    if controls['jump'] and (player.on_ground or flying):
        player.hitbox.vel.y = 12 * Block.scale
    elif flying:
        if controls['descend']:
            player.hitbox.vel.y = -12 * Block.scale
        else:
            player.hitbox.vel.y = 0


    # Apply gravity
    if not flying:
        player.hitbox.vel.y += gravity * dt

    # Apply max velocity clamping
    player.hitbox.vel.x = clamp(player.hitbox.vel.x, max_vel.x, -max_vel.x)
    player.hitbox.vel.y = clamp(player.hitbox.vel.y, max_vel.y, -max_vel.y)
    player.hitbox.vel.z = clamp(player.hitbox.vel.z, max_vel.z, -max_vel.z)

    # Rotate the velocity back in the camera's direction
    player.hitbox.vel = rotate(player.hitbox.vel, angle = -camera_angle_xz, axis = scene.up)

    # Check for and resolve collisions between the player and all the blocks
    player.on_ground = False
    hitboxes = []
    for block in get_local_blocks(player.hitbox, dt):
        hitboxes += [block.hitbox]
    player.on_ground = resolve_collisions(player.hitbox, hitboxes, dt)['top']

    # Update the player's position
    player.hitbox.pos = player.hitbox.pos + player.hitbox.vel * dt

    if player.hitbox.pos.y < -50:
        tp_player(vec(1, 1, 1))
        player.hitbox.vel = vec(0, 0, 0)

    # +++ Start of miscellaneous controls

    # Try to mine the block the player is looking at
    if controls['mine'] and not last_controls['mine'] or controls['place'] and not last_controls['place']:
        looking_at = block_through(player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0), scene.forward, 5)
        if controls['mine']:
            mine(looking_at.pos)
        elif looking_at.block_type != 'air':
            colliding, t_near, intersection, normal = ray_vs_hitbox(player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0), scene.forward.norm() * 5, looking_at.hitbox)
            if colliding:
                # Check to see if the block's new position would intersect the player's current position.
                new_block_hitbox = looking_at.hitbox.copy()
                new_block_hitbox.pos += normal * Block.scale
                new_block_hitbox.size -= 0.001 * vec(1, 1, 1)
                in_player = hitbox_vs_hitbox(player.hitbox, new_block_hitbox)
                if not in_player:
                    block_type = get_from_inventory(current_slot)
                    if block_type != 'air':
                        Block(looking_at.pos + normal * Block.scale, block_type)
                else:
                    print('Cannot place block here')
        else:
            print('Must be looking at a block\'s face to place blocks')

    # Toggle first person and third person views
    if controls['toggle_view'] and not last_controls['toggle_view']:
        print('Toggled first person view')
        first_person = not first_person
        if first_person:
            scene.userspin = False
            scene.userzoom = False
            mouse_spinning = False
            dragging = False
            move_camera(player)
            camera_angle_y = pi / 2 - scene.up.diff_angle(scene.forward)
            scene.forward = rotate(vec(1, 0, 0), angle = -camera_angle_xz, axis = scene.up)
            scene.camera.up = vec(scene.up)
            scene.camera.orthogonal = rotate(vec(0, 0, 1), angle = -camera_angle_xz, axis = scene.up)
            scene.forward = rotate(scene.forward, angle = camera_angle_y, axis = scene.camera.orthogonal)
            scene.camera.up = rotate(scene.camera.up, angle = camera_angle_y, axis = scene.camera.orthogonal)
            player.hide_model()
        else:
            scene.userspin = True
            scene.userzoom = True
            player.show_model()

    for i in range(1, 9):
        if controls['slot' + str(i)] and not last_controls['slot' + str(i)]:
            print('Selected slot ' + str(i))
            current_slot = i
            break

    if controls['print_inventory'] and not last_controls['print_inventory']:
        print_inventory()

    if controls['toggle_pause'] and not last_controls['toggle_pause']:
            print("The game is paused")
            paused = True

    if controls['instructor_mode'] and not last_controls['instructor_mode']:
        flying = not flying
        if flying:
            max_vel = 12 * Block.scale * vec(1, 1, 1)   # max_vel adjusted for flying
            print('Instructor mode enabled')
        else:
            max_vel = 5 * Block.scale * vec(1, 14, 1)   # Regular max_vel reset
            print('Instructor mode disabled')

    if controls['grutor_mode'] and not last_controls['grutor_mode']:
        add_inventory('wood', 64)
        print('Grutor mode: 64 blocks of wood were added to your inventory')

    # +++ Start of CAMERA ROTATIONS

    # Control camera with arrow keys
    if controls['camera_left']:
        rotate_camera(1 * pi / 180, 0)
    elif controls['camera_right']:
        rotate_camera(-1 * pi / 180, 0)
    if controls['camera_down']:
        rotate_camera(0, -1 * pi / 180)
    elif controls['camera_up']:
        rotate_camera(0, 1 * pi / 180)

    # Compute the angle in the horizontal direction of the mouse on the screen relative to the camera's line of sight
    proj_xz = scene.mouse.ray - scene.mouse.ray.proj(scene.camera.up)
    if proj_xz.cross(scene.forward).dot(scene.camera.up) > 0:
        angle_x = scene.forward.diff_angle(proj_xz)
    else:
        angle_x = -scene.forward.diff_angle(proj_xz)

    # Compute the angle in the vertical direction of the mouse on the screen relative to the camera's line of sight
    proj_xy = scene.mouse.ray - scene.mouse.ray.proj(scene.camera.orthogonal)
    if scene.forward.cross(proj_xy).dot(scene.camera.orthogonal) > 0:
        angle_y = scene.forward.diff_angle(proj_xy)
    else:
        angle_y = -scene.forward.diff_angle(proj_xy)

    # Convert angles to percentages in terms of distance from the center to the edge of screen
    percent_x = -angle_x / (scene.width / scene.height * scene.fov / 2)
    percent_y = angle_y / (scene.fov / 2)

    # Set a threshold to activate the screen rotation in the horizontal direction
    if abs(percent_x) < userspin_threshold:
        percent_x = 0
    else:
        # Correct for threshold so that the rotation is smooth on the boundary of the threshold
        percent_x = 1 / (1 - userspin_threshold) * (percent_x - userspin_threshold * sign(percent_x))
        percent_x *= abs(percent_x)

    # Set a threshold to activate the screen rotation in the vertical direction
    if abs(percent_y) < userspin_threshold:
        percent_y = 0
    else:
        # Correct for threshold so that the rotation is smooth on the boundary of the threshold
        percent_y = 1 / (1 - userspin_threshold) * (percent_y - userspin_threshold * sign(percent_y))
        percent_y *= abs(percent_y)

    # If the mouse is being used to drag the camera rotation, disable rotating the camera with the mouse position until the user returns their mouse to the center of the screen
    if dragging:
        mouse_spinning = False
    elif not dragging and not mouse_spinning:
        mouse_spinning = percent_x == 0 and percent_y == 0

    # Rotate camera based on how far up/down and left/right the user's mouse is, but only if they are not current dragging
    if mouse_spinning and mouse_onscreen:
        rotate_camera(percent_x * userspin_rate, percent_y * userspin_rate)

    # Only update scene.camera.pos after all the physics updates and rotations are complete to avoid chopiness in the camera movement
    player.sync_model()
    player.rotate_model(camera_angle_xz - player.model_angle)
    move_camera(player)
    cursor.pos = player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0) + scene.forward.norm() * 0.5
    last_controls = {key: controls[key] for key in controls}

# +++ Start of EVENT_HANDLING section -- separate functions for keypresses and mouse clicks.0..

def keyup_fun(event):
    '''This function is called each time a key is released'''
    key = event.key
    update_controls(key, False)

def keydown_fun(event):
    '''This function is called each time a key is pressed'''
    global current_slot
    key = event.key
    update_controls(key, True)

def update_controls(key, pressed):
    '''Updates the controls dictionary given a key string and whether it was just pressed or released'''
    if key in 'wW':
        controls['forward'] = pressed
    elif key in 'aA':
        controls['left'] = pressed
    elif key in 'sS':
        controls['backward'] = pressed
    elif key in 'dD':
        controls['right'] = pressed
    elif key == ' ':
        controls['jump'] = pressed
    elif key == 'shift':
        controls['descend'] = pressed
    elif key == 'up':
        controls['camera_up'] = pressed
    elif key == 'left':
        controls['camera_left'] = pressed
    elif key == 'down':
        controls['camera_down'] = pressed
    elif key == 'right':
        controls['camera_right'] = pressed
    elif key in 'qQ':
        controls['mine'] = pressed
    elif key in 'eE':
        controls['place'] = pressed
    elif key in 'vV':
        controls['toggle_view'] = pressed
    elif key in 'pP':
        controls['print_inventory'] = pressed
    elif key == '-':
        controls['slot_dec'] = pressed
    elif key in '+=':
        controls['slot_inc'] = pressed
    elif key == 'esc':
        controls['toggle_pause'] = pressed
    elif key in 'gG':
        controls['grutor_mode'] = pressed
    elif key in 'iI':
        controls['instructor_mode'] = pressed
    for i in range(1, 9):
        if key == str(i):
            controls['slot' + str(i)] = pressed
            break

previous_mouse_pos = vec(0, 0, 0)
def mousedown_fun(event):
    '''Runs when the mouse button is pressed'''
    global previous_mouse_pos, dragging
    dragging = True
    previous_mouse_pos = vec(event.pageX, event.pageY, 0)

def mousemove_fun(event):
    ''' Runs when the mouse is moved on the canvas. According to the documentaiton, it should run regardless 
        of whether the mouse is being held, but it doesn't
    '''
    global previous_mouse_pos
    mouse_pos = vec(event.pageX, event.pageY, 0)
    delta_pos = previous_mouse_pos - mouse_pos
    angle_x = -delta_pos.x / scene.width
    angle_y = -delta_pos.y / scene.height
    rotate_camera(angle_x, angle_y)
    move_camera(player)
    previous_mouse_pos = mouse_pos

def mouseup_fun(event):
    '''Runs when the mouse button is released'''
    global dragging
    dragging = False

def mouseenter_fun(event):
    '''Runs when the mouse enters the canvas'''
    global mouse_onscreen
    mouse_onscreen = True

def mouseleave_fun(event):
    '''Runs when the mouse leaves the canvas'''
    global mouse_onscreen
    mouse_onscreen = False

# +++ Start of utility functions

def sign(value):
    '''Returns the sign of the given value as either 1 or -1. If the value is 0, 1 is returned'''
    if value < 0:
        return -1
    else:
        return 1

def div(a, b):
    '''Division of a over b that takes into account dividing by 0 and returns infinity, -infinity, or NaN'''
    if a == 0 and b == 0:
        return NaN
    elif b == 0:
        return sign(a) * Infinity
    else:
        return a / b

def sort_pair(value0, value1):
    ''' Accepts two values and returns a tuple with the first element being the smaller of the two 
        values and the second element being the larger of the two values
    '''
    if value0 > value1:
        return (value1, value0)
    else:
        return (value0, value1)

def ray_vs_hitbox(origin, ray_dir, hitbox):
    ''' Checks for a collision between a ray and a hitbox given the ray's origin and a vector representing its 
        direction and magnitude.
    '''
    V0, V1 = hitbox.get_vertices()

    # Find the intersection points between the parameterization of the ray and the planes on which the hitbox's faces lie on
    t_x_near, t_x_far = sort_pair(div(V0.x - origin.x, ray_dir.x), div(V1.x - origin.x, ray_dir.x))
    t_y_near, t_y_far = sort_pair(div(V0.y - origin.y, ray_dir.y), div(V1.y - origin.y, ray_dir.y))
    t_z_near, t_z_far = sort_pair(div(V0.z - origin.z, ray_dir.z), div(V1.z - origin.z, ray_dir.z))

    # Check if the intersection points found give a point on one of the hitbox's faces
    if (t_x_near >= t_z_far or t_y_near >= t_z_far or
        t_y_near >= t_x_far or t_z_near >= t_x_far or
        t_z_near >= t_y_far or t_x_near >= t_y_far):
        return (False, 0, vec(0, 0, 0), vec(0, 0, 0))

    # Get the t values for the near and far intersection points. These can be plugged back into the parameterization of the ray to get the actual point
    t_near = max(t_x_near, t_y_near, t_z_near)
    t_far = min(t_x_far, t_y_far, t_z_far)

    # If the furthest intersection point along the ray is less than 0 or the nearest point is greater than 1, the collision didn't occur on the part of part of the ray being checked
    if isNaN(t_near) or isNaN(t_far) or t_far <= 0 or t_near > 1:
        return (False, 0, vec(0, 0, 0), vec(0, 0, 0))
    
    intersection = origin + ray_dir * t_near
    normal = vec(0, 0, 0)

    # Find the collision normal
    if t_x_near > t_y_near and t_x_near > t_z_near:
        normal = vec(-sign(ray_dir.x), 0, 0)
    elif t_y_near > t_x_near and t_y_near > t_z_near:
        normal = vec(0, -sign(ray_dir.y), 0)
    elif t_z_near > t_x_near and t_z_near > t_y_near:
        normal = vec(0, 0, -sign(ray_dir.z))
    
    return (True, t_near, intersection, normal)

def clamp(value, upper, lower = None):
    ''' Clamps a value to within the range [-upper, upper] or, if lower is specified, [lower, upper]
        If the given value for lower is greater than the value for upper (or if only upper is given and it is negative),
        for any value given within [upper, lower], the closer of the two endpoints is returned.
        Although this function is valid python, there seems to be a bug in VPython where I have to give a lower value
        or I get an error message.
    '''
    if lower == None:
        lower = -upper
    if lower > upper:
        mid = (lower + upper) / 2
        if value < upper or value > lower:
            return value
        elif value < mid:
            return upper
        else:
            return lower
    return min(max(value, lower), upper)

def tp_player(new_pos):
    '''Teleport the player so that their lower half occupies the block with the given position'''
    player.hitbox.pos.x = new_pos.x * Block.scale + Block.scale / 2
    player.hitbox.pos.y = new_pos.y * Block.scale + Block.scale
    player.hitbox.pos.z = new_pos.z * Block.scale + Block.scale / 2
    player.sync_model()

def nearest_block(pos, truncFunc = round):
    ''' Return the position of the nearest block to the given position. 
        The given function for truncFunc is the operation used to return the block position as integers. 
        It defaults to the round function
    '''
    block_pos = vec(0, 0, 0)
    block_pos.x = truncFunc((pos.x - Block.scale / 2) / Block.scale)
    block_pos.y = truncFunc((pos.y - Block.scale / 2) / Block.scale)
    block_pos.z = truncFunc((pos.z - Block.scale / 2) / Block.scale)
    return block_pos

def block_at(pos):
    '''Return the block in the map at the give position. If no block is found, an air block is returned'''
    key = (pos.x, pos.y, pos.z)
    if key in Block.blocks:
        return Block.blocks[key]
    else:
        return Block(pos, 'air')

def mine(pos):
    '''Attempts to mine the block at the given position. If the block is not already air, it is replaced with air'''
    block_pos = nearest_block(pos, round)
    block = block_at(block_pos)
    if block.block_type == 'air':
        print('Cannot mine air')
    else:
        print('Removed block of type', block.block_type)
        block.remove()
        add_inventory(block.block_type, 1)

def add_inventory(block_type, num):
    '''Add a block to the player's inventory'''
    first_unoccupied = 0
    for slot in range(1, 9):
        if slot in inventory:
            slot_type, number = inventory[slot]
            if slot_type == block_type:
                inventory[slot] = [slot_type, number + num]
                return
        elif first_unoccupied == 0:
            first_unoccupied = slot
    
    if first_unoccupied != 0:
        inventory[first_unoccupied] = (block_type, 1)

def get_from_inventory(slot):
    if slot in inventory:
        block_type, number = inventory[slot]
        if number == 1:
            del inventory[slot]
        else:
            inventory[slot] = [block_type, number - 1]
        return block_type
    else:
        print('You have nothing in your selected slot')
        return 'air'

def print_inventory():
    if len(inventory) == 0:
        print('Your inventory is empty')
    else:
        print('Your inventory contains')
        for slot in inventory:
            block_type, number = inventory[slot]
            print(str(number) + ' x ' + block_type + ' in slot ' + str(slot))
    print('Slot ' + str(current_slot) + ' is selected')
        

def get_local_blocks(hitbox, dt):
    '''Return the list of blocks immediately surrounding the given box that it could possible be colliding with'''
    blocks = []
    expanded_hitbox = Hitbox(hitbox.pos + hitbox.vel * dt / 2, vec(abs(hitbox.vel.x * dt), abs(hitbox.vel.y * dt), abs(hitbox.vel.z * dt)) + hitbox.size)
    v0, v1 = expanded_hitbox.get_vertices()
    block_pos_0 = nearest_block(v0, floor)
    block_pos_1 = nearest_block(v1, ceil)
    block_diff = block_pos_1 - block_pos_0

    for x in range(block_diff.x + 1):
        for y in range(block_diff.y + 1):
            for z in range(block_diff.z + 1):
                block = block_at(block_pos_0 + vec(x, y, z))
                if block.block_type != 'air':
                    blocks += [block]
    return blocks

def hitbox_vs_hitbox(hitboxA, hitboxB):
    '''Returns true if the two boxes overlap and false otherwise'''
    A1, A2 = hitboxA.get_vertices()
    B1, B2 = hitboxB.get_vertices()
    return (A2.x > B1.x and A1.x < B2.x and 
            A2.y > B1.y and A1.y < B2.y and 
            A2.z > B1.z and A1.z < B2.z)

def get_collision_manifold(hitboxA, hitboxB, dt):
    '''Gets the collision manifold of hitboxA and hitboxB, assuming hitboxA is the one that was moving'''
    # If A's velocity is 0, it can't be about to collide with B in the next frame, since it isn't moving
    if hitboxA.vel.mag == 0:
        return (False, 0, vec(0, 0, 0), vec(0, 0, 0))

    # Create the expanded hitbox
    expanded_hitbox = hitboxB.copy()
    expanded_hitbox.size += hitboxA.size
    return ray_vs_hitbox(hitboxA.pos, hitboxA.vel * dt, expanded_hitbox)

def insertion_sort(L, lt):
    """ Implementation of insertion sort given a less than comparator function. Using the key parameter in python's 
        built in sorted function doesn't seem to work in VPython. Solely used for sorting collision manifolds based
        on which collision occurs first. Since the actual number of blocks the player is colliding with at any point
        in time should be relatively small, insertion sort should be a good choice to quickly sort them.
    """
    for i in range(len(L)):
        # Element to be inserted into the part of the list behind it
        a = L[i]

        # Loop through the list behind the current element to be inserted
        for j in range(0, i):
            # Element to compare against
            b = L[i - j - 1]

            # If a < b, swap b one position up. Otherwise, a's position is right in front of b
            if lt(a, b):
                L[i - j] = b

                # If we are at the beginning of the list, that means a is smaller than all the elements behind it, and all those elements have been shifted 
                # one position forward. Therefore, the first element of the list is set to a
                if j == i - 1:
                    L[0] = a
            else:
                L[i - j] = a
                break
    return L

def resolve_collisions(hitboxA, hitboxes, dt):
    ''' Check for and resolve a collision between the given hitbox and the list of hitboxes. If a collision 
        is found, hitboxA is displaced to resolve the collision and has its velocity in the direction of the 
        collision canceled.
    '''
    faces = {'top': False}

    # Store the manifolds in a tuple with the hitbox that generated it
    manifold_wrappers = []
    for hitboxB in hitboxes:
        manifold = get_collision_manifold(hitboxA, hitboxB, dt)
        if manifold[0]:
            manifold_wrappers += [[manifold, hitboxB]]
    
    def comp_t_near(wrapperA, wrapperB):
        """Compare the t_near values of two manifolds"""
        return wrapperA[0][1] < wrapperB[0][1]

    # Sort manifolds by the ones corresponding to the hitbox closest to hitboxA
    # manifold_wrappers = sorted(manifold_wrappers, key = get_t_near)   # Doesn't work
    # manifold_wrappers = sorted(manifold_wrappers)                     # Also doesn't work
    insertion_sort(manifold_wrappers, comp_t_near)                      # I had to implement a sorting algorithm :(

    # Loop through sorted manifolds and resolve the collisions
    for manifold, hitboxB in manifold_wrappers:
        # The manifold has to be recalculated since resolving previous collisions changes the velocity of the hitbox
        colliding, t_near, intersection, normal = get_collision_manifold(hitboxA, hitboxB, dt)
        if colliding:
            if normal.y == 1:
                faces['top'] = True
            hitboxA.vel += vec(normal.x * abs(hitboxA.vel.x), normal.y * abs(hitboxA.vel.y), normal.z * abs(hitboxA.vel.z)) * (1 - t_near)

    return faces

def rotate_camera(angle_x, angle_y):
    '''Rotates the camera and other relevant vectors given an x and y angle'''
    if not first_person:
        return

    # Rotate around the scene.up vector for the x rotation
    scene.mouse.ray = rotate(scene.mouse.ray, angle = angle_x, axis = scene.up)
    scene.camera.up = rotate(scene.camera.up, angle = angle_x, axis = scene.up)
    scene.forward = rotate(scene.forward, angle = angle_x, axis = scene.up)

    # Find camera angle in the y direction and set upward and downward bounds
    camera_angle_y = scene.up.diff_angle(scene.forward)
    up_bound = 0.01 * pi / 180
    down_bound = (180 - 0.01) * pi / 180
    
    # If the camera is within the bounds, rotate around the vector orthogonal to the camera's up vector and the scene's forward vector for the y rotation
    if (camera_angle_y > up_bound and angle_y > 0) or (camera_angle_y < down_bound and angle_y < 0):
        # Set angle_y to the bound when it exceeds it
        if camera_angle_y - angle_y < up_bound:
            angle_y = camera_angle_y - up_bound
        elif camera_angle_y - angle_y > down_bound:
            angle_y = camera_angle_y - down_bound
        
        # Do the actual rotation
        scene.camera.orthogonal = scene.forward.cross(scene.camera.up)
        scene.camera.up = rotate(scene.camera.up, angle = angle_y, axis = scene.camera.orthogonal)
        scene.mouse.ray = rotate(scene.mouse.ray, angle = angle_y, axis = scene.camera.orthogonal)
        scene.forward = rotate(scene.forward, angle = angle_y, axis = scene.camera.orthogonal)

def move_camera(player):
    '''Moves the camera to the player object'''
    if first_person:
        # scene.camera.pos = player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0) + scene.forward.norm() * Player.scale / 2 * 1.001
        scene.camera.pos = player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0)
    else:
        scene.center = player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0)

def block_through(origin, direction, max_distance):
    ''' Uses a simple ray tracing algorithm to find the first block that intersects the ray from the given origin, 
        in the given direction, within the given range
    '''
    ds = Block.scale / 10
    direction = direction.norm()
    for i in range(max_distance / ds):
        block = block_at(nearest_block(origin + direction * ds * i, round))
        if block.block_type != 'air':
            return block
    return block