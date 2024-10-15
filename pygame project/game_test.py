import sys, pygame
import math, random
pygame.init()

size = width, height = 256, 224
screen = pygame.display.set_mode(size, pygame.SCALED)
black = (0, 0, 0)

#game variables
gameVars = {
    "inGame"    : True,
    "isPaused"  : False, #is the game not running (as in showing the pause menu)
    "isFrozen"  : False, #if frozen, halt every gameplay related things except rendering
}

control_names = ['left', 'right', 'up', 'down', 'jump', 'shoot', 'change (l)', 'change (r)', 'pause']

controls = {
    'left'      : pygame.K_LEFT,
    'right'     : pygame.K_RIGHT,
    'up'        : pygame.K_UP,
    'down'      : pygame.K_DOWN,
    'jump'      : pygame.K_z,
    'shoot'     : pygame.K_s,
    'change (l)': pygame.K_c,
    'change (r)': pygame.K_d,
    'pause'     : pygame.K_RETURN,
}

try:
    file = open("test/option_controls.txt", "r")
except FileNotFoundError:
    print("Control configuration file doesn't exist. Creating a new file...")

    file = open("test/option_controls.txt", "w")
    text = f"{controls['left']};{controls['right']};{controls['up']};{controls['down']};{controls['jump']};{controls['shoot']};{controls['change (l)']};{controls['change (r)']};{controls['pause']}"
    file.write(text)
    file.close()
else:
    line = file.read()
    temp = line.split(';')

    for k, v in enumerate(controls):
        controls[control_names[k]] = int(temp[k])
    file.close()

pygame.display.set_caption("Xyler Infiltration w10")
font = pygame.font.Font("pygame project/font/PressStart2P.ttf", 8)

# assets
bars = [
    pygame.image.load("pygame project/hud/bar_health.png"),
    pygame.image.load("pygame project/hud/bar_crystal_blast.png"),
    pygame.image.load("pygame project/hud/bar_shock_force.png"),
    pygame.image.load("pygame project/hud/bar_spiral_cyclone.png"),
    pygame.image.load("pygame project/hud/bar_burner_wave.png"),
    pygame.image.load("pygame project/hud/bar_leaf_guard.png"),
    pygame.image.load("pygame project/hud/bar_downpour_storm.png"),
    pygame.image.load("pygame project/hud/bar_empty.png"),
]

# constants
DIR_LEFT = -1
DIR_RIGHT = 1
DIR_UP = -2
DIR_DOWN = 2

BLOCK_SOLID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
BLOCK_SEMISOLID = [12, 13]
BLOCK_CLIMBABLE = [11, 12]

WEAPON_TRIPLE_SHOT = 0
WEAPON_CRYSTAL_BLAST = 1
WEAPON_SHOCK_FORCE = 2
WEAPON_SPIRAL_CYCLONE = 3
WEAPON_BURNER_WAVE = 4
WEAPON_LEAF_GUARD = 5
WEAPON_DOWNPOUR_STORM = 6

HEALTH_ENERGY_SMALL_VALUE = 3
HEALTH_ENERGY_LARGE_VALUE = 12
WEAPON_ENERGY_SMALL_VALUE = 3
WEAPON_ENERGY_LARGE_VALUE = 12

# functions
def lookForSection(x: int, y: int) -> int:
    for k, s in enumerate(currentLevel.sections):
        if x >= s.x and x <= s.x + s.width and y >= s.y and y <= s.y + s.height:
            return k
    
    return -1 #no sections are found

def math_clamp(num, min, max) -> float:
    return min if num < min else max if num > max else num

# classes
# used for boundaries in camera or npc behavior
class Section():
    def __init__(self, x: int, y: int, width: int, height: int, color: int, bgID: int) -> None:
        self.x          = x
        self.y          = y
        self.width      = width
        self.height     = height

        # background related. color is for the "sky color" of the level, and bgID is what's displayed above the "sky"
        self.color      = color
        self.bgID       = bgID

class Player():
    def __init__(self, x: int, y: int, section: int, level) -> None:
        self.gfx            = pygame.image.load("pygame project/test.png")
        self.rect           = self.gfx.get_rect()
        # Gameplay vars
        self.width          = self.rect.width
        self.height         = self.rect.height
        self.speedX         = 0
        self.speedY         = 0
        self.direction      = 1
        self.section        = section
        self.maxHealth      = 18
        self.health         = self.maxHealth
        self.weapon         = 0
        # Starting location
        self.rect.x         = level.sections[section].x + x
        self.rect.y         = level.sections[section].y + y
        # Player states
        self.jumpTimer      = 0
        self.hasJumped      = 0
        self.attackCooldown = 0
        self.isOnGround     = False
        self.isClimbing     = False
        self.nearLadder     = 0
        self.ladderX        = 0
        self.bulletsOut     = 0
        self.immuneFrames   = 0
        self.hpToRestore    = 0
        self.hasDied        = False
        self.deathTimer     = 0

    def harm(self, damage: int):
        self.health = self.health - damage

        if self.health <= 0:
            self.hasDied = True
        else:
            self.immuneFrames = 90
    
    def heal(self, healValue: int):
        self.hpToRestore = healValue 
    
    def handleControls(self):
        keypressed = pygame.key.get_pressed()
        if keypressed:
            if keypressed[controls['right']]:
                self.direction = DIR_RIGHT
            if keypressed[controls['left']]:
                self.direction = DIR_LEFT
            
            if not self.isClimbing:                    
                self.speedX = self.direction

                if keypressed[controls['jump']] and (not self.hasJumped) and self.isOnGround:
                    self.hasJumped = True
                
                if keypressed[controls['up']] and self.nearLadder > 0:
                    self.isClimbing = True
            else:
                if keypressed[controls['up']]:
                    self.speedY = -1
                if keypressed[controls['down']]:
                    self.speedY = 1

                if (not keypressed[controls['up']]) and (not keypressed[controls['down']]):
                    self.speedY = 0
                
                # dismount from ladder
                if keypressed[controls['jump']] and not (keypressed[controls['up']] or keypressed[controls['down']]):
                    self.isClimbing = False

            if (not keypressed[controls['right']]) and (not keypressed[controls['left']]):
                self.speedX = 0
            
            if keypressed[controls['shoot']] and self.attackCooldown == 0 and self.bulletsOut < 3:
                self.attackCooldown = 10
                self.bulletsOut += 1

                offset = 0
                if self.direction == 1:
                    offset = self.width
                
                sectionX = self.rect.x - currentLevel.sections[self.section].x
                sectionY = self.rect.y - currentLevel.sections[self.section].y

                npcClass = NPC(1, sectionX + offset, sectionY, self.section, self.direction, currentLevel)

                currentLevel.npcs.append(npcClass)
    
    def update(self):
        #self.health = (self.health + 1) % self.maxHealth + 1
        if not gameVars["isFrozen"]:
            if not self.hasDied:
                if not currentLevel.camera.isUpdating:
                    self.handleControls()
                    
                    if self.hasJumped and self.jumpTimer < 16:
                        self.speedY = -2.2

                        self.jumpTimer += 1
                        self.isOnGround = False
                    else:
                        if self.speedY < 3:
                            self.speedY += 0.4
                        else:
                            self.speedY = 3
                        self.isOnGround = False

                    if self.attackCooldown > 0:
                        self.attackCooldown -= 1

                    if self.isClimbing:
                        self.width = 16
                        self.rect.width = self.width

                        self.rect.x = math_clamp(self.rect.x, self.ladderX, self.ladderX)
                    else:
                        self.width = 32
                        self.rect.width = self.width
                else:
                    if currentLevel.camera.moveDir == DIR_LEFT or currentLevel.camera.moveDir == DIR_RIGHT:
                        self.direction = currentLevel.camera.moveDir
                        self.speedY = 0

                        if self.isOnGround:
                            self.speedX = self.direction

                for k, b in enumerate(currentLevel.blocks):
                    # ladder collision
                    if b.climbable:
                        if b.rect.colliderect(self.rect.x, self.rect.y, self.width / 2, self.height):
                            self.ladderX = b.rect.x
                            self.nearLadder = 2
                    
                    # horizontal collision
                    if b.solidSide:
                        if b.rect.colliderect(self.rect.x + self.speedX, self.rect.y, self.width, self.height):
                            self.speedX = 0

                    # vertical collision
                    if b.rect.colliderect(self.rect.x, self.rect.y + self.speedY, self.width, self.height):
                        # below the block
                        if self.speedY < 0:
                            if b.solidBottom:
                                self.speedY = b.rect.bottom - self.rect.top
                                self.speedY = 0
                        # above the block
                        elif self.speedY > 0:
                            if b.solidTop:
                                if not self.isClimbing:
                                    if b.solidSide:
                                        self.speedY = b.rect.top - self.rect.bottom
                                        # reset jump status
                                        self.hasJumped = False
                                        self.jumpTimer = 0
                                        self.isOnGround = True
                                    else:
                                        if (self.rect.bottom + self.speedX >= b.rect.top - 2) and (self.rect.centery + (self.height/3) < b.rect.top):
                                            self.speedY = b.rect.top - self.rect.bottom
                                            # reset jump status
                                            self.hasJumped = False
                                            self.jumpTimer = 0
                                            self.isOnGround = True
                                else:
                                    if b.solidSide:
                                        self.speedY = b.rect.top - self.rect.bottom

                                if b.climbable:
                                    if pygame.key.get_pressed()[controls['down']]:
                                        self.isClimbing = True
                                        self.speedY = 1
                        
                    #dismount from ladders
                    if self.isClimbing:
                        if b.climbable and b.solidTop:
                            # make sure no other ladders can affect the player from dismounting
                            if (self.rect.bottom < b.rect.top + 2) and (self.rect.left == b.rect.left):
                                self.isClimbing = False

                if self.immuneFrames > 0:
                    self.immuneFrames -= 1
                
                if self.bulletsOut < 0:
                    self.bulletsOut = 0

                self.rect.x += self.speedX
                self.rect.y += self.speedY

            #check which section the player is in
            for k, s in enumerate(currentLevel.sections):
                if self.rect.x >= s.x and self.rect.x <= s.x + s.width and self.rect.y >= s.y and self.rect.y <= s.y + s.height:
                    self.section = k
            
            if self.nearLadder > 0:
                self.nearLadder -= 1
            
            if lookForSection(self.rect.x, self.rect.y) == -1 and self.rect.y > s.y + s.height:
                self.harm(self.health)
        
        # flicker when the player gets damaged
        if self.immuneFrames % 4 == 0 and not self.hasDied:
            screen.blit(self.gfx, (self.rect.x - currentLevel.camera.x, self.rect.y - currentLevel.camera.y), (0, 0, self.width, self.height))
        
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - currentLevel.camera.x, self.rect.y - currentLevel.camera.y, self.width, self.height), 2)

class Block():
    def __init__(self, id: int, x: int, y: int, section: int, level) -> None:
        self.id                 = id
        self.gfx                = pygame.image.load(f"pygame project/block/block-{id}.png")
        self.rect               = self.gfx.get_rect()
        self.width              = self.rect.width
        self.height             = self.rect.height
        # Starting location
        self.rect.x             = level.sections[section].x + x
        self.rect.y             = level.sections[section].y + y
        # block behavior
        self.solidSide          = False
        self.solidBottom        = False
        self.solidTop           = False
        self.climbable          = False
        self.foreground         = False

        if self.id in BLOCK_CLIMBABLE:
            self.climbable      = True
        if self.id in BLOCK_SOLID:
            self.solidSide      = True
            self.solidBottom    = True
            self.solidTop       = True
            self.foreground     = True
        if self.id in BLOCK_SEMISOLID:
            self.solidTop       = True
    
    def update(self):
        screenX = self.rect.x - currentLevel.camera.x
        screenY = self.rect.y - currentLevel.camera.y
        
        if screenX > -16 and screenX < width + 16 and screenY > -16 and screenY < height + 16:
            screen.blit(self.gfx, (screenX, screenY))
        #pygame.draw.rect(screen, (0, 0, 255), self.rect, 2)

npc_cfg = {
    'width'                     : [8, 16, 8, 16, 8],
    'height'                    : [8, 16, 8, 16, 8],
    'gfxwidth'                  : [8, 18, 8, 16, 8],
    'gfxheight'                 : [8, 18, 8, 16, 8],
    'gfxoffsetX'                : [0, -1, 0, 0, 0],
    'gfxoffsetY'                : [0, -2, 0, 0, 0],
    'frames'                    : [2, 4, 1, 3, 3],
    'framestyle'                : [1, 1, 0, 0, 0],
    'framedelay'                : [0, 0, 0, 8, 8],
    'health'                    : [0, 1, 0, 0, 0],
    'nogravity'                 : [True, False, True, False, False],
    'noblockcollision'          : [True, False, True, False, False],
    'isWalker'                  : [False, False, False, False, False],
    'weakTo'                    : [[], [], [], [], []],
    'immuneTo'                  : [[], [], [], [], []],
    'respawnable'               : [False, True, False, False, False],
    'hittable'                  : [False, True, False, False, False],
    'dropsItems'                : [False, True, False, False, False],
}

class NPC():
    def __init__(self, id: int, x: int, y: int, section: int, direction: int, level) -> None:
        self.id             = id
        self.gfx            = pygame.image.load(f"pygame project/npc/npc-{id}.png")
        self.rect           = self.gfx.get_rect()
        self.rect.width     = npc_cfg["width"][id - 1]
        self.rect.height    = npc_cfg["height"][id - 1]
        self.gfxwidth       = npc_cfg["gfxwidth"][id - 1]
        self.gfxheight      = npc_cfg["gfxheight"][id - 1]
        # Starting location
        self.section        = section
        self.rect.x         = level.sections[section].x + x
        self.rect.y         = level.sections[section].y + y
        # NPC vars
        self.aiState        = 0
        self.aiTimer        = 0
        self.isValid        = True                      # if it's alive
        self.isActive       = True                      # if it's on-screen
        self.direction      = direction
        self.speedX         = 0
        self.speedY         = 0
        self.isOnGround     = False
        self.health         = npc_cfg["health"][id - 1] # if the npc relies on health, it won't die until it reaches 0.
        self.immuneFrames   = 0                         # invincibility frames (only when > 0)
        self.frame          = 0                         # frame in animation
        self.frameTimer     = 0
        self.imageState     = 0                         # mostly used to sync the weapon pickup to match player color

        #shorthands and shortcut vars
        self.width          = self.rect.width
        self.height         = self.rect.height

        self.startX         = self.rect.x
        self.startY         = self.rect.y
        self.startDir       = self.direction

        #behaviors
        self.nogravity          = npc_cfg["nogravity"][id - 1]
        self.noblockcollision   = npc_cfg["noblockcollision"][id - 1]
        self.isWalker           = npc_cfg["isWalker"][id - 1]
        self.weakTo             = npc_cfg["weakTo"][id - 1]
    
    def reinitialize(self):
        self.rect.x         = self.startX
        self.rect.y         = self.startY
        self.aiState        = 0
        self.aiTimer        = 0
        self.isValid        = True                      # if it's alive
        self.isActive       = True                      # if it's on-screen
        self.direction      = self.startDir
        self.speedX         = 0
        self.speedY         = 0
        self.isOnGround     = False
        self.health         = npc_cfg["health"][self.id - 1]    # if the npc relies on health, it won't die until it reaches 0.
        self.immuneFrames   = 0                                 # invincibility frames (only when > 0)
        self.frame          = 0                                 # frame in animation
        self.frameTimer     = 0
        self.imageState     = 0 
    
    def kill(self):
        self.isValid = False
        self.isActive = False

        if npc_cfg["dropsItems"][self.id - 1]:
            rng = random.randint(1, 100)

            if rng > 90:
                item = NPC(4, self.rect.x, self.rect.y, self.section, self.direction, currentLevel)
                item.speedY = -4

                currentLevel.npcs.append(item)
            elif rng > 70:
                item = NPC(5, self.rect.x, self.rect.y, self.section, self.direction, currentLevel)
                item.speedY = -4

                currentLevel.npcs.append(item)

        if not npc_cfg["respawnable"][self.id - 1]:
            currentLevel.npcs.remove(self)
    
    def harm(self, damage: int, invincibleFrames: int, damageType):
        multiplier = 1
        if damageType in npc_cfg["immuneTo"][self.id - 1]:
            multiplier = 0
        else:
            if npc_cfg["weakTo"][self.id - 1] != []:
                if damageType == npc_cfg["weakTo"][self.id - 1][0]:
                    multiplier = 4 # primary weakness
                elif damageType == npc_cfg["weakTo"][self.id - 1][1]:
                    multiplier = 2 # secondary weakness

        self.health = self.health - damage * multiplier

        if self.health <= 0:
            self.kill()
        else:
            self.immuneFrames = invincibleFrames
    
    def update(self):
        # the actual npc behavior
        if self.isValid:
            if self.isActive:
                dirOffset = 1

                if self.direction == DIR_RIGHT: dirOffset = 2

                # behavior codes (shared with multiple npcs)
                if npc_cfg["frames"][self.id - 1] > 1 and npc_cfg["framedelay"][self.id - 1] != 0:
                    self.frameTimer += 1

                    if self.frameTimer % npc_cfg["framedelay"][self.id - 1] == 0:
                        self.frame += 1
                    
                    if self.frame >= npc_cfg["frames"][self.id - 1]//dirOffset:
                        if npc_cfg["framestyle"][self.id - 1] == 1: #framestyle 1 (different left-right)
                            if self.direction == DIR_LEFT:
                                self.frame = 0
                            else:
                                self.frame = npc_cfg["frames"][self.id - 1]//dirOffset
                        elif npc_cfg["framestyle"][self.id - 1] == 0: #framestyle 0 (same left-right)
                            self.frame = 0
                
                if npc_cfg["hittable"][self.id - 1]:
                    valid = True

                    if (self.id == 2 and self.aiState == 0):
                        valid = False
                    
                    for k, v in enumerate(currentLevel.npcs):
                        if self.rect.colliderect(v.rect) and self.immuneFrames == 0:
                            if v.id == 1 and v.aiState == 0:
                                if valid:
                                    self.harm(1, 8, WEAPON_TRIPLE_SHOT)
                                else:
                                    v.direction = -v.direction
                                    v.speedY = -3/math.sqrt(2)
                                    v.speedX = 4 * v.direction
                                    v.aiState = 1
                            
                    
                if not self.nogravity:
                    if not self.isOnGround:
                        if self.speedY < 3:
                            self.speedY += 0.4
                        else:
                            self.speedY = 3
                
                if not self.noblockcollision:
                    for k, b in enumerate(currentLevel.blocks):
                        if b.solidSide:
                            if b.rect.colliderect(self.rect.x + self.speedX, self.rect.y, self.width, self.height):
                                self.speedX = 0

                                if self.isWalker:
                                    self.direction = -self.direction
                            
                        if b.solidTop:
                            if b.rect.colliderect(self.rect.x, self.rect.y + self.speedY, self.width, self.height):
                                if self.speedY < 0:
                                    if b.solidBottom:
                                        self.speedY = b.rect.bottom - self.rect.top
                                        self.speedY = 0
                                elif self.speedY > 0:
                                    self.speedY = b.rect.top - self.rect.bottom
                                    self.isOnGround = True
                    
                # individual npc codes
                if self.id == 1:
                    self.speedX = self.direction * 4

                    if self.rect.x + self.width < currentLevel.camera.x or self.rect.x > currentLevel.camera.x + currentLevel.camera.width:
                        currentLevel.player.bulletsOut -= 1
                        self.kill()
                    if currentLevel.camera.isUpdating:
                        currentLevel.player.bulletsOut -= 1
                        self.kill()
                    
                    if self.direction == DIR_LEFT:
                        self.frame = 0
                    else:
                        self.frame = 1
                if self.id == 2:
                    if self.aiState == 0:
                        if math.fabs(currentLevel.player.rect.centerx - self.rect.centerx) <= 80 and self.aiTimer == 0:
                            self.aiState = 1
                        
                        if currentLevel.player.rect.centerx - self.rect.centerx < 0:
                            self.direction = DIR_LEFT
                        else:
                            self.direction = DIR_RIGHT
                        
                        if self.direction == DIR_LEFT:
                            self.frame = 0
                        else:
                            self.frame = 2
                        
                        if self.aiTimer > 0:
                            self.aiTimer -= 1
                    else:
                        if self.aiTimer == 8:
                            sectionX = self.rect.x - currentLevel.sections[self.section].x
                            sectionY = self.rect.y - currentLevel.sections[self.section].y
                            
                            p1 = NPC(3, sectionX + self.width/2, sectionY + self.height/2, self.section, self.direction, currentLevel)
                            p1.speedX = 3/math.sqrt(2) * self.direction
                            p1.speedY = -3/math.sqrt(2)

                            p2 = NPC(3, sectionX + self.width/2, sectionY + self.height/2, self.section, self.direction, currentLevel)
                            p2.speedX = 3 * self.direction

                            p3 = NPC(3, sectionX + self.width/2, sectionY + self.height/2, self.section, self.direction, currentLevel)
                            p3.speedX = 3/math.sqrt(2) * self.direction
                            p3.speedY = 3/math.sqrt(2)

                            currentLevel.npcs.append(p1)
                            currentLevel.npcs.append(p2)
                            currentLevel.npcs.append(p3)

                        self.aiTimer += 1

                        if self.direction == DIR_LEFT:
                            self.frame = 1
                        else:
                            self.frame = 3

                        if self.aiTimer >= 96:
                            self.aiState = 0
                            self.aiTimer = 10
                    
                    if currentLevel.player.immuneFrames == 0:
                        if self.rect.colliderect(currentLevel.player.rect):
                            currentLevel.player.harm(1)
                if self.id == 3:
                    if self.rect.x + self.width < currentLevel.camera.x or self.rect.x > currentLevel.camera.x + currentLevel.camera.width:
                        currentLevel.player.bulletsOut -= 1
                        self.kill()
                    if currentLevel.camera.isUpdating:
                        currentLevel.player.bulletsOut -= 1
                        self.kill()
                    
                    if currentLevel.player.immuneFrames == 0:
                        if self.rect.colliderect(currentLevel.player.rect):
                            currentLevel.player.harm(2)
                if self.id == 4:
                    if self.rect.colliderect(currentLevel.player.rect):
                        currentLevel.player.heal(HEALTH_ENERGY_LARGE_VALUE)
                        self.kill()
                if self.id == 5:
                    if self.rect.colliderect(currentLevel.player.rect):
                        currentLevel.player.heal(HEALTH_ENERGY_SMALL_VALUE)
                        self.kill()
                
                self.rect.x += self.speedX
                self.rect.y += self.speedY
        
            if self.immuneFrames > 0:
                self.immuneFrames -= 1

            # render npcs
            screenX = self.rect.x - currentLevel.camera.x
            screenY = self.rect.y - currentLevel.camera.y

            # check which section the npc is in
            for k, s in enumerate(currentLevel.sections):
                if self.rect.x >= s.x and self.rect.x <= s.x + s.width:
                    self.section = k
            
            if screenX > -16 and screenX < width + 16 and screenY > -16 and screenY < height + 16:
                # same treatment as the player
                if self.immuneFrames % 4 == 0:
                    screen.blit(self.gfx, (screenX + npc_cfg["gfxoffsetX"][self.id - 1], screenY + npc_cfg["gfxoffsetY"][self.id - 1]), (self.gfxwidth * self.imageState, self.frame * self.gfxheight, self.gfxwidth, self.gfxheight))
                if self.health > 0 or self.health == npc_cfg["health"][self.id - 1]:
                    self.isActive = True

                # Debugging materials
                # text = font.render(f"{self.frame}", False, (255, 255, 255))
                # screen.blit(text, (screenX, screenY))
                # pygame.draw.rect(screen, (255, 0, 0), (screenX, screenY, self.width, self.height), 2)
            else:
                # reset some stuff
                self.isActive = False # might add exceptions because some enemies can work off-screen
                self.frame = 0
                self.frameTimer = 0
                self.aiTimer = 0
                self.aiState = 0

class Camera():
    def __init__(self, startX: int, startY: int, level) -> None:
        self.x          = startX
        self.y          = startY
        self.width      = width
        self.height     = height
        # movement vars (targetX, Y, and moveDir only used to nudge the player a bit)
        self.dx         = 0
        self.dy         = 0
        self.targetX    = 0
        self.targetY    = 0
        self.moveDir    = 0
        self.isUpdating = False
        self.section    = level.player.section
    
    def update(self):
        '''
        if not self.isUpdating:
            if player.rect.x + player.width > sections[self.section].x + sections[self.section].width: # right
                nextSection = lookForSection(player.rect.x + player.width, player.rect.y)

                if nextSection != -1:
                    self.dx = self.width
                    self.targetX = self.x + self.width
                    self.moveDir = DIR_RIGHT
            elif player.rect.x < sections[self.section].x: # left
                nextSection = lookForSection(player.rect.x, player.rect.y)
                
                if nextSection != -1:
                    self.dx = -self.width
                    self.targetX = self.x - self.width
                    self.moveDir = DIR_LEFT
            elif player.rect.y + player.height > sections[self.section].y + sections[self.section].height: # down
                nextSection = lookForSection(player.rect.x, player.rect.y + player.height)
                
                if nextSection != -1:
                    self.dy = self.height
                    self.targetY = self.y + self.height
                    self.moveDir = DIR_DOWN
            elif player.rect.y < sections[self.section].y: # up
                nextSection = lookForSection(player.rect.x, player.rect.y)

                if nextSection != -1:
                    self.dy = -self.height
                    self.targetY = self.y - self.height
                    self.moveDir = DIR_UP
            self.isUpdating = True
        print(f"{self.x}, {self.y}")

        if self.dx != 0:
            if self.dx > 0:
                self.dx -= 4
                self.x += 4
            else:
                self.dx += 4
                self.x -= 4
        
        if self.dy != 0:
            if self.dy > 0:
                self.dy -= 4
                self.y += 4
            else:
                self.dy += 4
                self.y -= 4
        
        if (self.dx == 0) and (self.dy == 0):
            self.isUpdating = False
        else:
            self.section = player.section
        '''
        if currentLevel.player.rect.x >= self.x + (self.width / 2) and currentLevel.player.speedX > 0:
            self.dx = currentLevel.player.speedX
        if currentLevel.player.rect.x <= self.x + (self.width / 2) and currentLevel.player.speedX < 0:
            self.dx = currentLevel.player.speedX
        
        self.x += self.dx
        self.y += self.dy
        self.x = math_clamp(self.x, currentLevel.sections[currentLevel.player.section].x, currentLevel.sections[currentLevel.player.section].x + currentLevel.sections[currentLevel.player.section].width - self.width)
        self.y = math_clamp(self.y, currentLevel.sections[currentLevel.player.section].y, currentLevel.sections[currentLevel.player.section].y + currentLevel.sections[currentLevel.player.section].height - self.height)
        self.dx = 0
        self.dy = 0

        if self.section != currentLevel.player.section:
            for k, v in enumerate(currentLevel.npcs):
                if v.section == currentLevel.player.section:
                    v.isValid = True
                    v.reinitialize()

        self.section = currentLevel.player.section

class Level():
    sections = []
    blocks = []
    npcs = []
    healTimer = 0

    def __init__(self, filename):
        self.levelName = filename # we may need this later
        file = open(f"pygame project/{filename}.lvl", "r")
        self.readmode = ""

        for line in file:
            if line == "[SECTIONS]\n":
                self.readmode = "S"
                continue
            elif line == "[PLAYER]\n":
                self.readmode = "P"
                continue
            elif line == "[BLOCKS]\n":
                self.readmode = "B"
                continue
            elif line == "[NPC]\n":
                self.readmode = "N"
                continue
            
            if line != "\n":
                if self.readmode == "S":
                    parameters = {
                        'x': 0,
                        'y': 0,
                        'width': 0,
                        'height': 0,
                        'colorR': 0,
                        'colorG': 0,
                        'colorB': 0,
                    }
                    temp = line.split(';')
                    parameters["x"] = int(temp[0])
                    parameters["y"] = int(temp[1])
                    parameters["width"] = int(temp[2])
                    parameters["height"] = int(temp[3])
                    parameters["colorR"] = int(temp[4])
                    parameters["colorG"] = int(temp[5])
                    parameters["colorB"] = int(temp[6])
                    
                    sectionClass = Section(parameters["x"], parameters["y"], parameters["width"], parameters["height"], (parameters["colorR"], parameters["colorG"], parameters["colorB"]), 0)
                    self.sections.append(sectionClass)
                elif self.readmode == "P":
                    parameters = {
                        'x': 0,
                        'y': 0,
                        'section': 0,
                    }
                    temp = line.split(';')
                    parameters["x"] = int(temp[0])
                    parameters["y"] = int(temp[1])
                    parameters["section"] = int(temp[2])
                    
                    self.player = Player(parameters["x"], parameters["y"], parameters["section"], self)
                    self.camera = Camera(self.player.rect.centerx - 128, self.player.rect.centery - 96, self)
                elif self.readmode == "B":
                    parameters = {
                        'id': 0,
                        'x': 0,
                        'y': 0,
                        'section': 0,
                    }

                    temp = line.split(';')
                    parameters["id"] = int(temp[0])
                    parameters["x"] = int(temp[1])
                    parameters["y"] = int(temp[2])
                    parameters["section"] = int(temp[3])

                    blockClass = Block(parameters["id"], parameters["x"], parameters["y"], parameters["section"], self)
                    self.blocks.append(blockClass)
                elif self.readmode == "N":
                    parameters = {
                        'id': 0,
                        'x': 0,
                        'y': 0,
                        'section': 0,
                        'direction': 0,
                    }

                    temp = line.split(';')
                    parameters["id"] = int(temp[0])
                    parameters["x"] = int(temp[1])
                    parameters["y"] = int(temp[2])
                    parameters["section"] = int(temp[3])
                    parameters["direction"] = int(temp[4])

                    npcClass = NPC(parameters["id"], parameters["x"], parameters["y"], parameters["section"], parameters["direction"], self)
                    self.npcs.append(npcClass)

        file.close()
    
    def runLevel(self):
        for k, s in enumerate(self.sections):
            if self.camera.section == k:
                screen.fill(s.color)

        for k, b in enumerate(self.blocks):
            if not b.foreground:
                b.update()
        
        self.player.update()
        if self.player.hpToRestore > 0:
            gameVars["isFrozen"] = True
            self.healTimer += 1

            # increase it one by one
            if self.healTimer % 4 == 0:
                if self.player.health < self.player.maxHealth:
                    self.player.health += 1
                    self.player.hpToRestore -= 1

                    if self.player.hpToRestore == 0:
                        self.player.hpToRestore = 0
                        gameVars["isFrozen"] = False
                else:
                    self.player.hpToRestore = 0
                    gameVars["isFrozen"] = False

        # foreground blocks
        for k, b in enumerate(self.blocks):
            if b.foreground:
                b.update()
        
        for k, v in enumerate(self.npcs):
            v.update()

# everything is now in this one level class
currentLevel = Level("test_level")
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    if gameVars["inGame"]:
        screen.fill((30, 86, 51))

        if not gameVars["isPaused"]:
            currentLevel.runLevel()
            
            # HUDs
            screen.blit(bars[7], (8, 78 - currentLevel.player.maxHealth * 2), (0, 0, 8, currentLevel.player.maxHealth * 2))

            for i in range(1, currentLevel.player.health + 1):
                x = 8
                y = 78 - 2 * i
                screen.blit(bars[0], (x, y))
            
            text = font.render(f"{currentLevel.player.health}", False, (255, 255, 255))
            screen.blit(text, (8, 88))
            
            currentLevel.camera.update()
        else:
            pass
    
    pygame.display.flip()
    clock.tick(60)