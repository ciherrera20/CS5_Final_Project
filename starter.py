GlowScript 3.0 VPython

scene.background = color.cyan
scene.width = 640                      # Make the 3D canvas larger
scene.height = 480
scene.resizable = False
scene.bind('keydown', keydown_fun)     # Function for key presses
scene.bind('keyup', keyup_fun)     # Function for key presses
scene.bind('mousedown', mousedown_fun)
scene.bind('mousemove', mousemove_fun)
scene.bind('mouseup', mouseup_fun)
scene.bind('mouseenter', mouseenter_fun)
scene.bind('mouseleave', mouseleave_fun)

# +++ Start of object creation -- Create the blocks making up the world and the player

# Represents the blocks that makeup the world
class Block:
    scale = 1
    color_map = {"dirt": vec(127 / 255, 92 / 255, 7 / 255), "leaf": vec(12 / 255, 179 / 255, 26 / 255), "stone": 0.5 * vec(1, 1, 1)}
    texture_map = {"dirt": texture = "https://lh3.googleusercontent.com/DpmqnZGty6vns7713z1kTAp3AwBqrZ5ZYz_jf-x04p3lFfQ3Q9j5KruZ-v81846PtM1A9HMHvxQkPpoOqViuvA=s400", 
                 "stone": texture = "https://art.pixilart.com/df108d01cd72892.png",
                 "lava": texture = "https://qph.fs.quoracdn.net/main-qimg-5691a6bcf4bd21df68e741ee1d9d4e0f",
                 "water": texture = "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcR-ErVpce1X6Y7Z4bYIK9PJfLL4hh_R9nvbFg&usqp=CAU",
                 "wood": texture = "https://lh3.googleusercontent.com/Sm5RI4dsQZxXHNQfpEBZZwbnuv_nUqNeSXMlpLSfdJC8mGb7REfYBLUNxiyZYTeXmOo-YkdWAGLBnuUj6-iHCA=s400",
                 "grass": texture = "https://lh3.googleusercontent.com/0Xh1P9-7QIXw2j-TM5lGIo5Vvtkq3UIwynD04RgngIOU-4KOy06ZONL93Ht4YyCXEVXojj5Xn-H1m6NHC4rmW-g=s400"}
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
            if block_type in Block.texture_map:
                self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, texture = Block.texture_map[block_type], emissive = True, shininess = 0)
            elif block_type in Block.color_map:
                self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, color = Block.color_map[block_type], emissive = True, shininess = 0)
            else:
                self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, color = color.magenta, emissive = True, shininess = 0)

        # Add the block to the map, or if its an air block, just remove the previous block
        key = (floor(pos.x), floor(pos.y), floor(pos.z))
        if key in Block.blocks:
            oldBlock = Block.blocks[key]
            oldBlock.model.visible = False
            del oldBlock.model
            del Block.blocks[key]
        if block_type != "air":
            Block.blocks[key] = self
    
    def __repr__(self):
        return self.block_type + "block"

player = box(size = vec(Block.scale, Block.scale * 2, Block.scale), pos = vec(0, Block.scale, 0), color = color.black)
# cube = box(pos = vec(Block.scale / 2, Block.scale / 2, Block.scale / 2), axis = vec(1, 0, 0), size = vec(1, 1, 1), opacity=0.5, color = color.yellow)
player.vel = vec(0, 0, 0)     # this is its initial velocity
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

Block(vec(1, 1, 0), "grass")

# +++ Start of game loop section -- update the position of the player and other entities continuously

# Other constants
RATE = 60                                   # The number of times the while loop runs each second
dt = 1.0 / (1.0 * RATE)                     # The time step each time through the while loop
player.visible = False                      # Set to false since the camera is inside the player
player.on_ground = False                    # False initially. Keeps track of whether the player is touching the ground
scene.autoscale = False                     # Avoids changing the view automatically
scene.userspin = False                      # Disables the default rotation controls
scene.userpan = False                       # Disables the default panning controls
scene.forward = vec(1, 0, 0)                # Initialize forward as a unit vector in the x direction. Rotates with the camera
scene.mouse.ray = vec(1, 0, 0)              # Initialize mouse.ray as a unit vector in the x direction. Rotates with the camera
scene.camera.up = vec(0, 1, 0)              # Initialize camera.up as a unit vector in the y direction. Rotates with the camera, unlike scene.up
scene.camera.orthogonal = vec(0, 0, 1)      # Initialize camera.orthogonal as a unit vector in the z direction. Rotates with the camera
friction_coef = 0.3                         # Friction coefficient applied when the player is not walking
max_vel = 10 * Block.scale * vec(1, 2, 1)   # Maximum value for the x and z components of the player's velocity
accel = 3 * Block.scale                     # Acceleration used in the x and z directions while walking
gravity = -9.8 * Block.scale * 5            # Acceleration used in the y direction while falling
scene.fov = pi / 3                          # Set field of view
userspin_rate = 8 * pi / 180                # Set the rate at which the camera rotates when the mouse is dragged near the edge of the screen
userspin_threshold = 0.3                    # Set the threshold for the mouse position on the screen before the camera starts rotating
dragging = False                            # Keeps track of whether the player is dragging to rotate the camers
mouse_onscreen = False                      # Keeps track of whether the mouse is on the screen
mouse_spinning = True                       # Keeps track of whether rotating the camera using the mouse's position is enabled

cursor = sphere(radius = 0.005, color = color.black, emissive = True)

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
    player.vel = rotate(player.vel, angle = camera_angle_xz, axis = vec(0, 1, 0))

    # Apply velocity updates in the x and z directions based on the current controls
    if controls['forward']:
        player.vel.x += accel
    elif controls['backward']:
        player.vel.x -= accel
    else:
        player.vel.x *= friction_coef

    if controls['right']:
        player.vel.z += accel
    elif controls['left']:
        player.vel.z -= accel
    else:
        player.vel.z *= friction_coef

    # Set velocity when the player jumps
    if controls['jump'] and player.on_ground:
        player.vel.y = 12 * Block.scale

    # Apply gravity
    player.vel.y += gravity * dt

    # Apply max velocity clamping
    player.vel.x = clamp(player.vel.x, max_vel.x, -max_vel.x)
    player.vel.y = clamp(player.vel.y, max_vel.y, -max_vel.y)
    player.vel.z = clamp(player.vel.z, max_vel.z, -max_vel.z)

    # Rotate the velocity back in the camera's direction
    player.vel = rotate(player.vel, angle = -camera_angle_xz, axis = vec(0, 1, 0))

    # Update the player's position
    player.pos = player.pos + player.vel * dt

    # Check for and resolve collisions between the player and all the blocks
    player.on_ground = False
    for pos in Block.blocks:
        resolved_dir = resolve_collision(Block.blocks[pos].model, player)
        if resolved_dir.y > 0:
            player.on_ground = True

    # +++ Start of MINING

    # Try to mine the block the player is looking at
    if controls["mine"]:
        looking_at = block_through(scene.camera.pos, scene.forward, 3)
        mine(looking_at.pos)

    # +++ Start of CAMERA ROTATIONS

    # Control camera with arrow keys
    if controls["camera_left"]:
        rotate_camera(1 * pi / 180, 0)
    elif controls['camera_right']:
        rotate_camera(-1 * pi / 180, 0)
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

    # Only update scene.camera.pos after all the physics updates and rotations are complete to avoid chopiness in the camera movement
    scene.camera.pos = player.pos + vec(0, Block.scale / 2, 0)
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
    global previous_mouse_pos, dragging
    dragging = True
    previous_mouse_pos = vec(event.pageX, event.pageY, 0)

def mousemove_fun(event):
    global previous_mouse_pos
    mouse_pos = vec(event.pageX, event.pageY, 0)
    delta_pos = previous_mouse_pos - mouse_pos
    angle_x = -delta_pos.x / scene.width
    angle_y = -delta_pos.y / scene.height
    rotate_camera(angle_x, angle_y)
    scene.camera.pos = player.pos + vec(0, Block.scale / 2, 0)
    previous_mouse_pos = mouse_pos

def mouseup_fun(event):
    global dragging
    dragging = False

def mouseenter_fun(event):
    global mouse_onscreen
    mouse_onscreen = True

def mouseleave_fun(event):
    global mouse_onscreen
    mouse_onscreen = False

# def click_fun(event):
#     """This function is called each time the mouse is clicked."""
#     print("event is", event.event, event.which)

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
    player.pos.x = new_pos.x * Block.scale + Block.scale / 2
    player.pos.y = new_pos.y * Block.scale + Block.scale
    player.pos.z = new_pos.z * Block.scale + Block.scale / 2

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
        print("Cannot mine")
    else:
        Block(block_pos, "air")

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
        (delx, dely, delz) = (0, 0, 0)
        if boxA.pos.x < boxB.pos.x:
            delx = Ax2 - Bx1
        else:
            delx = Ax1 - Bx2

        if boxA.pos.y < boxB.pos.y:
            dely = Ay2 - By1
        else:
            dely = Ay1 - By2

        if boxA.pos.z < boxB.pos.z:
            delz = Az2 - Bz1
        else:
            delz = Az1 - Bz2
        # return (True, (delx, dely, delz))
        return (True, delx, dely, delz)
    else:
        # return (False, (0, 0, 0))
        return (False, 0, 0, 0)

def resolve_collision(boxA, boxB):
    """ Check for and resolve a collision between the two given boxes. If a collision is found, boxB is 
        displaced to resolve the collision and has its velocity in the direction of the collision set to 0.
        Returns a unit vector in the direction of the collision. The unit vector is always along one axis.
    """
    colliding, delx, dely, delz = get_collision_manifold(boxA, boxB)

    # Only resolve the collision if the two boxes are actually colliding
    if colliding:
        # Find the magnitude of the minimum displacement necessary to resolve the collision
        minDel = min(abs(delx), abs(dely), abs(delz))
        displacement = vec(delx, dely, delz)
        velCorrection = vec(-boxB.vel.x, -boxB.vel.y, -boxB.vel.z)
        resolved_dir = vec(sign(delx), sign(dely), sign(delz))

        # Figure out which direction to apply the displacement and velocity correction in
        if abs(delx) > minDel:
            displacement.x = 0
            velCorrection.x = 0
            resolved_dir.x = 0
        if abs(dely) > minDel:
            displacement.y = 0
            velCorrection.y = 0
            resolved_dir.y = 0
        if abs(delz) > minDel:
            displacement.z = 0
            velCorrection.z = 0
            resolved_dir.z = 0

        # Apply displacement to boxB
        boxB.pos += displacement

        # Only correct velocity if it is in the direction of the collision
        if displacement.dot(velCorrection) > 0:
            boxB.vel += velCorrection

        return resolved_dir
    else:
        return vec(0, 0, 0)

def rotate_camera(angle_x, angle_y):
    """Rotates the camera and other relevant vectors given an x and y angle"""
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
