GlowScript 3.0 VPython

class Block:
    scale = 1
    color_map = {"dirt": vec(127 / 255, 92 / 255, 7 / 255), "grass": color.green, "stone": color.grey}
    def __init__(self, pos, type):
        self.pos = vec(0, 0, 0)
        self.pos.x = floor(pos.x) * Block.scale
        self.pos.y = floor(pos.y) * Block.scale
        self.pos.z = floor(pos.z) * Block.scale
        self.type = type
        self.model = box(size = vec(Block.scale, Block.scale, Block.scale), pos = self.pos, color = Block.color_map[type])

for x in range(10):
    for z in range(10):
        Block(vec(x, 0, z), "grass")
        
for x in range(10):
    for z in range(10):
        Block(vec(x, -1, z), "dirt")