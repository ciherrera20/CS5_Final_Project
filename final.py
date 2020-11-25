GlowScript 3.0 VPython

# Scene background color and dimensions
scene.background = color.cyan
scene.width = 640
scene.height = 480
scene.resizable = True

# Bind event listeners
scene.bind('keydown', keydown_fun)
scene.bind('keyup', keyup_fun)
scene.bind('mousedown', mousedown_fun)
scene.bind('mousemove', mousemove_fun)
scene.bind('mouseup', mouseup_fun)
scene.bind('mouseenter', mouseenter_fun)
scene.bind('mouseleave', mouseleave_fun)

# +++ Start of CLASS CREATION -- Create the classes used throughout the game

class Hitbox:
    ''' Wrapper class to hold information about axis aligned hitboxes. Used for collision detection instead of the 
        box class in VPython, since the hitboxes don't need to be displayed or have as many options.
    '''
    def __init__(self, pos, size, vel = vec(0, 0, 0)):
        self.pos = pos
        self.vel = vel
        self.size = size

    def get_vertices(self):
        return (vec(self.pos.x - self.size.x / 2, self.pos.y - self.size.y / 2, self.pos.z - self.size.z / 2), vec(self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2, self.pos.z + self.size.z / 2))

    def copy(self):
        return Hitbox(vec(self.pos), vec(self.size), vec(self.vel))

class Face:
    '''Wrapper class for a quad object to allow it to be easily created, textured/colored, moved, and rotated'''
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
        '''Moves all the vertices in the quad to the given new position. Not guaranteed to work if self.pos has been modified since vertex offsets are computed to it'''
        for vertex in self.vertices:
            vertex.pos = vertex.pos - self.pos + new_pos
        self.pos = vec(new_pos)

    def rotate(self, angle, axis, origin):
        '''Rotate all vertices by the given angle about the given axis and origin'''
        for vertex in self.vertices:
            vertex.rotate(angle = angle, axis = axis, origin = origin)

    def hide(self):
        '''Hide the quad'''
        self.quad.visible = False

    def show(self):
        '''Show the quad'''
        self.quad.visible = True

class Block:
    '''Represents the blocks that make up the world'''
    scale = 1       # Everything should be defined in relation to this block scale, but we haven't actually tested changing it
    color_map = {'dirt': vec(127 / 255, 92 / 255, 7 / 255), 'leaf': vec(12 / 255, 179 / 255, 26 / 255), 'cobblestone': 0.5 * vec(1, 1, 1)}
    texture_map = {'dirt': texture = 'https://lh3.googleusercontent.com/DpmqnZGty6vns7713z1kTAp3AwBqrZ5ZYz_jf-x04p3lFfQ3Q9j5KruZ-v81846PtM1A9HMHvxQkPpoOqViuvA=s400', 
                'cobblestone': texture = 'https://i.imgur.com/2wWquQv.png',
                'lava': texture = 'https://qph.fs.quoracdn.net/main-qimg-5691a6bcf4bd21df68e741ee1d9d4e0f',
                'water': texture = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcR-ErVpce1X6Y7Z4bYIK9PJfLL4hh_R9nvbFg&usqp=CAU',
                'wood': texture = 'https://i.imgur.com/n6J1Jhz.jpg',
                'leaf': texture = 'https://i.imgur.com/E4ycyzv.jpg',
                'grass_top': texture = {'file': 'https://lh3.googleusercontent.com/0Xh1P9-7QIXw2j-TM5lGIo5Vvtkq3UIwynD04RgngIOU-4KOy06ZONL93Ht4YyCXEVXojj5Xn-H1m6NHC4rmW-g=s400', 'place':['sides']},
                'grass': texture = {'file':'https://lh3.googleusercontent.com/2ZdPa8KBDybnUudpc9yRmaCU3DYHH4SL7gxRTPwyk1oCn_1xCzntDLkb02MChMipFu-N3BzNAtXP2BCiwOl9WgM', 'place':['sides']}}
    solid_map = {'dirt': True, 'air': False, 'water': False, 'lava': False, 'wood': True, 'grass': True, 'leaf': True, 'cobblestone': True}
    blocks = {}     # Map of grid positions to the blocks occupying them
    def __init__(self, pos, block_type, block_data = 0):
        # Align the block to a grid
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Block.scale + Block.scale / 2
        self.pos.y = floor(pos.y) * Block.scale + Block.scale / 2
        self.pos.z = floor(pos.z) * Block.scale + Block.scale / 2
        self.block_data = block_data
        if block_type in Block.solid_map:
            self.solid = Block.solid_map[block_type]
        else:
            self.solid = False

        # Array to hold the VPython objects which make up the block's model
        self.model = []

        # The block's actual hitbox
        self.hitbox = Hitbox(self.pos, vec(Block.scale, Block.scale, Block.scale))

        # Texture the faces based on the block's type
        self.block_type = block_type
        if block_type != 'air':
            # Default is no textures and a magenta color indicating an unknown block
            block_north = block_east = block_south = block_west = block_top = block_bottom = None
            block_color = color.magenta
            if block_type in Block.texture_map:
                block_north = block_east = block_south = block_west = block_top = block_bottom = Block.texture_map[block_type]
                block_color = vec(1, 1, 1)
                if block_type == 'grass':
                    block_north = block_east = block_south = block_west = Block.texture_map['grass']
                    block_top = Block.texture_map['grass_top']
                    block_bottom = Block.texture_map['dirt']
                
                #checks when lava or water and block_data counts how many blocks can go out
                elif (block_type == 'water' or block_type == 'lava') and self.block_data < 5 and pos.y > -10:
                    first_around = [vec(pos.x+1,pos.y,pos.z), vec(pos.x-1,pos.y,pos.z), vec(pos.x,pos.y,pos.z+1), vec(pos.x,pos.y,pos.z-1)]
                    around = [vec(pos.x+1,pos.y,pos.z), vec(pos.x-1,pos.y,pos.z), vec(pos.x,pos.y,pos.z+1), vec(pos.x,pos.y,pos.z-1), vec(pos.x,pos.y-1,pos.z-1), vec(pos.x,pos.y+1,pos.z)]
                    #checks if block below is empty
                    if block_at(pos + vec(0,-1,0)).block_type == 'air':
                        Block(pos + vec(0,-1,0), block_type, self.block_data) 
                    else: 
                        #loops through possible directions the flow can go
                        for i in first_around:
                            closest = block_at(i)
                            if closest.block_type == 'air':
                                Block(i,self.block_type, self.block_data + 1)
                    for a in around: 
                        nearby = block_at(a)
                        if (self.block_type == "water" and nearby.block_type == 'lava') or (self.block_type == "lava" and nearby.block_type == 'water'):
                            Block(a, 'cobblestone')

            # If the block type is found in the texture map, apply those textures
            if block_type in Block.texture_map:
                block_north = block_east = block_south = block_west = block_top = block_bottom = Block.texture_map[block_type]
                block_color = vec(1, 1, 1)
                if block_type == 'grass':
                    block_north = block_east = block_south = block_west = Block.texture_map['grass']
                    block_top = Block.texture_map['grass_top']
                    block_bottom = Block.texture_map['dirt']
            elif block_type in Block.color_map:     # If the block type is found in the color map, apply that color
                block_color = Block.color_map[block_type]

            # Create the 6 faces of the block with the specified textures/color and add them to the model array            
            self.west = Face(pos = vec(self.pos.x, self.pos.y, self.pos.z - Block.scale / 2), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 0, -1), axis = vec(-1, 0, 0), texture = block_west, color = block_color)
            self.east = Face(pos = vec(self.pos.x, self.pos.y, self.pos.z + Block.scale / 2), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 0, 1), axis = vec(1, 0, 0), texture = block_east, color = block_color)
            self.south = Face(pos = vec(self.pos.x - Block.scale / 2, self.pos.y, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(-1, 0, 0), axis = vec(0, 0, 1), texture = block_south, color = block_color)
            self.north = Face(pos = vec(self.pos.x + Block.scale / 2, self.pos.y, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(1, 0, 0), axis = vec(0, 0, -1), texture = block_north, color = block_color)
            self.top = Face(pos = vec(self.pos.x, self.pos.y + Block.scale / 2, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 1, 0), axis = vec(0, 0, 1), texture = block_top, color = block_color)
            self.bottom = Face(pos = vec(self.pos.x, self.pos.y - Block.scale / 2, self.pos.z), size = vec(Block.scale, Block.scale, 0), normal = vec(0, 1, 0), axis = vec(0, 0, -1), texture = block_bottom, color = block_color)
            self.model = [self.north, self.east, self.west, self.south, self.bottom, self.top]

        # Add the block to the map, or if its an air block, just remove the previous block
        key = (floor(pos.x), floor(pos.y), floor(pos.z))
        if key in Block.blocks:
            # Hide the old block's model and delete it from the map
            oldBlock = Block.blocks[key]
            for side in oldBlock.model:
                side.hide()
            del Block.blocks[key]
        if block_type != 'air':
            Block.blocks[key] = self

    def __repr__(self):
        return self.block_type + 'block'

    def remove(self):
        '''Remove the block by replacing it with an air block'''
        Block(self.pos, 'air')

class Player:
    '''Represents the player interacting with the world'''
    scale = 0.93 * Block.scale / 2
    
    def __init__(self, pos):
        # Create the player's hitbox
        self.hitbox = Hitbox(pos, vec(Block.scale * 0.6, Block.scale * 1.8, Block.scale * 0.6))
        self.hitbox.vel = vec(0, 0, 0)
        self.hitbox.last_pos = vec(self.hitbox.pos)
        
        # Array to hold the VPython objects which make up the player's model
        self.model = []

        #head
        self.face = box(size = vec(Player.scale, Player.scale, 0.001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, self.hitbox.pos.y, self.hitbox.pos.z), texture= 'https://i.imgur.com/xGBPM4r.png', emissive = True)
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

        # Create the property model_angle which rotate_model depends on, rotate the model, and then reset model_angle to 
        # change its orientation relative to the camera's angle
        self.model_angle = 0
        self.rotate_model(-pi / 2)
        self.model_angle = 0

        # Move each part of the model up and in x direction a bit to align it with the hitbox's position
        for part in self.model:
            part.pos.y += 0.93 * Block.scale - Player.scale / 2
            part.pos.x += Player.scale / 2

        # Display hitbox with a white transparent box
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
        '''Hide the player's model'''
        for part in self.model:
            part.visible = False

    def show_model(self):
        '''Show the player's model'''
        for part in self.model:
            part.visible = True

class Entity:
    entities = []
    def __init__(self, pos, size, vel = vec(0, 0, 0), center_point = vec(0, 0, 0), k = 1):
        actual_pos = vec(0, 0, 0)
        actual_pos.x = floor(pos.x) * Block.scale + Block.scale / 2
        actual_pos.y = floor(pos.y) * Block.scale + Block.scale / 2
        actual_pos.z = floor(pos.z) * Block.scale + Block.scale / 2

        self.center_point = vec(0, 0, 0)
        self.center_point.x = floor(center_point.x) * Block.scale + Block.scale / 2
        self.center_point.y = floor(center_point.y) * Block.scale + Block.scale / 2
        self.center_point.z = floor(center_point.z) * Block.scale + Block.scale / 2

        self.hitbox = Hitbox(actual_pos, size, vel)
        self.hitbox.last_pos = vec(actual_pos)
        self.k = k
        self.model = [box(pos = actual_pos, size = size, color = color.green, emissive = True)]
        Entity.entities += [self]
    
    def physics_update(self, dt):
        '''Update acceleration to point toward the center point'''
        self.hitbox.accel = -self.k * (self.hitbox.pos - self.center_point)
        self.hitbox.vel += self.hitbox.accel * dt
        self.hitbox.pos += self.hitbox.vel * dt
        self.sync_model()
    
    def sync_model(self):
        '''Move all the boxes which make up the entity's model the same amount that the entity's hitbox has moved'''
        displacement = self.hitbox.pos - self.hitbox.last_pos
        for box in self.model:
            box.pos += displacement
        self.hitbox.last_pos = vec(self.hitbox.pos)
    
    def hide_model(self):
        '''Hide the entity's model'''
        for part in self.model:
            part.visible = False

    def show_model(self):
        '''Show the entity's model'''
        for part in self.model:
            part.visible = True


# +++ Start of object creation -- Create the player and the blocks making up the world

# Create player and move them to the position (1, 1, 1)
player = Player(vec(0, Block.scale, 0))
tp_player(vec(1, 1, 1))

# Create entity obstacles that try to push you off the map
Entity(pos = vec(6, 1, 6), size = vec(1, 1, 1), center_point = vec(3, 1, 6), k = 3)
Entity(pos = vec(2, 1, 8), size = vec(1, 1, 1), center_point = vec(2, 1, 11), k = 3)

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

Block(vec(3,0,4), 'cobblestone')
Block(vec(3,0,6), 'cobblestone')
Block(vec(4,0,6), 'cobblestone')
Block(vec(4,0,7), 'cobblestone')
Block(vec(4,0,9), 'cobblestone')
Block(vec(2,0,9), 'cobblestone')
Block(vec(2,0,10), 'cobblestone')
Block(vec(2,0,11), 'cobblestone')

#wall
for y in range(-1,4):
    for z in range(11,16):
        Block(vec(3,y,z), 'cobblestone')

Block(vec(3,0,18), 'cobblestone')
Block(vec(3,-6,20), 'cobblestone')

#stairs
Block(vec(3,-6,22), 'wood')
Block(vec(3,-6,23), 'wood')
Block(vec(3,-5,23), 'wood')
Block(vec(3,-5,24), 'wood')
Block(vec(3,-4,24), 'wood')
Block(vec(3,-4,25), 'wood')
Block(vec(3,-3,25), 'wood')
Block(vec(3,-3,26), 'wood')
Block(vec(3,-2,26), 'wood')
Block(vec(3,-2,27), 'wood')
Block(vec(3,-1,27), 'wood')
Block(vec(3,-1,28), 'wood')
Block(vec(3,-0,28), 'wood')


#rest island
for x in range(1,4):
    for y in range(1,3):
        for z in range(30,33):
            Block(vec(x, 0, z), 'grass')
            Block(vec(x, -y, z), 'dirt')

Block(vec(0,0,35), 'cobblestone')
Block(vec(0,-1,37), 'cobblestone')
Block(vec(0,-1,39), 'cobblestone')
Block(vec(0,-1,41), 'cobblestone')
Block(vec(0,0,43), 'cobblestone')
Block(vec(3,0,45), 'cobblestone')
Block(vec(3,0,48), 'cobblestone')
Block(vec(3,0,51), 'cobblestone')
Block(vec(6,0,51), 'cobblestone')
Block(vec(6,0,54), 'cobblestone')
Block(vec(6,0,57), 'cobblestone')
Block(vec(3,0,57), 'cobblestone')
Block(vec(1,-8,57), 'cobblestone')
Block(vec(1,-8,59), 'cobblestone')

#pillar: tower or build staircase
for y in range(1,8):
    Block(vec(1,-y,62), 'cobblestone')

Block(vec(1,0,65), 'cobblestone')
Block(vec(1,0,66), 'cobblestone')
Block(vec(1,-1,69), 'cobblestone')
Block(vec(1,-1,70), 'cobblestone')
Block(vec(1,-1,71), 'cobblestone')
Block(vec(3,-1,73), 'cobblestone')
Block(vec(3,-1,74), 'cobblestone')
Block(vec(3,-1,75), 'cobblestone')
Block(vec(1,0,77), 'cobblestone')
Block(vec(1,0,78), 'cobblestone')
Block(vec(1,0,79), 'cobblestone')

#rest island
for x in range(1,4):
    for y in range(1,3):
        for z in range(81,84):
            Block(vec(x, 0, z), 'grass')
            Block(vec(x, -y, z), 'dirt')

#U1
Block(vec(2,0,86), 'cobblestone')
Block(vec(2,0,87), 'cobblestone')
Block(vec(1,0,87), 'cobblestone')
Block(vec(3,0,87), 'cobblestone')
Block(vec(1,1,87), 'cobblestone')
Block(vec(3,1,87), 'cobblestone')
Block(vec(1,2,87), 'cobblestone')
Block(vec(3,2,87), 'cobblestone')
#U2
Block(vec(3,0,89), 'cobblestone')
Block(vec(2,0,89), 'cobblestone')
Block(vec(4,0,89), 'cobblestone')
Block(vec(2,1,89), 'cobblestone')
Block(vec(4,1,89), 'cobblestone')
Block(vec(2,2,89), 'cobblestone')
Block(vec(4,2,89), 'cobblestone')
#U3
Block(vec(2,0,91), 'cobblestone')
Block(vec(1,0,91), 'cobblestone')
Block(vec(3,0,91), 'cobblestone')
Block(vec(1,1,91), 'cobblestone')
Block(vec(3,1,91), 'cobblestone')
Block(vec(1,2,91), 'cobblestone')
Block(vec(3,2,91), 'cobblestone')
#U4
Block(vec(3,0,93), 'cobblestone')
Block(vec(2,0,93), 'cobblestone')
Block(vec(4,0,93), 'cobblestone')
Block(vec(2,1,93), 'cobblestone')
Block(vec(4,1,93), 'cobblestone')
Block(vec(2,2,93), 'cobblestone')
Block(vec(4,2,93), 'cobblestone')

#floor:
for x in range(-1,5):
        for z in range(95,100):
            Block(vec(x, 0, z), 'grass')

# +++ Start of game loop section -- update the position of the player and other entities continuously

# Other constants
RATE = 30                                   # The number of times the while loop runs each second
dt = 1.0 / (1.0 * RATE)                     # The time step each time through the while loop
player.on_ground = False                    # False initially. Keeps track of whether the player is touching the ground
scene.autoscale = False                     # Avoids changing the view automatically
scene.userpan = False                       # Disables the default panning controls
scene.range = 3                             # Default camera distance from the center of the scene
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
first_person = True                         # Starts off in third person
paused = False                              # Starts off unpaused
infinite_blocks = False                      # Keeps track of whether the player has infinite bocks
flying = False                              # Keeps track of whether the player is flying
current_slot = 1                            # Keeps track of which slot of the player's inventory is currently selected
queued_rot_x = 0                            # Keeps track of the amount of rotation in the x direction queued for the while loop by mousemove_fun
queued_rot_y = 0                            # Keeps track of the amount of rotation in the y direction queued for the while loop by mousemove_fun
inventory = {1: ['dirt', 1], 2: ['water', 1], 3: ['lava', 1]}
if first_person:
    scene.userzoom = False
    scene.userspin = False
    player.hide_model()
else:
    scene.userzoom = True
    scene.userspin = True
    player.show_model()

# Visual cursor to show what blocks the player is looking at
cursor = box(size = vec(0.01, 0.01, 0.01), color = color.black, emissive = True)

# Dictionary mapping a control to whether it is active. Updated by keyboard events
controls = {control: False for control in ['up', 'down', 'left', 'right', 'jump', 'descend', 'camera_up', 'camera_down', 'camera_left', 'camera_right', 'mine', 'place', 'toggle_view', 'print_inventory', 'slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8', 'slot9', 'toggle_pause', 'grutor_mode', 'professor_mode']}
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

    # Apply velocity updates in the x and z directions
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

    # Set velocity when the player jumps/flies
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

    # Check for and resolve collisions between the player and the entities
    for entity in Entity.entities:
        entity.physics_update(dt)
        colliding = hitbox_vs_hitbox(player.hitbox, entity.hitbox)
        if colliding:
            pos_diff = player.hitbox.pos - entity.hitbox.pos
            distance = mag(pos_diff)
            normal = vec(pos_diff.x, 0, pos_diff.z).norm()
            max_distance = abs((player.hitbox.size + entity.hitbox.size).dot(vec(abs(normal.x), 0, abs(normal.z))))
            strength = max_distance - distance
            player.hitbox.vel += -player.hitbox.vel.proj(normal) * (1 - distance / max_distance) + normal * max(entity.hitbox.vel.dot(normal), 0)

    # Check for and resolve collisions between the player and all the blocks surrounding them
    player.on_ground = False
    hitboxes = []
    for block in get_local_blocks(player.hitbox, dt):
        hitboxes += [block.hitbox]
    player.on_ground = resolve_collisions(player.hitbox, hitboxes, dt)['top']

    # Update the player's position
    player.hitbox.pos = player.hitbox.pos + player.hitbox.vel * dt

    # Reset the player's position if they fall too far
    if player.hitbox.pos.y < -50:
        print('You fell into the void')
        tp_player(vec(1, 1, 1))
        player.hitbox.vel = vec(0, 0, 0)

    # +++ Start of miscellaneous controls

    # Mining and block placing
    if (controls['mine'] and not last_controls['mine']) or (controls['place'] and not last_controls['place']):
        # Find the block the player is looking at
        looking_at = block_through(player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0), scene.forward, 5)

        # If the selected action is mining, attempt to mine the block being looked at. Otherwise, attempt to place a block against it
        if controls['mine']:
            mine(looking_at.pos)
        else:
            # Only place a block if the block being looked at is not air
            if looking_at.solid:
                # Find the normal vector to the face the player is looking at
                colliding, t_near, intersection, normal = ray_vs_hitbox(player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0), scene.forward.norm() * 5, looking_at.hitbox)
                if colliding:
                    # Check to see if the placed block's position would intersect the player's current position.
                    new_block_hitbox = looking_at.hitbox.copy()                         # Copy the hitbox of the block being looked at as the new block's hitbox
                    new_block_hitbox.pos += normal * Block.scale                        # Adjust the new block's hitbox to be against the face being looked at
                    new_block_hitbox.size -= 0.001 * vec(1, 1, 1)                       # Small size adjustment to allow for the player's hitbox being right up against the new block's
                    in_player = hitbox_vs_hitbox(player.hitbox, new_block_hitbox)       # Perform the collision detection
                    if not in_player:
                        # Check the currently selected slot in the player's inventory to see if they have a placeable block
                        block_type = get_from_inventory(current_slot)
                        if block_type != 'air':
                            Block(nearest_block(looking_at.pos, floor) + normal * Block.scale, block_type)
                        else:
                            print('You have nothing in your selected slot')
                    else:
                        print('Cannot place block overlapping with player')
                else:
                    print('If you see this message, the ray vs box collision algorithm failed :(')
            else:
                print('Must be looking at a solid block\'s face to place blocks')

    # Toggle first person and third person views
    if controls['toggle_view'] and not last_controls['toggle_view']:
        print('Toggled first person view')
        first_person = not first_person
        if first_person:
            # Disable default spinning and panning options
            scene.userspin = False
            scene.userzoom = False
            mouse_spinning = False
            dragging = False

            # Set camera position to the player
            move_camera(player)

            # Some vectors need to be reset and the rotates to the current camera angle
            camera_angle_y = pi / 2 - scene.up.diff_angle(scene.forward)
            scene.camera.up = vec(scene.up)
            scene.camera.orthogonal = rotate(vec(0, 0, 1), angle = -camera_angle_xz, axis = scene.up)
            scene.camera.up = rotate(scene.camera.up, angle = camera_angle_y, axis = scene.camera.orthogonal)

            # Hide player model so it doesn't interfere with the first person view
            player.hide_model()
        else:
            # Enable default spinning and panning options
            scene.userspin = True
            scene.userzoom = True

            # Show player model in third person view
            player.show_model()

    # Check controls dictionary for any inventory slot switches
    for i in range(1, 9):
        if controls['slot' + str(i)] and not last_controls['slot' + str(i)]:
            print('Selected slot ' + str(i))
            current_slot = i
            break
    
    # Print the player's inventory
    if controls['print_inventory'] and not last_controls['print_inventory']:
        print_inventory()

    # Toggle pausing/unpausing the game
    if controls['toggle_pause'] and not last_controls['toggle_pause']:
            print('The game is paused')
            print(nearest_block(player.hitbox.pos - vec(0, 0.5, 0), round))
            paused = True

    # Toggle professor mode
    if controls['professor_mode'] and not last_controls['professor_mode']:
        flying = not flying
        if flying:
            max_vel = 12 * Block.scale * vec(1, 1, 1)   # max_vel adjusted for flying
            print('Instructor mode enabled')
        else:
            max_vel = 5 * Block.scale * vec(1, 14, 1)   # max_vel reset to non-flying value
            print('Instructor mode disabled')

    # Check for the grutor_mode key
    if controls['grutor_mode'] and not last_controls['grutor_mode']:
        infinite_blocks = not infinite_blocks
        if infinite_blocks:
            print('Grutor mode enabled')
        else:
            print('Grutor mode disabled')

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

    # Rotate camera based on how far up/down and left/right the user's mouse is
    if mouse_spinning and mouse_onscreen:
        rotate_camera(percent_x * userspin_rate, percent_y * userspin_rate)
    elif dragging:
        rotate_camera(queued_rot_x, queued_rot_y)
        queued_rot_x = 0
        queued_rot_y = 0

    # +++ Start of GRAPHICAL UPDATES

    # Only update the camera position after all the physics updates and rotations are complete to avoid chopiness in the camera movement
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
    elif key == 'esc':
        controls['toggle_pause'] = pressed
    elif key in 'gG':
        controls['grutor_mode'] = pressed
    elif key in 'iI':
        controls['professor_mode'] = pressed
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
    ''' Runs when the mouse is moved on the canvas. According to the VPython documentation, it should run regardless 
        of whether the mouse button is being held down, but it doesn't.
    '''
    global previous_mouse_pos, queued_rot_x, queued_rot_y
    mouse_pos = vec(event.pageX, event.pageY, 0)
    delta_pos = previous_mouse_pos - mouse_pos
    queued_rot_x += 5 * delta_pos.x / scene.width
    queued_rot_y += 5 * delta_pos.y / scene.height
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

    # Get the t values for the near and far intersection points. These can be plugged into the parameterization of the ray to get the 3d coordinates of the intersection point
    t_near = max(t_x_near, t_y_near, t_z_near)
    t_far = min(t_x_far, t_y_far, t_z_far)

    # If the furthest intersection point along the ray is less than or equal to 0 or the nearest point is greater than 1, the collision didn't occur on the part of part of the ray being checked
    if isNaN(t_near) or isNaN(t_far) or t_far <= 0 or t_near > 1:
        return (False, 0, vec(0, 0, 0), vec(0, 0, 0))
    
    # Calculate the intersection point
    intersection = origin + ray_dir * t_near

    # Find the collision normal
    normal = vec(0, 0, 0)
    if t_x_near > t_y_near and t_x_near > t_z_near:
        normal = vec(-sign(ray_dir.x), 0, 0)
    elif t_y_near > t_x_near and t_y_near > t_z_near:
        normal = vec(0, -sign(ray_dir.y), 0)
    elif t_z_near > t_x_near and t_z_near > t_y_near:
        normal = vec(0, 0, -sign(ray_dir.z))
    
    # Return all the information about the collision in a tuple
    return (True, t_near, intersection, normal)

def clamp(value, upper, lower = None):
    ''' Clamps a value to within the range [-upper, upper] or, if lower is specified, [lower, upper]
        If the given value for lower is greater than the value for upper (or if only upper is given and it is negative),
        for any value given within [upper, lower], the closer of the two endpoints is returned.
        Although this function is valid python, there seems to be a bug in VPython where I always have to give a lower value
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
        The given truncFunc function is the operation used to convert the block position to integers.
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
    block_pos = nearest_block(pos, floor)
    block = block_at(block_pos)
    around = [block_at(nearest_block(vec(pos.x+1,pos.y,pos.z), floor)), 
                block_at(nearest_block(vec(pos.x-1,pos.y,pos.z), floor)),
                block_at(nearest_block(vec(pos.x,pos.y,pos.z+1), floor)), 
                block_at(nearest_block(vec(pos.x,pos.y,pos.z-1), floor)), 
                block_at(nearest_block(vec(pos.x,pos.y+1,pos.z), floor)), 
                block_at(nearest_block(vec(pos.x,pos.y-1,pos.z), floor))]  
    types = []
    if block.block_type == 'air':
        print('Cannot mine air')
    else: 
        print('Removed block of type', block.block_type)
        block.remove()
        add_inventory(block.block_type, 1)

        if block.block_type == 'cobblestone':
            for i in around:
                types += [i.block_type]
            if 'lava' in types and 'water' in types:
                print('Generated block of cobblestone')
                add_inventory(block.block_type, 1)
    
    for i in around:
        if i.block_type == 'water':
            Block(nearest_block(i.pos, floor), 'water')
        elif i.block_type == 'lava':
            Block(nearest_block(i.pos, floor), 'lava')

def add_inventory(block_type, num = 1):
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
        inventory[first_unoccupied] = (block_type, num)

def get_from_inventory(slot):
    '''Take a block from the given slot in the player's inventory'''
    if slot in inventory:
        block_type, number = inventory[slot]
        if not infinite_blocks:
            if number == 1:
                del inventory[slot]
            else:
                inventory[slot] = [block_type, number - 1]
        return block_type
    else:
        return 'air'

def print_inventory():
    '''Print the player's inventory'''
    if len(inventory) == 0:
        print('Your inventory is empty')
    else:
        print('Your inventory contains')
        for slot in inventory:
            block_type, number = inventory[slot]
            if infinite_blocks:
                print('Infinity x ' + block_type + ' in slot ' + str(slot))
            else:
                print(str(number) + ' x ' + block_type + ' in slot ' + str(slot))
    print('Slot ' + str(current_slot) + ' is selected')
        

def get_local_blocks(hitbox, dt):
    '''Return the list of blocks immediately surrounding the given box that it could possibly be colliding with'''
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
                if block.solid:
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
    '''Gets the collision manifold of hitboxA and hitboxB, assuming hitboxA is the one moving'''
    # If A's velocity is 0, it can't be about to collide with B in the next frame, since it isn't moving
    if hitboxA.vel.mag == 0:
        return (False, 0, vec(0, 0, 0), vec(0, 0, 0))

    # Create the expanded hitbox
    expanded_hitbox = hitboxB.copy()
    expanded_hitbox.size += hitboxA.size

    # Return the results of testing hitboxA's velocity ray against the expanded hitbox
    return ray_vs_hitbox(hitboxA.pos, hitboxA.vel * dt, expanded_hitbox)

def insertion_sort(L, lt):
    ''' Implementation of insertion sort given a less than comparator function. Using the key parameter in python's 
        built in sorted function doesn't seem to work in VPython. Solely used for sorting collision manifolds based
        on which collision occurs first. Since the actual number of blocks the player is colliding with at any point
        in time should be relatively small, insertion sort should be a good choice to quickly sort them.
    '''
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
    ''' Check for and resolve a collision between the given hitbox and the list of hitboxes. If collisions 
        are detected, hitboxA has part of its velocity in the direction of each collision canceled.
    '''
    faces = {'top': False}

    # Store the manifolds in a tuple with the hitbox that generated it
    manifold_wrappers = []
    for hitboxB in hitboxes:
        manifold = get_collision_manifold(hitboxA, hitboxB, dt)
        if manifold[0]:
            manifold_wrappers += [[manifold, hitboxB]]
    
    def comp_t_near(wrapperA, wrapperB):
        '''Helper function to compare the t_near values of two manifolds'''
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
        
        # Do the y rotation
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
        if block.solid:
            return block
    return block