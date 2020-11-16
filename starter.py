GlowScript 3.0 VPython

scene.background = color.cyan
scene.width = 640                      # Make the 3D canvas larger
scene.height = 480
scene.bind('keydown', keydown_fun)     # Function for key presses
scene.bind('keyup', keyup_fun)     # Function for key presses

# +++ Start of object creation -- Create the blocks making up the world and the player

# Represents the blocks that makeup the world
class Block:
    scale = 1
    color_map = {"dirt": vec(127 / 255, 92 / 255, 7 / 255), "grass": color.green, "stone": 0.5 * vec(1, 1, 1)}
    blocks = {}
    def __init__(self, pos, block_type):
        # Align the block to a grid
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Block.scale + Block.scale / 2
        self.pos.y = floor(pos.y) * Block.scale + Block.scale / 2
        self.pos.z = floor(pos.z) * Block.scale + Block.scale / 2

        self.block_type = block_type
        if block_type != "air":
            # Create block model
            self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, color = Block.color_map[block_type])

        # Add the block to the map, or if its an air block, just remove the previous block
        key = (floor(pos.x), floor(pos.y), floor(pos.z))
        if key in Block.blocks:
            oldBlock = Block.blocks[key]
            oldBlock.visible = False
            del oldBlock
            del Block.blocks[key]
        if block_type != "air":
            Block.blocks[key] = self
    
    def __repr__(self):
        return self.block_type + "block"

player = box(size = vec(Block.scale, Block.scale * 2, Block.scale), pos = vec(0, Block.scale, 0), color = color.black)
player.vel = vec(0, 0, 0)     # this is its initial velocity
tpPlayer(vec(4.5, 5, 4.5))

for x in range(10):
    for y in range(5):
        if 5 - y == 1:
            block_type = "grass"
        elif 5 - y < 4:
            block_type = "dirt"
        else:
            block_type = "stone"
        for z in range(10):
            Block(vec(x, y, z), block_type)

# +++ Start of game loop section -- update the position of the player and other entities continuously

# Other constants
RATE = 30                # The number of times the while loop runs each second
dt = 1.0 / (1.0 * RATE)      # The time step each time through the while loop
scene.autoscale = False  # Avoids changing the view automatically
scene.forward = vec(0, -3, -2)  # Ask for a bird's-eye view of the scene...
friction_coef = 0.3
max_vel = 10 * Block.scale * vec(1, 2, 1)
accel = 3 * Block.scale
# gravity = -9.8 * Block.scale
gravity = 0
controls = {control: False for control in ["up", "down", "left", "right"]}

# This is the "event loop" or "animation loop"
# Each pass through the loop will animate one step in time, dt
#
while True:
    rate(RATE)                             # maximum number of times per second the while loop runs

    # +++ Start of PHYSICS UPDATES -- update all velocities and positions here, every time step

    if controls['up']:
        player.vel.z -= accel
    elif controls['down']:
        player.vel.z += accel
    else:
        player.vel.z *= friction_coef

    if controls['right']:
        player.vel.x += accel
    elif controls['left']:
        player.vel.x -= accel
    else:
        player.vel.x *= friction_coef
    
    player.vel.y += gravity * dt

    player.vel.x = clamp(player.vel.x, max_vel.x, -max_vel.x)
    player.vel.y = clamp(player.vel.y, max_vel.y, -max_vel.y)
    player.vel.z = clamp(player.vel.z, max_vel.z, -max_vel.z)
    player.pos = player.pos + player.vel * dt
    scene.center = player.pos

    standing_on = blockAt(nearestBlock() - vec(0, 1, 0))
    print(standing_on.block_type)

# +++ Start of EVENT_HANDLING section -- separate functions for keypresses and mouse clicks...

controls = {control: False for control in ["up", "down", "left", "right"]}

def keyup_fun(event):
    """This function is called each time a key is released."""
    key = event.key
    if key == 'up' or key in 'wWiI':
        controls['up'] = False
    elif key == 'left' or key in 'aAjJ':
        controls['left'] = False
    elif key == 'down' or key in 'sSkK':
        controls['down'] = False
    elif key == 'right' or key in "dDlL":
        controls['right'] = False

def keydown_fun(event):
    """This function is called each time a key is released."""
    key = event.key
    if key == 'up' or key in 'wWiI':
        controls['up'] = True
    elif key == 'left' or key in 'aAjJ':
        controls['left'] = True
    elif key == 'down' or key in 'sSkK':
        controls['down'] = True
    elif key == 'right' or key in "dDlL":
        controls['right'] = True

# def click_fun(event):
#     """This function is called each time the mouse is clicked."""
#     print("event is", event.event, event.which)

# +++ Start of utility functions

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

def tpPlayer(new_pos):
    """Teleport the player so that their lower half occupies the block with the given position"""
    player.pos.x = new_pos.x * Block.scale + Block.scale / 2
    player.pos.y = new_pos.y * Block.scale + Block.scale
    player.pos.z = new_pos.z * Block.scale + Block.scale / 2
    scene.center = player.pos

def nearestBlock():
    """Return the position of the nearest block to the player's lower half"""
    block_pos = vec(0, 0, 0)
    block_pos.x = round((player.pos.x - Block.scale / 2) / Block.scale)
    block_pos.y = round((player.pos.y - Block.scale) / Block.scale)
    block_pos.z = round((player.pos.z - Block.scale / 2) / Block.scale)
    return block_pos

def blockAt(pos):
        """Return the block in the map at the give position, or None"""
        key = (pos.x, pos.y, pos.z)
        if key in Block.blocks:
            return Block.blocks[key]
        else:
            return Block(pos, "air")