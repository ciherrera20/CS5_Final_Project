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
scene.wrapper.css("height", "100%")
scene.wrapper.css("min-height", "100%")
scene.wrapper.css("margin", "0")

# +++ Start of object creation -- Create the blocks making up the world and the player

# Represents the blocks that makeup the world
class Block:
    scale = 1
    color_map = {"dirt": vec(127 / 255, 92 / 255, 7 / 255), "leaf": vec(12 / 255, 179 / 255, 26 / 255), "stone": 0.5 * vec(1, 1, 1)}
    texture_map = {"dirt": texture = "https://lh3.googleusercontent.com/DpmqnZGty6vns7713z1kTAp3AwBqrZ5ZYz_jf-x04p3lFfQ3Q9j5KruZ-v81846PtM1A9HMHvxQkPpoOqViuvA=s400", 
                "stone": texture = "https://art.pixilart.com/df108d01cd72892.png",
                "lava": texture = "https://qph.fs.quoracdn.net/main-qimg-5691a6bcf4bd21df68e741ee1d9d4e0f",
                "water": texture = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcR-ErVpce1X6Y7Z4bYIK9PJfLL4hh_R9nvbFg&usqp=CAU",
                "wood": texture = "https://i.imgur.com/n6J1Jhz.jpg",
                "leaf": texture = "https://i.imgur.com/E4ycyzv.jpg",
                "grass_top": texture = {'file': "https://lh3.googleusercontent.com/0Xh1P9-7QIXw2j-TM5lGIo5Vvtkq3UIwynD04RgngIOU-4KOy06ZONL93Ht4YyCXEVXojj5Xn-H1m6NHC4rmW-g=s400", 'place':['sides']},
                "grass": texture = {'file':"https://lh3.googleusercontent.com/2ZdPa8KBDybnUudpc9yRmaCU3DYHH4SL7gxRTPwyk1oCn_1xCzntDLkb02MChMipFu-N3BzNAtXP2BCiwOl9WgM", 'place':['sides']}}
    blocks = {}
    def __init__(self, pos, block_type):
        # Align the block to a grid
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Block.scale + Block.scale / 2
        self.pos.y = floor(pos.y) * Block.scale + Block.scale / 2
        self.pos.z = floor(pos.z) * Block.scale + Block.scale / 2

        self.model = []

        self.block_type = block_type
        if block_type != "air":
            # Create block model
            if block_type in Block.texture_map:
                if block_type == "grass":
                    self.b1 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x,self.pos.y,self.pos.z -Block.scale*.5), axis = vec(1,0,0), texture = Block.texture_map["grass"], emissive = True)
                    self.b2 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x,self.pos.y,self.pos.z+ Block.scale -Block.scale*.5), axis = vec(1,0,0), texture = Block.texture_map["grass"], emissive = True)
                    self.b3 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x + Block.scale*(-.5),self.pos.y,self.pos.z + Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["grass"], emissive = True)
                    self.b4 = box(size = vec(Block.scale, Block.scale, .0001), pos = vec(self.pos.x+ Block.scale*(.5),self.pos.y,self.pos.z+Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["grass"], emissive = True)
                    self.bottom = box(size = vec(Block.scale, .001, Block.scale), pos = vec(self.pos.x,self.pos.y+ Block.scale*(-.5),self.pos.z+Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["dirt"], emissive = True)
                    self.grass_top = box(size = vec(Block.scale, .001, Block.scale), pos = vec(self.pos.x,self.pos.y+Block.scale*(.5),self.pos.z+Block.scale*(.5)-Block.scale*.5), axis = vec(0,0,1), texture = Block.texture_map["grass_top"], emissive = True)

                    self.model = [self.b1, self.b2, self.b3, self.b4, self.bottom, self.grass_top]

                    self.hitbox = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, opacity = 0, emissive = True)    
                    self.hitbox.visible = False
                else:
                    self.hitbox = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, texture = Block.texture_map[block_type], emissive = True, shininess = 0)
            elif block_type in Block.color_map:
                self.hitbox = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, color = Block.color_map[block_type], emissive = True, shininess = 0)
            else:
                self.hitbox = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, color = color.magenta, emissive = True, shininess = 0)

        # Add the block to the map, or if its an air block, just remove the previous block
        key = (floor(pos.x), floor(pos.y), floor(pos.z))
        if key in Block.blocks:
            oldBlock = Block.blocks[key]
            oldBlock.model.visible = False
            del oldBlock.hitbox
            del Block.blocks[key]
        if block_type != "air":
            Block.blocks[key] = self

    def __repr__(self):
        return self.block_type + "block"

    def remove(self):
        """Remove the block by replacing it with an air block"""
        self.hitbox.visible = False
        for side in self.model:
            side.visible = False
        Block(self.pos, "air")

class Player:
    scale = Block.scale / 2
    
    def __init__(self, pos):
        self.hitbox = box(size = vec(Block.scale, Block.scale * 2, Block.scale), pos = pos, visible = False)
        self.hitbox.vel = vec(0, 0, 0)
        self.hitbox.pos = vec(0, 0, 0)
        self.hitbox.pos.x = floor(pos.x) * Player.scale 
        self.hitbox.pos.y = floor(pos.y) * Player.scale - 0.5 * Player.scale
        self.hitbox.pos.z = floor(pos.z) * Player.scale
        self.hitbox.last_pos = vec(self.hitbox.pos)
        
        self.model = []
        self.right_arm_model = []
        self.left_arm_model = []
        self.right_leg_model = []
        self.left_leg_model = []

        #head
        self.face = box(size = vec(Player.scale, Player.scale, .001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, self.hitbox.pos.y, self.hitbox.pos.z), texture= "https://i.imgur.com/xGBPM4r.png", emissive = True)
        self.left_face = box(size = vec(Player.scale, Player.scale, .001), axis = vec(0, 0, 1), pos = vec(.5*Player.scale + self.hitbox.pos.x, self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/0MweIHN.png", emissive = True)
        self.right_face = box(size = vec(Player.scale, Player.scale, .001), axis = vec(0, 0, 1), pos = vec(-.5*Player.scale + self.hitbox.pos.x, self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/KBu05a4.png", emissive = True)
        self.forehead = box(size = vec(Player.scale, .001, Player.scale), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, .5*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/5zchhnC.png", emissive = True)
        self.bottom = box(size = vec(Player.scale, .001, Player.scale), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x,-.5*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/5zchhnC.png", emissive = True)
        self.back_head = box(size = vec(Player.scale, Player.scale, .001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x, self.hitbox.pos.y,-1*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/GM3mhsQ.jpg", emissive = True)
        
        #body
        self.front_body = box(size = vec(Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.25*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/VPh0BcH.png", emissive = True)
        self.back_body = box(size = vec(Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.75*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/g5SiySx.png", emissive = True)
        self.left_innerbody = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(.5*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/yUUrBWl.png", emissive = True)
        self.right_innerbody = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(-.5*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/yUUrBWl.png", emissive = True)
        
        #arms
        self.left_arm_front = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(.75*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.25*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/RGQfD6E.png", emissive = True)
        self.right_arm_front = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(-.75*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.25*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/RGQfD6E.png", emissive = True)
        self.left_arm_back = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(.75*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.75*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/joEQh9C.png", emissive = True)
        self.right_arm_back = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(-.75*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.75*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/joEQh9C.png", emissive = True)
        self.left_arm_side = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(1*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/hasbIck.png", emissive = True)
        self.right_arm_side = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(-1*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/YCj05N3.png", emissive = True)
        self.left_arm_inner = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(.5*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/hasbIck.png", emissive = True)
        self.right_arm_inner = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(-.5*Player.scale + self.hitbox.pos.x,-1.25*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/hasbIck.png", emissive = True)
        
        #legs
        self.left_leg_front = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(.25*Player.scale + self.hitbox.pos.x,-2.75*Player.scale + self.hitbox.pos.y,-.25*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/raDULwo.png", emissive = True)
        self.left_leg_back = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(.25*Player.scale + self.hitbox.pos.x,-2.75*Player.scale + self.hitbox.pos.y,-.75*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/RVFoPxR.png", emissive = True)
        self.left_leg_side = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(.5*Player.scale + self.hitbox.pos.x,-2.75*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/zwFnZgN.png", emissive = True)
        self.right_leg_front = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(-.25*Player.scale + self.hitbox.pos.x,-2.75*Player.scale + self.hitbox.pos.y,-.25*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/raDULwo.png", emissive = True)
        self.right_leg_back = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 0), pos = vec(-.25*Player.scale + self.hitbox.pos.x,-2.75*Player.scale + self.hitbox.pos.y,-.75*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/RVFoPxR.png", emissive = True)
        self.right_leg_side = box(size = vec(.5*Player.scale, 1.5*Player.scale, .001), axis = vec(0, 0, 1), pos = vec(-.5*Player.scale + self.hitbox.pos.x,-2.75*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/zwFnZgN.png", emissive = True)
        
        #shoulders
        self.shoulders = box(size = vec(2*Player.scale, .001, .5*Player.scale), axis = vec(0, 0, 0), pos = vec(self.hitbox.pos.x,-.5*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/4Sl9Hde.png", emissive = True)
        #hands
        self.left_hand = box(size = vec(.5*Player.scale, .001, .5*Player.scale), axis = vec(0, 0, 0), pos = vec(.75*Player.scale + self.hitbox.pos.x,-2*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/DtRDWLo.png", emissive = True)
        self.right_hand = box(size = vec(.5*Player.scale, .001, .5*Player.scale), axis = vec(0, 0, 0), pos = vec(-.75*Player.scale + self.hitbox.pos.x,-2*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/DtRDWLo.png", emissive = True)
        #feet
        self.left_foot = box(size = vec(.5*Player.scale, .001, .5*Player.scale), axis = vec(0, 0, 0), pos = vec(.25*Player.scale + self.hitbox.pos.x,-3.5*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/gNBY1QG.png", emissive = True)
        self.right_foot = box(size = vec(.5*Player.scale, .001, .5*Player.scale), axis = vec(0, 0, 0), pos = vec(-.25*Player.scale + self.hitbox.pos.x,-3.5*Player.scale + self.hitbox.pos.y,-.5*Player.scale + self.hitbox.pos.z), texture= "https://i.imgur.com/gNBY1QG.png", emissive = True)

        # self.face.visible = False
        # self.left_face.visible = False
        # self.right_face.visible = False
        # self.back_head.visible = False
        
        # Add all the boxes in the player model to an array
        #for the arms and legs specifically
        self.right_arm_model = [self.right_arm_front, self.right_arm_back, self.right_arm_side, self.right_arm_inner, self.right_hand]
        self.left_arm_model = [self.left_arm_front, self.left_arm_back, self.left_arm_side, self.left_arm_inner, self.left_hand]
        self.right_leg_model = [self.right_leg_front, self.right_leg_back, self.right_leg_side, self.right_foot]
        self.left_leg_model = [self.left_leg_front, self.left_leg_back, self.left_leg_side, self.left_foot]
        
        self.model = [self.face, self.left_face, self.right_face, self.forehead, self.bottom, self.back_head, self.front_body, self.back_body, self.left_innerbody, self.right_innerbody,
                    self.left_arm_front, self.right_arm_front, self.left_arm_back, self.right_arm_back, self.left_arm_side, self.right_arm_side, self.left_arm_inner, self.right_arm_inner,
                    self.left_leg_front, self.right_leg_front, self.left_leg_back, self.right_leg_back, self.left_leg_side, self.right_leg_side, self.shoulders, self.left_hand,
                    self.right_hand, self.left_foot, self.right_foot]
    
        for part in self.model:
            part.pos.y += Block.scale - Player.scale / 2
            part.pos.y += Block.scale
            part.pos.z += Player.scale / 2
        
        #self.model = []

    
    def sync_model(self):
        """Move all the boxes which make up the player model the same amount that the player's hitbox has moved"""
        displacement = self.hitbox.pos - self.hitbox.last_pos
        for box in self.model:
            box.pos += displacement
        self.hitbox.last_pos = vec(self.hitbox.pos)

# player = box(size = vec(Block.scale, Block.scale * 2, Block.scale), pos = vec(0, Block.scale, 0), color = color.black)
player = Player(vec(0, Block.scale, 0))
inventory = {}
# cube = box(pos = vec(Block.scale / 2, Block.scale / 2, Block.scale / 2), axis = vec(1, 0, 0), size = vec(1, 1, 1), opacity=0.5, color = color.yellow)
# player.vel = vec(0, 0, 0)     # this is its initial velocity
tp_player(vec(1, 1, 1))

#island
for x in range(7):
    for y in range(3):
        for z in range(3):
            if y == 0:
                Block(vec(x, -y, z), "grass")
            else:
                Block(vec(x, -y, z), "dirt")
for x in range(3):
    for y in range(3):
        for z in range(1, 4):
            if y == 0:
                Block(vec(x, -y, -z), "grass")
            else:
                Block(vec(x, -y, -z), "dirt")
#tree
for x in range(3):
    for y in range(3,6):
        for z in range(-3, 0):
                Block(vec(x, y, z), "leaf")
for y in range(1, 5):
    Block(vec(1, y, -2), "wood")

# +++ Start of game loop section -- update the position of the player and other entities continuously

# Other constants
RATE = 15                                   # The number of times the while loop runs each second
dt = 1.0 / (1.0 * RATE)                     # The time step each time through the while loop
player.on_ground = False                    # False initially. Keeps track of whether the player is touching the ground
scene.autoscale = False                     # Avoids changing the view automatically
scene.userspin = True                      # Disables the default rotation controls
scene.userpan = False                       # Disables the default panning controls
scene.userzoom = True
scene.forward = vec(1, 0, 0)                # Initialize forward as a unit vector in the x direction. Rotates with the camera
scene.mouse.ray = vec(1, 0, 0)              # Initialize mouse.ray as a unit vector in the x direction. Rotates with the camera
scene.camera.up = vec(0, 1, 0)              # Initialize camera.up as a unit vector in the y direction. Rotates with the camera, unlike scene.up
scene.camera.orthogonal = vec(0, 0, 1)      # Initialize camera.orthogonal as a unit vector in the z direction. Rotates with the camera
friction_coef = 0.3                         # Friction coefficient applied when the player is not walking
max_vel = 10 * Block.scale * vec(1, 2, 1)   # Maximum value for the x and z components of the player's velocity
accel = 1 * Block.scale                     # Acceleration used in the x and z directions while walking
gravity = -9.8 * Block.scale * 5            # Acceleration used in the y direction while falling
scene.fov = pi / 3                          # Set field of view
userspin_rate = 8 * pi / 180                # Set the rate at which the camera rotates when the mouse is dragged near the edge of the screen
userspin_threshold = 0.3                    # Set the threshold for the mouse position on the screen before the camera starts rotating
dragging = False                            # Keeps track of whether the player is dragging to rotate the camers
mouse_onscreen = False                      # Keeps track of whether the mouse is on the screen
mouse_spinning = True                       # Keeps track of whether rotating the camera using the mouse's position is enabled

cursor = box(size = vec(0.01, 0.01, 0.01), color = color.black, emissive = True)

# Dictionary mapping a control to whether it is active. Updated by keyboard events
controls = {control: False for control in ["up", "down", "left", "right", "camera_left", "camera_right", "mine", "jump"]}

# This is the "event loop" or "animation loop"
# Each pass through the loop will animate one step in time, dt
while True:
    rate(RATE)                             # maximum number of times per second the while loop runs

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
    if controls['jump'] and player.on_ground:
        player.hitbox.vel.y = 12 * Block.scale

    # Apply gravity
    player.hitbox.vel.y += gravity * dt

    # Apply max velocity clamping
    player.hitbox.vel.x = clamp(player.hitbox.vel.x, max_vel.x, -max_vel.x)
    player.hitbox.vel.y = clamp(player.hitbox.vel.y, max_vel.y, -max_vel.y)
    player.hitbox.vel.z = clamp(player.hitbox.vel.z, max_vel.z, -max_vel.z)

    # Rotate the velocity back in the camera's direction
    player.hitbox.vel = rotate(player.hitbox.vel, angle = -camera_angle_xz, axis = scene.up)

    # Update the player's position
    player.hitbox.pos = player.hitbox.pos + player.hitbox.vel * dt

    # Artificial vertical displacement to prevent collision issues with the player sinking into the floor
    # player.hitbox.pos.y -= 0.5 * gravity * dt * dt

    # Check for and resolve collisions between the player and all the blocks
    player.on_ground = False
    # for pos in Block.blocks:
    #     resolved_dir = resolve_collision(Block.blocks[pos].model, player.hitbox)
    #     if resolved_dir.y > 0:
    #         player.on_ground = True
    for block in get_local_blocks(player.hitbox):
        resolved_dir = resolve_collision(block.hitbox, player.hitbox)
        if resolved_dir.y > 0:
            player.on_ground = True

    # +++ Start of MINING

    # Try to mine the block the player is looking at
    if controls["mine"]:
        looking_at = block_through(scene.camera.pos, scene.forward, 3.5)
        mine(looking_at.pos)

    # +++ Start of CAMERA ROTATIONS

    # Control camera with arrow keys
    if controls["camera_left"]:
        rotate_camera(1 * pi / 180, 0)
        rot_player(1 * pi / 180)
    elif controls['camera_right']:
        rotate_camera(-1 * pi / 180, 0)
        rot_player(-1 * pi / 180)
    if controls["camera_down"]:
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
        rot_player(percent_x* userspin_rate)

    # Only update scene.camera.pos after all the physics updates and rotations are complete to avoid chopiness in the camera movement
    player.sync_model()
    move_camera(player)
    cursor.pos = scene.camera.pos + scene.forward.norm() * 0.5

# +++ Start of EVENT_HANDLING section -- separate functions for keypresses and mouse clicks...

def keyup_fun(event):
    """This function is called each time a key is released"""
    key = event.key
    update_controls(key, False)

def keydown_fun(event):
    """This function is called each time a key is pressed"""
    key = event.key
    update_controls(key, True)

def update_controls(key, pressed):
    """Updates the controls dictionary given a key string and whether it was just pressed or released"""
    if key in 'wWiI':
        controls['forward'] = pressed
    elif key in 'aAjJ':
        controls['left'] = pressed
    elif key in 'sSkK':
        controls['backward'] = pressed
    elif key in "dDlL":
        controls['right'] = pressed
    elif key == "up":
        controls['camera_up'] = pressed
    elif key == "left":
        controls['camera_left'] = pressed
    elif key == "down":
        controls['camera_down'] = pressed
    elif key == "right":
        controls['camera_right'] = pressed
    elif key in "qQ":
        controls["mine"] = pressed
    elif key == " ":
        controls["jump"] = pressed

previous_mouse_pos = vec(0, 0, 0)
def mousedown_fun(event):
    """Runs when the mouse button is pressed"""
    global previous_mouse_pos, dragging
    dragging = True
    previous_mouse_pos = vec(event.pageX, event.pageY, 0)

def mousemove_fun(event):
    """ Runs when the mouse is moved on the canvas. According to the documentaiton, it should run regardless 
        of whether the mouse is being held, but it doesn't
    """
    global previous_mouse_pos
    mouse_pos = vec(event.pageX, event.pageY, 0)
    delta_pos = previous_mouse_pos - mouse_pos
    angle_x = -delta_pos.x / scene.width
    angle_y = -delta_pos.y / scene.height
    rotate_camera(angle_x, angle_y)
    move_camera(player)
    rot_player(angle_x)
    previous_mouse_pos = mouse_pos

def mouseup_fun(event):
    """Runs when the mouse button is released"""
    global dragging
    dragging = False

def mouseenter_fun(event):
    """Runs when the mouse enters the canvas"""
    global mouse_onscreen
    mouse_onscreen = True

def mouseleave_fun(event):
    """Runs when the mouse leaves the canvas"""
    global mouse_onscreen
    mouse_onscreen = False

# +++ Start of utility functions

def sign(value):
    """Returns the sign of the given value as either 1 or -1"""
    return value / abs(value)

def clamp(value, upper, lower = None):
    """ Clamps a value to within the range [-upper, upper] or, if lower is specified, [lower, upper]
        If the given value for lower is greater than the value for upper (or if only upper is given and it is negative),
        for any value given within [upper, lower], the closer of the two endpoints is returned.
        Although this function is valid python, there seems to be a bug in VPython where I have to give a lower value
        or I get an error message.
    """
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
    """Teleport the player so that their lower half occupies the block with the given position"""
    player.hitbox.pos.x = new_pos.x * Block.scale + Block.scale / 2
    player.hitbox.pos.y = new_pos.y * Block.scale + Block.scale
    player.hitbox.pos.z = new_pos.z * Block.scale + Block.scale / 2
    player.sync_model

def nearest_block(pos, truncFunc = round):
    """ Return the position of the nearest block to the given position. 
        The given function for truncFunc is the operation used to return the block position as integers. 
        It defaults to the round function
    """
    block_pos = vec(0, 0, 0)
    block_pos.x = truncFunc((pos.x - Block.scale / 2) / Block.scale)
    block_pos.y = truncFunc((pos.y - Block.scale / 2) / Block.scale)
    block_pos.z = truncFunc((pos.z - Block.scale / 2) / Block.scale)
    return block_pos

def block_at(pos):
    """Return the block in the map at the give position. If no block is found, an air block is returned"""
    key = (pos.x, pos.y, pos.z)
    if key in Block.blocks:
        return Block.blocks[key]
    else:
        return Block(pos, "air")

def mine(pos):
    """Attempts to mine the block at the given position. If the block is not already air, it is replaced with air"""
    block_pos = nearest_block(pos, round)
    block = block_at(block_pos)
    if block.block_type == "air":
        print("Cannot mine air")
    else:
        block.remove()
        # Block(block_pos, "air")

    add_inventory(block.block_type)

def add_inventory(block):
    if inventory[block] == undefined:
        inventory[block] = 1
    else:
        inventory[block] += 1

def get_local_blocks(box):
    """Return the list of blocks immediately surrounding the given box that it could possible be colliding with"""
    blocks = []

    # Temporary fix for collision issues. Add the block the player is most on fir
    standing_on = block_at(nearest_block(vec(box.pos.x, box.pos.y - box.size.y / 2 - Block.scale / 2, box.pos.z), round))
    if standing_on.block_type != "air":
        blocks += [standing_on]
    for x in range(-1, ceil(box.size.x / Block.scale)):
        for y in range(-1, ceil(box.size.y / Block.scale)):
            for z in range(-1, ceil(box.size.z / Block.scale)):
                block = block_at(nearest_block(vec(box.pos.x - x, box.pos.y - y, box.pos.z - z), floor))
                if block.block_type != "air":
                    blocks += [block]
    return blocks

def get_collision_manifold(boxA, boxB):
    """ Gets the collision manifold, or the dimensions in which the two boxes intersect, between the given two boxes.
        Returns a tuple whose first value is a boolean indicating whether the two boxes intersect at all, and whose second
        through fourth values are the penetration depth in the x, y, and z directions. If the boxes don't intersect, 
        all three components are 0. The boxes must not be rotated.
    """
    (Ax1, Ay1, Az1) = (boxA.pos.x - boxA.size.x / 2, boxA.pos.y - boxA.size.y / 2, boxA.pos.z - boxA.size.z / 2)
    (Ax2, Ay2, Az2) = (boxA.pos.x + boxA.size.x / 2, boxA.pos.y + boxA.size.y / 2, boxA.pos.z + boxA.size.z / 2)
    (Bx1, By1, Bz1) = (boxB.pos.x - boxB.size.x / 2, boxB.pos.y - boxB.size.y / 2, boxB.pos.z - boxB.size.z / 2)
    (Bx2, By2, Bz2) = (boxB.pos.x + boxB.size.x / 2, boxB.pos.y + boxB.size.y / 2, boxB.pos.z + boxB.size.z / 2)
    if Ax2 > Bx1 and Ax1 < Bx2 and Ay2 > By1 and Ay1 < By2 and Az2 > Bz1 and Az1 < Bz2:
        (del_x, del_y, del_z) = (0, 0, 0)
        if boxA.pos.x < boxB.pos.x:
            del_x = Ax2 - Bx1
        else:
            del_x = Ax1 - Bx2

        if boxA.pos.y < boxB.pos.y:
            del_y = Ay2 - By1
        else:
            del_y = Ay1 - By2

        if boxA.pos.z < boxB.pos.z:
            del_z = Az2 - Bz1
        else:
            del_z = Az1 - Bz2
        # return (True, (del_x, del_y, del_z))
        return (True, del_x, del_y, del_z)
    else:
        # return (False, (0, 0, 0))
        return (False, 0, 0, 0)

def resolve_collision(boxA, boxB):
    """ Check for and resolve a collision between the two given boxes. If a collision is found, boxB is 
        displaced to resolve the collision and has its velocity in the direction of the collision set to 0.
        Returns a unit vector in the direction of the collision. The unit vector is always along one axis.
    """
    colliding, del_x, del_y, del_z = get_collision_manifold(boxA, boxB)

    # Only resolve the collision if the two boxes are actually colliding
    if colliding:
        # Find the magnitude of the minimum displacement necessary to resolve the collision
        min_del = min(abs(del_x), abs(del_y), abs(del_z))
        displacement = vec(del_x, del_y, del_z)
        vel_correction = vec(-boxB.vel.x, -boxB.vel.y, -boxB.vel.z)
        resolved_dir = vec(sign(del_x), sign(del_y), sign(del_z))

        # Figure out which direction to apply the displacement and velocity correction in
        if abs(del_x) > min_del:
            displacement.x = 0
            vel_correction.x = 0
            resolved_dir.x = 0
        if abs(del_y) > min_del:
            displacement.y = 0
            vel_correction.y = 0
            resolved_dir.y = 0
        if abs(del_z) > min_del:
            displacement.z = 0
            vel_correction.z = 0
            resolved_dir.z = 0

        # Apply displacement to boxB
        boxB.pos += displacement

        # Only correct velocity if it is in the direction of the collision
        if displacement.dot(vel_correction) > 0:
            boxB.vel += vel_correction

        return resolved_dir
    else:
        return vec(0, 0, 0)

def rotate_camera(angle_x, angle_y):
    """Rotates the camera and other relevant vectors given an x and y angle"""
    # return
    # Rotate around the scene.up vector for the x rotation
    scene.mouse.ray = rotate(scene.mouse.ray, angle = angle_x, axis = scene.up)
    scene.camera.up = rotate(scene.camera.up, angle = angle_x, axis = scene.up)
    scene.forward = rotate(scene.forward, angle = angle_x, axis = scene.up)

    # Find camera angle in the y direction and set upward and downward bounds
    camera_angle_y = scene.up.diff_angle(scene.forward)
    up_bound = 1 * pi / 180
    down_bound = (180 - 5) * pi / 180
    
    # If the camera is within the bounds, rotate around the vector orthogonal to the camera's up vector and the scene's forward vector for the y rotation
    if (camera_angle_y > up_bound and angle_y > 0) or (camera_angle_y < down_bound and angle_y < 0):
        # Set angle_y to the bound when it exceeds it
        if camera_angle_y - angle_y < up_bound:
            angle_y = camera_angle_y - up_bound
        elif camera_angle_y - angle_y > down_bound:
            angle_y = camera_angle_y - down_bound
        
        # Do the actual rotation
        scene.camera.orthogonal = scene.forward.cross(scene.camera.up)
        scene.mouse.ray = rotate(scene.mouse.ray, angle = angle_y, axis = scene.camera.orthogonal)
        scene.camera.up = rotate(scene.camera.up, angle = angle_y, axis = scene.camera.orthogonal)
        scene.forward = rotate(scene.forward, angle = angle_y, axis = scene.camera.orthogonal)
        
def rot_player(angle_x):
    for item in player.model:
        item.rotate(angle = angle_x, axis = vec(0,1,0), origin = vec(player.hitbox.pos.x, player.hitbox.pos.y, player.hitbox.pos.z))   

def move_camera(player):
    """Moves the camera to the player object"""
    scene.camera.pos = player.hitbox.pos + vec(0, Block.scale / 2 + Player.scale / 2, 0)

def block_through(origin, direction, max_distance):
    """ Uses a simple ray tracing algorithm to find the first block that intersects the ray from the given origin, 
        in the given direction, within the given range
    """
    ds = Block.scale / 10
    direction = direction.norm()
    for i in range(max_distance / ds):
        block = block_at(nearest_block(origin + direction * ds * i, round))
        if block.block_type != "air":
            return block
    return block