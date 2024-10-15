import sys, pygame
import math, random
pygame.init()

size = width, height = 256, 224
screen = pygame.display.set_mode(size, pygame.SCALED)
black = (0, 0, 0)

#game variables
gameVars = {
    "inGame"                : True,
    "isPaused"              : False, #is the game not running (as in showing the pause menu)
    "isFrozen"              : False, #if frozen, halt every gameplay related things except rendering
    "menuTransitionTimer"   : 0,
    "pauseMenuScreen"       : 0,
    "pauseMenuCol"          : 0,
    "pauseMenuRow"          : 0,
    "weaponChangeTimer"     : 0,
    "pauseMenuTimer"        : 0, #handling button delays
    "pauseMenuTakesChanges" : False,
    "pauseSavingTextTimer"  : 0,
    "currentLevel"          : None,
    "levelDestination"      : '',

    # already pressed keys
    "leftKeyPressed"        : False,
    "rightKeyPressed"       : False,
    "upKeyPressed"          : False,
    "downKeyPressed"        : False,
    "jumpKeyPressed"        : False,
    "pauseKeyPressed"       : False,
    "changeLKeyPressed"     : False,
    "changeRKeyPressed"     : False,
    "keyDelay"              : 0,
}

gameData = {
    "energyUpObtained"  : 0,
    "energyUp1_taken"   : False,
    "energyUp2_taken"   : False,
    "energyUp3_taken"   : False,
    "energyUp4_taken"   : False,
    "energyUp5_taken"   : False,
    "energyUp6_taken"   : False,
    "hasFlashDash"      : False,
    "hasWallCling"      : False,
    "hasPowerPlasma"    : False,
    "bossesDefeated"    : 0,
    "defeatedVasudha"   : True,
    "defeatedAnguille"  : True,
    "defeatedZephuros"  : True,
    "defeatedHonouou"   : True,
    "defeatedArbor"     : True,
    "defeatedKalypso"   : True,
}
#gameData["energyUpObtained"] = int(gameData["energyUp1_taken"]) + int(gameData["energyUp2_taken"]) + int(gameData["energyUp3_taken"]) + int(gameData["energyUp4_taken"]) + int(gameData["energyUp5_taken"]) + int(gameData["energyUp1_taken"])

controls = {
    "left"      : pygame.K_LEFT,
    "right"     : pygame.K_RIGHT,
    "up"        : pygame.K_UP,
    "down"      : pygame.K_DOWN,
    "jump"      : pygame.K_z,
    "shoot"     : pygame.K_s,
    "dash"      : pygame.K_a,
    "change (l)": pygame.K_c,
    "change (r)": pygame.K_d,
    "pause"     : pygame.K_RETURN,
}

new_controls = {
    "left"      : 0,
    "right"     : 0,
    "up"        : 0,
    "down"      : 0,
    "jump"      : 0,
    "shoot"     : 0,
    "dash"      : 0,
    "change (l)": 0,
    "change (r)": 0,
    "pause"     : 0,
}

control_names = ['left', 'right', 'up', 'down', 'jump', 'shoot', 'dash', 'change (l)', 'change (r)', 'pause']

settings = {
    "BGM_volume": 1.0,
    "SFX_volume": 1.0,
    "autosaves" : False,
}

setting_names = ['BGM_volume', 'SFX_volume', 'autosaves']

pygame.display.set_caption("Xyler Infiltration w14")
font = pygame.font.Font("font/PressStart2P.ttf", 8)

# assets
bars = [
    pygame.image.load("hud/bar_health.png"),
    pygame.image.load("hud/bar_crystal_blast.png"),
    pygame.image.load("hud/bar_shock_force.png"),
    pygame.image.load("hud/bar_spiral_cyclone.png"),
    pygame.image.load("hud/bar_burner_wave.png"),
    pygame.image.load("hud/bar_leaf_guard.png"),
    pygame.image.load("hud/bar_downpour_storm.png"),
    pygame.image.load("hud/hud_health_bar.png"),
    pygame.image.load("hud/hud_health_bar_hollow.png"),
    pygame.image.load("hud/hud_weapon_bar.png"),
    pygame.image.load("hud/hud_weapon_bar_hollow.png"),
    pygame.image.load("hud/hud_deco.png"),
]
chargeEffects = [
    pygame.image.load("player/chargeEffect1.png"),
    pygame.image.load("player/chargeEffect2.png"),
    pygame.image.load("player/chargeEffect3.png"),
    pygame.image.load("player/chargeEffect4.png"),
]
pauseMenuHuds = [
    pygame.image.load("hud/pause_screen_weapon.png"),
    pygame.image.load("hud/pause_screen_selection.png"),
    pygame.image.load("hud/pause_screen_genericMenu.png"),
]
icons = [
    pygame.image.load("hud/icon_weapons.png"),
    pygame.image.load("hud/icon_upgrades.png"),
]
playerAssets = [
    pygame.image.load("player/player-1.png"),
    pygame.image.load("player/player-2.png"),
    pygame.image.load("player/player-3.png"),
    pygame.image.load("player/player-4.png"),
    pygame.image.load("player/player-5.png"),
    pygame.image.load("player/player-6.png"),
    pygame.image.load("player/player-7.png"),
]

# constants
# directions
DIR_LEFT                = -1
DIR_RIGHT               = 1
DIR_UP                  = -2
DIR_DOWN                = 2

# block categories
BLOCK_SOLID             = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
BLOCK_SEMISOLID         = [12, 13]
BLOCK_CLIMBABLE         = [11, 12]
BLOCK_SPIKES            = [14]

# player animation states
ANIM_IDLE               = 0
ANIM_RUN                = 1
ANIM_JUMP               = 2
ANIM_FALL               = 3
ANIM_CLIMB              = 4
ANIM_DASH               = 5
ANIM_HURT               = 6
ANIM_SHOOT              = 7
ANIM_SHOOT_RUN          = 8
ANIM_SHOOT_MIDAIR       = 9
ANIM_SHOOT_CLIMB        = 10
ANIM_VICTORY            = 11

# player weapon types
WEAPON_TRIPLE_SHOT      = 0
WEAPON_CRYSTAL_BLAST    = 1
WEAPON_SHOCK_FORCE      = 2
WEAPON_SPIRAL_CYCLONE   = 3
WEAPON_BURNER_WAVE      = 4
WEAPON_LEAF_GUARD       = 5
WEAPON_DOWNPOUR_STORM   = 6

# health/weapon pickup values
HEALTH_ENERGY_SMALL_VALUE = 3
HEALTH_ENERGY_LARGE_VALUE = 12
WEAPON_ENERGY_SMALL_VALUE = 3
WEAPON_ENERGY_LARGE_VALUE = 12

# functions
# necessary before play
def loadSettings() -> None:
    try:
        file = open("settings_general.txt", "r")
    except FileNotFoundError:
        file = open("settings_general.txt", "w")

        text = f"{settings['BGM_volume']};{settings['SFX_volume']};{settings['autosaves']}"
        file.write(text)
        file.close()
    else:
        line = file.read()
        temp = line.split(';')
        for k, v in enumerate(settings):
            if type(settings[setting_names[k]]) == float:
                settings[setting_names[k]] = float(temp[k])
            else:
                if temp[k] == "False":
                    settings[setting_names[k]] = False #why the hell is bool(temp[k]) is True even though the string is False??
                else:
                    settings[setting_names[k]] = True

        file.close()

def loadControls() -> None:
    try:
        file = open("settings_controls.txt", "r")
    except FileNotFoundError:
        file = open("settings_controls.txt", "w")

        text = f"{controls['left']};{controls['right']};{controls['up']};{controls['down']};{controls['jump']};{controls['shoot']};{controls['dash']};{controls['change (l)']};{controls['change (r)']};{controls['pause']}"
        file.write(text)
        file.close()
    else:
        line = file.read()
        temp = line.split(';')

        for k, v in enumerate(controls):
            controls[control_names[k]] = int(temp[k])
        file.close()

def saveSettings() -> None:
    file = open("settings_general.txt", "w")

    text = f"{settings['BGM_volume']};{settings['SFX_volume']};{settings['autosaves']}"
    file.write(text)
    file.close()

def saveControls() -> None:
    gameVars["pauseSavingTextTimer"] = 120
    file = open("settings_controls.txt", "w")

    text = f"{new_controls['left']};{new_controls['right']};{new_controls['up']};{new_controls['down']};{new_controls['jump']};{new_controls['shoot']};{new_controls['dash']};{new_controls['change (l)']};{new_controls['change (r)']};{new_controls['pause']}"
    file.write(text)
    file.close()

# used to update energyUpObtained and bossesDefeated
def updateGameDataCounts():
    gameData["energyUpObtained"] = 0
    for i in range(1, 7):
        if gameData[f"energyUp{i}_taken"]:
            gameData["energyUpObtained"] += 1
    
    gameData["bossesDefeated"] = 0

    bossNames = ["Vasudha", "Anguille", "Zephuros", "Honouou", "Arbor", "Kalypso"]
    for i in range(len(bossNames)):
        if gameData[f"defeated{bossNames[i]}"]:
            gameData["bossesDefeated"] += 1
# necessary during play
def swapLevel(levelName):
    gameVars["currentLevel"] = None

    temp = Level(levelName)
    gameVars["currentLevel"] = temp
    gameVars["levelDestination"] = ''

def lookForSection(x: int, y: int) -> int:
    for k, s in enumerate(gameVars["currentLevel"].sections):
        if x >= s.x and x <= s.x + s.width and y >= s.y and y <= s.y + s.height:
            return k
    
    return -1 #no sections are found

def math_clamp(num, min, max) -> float:
    return min if num < min else max if num > max else num

def get_NPC(idFilter, sectionFilter) -> list:
    ret = []

    idLookup = None
    sectionLookup = None

    if type(idFilter) == list:
        idLookup = idFilter
        idFilter = None
    elif type(idFilter) == int:
        idLookup = [idFilter]
        idFilter = None
    else:
        print("get_NPC error: Invalid id parameters")
    
    if type(sectionFilter) == list:
        sectionLookup = sectionFilter
        sectionFilter = None
    elif type(sectionFilter) == int:
        sectionLookup = [sectionFilter]
        sectionFilter = None
    elif sectionFilter == None:
        sectionLookup = [gameVars["currentLevel"].player.section]
    else:
        print("get_NPC error: Invalid section parameters")
    
    for k, v in enumerate(gameVars["currentLevel"].npcs):
        if v.id != []:
            if v.id in idLookup and v.section in sectionLookup:
                ret.append(v)
        else:
            if v.section in sectionFilter:
                ret.append(v)
    
    return ret

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
        self.gfx            = playerAssets[0]
        self.rect           = self.gfx.get_rect()
        self.rect.width     = 21
        self.rect.height    = 32
        # Gameplay vars
        self.width          = self.rect.width
        self.height         = self.rect.height
        self.speedX         = 0
        self.speedY         = 0
        self.direction      = 1
        self.section        = section
        self.maxHealth      = 18 + 3 * gameData["energyUpObtained"]
        self.health         = self.maxHealth
        self.weapon         = WEAPON_TRIPLE_SHOT
        # Starting location
        self.rect.x         = level.sections[section].x + x
        self.rect.y         = level.sections[section].y + y
        # Player states
        self.frame          = 0
        self.frameTimer     = 0
        self.animState      = ANIM_IDLE
        self.animOffset     = 0
        self.jumpTimer      = 0
        self.hasJumped      = 0
        self.attackCooldown = 0
        self.isOnGround     = False
        self.isClimbing     = False
        self.nearLadder     = 0
        self.ladderX        = 0
        self.chargeTimer    = 0
        self.bulletsOut     = 0
        self.hurtTimer      = 0
        self.immuneFrames   = 0
        self.hpToRestore    = 0
        self.hasDied        = False
        self.deathTimer     = 0

        self.chargeFxFrame  = 0
        self.chargeFxTimer  = 0
        self.chargeFxState  = 0
        # additional ability stuff
        self.weaponOwned    = self.weaponSet()
        self.weaponOwnedIdx = 0
        self.weaponEnergies = [0, 36, 36, 36, 36, 36, 36]
        self.hasFlashDash   = gameData["hasFlashDash"]
        self.dashTimer      = 0
        self.dashCooldown   = 0
        self.hasDashed      = False
        self.hasWallCling   = gameData["hasWallCling"]
        self.hasPowerPlasma = gameData["hasPowerPlasma"]
        #weapon vars
        self.shockForceTimer    = 0

        self.startX         = self.rect.x
        self.startY         = self.rect.y
        self.startDirection = self.direction
        self.startSection   = self.section
    
    def weaponSet(self):
        ret = [WEAPON_TRIPLE_SHOT]

        if gameData["defeatedVasudha"]:
            ret.append(WEAPON_CRYSTAL_BLAST)
        if gameData["defeatedAnguille"]:
            ret.append(WEAPON_SHOCK_FORCE)
        if gameData["defeatedZephuros"]:
            ret.append(WEAPON_SPIRAL_CYCLONE)
        if gameData["defeatedHonouou"]:
            ret.append(WEAPON_BURNER_WAVE)
        if gameData["defeatedArbor"]:
            ret.append(WEAPON_LEAF_GUARD)
        if gameData["defeatedKalypso"]:
            ret.append(WEAPON_DOWNPOUR_STORM)
        
        return ret

    def reinitialize(self):
        self.gfx            = playerAssets[0]
        self.rect.x         = self.startX
        self.rect.y         = self.startY
        self.direction      = self.startDirection
        self.section        = self.section

        self.maxHealth      = 18 + 3 * gameData["energyUpObtained"]
        self.health         = self.maxHealth
        self.weapon         = WEAPON_TRIPLE_SHOT
        # Player states
        self.frame          = 0
        self.frameTimer     = 0
        self.animState      = ANIM_IDLE
        self.animOffset     = 0
        self.jumpTimer      = 0
        self.hasJumped      = 0
        self.attackCooldown = 0
        self.isOnGround     = False
        self.isClimbing     = False
        self.nearLadder     = 0
        self.ladderX        = 0
        self.chargeTimer    = 0
        self.bulletsOut     = 0
        self.hurtTimer      = 0
        self.immuneFrames   = 0
        self.hpToRestore    = 0
        self.hasDied        = False
        self.deathTimer     = 0

        self.chargeFxFrame  = 0
        self.chargeFxTimer  = 0
        self.chargeFxState  = 0
        # additional ability stuff
        self.weaponOwnedIdx = 0
        self.hasFlashDash   = gameData["hasFlashDash"]
        self.dashTimer      = 0
        self.dashCooldown   = 0
        self.hasDashed      = False
        self.hasWallCling   = gameData["hasWallCling"]
        self.hasPowerPlasma = gameData["hasPowerPlasma"]
        #weapon vars
        self.shockForceTimer    = 0

    def harm(self, damage: int):
        self.health = self.health - damage
        self.hurtTimer = 60
        self.animState = ANIM_HURT

        if self.health <= 0:
            self.hasDied = True
            self.health = 0
        else:
            self.immuneFrames = 90
    
    def heal(self, healValue: int):
        self.hpToRestore = healValue
    
    def changeWeapon(self, weaponID: int):
        self.weapon = weaponID
        self.gfx = playerAssets[self.weapon]

        for idx, wpn in enumerate(self.weaponOwned):
            #print(idx, wpn)
            if wpn == self.weapon:
                self.weaponOwnedIdx = idx
                break

        # reset every weapon states
        # TRIPLE SHOT
        self.bulletsOut = 0
        self.chargeTimer = 0
        self.chargeFxFrame = 0
        self.chargeFxTimer = 0
        self.chargeFxState = 0

        # SHOCK FORCE
        self.shockForceTimer = 0
    
    def shootProjectile(self, timerAt):
        self.chargeFxState = 0
        sectionX = self.rect.x - gameVars["currentLevel"].sections[self.section].x
        sectionY = self.rect.y - gameVars["currentLevel"].sections[self.section].y + 8

        offset = -16
        if self.direction == 1:
            offset = self.width + 9

        if self.animState == ANIM_SHOOT_CLIMB:
            sectionY = sectionY - 4

        if timerAt < 20:
            pass
        elif timerAt < 80:
            npcClass = NPC(1, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            npcClass.origin = self

            gameVars["currentLevel"].npcs.append(npcClass)

            self.bulletsOut += 1
        elif timerAt < 120:
            p1 = NPC(1, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            p1.speedY = -3/math.sqrt(2)
            p1.origin = self

            p2 = NPC(1, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            p2.origin = self

            p3 = NPC(1, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            p3.speedY = 3/math.sqrt(2)
            p3.origin = self

            gameVars["currentLevel"].npcs.append(p1)
            gameVars["currentLevel"].npcs.append(p2)
            gameVars["currentLevel"].npcs.append(p3)

            self.bulletsOut += 3
        elif timerAt < 160:
            npcClass = NPC(7, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            npcClass.origin = self

            gameVars["currentLevel"].npcs.append(npcClass)

            self.bulletsOut += 1
        else:
            p1 = NPC(7, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            p1.speedY = -3/math.sqrt(2)
            p1.origin = self

            p2 = NPC(7, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            p2.origin = self

            p3 = NPC(7, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
            p3.speedY = 3/math.sqrt(2)
            p3.origin = self

            gameVars["currentLevel"].npcs.append(p1)
            gameVars["currentLevel"].npcs.append(p2)
            gameVars["currentLevel"].npcs.append(p3)

            self.bulletsOut += 3
        self.chargeTimer = 0
    
    def handleControls(self):
        keypressed = pygame.key.get_pressed()

        if keypressed:
            if keypressed[controls['right']]:
                self.direction = DIR_RIGHT

                if self.isOnGround:
                    self.animState = ANIM_RUN
            if keypressed[controls['left']]:
                self.direction = DIR_LEFT

                if self.isOnGround:
                    self.animState = ANIM_RUN
            
            if not self.isClimbing:
                self.speedX = self.direction

                if keypressed[controls['jump']] and (not self.hasJumped) and self.isOnGround:
                    self.hasJumped = True
                
                if keypressed[controls['up']] and self.nearLadder > 0:
                    self.isClimbing = True
            else:
                self.animState = ANIM_CLIMB
                if self.chargeTimer == 0 and not keypressed[controls['shoot']]:
                    if keypressed[controls['up']]:
                        self.speedY = -1
                        
                        self.frameTimer += 1
                    if keypressed[controls['down']]:
                        self.speedY = 1

                        self.frameTimer -= 1
                else:
                    if keypressed[controls['up']] or keypressed[controls['down']]:
                        self.speedY = 0

                if (not keypressed[controls['up']]) and (not keypressed[controls['down']]):
                    self.speedY = 0
                
                # dismount from ladder
                if keypressed[controls['jump']] and not (keypressed[controls['up']] or keypressed[controls['down']]):
                    self.isClimbing = False
                    self.hasJumped = True
                    self.jumpTimer = 17

            if (not keypressed[controls['right']]) and (not keypressed[controls['left']]):
                self.speedX = 0
            
            if keypressed[controls['shoot']]:
                if self.animState == ANIM_IDLE:
                    self.animState = ANIM_SHOOT
                elif self.animState == ANIM_RUN:
                    self.animState = ANIM_SHOOT_RUN
                elif self.animState == ANIM_FALL or self.animState == ANIM_JUMP:
                    self.animState = ANIM_SHOOT_MIDAIR
                elif self.animState == ANIM_CLIMB:
                    self.animState = ANIM_SHOOT_CLIMB
                
                if self.weapon == WEAPON_TRIPLE_SHOT:
                    if self.attackCooldown == 0 and self.bulletsOut < 3 and self.chargeTimer < 20:
                        self.attackCooldown = 10
                        self.bulletsOut += 1

                        offset = -16
                        if self.direction == DIR_RIGHT:
                            offset = self.width + 9
                        
                        sectionX = self.rect.x - gameVars["currentLevel"].sections[self.section].x
                        sectionY = self.rect.y - gameVars["currentLevel"].sections[self.section].y + 8

                        if self.animState == ANIM_SHOOT_CLIMB:
                            sectionY = sectionY - 4

                        npcClass = NPC(1, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
                        npcClass.origin = self

                        gameVars["currentLevel"].npcs.append(npcClass)
                
                    self.chargeTimer += 1

                    if self.chargeTimer > 180:
                        self.chargeTimer = 180
                elif self.weapon == WEAPON_SHOCK_FORCE:
                    if self.shockForceTimer == 0 and self.weaponEnergies[self.weapon] > 0:
                        self.weaponEnergies[self.weapon] -= 6
                        self.shockForceTimer = 240
                elif self.weapon == WEAPON_BURNER_WAVE:
                    if self.attackCooldown == 0 and self.weaponEnergies[self.weapon] > 0:
                        self.weaponEnergies[self.weapon] -= 6
                        self.attackCooldown = 10
                    
                        offset = -16
                        if self.direction == DIR_RIGHT:
                            offset = self.width + 9
                        
                        sectionX = self.rect.x - gameVars["currentLevel"].sections[self.section].x
                        sectionY = self.rect.y - gameVars["currentLevel"].sections[self.section].y + 8

                        if self.animState == ANIM_SHOOT_CLIMB:
                            sectionY = sectionY - 4
                        
                        npcClass = NPC(10, sectionX + offset, sectionY, self.section, self.direction, gameVars["currentLevel"])
                        npcClass.origin = self

                        gameVars["currentLevel"].npcs.append(npcClass)
                    
            
            if keypressed[controls['dash']] and self.dashCooldown == 0 and not self.hasDashed:
                if not self.isClimbing:
                    self.dashTimer = 30
                    self.animState = ANIM_DASH
            
            if keypressed[controls['change (l)']] and not gameVars["changeLKeyPressed"]:
                self.weaponOwnedIdx -= 1
                gameVars["changeLKeyPressed"] = True

                if self.weaponOwnedIdx < 0:
                    self.weaponOwnedIdx = len(self.weaponOwned) - 1

                self.changeWeapon(self.weaponOwned[self.weaponOwnedIdx])
                gameVars["weaponChangeTimer"] = 60
            
            if keypressed[controls['change (r)']] and not gameVars["changeRKeyPressed"]:
                self.weaponOwnedIdx += 1
                gameVars["changeRKeyPressed"] = True

                if self.weaponOwnedIdx > len(self.weaponOwned) - 1:
                    self.weaponOwnedIdx = 0
                
                self.changeWeapon(self.weaponOwned[self.weaponOwnedIdx])
                gameVars["weaponChangeTimer"] = 60
            
            if keypressed[controls['pause']] and gameVars["menuTransitionTimer"] == 0 and not gameVars["pauseKeyPressed"]:
                gameVars["isPaused"] = True
                gameVars["pauseKeyPressed"] = True
                gameVars['menuTransitionTimer'] = 16
    
    def handleAnimation(self):
        if self.direction == DIR_RIGHT:
            self.animOffset = 1
        else:
            self.animOffset = 0
        
        if self.animState == ANIM_IDLE:
            self.frameTimer = 0
            self.frame = 0
        elif self.animState == ANIM_SHOOT:
            self.frame = 1

            if self.bulletsOut != 0:
                self.frameTimer = 8
            
            if self.frameTimer > 0:
                self.frameTimer -= 1
            else:
                self.animState = ANIM_IDLE
        elif self.animState == ANIM_RUN:
            if self.frame < 2 or self.frame > 5:
                self.frame = 2

            self.frameTimer += 1

            if self.frameTimer % 8 == 0:
                self.frame += 1
            
            if self.frame > 5:
                self.frame -= 3
            
            if self.speedX == 0:
                self.animState = ANIM_IDLE
            
            if self.speedY > 1 and not self.isOnGround:
                self.animState = ANIM_FALL
        elif self.animState == ANIM_JUMP:
            self.frameTimer = 0
            self.frame = 10

            if self.speedY > 0:
                self.animState = ANIM_FALL
        elif self.animState == ANIM_FALL:
            self.frameTimer = 0
            self.frame = 11

            if self.isOnGround:
                self.animState = ANIM_IDLE
        elif self.animState == ANIM_CLIMB:
            if self.frame < 13 or self.frame > 16:
                self.frame = 13
            
            if self.frameTimer % 8 == 0:
                if self.frameTimer > 0:
                    self.frame += 1
                elif self.frameTimer < 0:
                    self.frame -= 1
                
                self.frameTimer = 0
            
            if self.frame > 16:
                self.frame -= 3
            
            if self.frame < 13:
                self.frame += 3
            
            if not self.isClimbing:
                if self.isOnGround:
                    self.animState = ANIM_IDLE
                else:
                    self.animState = ANIM_FALL
        elif self.animState == ANIM_DASH:
            self.hasDashed = True
            if self.frame < 18 or self.frame > 19:
                self.frame = 18
            
            if self.dashTimer <= 8 and self.dashTimer > 0:
                self.frame = 19
            elif self.dashTimer <= 0:
                self.dashCooldown = 20
                if self.isOnGround:
                    self.animState = ANIM_IDLE
                else:
                    self.animState = ANIM_FALL
        elif self.animState == ANIM_HURT:
            if self.frame < 20 or self.frame > 21:
                self.frame = 20
            
            self.frameTimer += 1

            if self.frameTimer > 8:
                self.frame = 21
            
            if self.hurtTimer == 0:
                self.animState = ANIM_IDLE
        elif self.animState == ANIM_SHOOT_RUN:
            if self.frame < 6 or self.frame > 9:
                self.frame = 6

            self.frameTimer += 1

            if self.frameTimer % 8 == 0:
                self.frame += 1
            
            if self.frame > 9:
                self.frame -= 3
            
            if self.speedX == 0:
                self.animState = ANIM_SHOOT
        elif self.animState == ANIM_SHOOT_MIDAIR:
            self.frame = 12
            
            if self.bulletsOut != 0:
                self.frameTimer = 16
            
            if self.frameTimer > 0:
                self.frameTimer -= 1
            else:
                if self.speedY > 0:
                    self.animState = ANIM_FALL
                elif self.speedY < 0:
                    self.animState = ANIM_JUMP
            
            if self.isOnGround:
                self.animState = ANIM_SHOOT
        elif self.animState == ANIM_SHOOT_CLIMB:
            self.frame = 17

            if self.bulletsOut != 0:
                self.frameTimer = 8
            
            if self.frameTimer > 0:
                self.frameTimer -= 1
            else:
                self.animState = ANIM_CLIMB
            
            if not self.isClimbing:
                if self.isOnGround:
                    self.animState = ANIM_SHOOT
                else:
                    self.animState = ANIM_SHOOT_MIDAIR
    
    def update(self):
        #self.health = (self.health + 1) % self.maxHealth + 1
        if not gameVars["isFrozen"] and gameVars["menuTransitionTimer"] == 0:
            if not self.hasDied:
                if not gameVars["currentLevel"].camera.isUpdating:                    
                    if self.hurtTimer == 0:
                        self.handleControls()
                    else:
                        if self.hurtTimer % 2 == 0:
                            if self.isOnGround:
                                self.rect.x = self.rect.x - self.direction
                            else:
                                self.speedX = 0
                                self.speedY = 0

                        self.hurtTimer -= 1
                    
                    if self.dashTimer > 0:
                        self.speedY = 0
                        self.speedX = 2 * self.direction

                        self.dashTimer -= 1
                    
                    if self.hasJumped and self.jumpTimer < 16:
                        self.speedY = -2.2

                        self.jumpTimer += 1
                        self.isOnGround = False
                        self.animState = ANIM_JUMP
                    else:
                        if self.speedY < 3:
                            self.speedY += 0.4
                        else:
                            self.speedY = 3
                        self.isOnGround = False
                    
                    if self.dashCooldown > 0:
                        self.dashCooldown -= 1

                    if self.attackCooldown > 0:
                        self.attackCooldown -= 1
                    
                    if self.chargeTimer != 0:
                        self.chargeFxTimer += 1

                        if self.chargeFxTimer % 4 == 0:
                            self.chargeFxFrame += 1
                        
                        if self.chargeFxFrame > 2:
                            self.chargeFxFrame = 0
                        
                        if self.chargeTimer > 20:
                            if self.chargeTimer < 80:
                                self.chargeFxState = 1
                            elif self.chargeTimer < 120:
                                self.chargeFxState = 2
                            elif self.chargeTimer < 160:
                                self.chargeFxState = 3
                            else:
                                self.chargeFxState = 4

                    if self.isClimbing:
                        self.width = 16
                        self.rect.width = self.width

                        self.rect.x = math_clamp(self.rect.x, self.ladderX, self.ladderX)
                    else:
                        self.width = 21
                        self.rect.width = self.width
                else:
                    if gameVars["currentLevel"].camera.moveDir == DIR_LEFT or gameVars["currentLevel"].camera.moveDir == DIR_RIGHT:
                        self.direction = gameVars["currentLevel"].camera.moveDir
                        self.speedY = 0

                        if self.isOnGround:
                            self.speedX = self.direction

                for k, b in enumerate(gameVars["currentLevel"].blocks):
                    if b.isSpike:
                        if b.innerHitbox.colliderect(self.rect.x, self.rect.y, self.width, self.height):
                            if self.immuneFrames == 0:
                                self.harm(self.health)

                    # ladder collision
                    if b.climbable:
                        if b.rect.colliderect(self.rect.x, self.rect.y, self.width / 2, self.height):
                            self.ladderX = b.rect.x
                            self.nearLadder = 2
                    
                    # horizontal collision
                    if b.solidSide:
                        if b.rect.colliderect(self.rect.x + self.speedX, self.rect.y, self.width, self.height):
                            self.speedX = 0

                            if self.animState == ANIM_RUN:
                                self.animState = ANIM_IDLE
                            elif self.animState == ANIM_SHOOT_RUN:
                                self.animState = ANIM_SHOOT

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
                                        self.hasDashed = False
                                    else:
                                        if (self.rect.bottom + self.speedX >= b.rect.top - 2) and (self.rect.centery + (self.height/3) < b.rect.top):
                                            self.speedY = b.rect.top - self.rect.bottom
                                            # reset jump status
                                            self.hasJumped = False
                                            self.jumpTimer = 0
                                            self.isOnGround = True
                                            self.hasDashed = False
                                else:
                                    if b.solidSide and self.rect.bottom + self.speedX >= b.rect.top:
                                        self.speedY = b.rect.top - self.rect.bottom

                                if b.climbable:
                                    if pygame.key.get_pressed()[controls["down"]]:
                                        if not self.isClimbing:
                                            self.rect.y = b.rect.top - 16
                                        self.isClimbing = True
                        
                    #dismount from ladders
                    if self.isClimbing:
                        if b.climbable and b.solidTop:
                            # make sure no other ladders can affect the player from dismounting
                            if (self.rect.bottom < b.rect.top + 2) and (self.rect.left == b.rect.left):
                                self.isClimbing = False
                
                if self.hurtTimer > 0:
                    self.animState == ANIM_HURT

                self.handleAnimation()

                if self.immuneFrames > 0:
                    self.immuneFrames -= 1
                
                if self.bulletsOut < 0:
                    self.bulletsOut = 0

                self.rect.x += self.speedX
                self.rect.y += self.speedY

                if self.nearLadder > 0:
                    self.nearLadder -= 1
                
                #check which section the player is in
                for k, s in enumerate(gameVars["currentLevel"].sections):
                    if not gameVars["currentLevel"].camera.isUpdating:
                        if self.rect.x >= s.x and self.rect.x <= s.x + s.width and self.rect.y >= s.y and self.rect.y <= s.y + s.height:
                            self.section = k
                
                    if lookForSection(self.rect.x, self.rect.y) == -1 and self.rect.y > s.y + s.height and not self.hasDied:
                        self.harm(self.health)
            else:
                self.deathTimer += 1

                if self.deathTimer > 60:
                    gameVars["currentLevel"].restartLevel()
        
        # flicker when the player gets damaged
        if not self.hasDied:
            # character draw
            if self.immuneFrames % 4 == 0:
                offsetX = 14
                offsetY = 8

                if self.animState == ANIM_CLIMB or self.animState == ANIM_SHOOT_CLIMB:
                    offsetX = offsetX + 3
                
                screen.blit(self.gfx, (self.rect.x - gameVars["currentLevel"].camera.x - offsetX, self.rect.y - gameVars["currentLevel"].camera.y - offsetY), (49 * self.animOffset, 40 * self.frame, 49, 40))
            
            # charge effect draw
            if self.chargeTimer != 0 and self.chargeFxState > 0:
                offsetX = 6

                screen.blit(chargeEffects[self.chargeFxState - 1], (self.rect.x - gameVars["currentLevel"].camera.x - offsetX, self.rect.y - gameVars["currentLevel"].camera.y), (0, 32 * self.chargeFxFrame, 32, 32))

        # debug
        # print(self.rect.x, self.rect.y)
        # pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - gameVars["currentLevel"].camera.x, self.rect.y - gameVars["currentLevel"].camera.y, self.width, self.height), 2)

class Block():
    def __init__(self, id: int, x: int, y: int, section: int, level) -> None:
        self.id                 = id
        self.gfx                = pygame.image.load(f"block/block-{id}.png")
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
        self.isSpike            = False

        if self.id in BLOCK_CLIMBABLE:
            self.climbable      = True
        if self.id in BLOCK_SOLID:
            self.solidSide      = True
            self.solidBottom    = True
            self.solidTop       = True
            self.foreground     = True
        if self.id in BLOCK_SEMISOLID:
            self.solidTop       = True
        if self.id in BLOCK_SPIKES:
            self.isSpike        = True
            self.foreground     = True

            self.innerHitbox    = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 12, 12)
    
    def update(self):
        screenX = self.rect.x - gameVars["currentLevel"].camera.x
        screenY = self.rect.y - gameVars["currentLevel"].camera.y
        
        if screenX > -16 and screenX < width + 16 and screenY > -16 and screenY < height + 16:
            screen.blit(self.gfx, (screenX, screenY))
        
            '''if self.isSpike:
                pygame.draw.rect(screen, (0, 0, 255), (self.innerHitbox.x - gameVars["currentLevel"].camera.x, self.innerHitbox.y - gameVars["currentLevel"].camera.y, 12, 12), 2)
        '''
        #pygame.draw.rect(screen, (0, 0, 255), self.rect, 2)

npc_cfg = {
    'width'                     : [8, 16, 8, 16, 8, 24, 18, 16, 8, 32, 16],
    'height'                    : [8, 16, 8, 16, 8, 32, 12, 16, 8, 32, 16],
    'gfxwidth'                  : [8, 18, 8, 16, 8, 24, 18, 16, 8, 32, 16],
    'gfxheight'                 : [8, 18, 8, 16, 8, 32, 12, 16, 8, 32, 16],
    'gfxoffsetX'                : [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'gfxoffsetY'                : [0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'frames'                    : [2, 4, 1, 3, 3, 5, 2, 3, 3, 6, 1],
    'framestyle'                : [1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0],
    'framedelay'                : [0, 0, 0, 8, 8, 0, 0, 8, 8, 5, 0],
    'health'                    : [0, 1, 0, 0, 0, 4, 0, 0, 0, 0, 0],
    'nogravity'                 : [True, False, True, False, False, True, True, False, False, True, True],
    'noblockcollision'          : [True, False, True, False, False, False, True, False, False, True, True],
    'isWalker'                  : [False, False, False, False, False, False, False, False, False, False, False],
    'weakTo'                    : [[], [], [], [], [], [], [], [], [], [], []],
    'immuneTo'                  : [[], [], [], [], [], [], [], [], [], [], []],
    'respawnable'               : [False, True, False, False, False, True, False, False, False, False, True],
    'hittable'                  : [False, True, False, False, False, True, False, False, False, False, False],
    'dropsItems'                : [False, True, False, False, False, True, False, False, False, False, False],
}

class NPC():
    def __init__(self, id: int, x: int, y: int, section: int, direction: int, level) -> None:
        self.id             = id
        self.gfx            = pygame.image.load(f"npc/npc-{id}.png")
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
        self.origin         = None
        # "Free" NPC vars (for AI purposes, can be reassigned as string, array, etc)
        self.var1           = 0
        self.var2           = 0
        self.var3           = 0
        self.var4           = 0
        self.var5           = 0

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

        self.var1           = 0
        self.var2           = 0
        self.var3           = 0
        self.var4           = 0
        self.var5           = 0
    
    def kill(self):
        self.isValid = False
        self.isActive = False

        if self.id == 1 or self.id == 7:
            gameVars["currentLevel"].player.bulletsOut -= 1

        if npc_cfg["dropsItems"][self.id - 1]:
            rng = random.randint(1, 100)

            if rng > 90:
                item = NPC(4, self.rect.x, self.rect.y, self.section, self.direction, gameVars["currentLevel"])
                item.speedY = -4
                item.origin = self

                gameVars["currentLevel"].npcs.append(item)
            elif rng > 80:
                item = NPC(8, self.rect.x, self.rect.y, self.section, self.direction, gameVars["currentLevel"])
                item.speedY = -4
                item.origin = self

                gameVars["currentLevel"].npcs.append(item)
            elif rng > 60:
                item = NPC(5, self.rect.x, self.rect.y, self.section, self.direction, gameVars["currentLevel"])
                item.speedY = -4
                item.origin = self

                gameVars["currentLevel"].npcs.append(item)
            elif rng > 40:
                item = NPC(9, self.rect.x, self.rect.y, self.section, self.direction, gameVars["currentLevel"])
                item.speedY = -4
                item.origin = self

                gameVars["currentLevel"].npcs.append(item)
                
        
        for k, v in enumerate(get_NPC(idFilter = 3, sectionFilter= self.section)):
            if v.origin == self and v.speedX == 0 and v.speedY == 0:
                v.kill()

        if self.origin != None:
            try:
                gameVars["currentLevel"].npcs.remove(self)
            except ValueError:
                pass
    
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
                dirOffset = 0
                # behavior codes (shared with multiple npcs)
                if npc_cfg["frames"][self.id - 1] > 1 and npc_cfg["framedelay"][self.id - 1] != 0:
                    if npc_cfg["framestyle"][self.id - 1] == 1:
                        dirOffset = 2

                        if self.direction == DIR_RIGHT: dirOffset = 1
                    else:
                        dirOffset = 1

                        if self.direction == DIR_RIGHT: dirOffset = 2
                    
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

                    # THE GRAND CATALOG OF "SHIELD" BEHAVIOR
                    if (self.id == 2 and self.aiState == 0):
                        valid = False
                    
                    if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                        if gameVars["currentLevel"].player.shockForceTimer > 0 and self.health > 0:
                            self.harm(6, 48, WEAPON_SHOCK_FORCE)
                    
                    for k, v in enumerate(gameVars["currentLevel"].npcs):
                        if self.rect.colliderect(v.rect) and self.immuneFrames == 0:
                            # Flying Shield's behavior is here because it needed the bullets
                            if self.id == 6 and (self.direction != v.direction):
                                valid = False

                            if v.id == 1 and v.aiState == 0:
                                if valid:
                                    if self.health > 0:
                                        self.harm(1, 8, WEAPON_TRIPLE_SHOT)
                                    v.kill()
                                else:
                                    v.direction = -v.direction
                                    v.speedY = -3/math.sqrt(2)
                                    v.speedX = 4 * v.direction
                                    v.aiState = 1
                            if v.id == 7:
                                if valid:
                                    if self.health > 0:
                                        self.harm(3, 8, WEAPON_TRIPLE_SHOT)
                                else:
                                    if self.id == 2:
                                        # make the enemy vulnerable
                                        self.aiState = 1
                                        self.aiTimer = 16
                                        self.isOnGround = False
                                        gameVars["currentLevel"].player.bulletsOut -= 1
                                    v.kill()
                            if v.id == 10:
                                if self.health > 0:
                                    self.harm(4, 12, WEAPON_BURNER_WAVE)
                                v.kill()
                    
                if not self.nogravity:
                    if not self.isOnGround:
                        if self.speedY < 3:
                            self.speedY += 0.4
                        else:
                            self.speedY = 3
                
                if not self.noblockcollision:
                    for k, b in enumerate(gameVars["currentLevel"].blocks):
                        if b.solidSide:
                            if b.rect.colliderect(self.rect.x + self.speedX, self.rect.y, self.width, self.height):
                                self.speedX = 0

                                if self.isWalker:
                                    self.direction = -self.direction
                                
                                if self.id == 6 and self.aiState == 0 and self.aiTimer == 0:
                                    self.aiState = 1
                            
                        if b.solidTop or b.isSpike:
                            if b.rect.colliderect(self.rect.x, self.rect.y + self.speedY, self.width, self.height):
                                if self.speedY < 0:
                                    if b.solidBottom:
                                        self.speedY = b.rect.bottom - self.rect.top
                                        self.speedY = 0
                                elif self.speedY > 0:
                                    self.speedY = b.rect.top - self.rect.bottom
                                    self.isOnGround = True
                    
                # individual npc codes
                if self.id == 1: # PLAYER BULLET
                    self.speedX = self.direction * 4

                    if self.rect.x + self.width < gameVars["currentLevel"].camera.x or self.rect.x > gameVars["currentLevel"].camera.x + gameVars["currentLevel"].camera.width:
                        self.kill()
                    if gameVars["currentLevel"].camera.isUpdating:
                        self.kill()
                    
                    if self.direction == DIR_LEFT:
                        self.frame = 0
                    else:
                        self.frame = 1
                if self.id == 2: # TRACKER
                    if self.aiState == 0:
                        if math.fabs(gameVars["currentLevel"].player.rect.centerx - self.rect.centerx) <= 80 and self.aiTimer == 0 and not gameVars["currentLevel"].player.hasDied:
                            self.aiState = 1
                        
                        if gameVars["currentLevel"].player.rect.centerx - self.rect.centerx < 0:
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
                            sectionX = self.rect.x - gameVars["currentLevel"].sections[self.section].x
                            sectionY = self.rect.y - gameVars["currentLevel"].sections[self.section].y

                            # initialize angle
                            _x = (gameVars["currentLevel"].player.rect.x + 0.5 * gameVars["currentLevel"].player.width) - (self.rect.x + 0.5 * self.width)
                            _y = (gameVars["currentLevel"].player.rect.y + 0.5 * gameVars["currentLevel"].player.height) - (self.rect.y + 0.5 * self.height)
                            _angle = math.degrees(math.atan(_y/_x))

                            _vector = [self.direction, 0]

                            # rudimentary vector rotation
                            _rad = math.radians(_angle)
                            _sinrad = math.sin(_rad)
                            _cosrad = math.cos(_rad)

                            _vector = [_vector[0] * _cosrad - _vector[1] * _sinrad, _vector[0] * _sinrad + _vector[1] * _cosrad]

                            p = NPC(3, sectionX + self.width/2, sectionY + self.height/2, self.section, self.direction, gameVars["currentLevel"])
                            p.speedX = 3 * _vector[0]
                            p.speedY = 3 * _vector[1]
                            p.origin = self

                            gameVars["currentLevel"].npcs.append(p)

                        self.aiTimer += 1

                        if self.direction == DIR_LEFT:
                            self.frame = 1
                        else:
                            self.frame = 3

                        if self.aiTimer >= 96:
                            self.aiState = 0
                            self.aiTimer = 10
                    
                    if gameVars["currentLevel"].player.immuneFrames == 0 and ((gameVars["currentLevel"].player.dashTimer == 0 and gameVars["currentLevel"].player.hasFlashDash) or not gameVars["currentLevel"].player.hasFlashDash) and gameVars["currentLevel"].player.shockForceTimer == 0:
                        if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                            gameVars["currentLevel"].player.harm(1)
                if self.id == 3: # TRACKER BULLET
                    if self.rect.x + self.width < gameVars["currentLevel"].camera.x or self.rect.x > gameVars["currentLevel"].camera.x + gameVars["currentLevel"].camera.width:
                        self.kill()
                    if gameVars["currentLevel"].camera.isUpdating:
                        self.kill()
                    
                    if gameVars["currentLevel"].player.immuneFrames == 0 and ((gameVars["currentLevel"].player.dashTimer == 0 and gameVars["currentLevel"].player.hasFlashDash) or not gameVars["currentLevel"].player.hasFlashDash) and gameVars["currentLevel"].player.shockForceTimer == 0:
                        if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                            gameVars["currentLevel"].player.harm(2)
                if self.id == 4: # HEALTH ENERGY (BIG)
                    if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                        gameVars["currentLevel"].player.heal(HEALTH_ENERGY_LARGE_VALUE)
                        self.kill()
                if self.id == 5: # HEALTH ENERGY (SMALL)
                    if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                        gameVars["currentLevel"].player.heal(HEALTH_ENERGY_SMALL_VALUE)
                        self.kill()
                if self.id == 6:
                    if gameVars["currentLevel"].player.immuneFrames == 0 and ((gameVars["currentLevel"].player.dashTimer == 0 and gameVars["currentLevel"].player.hasFlashDash) or not gameVars["currentLevel"].player.hasFlashDash) and gameVars["currentLevel"].player.shockForceTimer == 0:
                        if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                            gameVars["currentLevel"].player.harm(4)

                    if self.aiState == 0:
                        if self.aiTimer > 0:
                            self.aiTimer -= 1

                        self.speedX = self.direction
                        if (self.frame < 0 or self.frame > 1) and self.direction == DIR_LEFT:
                            self.frame = 0
                        if (self.frame < 5 or self.frame > 6) and self.direction == DIR_RIGHT:
                            self.frame = 5
                        
                        self.frameTimer += 1

                        if self.frameTimer % 8 == 0:
                            self.frame += 1
                        
                        if (self.frame > 1 and self.direction == DIR_LEFT) or (self.frame > 6 and self.direction == DIR_RIGHT):
                            self.frame = int(self.direction == DIR_RIGHT) * 5
                    else:
                        _frameTable = [[2, 3, 4, 8, 7], [7, 8, 9, 3, 2]]
                        offset = 0
                        if self.direction == DIR_RIGHT:
                            offset = 1
                        
                        self.speedX = 0
                        self.aiTimer += 1

                        if self.aiTimer <= 20:
                            self.frame = _frameTable[offset][self.var1]
                            if self.aiTimer % 4 == 0 and self.aiTimer != 0:
                                self.var1 += 1
                                
                                if self.var1 > 4:
                                    self.var1 = 4
                        else:
                            self.direction = -self.direction
                            self.aiState = 0
                            self.aiTimer = 10
                            self.var1 = 0
                if self.id == 7: # PLAYER BULLET (CHARGED)
                    self.speedX = self.direction * 4

                    if (self.rect.x + self.width < gameVars["currentLevel"].camera.x) or (self.rect.x > gameVars["currentLevel"].camera.x + gameVars["currentLevel"].camera.width):
                        self.kill()
                    if gameVars["currentLevel"].camera.isUpdating:
                        self.kill()
                    
                    if self.direction == DIR_LEFT:
                        self.frame = 0
                    else:
                        self.frame = 1
                if self.id == 8: # WEAPON ENERGY (BIG)
                    self.imageState = gameVars["currentLevel"].player.weapon

                    if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                        if gameVars["currentLevel"].player.weapon != 0:
                            gameVars["currentLevel"].player.weaponEnergies[gameVars["currentLevel"].player.weapon] += WEAPON_ENERGY_LARGE_VALUE
                        self.kill()
                if self.id == 9: # WEAPON ENERGY (SMALL)
                    self.imageState = gameVars["currentLevel"].player.weapon

                    if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                        if gameVars["currentLevel"].player.weapon != 0:
                            gameVars["currentLevel"].player.weaponEnergies[gameVars["currentLevel"].player.weapon] += WEAPON_ENERGY_SMALL_VALUE
                        self.kill()
                if self.id == 10:
                    self.speedX = self.direction * 4

                    if self.direction == DIR_LEFT:
                        if self.frame < 0 or self.frame > 2:
                            self.frame = 0
                    else:
                        if self.frame < 3 or self.frame > 5:
                            self.frame = 3

                    if self.rect.x + self.width < gameVars["currentLevel"].camera.x or self.rect.x > gameVars["currentLevel"].camera.x + gameVars["currentLevel"].camera.width:
                        self.kill()
                    if gameVars["currentLevel"].camera.isUpdating:
                        self.kill()
                if self.id == 11:
                    if self.rect.colliderect(gameVars["currentLevel"].player.rect):
                        gameVars["menuTransitionTimer"] = 60
                        self.kill()
                
                self.rect.x += self.speedX
                self.rect.y += self.speedY
        
            if self.immuneFrames > 0:
                self.immuneFrames -= 1

            # render npcs
            screenX = self.rect.x - gameVars["currentLevel"].camera.x
            screenY = self.rect.y - gameVars["currentLevel"].camera.y

            # check which section the npc is in
            for k, s in enumerate(gameVars["currentLevel"].sections):
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
                if self.id == 11: return

                # reset some stuff
                self.isActive = False # might add exceptions because some enemies can work off-screen
                self.frame = 0
                self.frameTimer = 0
                self.aiTimer = 0
                self.aiState = 0

                if self.id == 1 or self.id == 7 or self.origin != None:
                    self.kill()

class Camera():
    def __init__(self, startX: int, startY: int, level) -> None:
        self.x              = startX
        self.y              = startY
        self.width          = width
        self.height         = height
        # movement vars (targetX, Y, and moveDir only used to nudge the player a bit)
        self.dx             = 0
        self.dy             = 0
        self.moveDir        = 0
        self.isUpdating     = False
        self.section        = level.player.section
    
    def update(self):
        # shorthands so i don't have to write long vars only to refer to one thing
        player = gameVars["currentLevel"].player
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
        if not self.isUpdating:
            if not player.hasDied:
                if player.rect.x >= self.x + (self.width / 2) and player.speedX > 0:
                    self.dx = player.speedX
                if player.rect.x <= self.x + (self.width / 2) and player.speedX < 0:
                    self.dx = player.speedX
                if player.rect.y >= self.y + (self.height / 2) and player.speedY >= 1:
                    self.dy = player.speedY
                if player.rect.y <= self.y + (self.height / 2) and player.speedY <= 1:
                    self.dy = player.speedY
                
                self.x += self.dx
                self.y += self.dy
                self.x = math_clamp(self.x, gameVars["currentLevel"].sections[player.section].x, gameVars["currentLevel"].sections[player.section].x + gameVars["currentLevel"].sections[player.section].width - self.width)
                self.y = math_clamp(self.y, gameVars["currentLevel"].sections[player.section].y, gameVars["currentLevel"].sections[player.section].y + gameVars["currentLevel"].sections[player.section].height - self.height)
                self.dx = 0
                self.dy = 0

                if self.section != player.section:
                    for k, v in enumerate(gameVars["currentLevel"].npcs):
                        if v.section == player.section:
                            if (v.origin == None) and (npc_cfg["respawnable"][v.id - 1]):
                                v.isValid = True
                                v.reinitialize()
                
                self.section = player.section
        else:
            pass

class Level():
    sections            = []
    blocks              = []
    npcs                = []
    healTimer           = 0
    checkpointReached   = 0
    transitionTimer     = 0

    def __init__(self, filename):
        self.levelName = filename # we may need this later
        file = open(f"{filename}.lvl", "r")
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

                    if parameters["id"] == 11:
                        npcClass.var1 = temp[5]
                    self.npcs.append(npcClass)

        file.close()
    
    def restartLevel(self):
        self.transitionTimer = 60

        for k, v in enumerate(self.npcs):
            if v.origin == None:
                v.reinitialize()
            else:
                v.kill()
        
        self.player.reinitialize()

        self.camera.section = self.player.section
        self.camera.x = self.player.rect.centerx - 128
        self.camera.y = self.player.rect.centery - 96
    
    def runLevel(self):
        if self.transitionTimer == 0:
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
        else:
            self.transitionTimer -= 1

# everything is now in this one level class
updateGameDataCounts()
clock = pygame.time.Clock()

keyIdx = 0

pauseMenuWeapons = [[WEAPON_TRIPLE_SHOT, WEAPON_CRYSTAL_BLAST], [WEAPON_SHOCK_FORCE, WEAPON_SPIRAL_CYCLONE], [WEAPON_BURNER_WAVE, WEAPON_LEAF_GUARD], [WEAPON_DOWNPOUR_STORM, -1, -1, -1]]
pauseMenuWeaponNames = [["TRIPLE SHOT", "CRYSTAL B."], ["SHOCK FORCE", "S. CYCLONE"], ["BURNER WAVE", "LEAF GUARD"], ["DOWNPOUR S.", "", "", ""]]
weaponDescHeader = [["-TRIPLE SHOT-", "-CRYSTAL BLAST-"],
                    ["-SHOCK FORCE-", "-SPIRAL CYCLONE-"],
                    ["-BURNER WAVE-", "-LEAF GUARD-"],
                    ["-DOWNPOUR STORM-", "", "", ""]]
weaponDesc = [["SHOOTS A SMALL PROJECTILE.\nCHARGE TO RELEASE 3 LARGER\nPROJECTILES AT ONCE.",
               "ENCASES AN ENEMY IN\nCRYSTAL THAT CAN BE USED\nAS A PLATFORM."],
              ["FOR A TEMPORARY AMOUNT OF\nTIME, ANY ENEMIES MADE\nCONTACT WITH THE PLAYER\nGETS HIT WITH ELECTRICITY.",
               "RELEASES A GUST OF WIND\nSTRAIGHT FORWARD. ANY\nENEMIES WITH SHIELDS CAN\nSTILL TAKE DAMAGE."],
              ["SUMMONS A WAVE OF FIRE\nTHAT CAN BE USED ON THE\nGROUND OR IN MID-AIR.",
               "PROTECTS YOU FROM ENEMY\nPROJECTILES, CAN BE\nUNLEASHED TO DEAL DAMAGE."],
              ["SHOOTS A WATER SPHERE\nUPWARDS. RAINS DOWN WATER\nIF IT GOES OFFSCREEN.",
               "", "", ""],
             ]

def main():
    loadControls()
    loadSettings()
    updateGameDataCounts()

    gameVars["currentLevel"] = Level("test_level")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if gameVars["inGame"]:
                    if event.key == controls['shoot'] and gameVars["currentLevel"].player.weapon == WEAPON_TRIPLE_SHOT and not gameVars["currentLevel"].player.hasDied:
                        gameVars["currentLevel"].player.shootProjectile(gameVars["currentLevel"].player.chargeTimer)
                
                # button shenanigans (mostly menu)
                if event.key == controls['left']:
                    gameVars["leftKeyPressed"] = False
                if event.key == controls['right']:
                    gameVars["rightKeyPressed"] = False
                if event.key == controls['up']:
                    gameVars["upKeyPressed"] = False
                if event.key == controls['down']:
                    gameVars["downKeyPressed"] = False
                if event.key == controls['jump']:
                    gameVars["jumpKeyPressed"] = False
                if event.key == controls['change (l)']:
                    gameVars["changeLKeyPressed"] = False
                if event.key == controls['change (r)']:
                    gameVars["changeRKeyPressed"] = False
                if event.key == controls['pause']:
                    gameVars["pauseKeyPressed"] = False
            if event.type == pygame.KEYDOWN and gameVars["isPaused"] and gameVars["pauseMenuScreen"] == 3 and gameVars["pauseMenuTakesChanges"]:
                new_controls[control_names[gameVars["pauseMenuRow"]]] = event.key
                gameVars["keyDelay"] = 10
                gameVars["pauseMenuTakesChanges"] = False
        
        if gameVars["inGame"]:
            screen.fill((30, 86, 51))

            if not gameVars["isPaused"]:
                gameVars["currentLevel"].runLevel()
                
                # HUDs
                ## OLD HUD
                '''screen.blit(bars[7], (8, 78 - gameVars["currentLevel"].player.maxHealth * 2), (0, 0, 8, gameVars["currentLevel"].player.maxHealth * 2))

                for i in range(1, gameVars["currentLevel"].player.health + 1):
                    y = 78 - 2 * i
                    screen.blit(bars[0], (8, y))

                if gameVars["currentLevel"].player.weapon > 0:
                    screen.blit(bars[7], (24, 78 - 36 * 2))

                    for i in range(1, gameVars["currentLevel"].player.weaponEnergies[gameVars["currentLevel"].player.weapon] + 1):
                        y = 78 - 2 * i
                        screen.blit(bars[gameVars["currentLevel"].player.weapon], (24, y))'''

                ## NEW HUD
                screen.blit(bars[11], (0, 0))
                screen.blit(bars[8], (16, 8), (36 - 6 * gameData["energyUpObtained"], 0, gameVars["currentLevel"].player.maxHealth * 2 + 1, 8))
                for i in range(1, gameVars["currentLevel"].player.health + 1):
                    x = 16 + 2 * (i - 1)
                    screen.blit(bars[0], (x, 8))
                screen.blit(bars[7], (16, 8), (36 - 6 * gameData["energyUpObtained"], 0, gameVars["currentLevel"].player.maxHealth * 2 + 1, 8))
                
                text = font.render(f"{gameVars['currentLevel'].player.health}", False, (255, 255, 255))
                screen.blit(text, (8, 32))

                if gameVars["currentLevel"].player.weapon != 0:
                    screen.blit(bars[10], (16, 16))
                    for i in range(1, gameVars["currentLevel"].player.weaponEnergies[gameVars["currentLevel"].player.weapon] + 1):
                        x = 16 + 2 * (i - 1)
                        screen.blit(bars[gameVars["currentLevel"].player.weapon], (x, 15))
                    screen.blit(bars[9], (16, 15))

                if gameVars["weaponChangeTimer"] > 0:
                    offsetX = gameVars["currentLevel"].player.width // 2 - 8
                    offsetY = -20
                    if gameVars["currentLevel"].player.rect.y - gameVars["currentLevel"].camera.y < 48:
                        offsetY = gameVars["currentLevel"].player.height + 4
                    
                    screen.blit(icons[0], (gameVars["currentLevel"].player.rect.x - gameVars["currentLevel"].camera.x + offsetX, gameVars["currentLevel"].player.rect.y - gameVars["currentLevel"].camera.y + offsetY), (16 * gameVars["currentLevel"].player.weapon, 0, 16, 16))
                    gameVars["weaponChangeTimer"] -= 1

                #text2 = font.render(f"{gameVars["currentLevel"].player.weaponOwnedIdx}", False, (255, 255, 255))
                #screen.blit(text2, (8, 96))
                
                gameVars["currentLevel"].camera.update()
            else:
                gameVars["weaponChangeTimer"] = 0
                keypressed = pygame.key.get_pressed()

                if not gameVars["pauseMenuTakesChanges"] and gameVars["pauseSavingTextTimer"] == 0 and gameVars["keyDelay"] == 0:
                    if keypressed and gameVars["menuTransitionTimer"] == 0:
                        if keypressed[controls['pause']] and not gameVars["pauseKeyPressed"] and gameVars["pauseMenuScreen"] != 3:
                            gameVars["isPaused"] = False
                            gameVars["pauseKeyPressed"] = True
                            gameVars["menuTransitionTimer"] = 16
                            gameVars["pauseMenuRow"] = 0
                            gameVars["pauseMenuCol"] = 0
                            gameVars["pauseMenuTimer"] = 0
                            gameVars["pauseMenuScreen"] = 0

                            saveSettings()
                        
                        if keypressed[controls['jump']] and not gameVars["jumpKeyPressed"]:
                            if gameVars["pauseMenuScreen"] == 0:
                                # basically the same as pause button, but you selected a weapon instead
                                gameVars["currentLevel"].player.changeWeapon(pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]])

                                gameVars["isPaused"] = False
                                gameVars["jumpKeyPressed"] = True
                                gameVars["menuTransitionTimer"] = 16
                                gameVars["pauseMenuRow"] = 0
                                gameVars["pauseMenuCol"] = 0
                                gameVars["pauseMenuTimer"] = 0
                                gameVars["pauseMenuScreen"] = 0
                            elif gameVars["pauseMenuScreen"] == 1:
                                gameVars["jumpKeyPressed"] = True
                                if gameVars["pauseMenuRow"] == 2:
                                    gameVars["pauseMenuScreen"] = 3
                                    gameVars["pauseMenuCol"] = 0
                                    gameVars["pauseMenuRow"] = 0
                                    gameVars["pauseMenuTimer"] = 0

                                    for k, v in enumerate(controls):
                                        new_controls[control_names[k]] = controls[v]
                                elif gameVars["pauseMenuRow"] == 3:
                                    gameVars["jumpKeyPressed"] = True
                                    settings[setting_names[gameVars["pauseMenuRow"] - 1]] = not settings[setting_names[gameVars["pauseMenuRow"] - 1]]
                            elif gameVars["pauseMenuScreen"] == 2:
                                if gameVars["pauseMenuRow"] == 1:
                                    pygame.quit()
                                    sys.exit()
                            elif gameVars["pauseMenuScreen"] == 3:
                                if gameVars["pauseMenuRow"] < len(controls):
                                    gameVars["pauseMenuTakesChanges"] = True
                                else:
                                    if gameVars["pauseMenuRow"] == len(controls):
                                        saveControls()
                                    elif gameVars["pauseMenuRow"] == len(controls) + 1:
                                        gameVars["pauseMenuScreen"] = 1
                                        gameVars["pauseMenuCol"] = 0
                                        gameVars["pauseMenuRow"] = 0
                                        gameVars["pauseMenuTimer"] = 0
                        
                        if keypressed[controls['left']] and not gameVars["leftKeyPressed"]:
                            if gameVars["pauseMenuScreen"] == 0:
                                gameVars["leftKeyPressed"] = True
                                gameVars["pauseMenuCol"] -= 1

                                if gameVars["pauseMenuCol"] < 0:
                                    gameVars["pauseMenuCol"] += 2
                                    gameVars["pauseMenuRow"] -= 1
                                    
                                if gameVars["pauseMenuRow"] < 0:
                                    gameVars["pauseMenuCol"] = 1
                                    gameVars["pauseMenuRow"] += 4

                                # make sure the selection can't get to weapons that aren't unlocked yet
                                while not(pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]] in gameVars["currentLevel"].player.weaponOwned):
                                    gameVars["pauseMenuCol"] -= 1

                                    if gameVars["pauseMenuCol"] < 0:
                                        gameVars["pauseMenuCol"] += 2
                                        gameVars["pauseMenuRow"] -= 1
                                    
                                    if gameVars["pauseMenuRow"] < 0:
                                        gameVars["pauseMenuCol"] = 1
                                        gameVars["pauseMenuRow"] += 4
                            elif gameVars["pauseMenuScreen"] == 1:
                                if gameVars["pauseMenuRow"] < 2:
                                    if gameVars["pauseMenuTimer"] % 4 == 0:
                                        settings[setting_names[gameVars["pauseMenuRow"]]] -= 0.01

                                    if settings[setting_names[gameVars["pauseMenuRow"]]] < 0:
                                        settings[setting_names[gameVars["pauseMenuRow"]]] = 0.0

                        if keypressed[controls['right']] and not gameVars["rightKeyPressed"]:
                            if gameVars["pauseMenuScreen"] == 0:
                                gameVars["rightKeyPressed"] = True
                                gameVars["pauseMenuCol"] += 1

                                if gameVars["pauseMenuCol"] > 1:
                                    gameVars["pauseMenuCol"] -= 2
                                    gameVars["pauseMenuRow"] += 1
                                
                                if gameVars["pauseMenuRow"] > 3 - gameVars["pauseMenuCol"]:
                                    gameVars["pauseMenuRow"] -= 4

                                # make sure the selection can't get to weapons that aren't unlocked yet
                                while not(pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]] in gameVars["currentLevel"].player.weaponOwned):
                                    gameVars["pauseMenuCol"] += 1

                                    if gameVars["pauseMenuCol"] > 1:
                                        gameVars["pauseMenuCol"] -= 2
                                        gameVars["pauseMenuRow"] += 1
                                    
                                    if gameVars["pauseMenuRow"] > 3 - gameVars["pauseMenuCol"]:
                                        gameVars["pauseMenuRow"] -= 4
                            elif gameVars["pauseMenuScreen"] == 1:
                                if gameVars["pauseMenuRow"] < 2:
                                    if gameVars["pauseMenuTimer"] % 4 == 0:
                                        settings[setting_names[gameVars["pauseMenuRow"]]] += 0.01

                                    if settings[setting_names[gameVars["pauseMenuRow"]]] > 1.0:
                                        settings[setting_names[gameVars["pauseMenuRow"]]] = 1.0
                        
                        if keypressed[controls['up']] and not gameVars["upKeyPressed"]:
                            gameVars["upKeyPressed"] = True
                            if gameVars["pauseMenuScreen"] == 0:
                                gameVars["pauseMenuRow"] -= 1

                                if gameVars["pauseMenuRow"] < 0:
                                    gameVars["pauseMenuRow"] += (3 + gameVars["pauseMenuCol"])
                                    gameVars["pauseMenuCol"] -= 1
                                
                                if gameVars["pauseMenuCol"] < 0:
                                    gameVars["pauseMenuCol"] += 2
                                
                                # make sure the selection can't get to weapons that aren't unlocked yet
                                while not(pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]] in gameVars["currentLevel"].player.weaponOwned):
                                    gameVars["pauseMenuRow"] -= 1

                                    if gameVars["pauseMenuRow"] < 0:
                                        gameVars["pauseMenuRow"] += (3 + gameVars["pauseMenuCol"])
                                        gameVars["pauseMenuCol"] -= 1
                                    
                                    if gameVars["pauseMenuCol"] < 0:
                                        gameVars["pauseMenuCol"] += 2
                            elif gameVars["pauseMenuScreen"] == 1:
                                gameVars["pauseMenuRow"] -= 1

                                if gameVars["pauseMenuRow"] < 0:
                                    gameVars["pauseMenuRow"] += 4
                            elif gameVars["pauseMenuScreen"] == 2:
                                gameVars["pauseMenuRow"] -= 1

                                if gameVars["pauseMenuRow"] < 0:
                                    gameVars["pauseMenuRow"] += 2
                            elif gameVars["pauseMenuScreen"] == 3:
                                gameVars["pauseMenuRow"] -= 1

                                if gameVars["pauseMenuRow"] < 0:
                                    gameVars["pauseMenuRow"] += len(controls) + 2
                        
                        if keypressed[controls['down']] and not gameVars["downKeyPressed"]:
                            gameVars["downKeyPressed"] = True
                            if gameVars["pauseMenuScreen"] == 0:
                                gameVars["pauseMenuRow"] += 1

                                if gameVars["pauseMenuRow"] > 3 - gameVars["pauseMenuCol"]:
                                    gameVars["pauseMenuRow"] -= (4 - gameVars["pauseMenuCol"])
                                    gameVars["pauseMenuCol"] += 1

                                if gameVars["pauseMenuCol"] > 1:
                                    gameVars["pauseMenuCol"] -= 2
                                
                                # make sure the selection can't get to weapons that aren't unlocked yet
                                while not(pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]] in gameVars["currentLevel"].player.weaponOwned):
                                    gameVars["pauseMenuRow"] += 1

                                    if gameVars["pauseMenuRow"] > 3 - gameVars["pauseMenuCol"]:
                                        gameVars["pauseMenuRow"] -= (4 - gameVars["pauseMenuCol"])
                                        gameVars["pauseMenuCol"] += 1
                                    
                                    if gameVars["pauseMenuCol"] > 1:
                                        gameVars["pauseMenuCol"] -= 2
                            elif gameVars["pauseMenuScreen"] == 1:
                                gameVars["pauseMenuRow"] += 1

                                if gameVars["pauseMenuRow"] > 3:
                                    gameVars["pauseMenuRow"] -= 4
                            elif gameVars["pauseMenuScreen"] == 2:
                                gameVars["pauseMenuRow"] += 1

                                if gameVars["pauseMenuRow"] > 1:
                                    gameVars["pauseMenuRow"] -= 2
                            elif gameVars["pauseMenuScreen"] == 3:
                                gameVars["pauseMenuRow"] += 1

                                if gameVars["pauseMenuRow"] > len(controls) + 1:
                                    gameVars["pauseMenuRow"] -= len(controls) + 2
                        
                        if keypressed[controls["change (l)"]] and not gameVars["changeLKeyPressed"]:
                            gameVars["changeLKeyPressed"] = True
                            if gameVars["pauseMenuScreen"] > 0 and gameVars["pauseMenuScreen"] != 4:
                                gameVars["pauseMenuScreen"] -= 1
                                gameVars["pauseMenuCol"] = 0
                                gameVars["pauseMenuRow"] = 0
                                gameVars["pauseMenuTimer"] = 0
                        
                        if keypressed[controls["change (r)"]] and not gameVars["changeRKeyPressed"]:
                            gameVars["changeRKeyPressed"] = True
                            if gameVars["pauseMenuScreen"] < 2:
                                gameVars["pauseMenuScreen"] += 1
                                gameVars["pauseMenuCol"] = 0
                                gameVars["pauseMenuRow"] = 0
                                gameVars["pauseMenuTimer"] = 0

                screen.fill((0, 0, 0))

                # screen
                if gameVars["pauseMenuScreen"] == 0: # WEAPON SELECT
                    screen.blit(pauseMenuHuds[0], (0, 0))

                    #hp bar drop shadow
                    pygame.draw.rect(screen, (0, 0, 0), (58, 25, gameVars["currentLevel"].player.maxHealth * 2 + 1, 8))
                    # current health
                    screen.blit(bars[8], (56, 24), (36 - 6 * gameData["energyUpObtained"], 0, gameVars["currentLevel"].player.maxHealth * 2 + 1, 8))
                    for i in range(1, gameVars["currentLevel"].player.health + 1):
                        x = 56 + 2 * (i - 1)
                        screen.blit(bars[0], (x, 24))
                    screen.blit(bars[7], (55, 24), (72, 0, 1, 8))
                    screen.blit(bars[7], (56, 24), (36 - 6 * gameData["energyUpObtained"], 0, gameVars["currentLevel"].player.maxHealth * 2 + 1, 8))

                    # player appearance
                    if pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]] != -1:
                        screen.blit(playerAssets[pauseMenuWeapons[gameVars["pauseMenuRow"]][gameVars["pauseMenuCol"]]], (0, 0), (58, 0, 32, 32))
                    else:
                        screen.blit(playerAssets[gameVars["currentLevel"].player.weapon], (0, 0), (58, 0, 32, 32))

                    # icons & texts
                    for i in range(4):
                        for j in range(2):
                            if pauseMenuWeapons[i][j] == -1: continue

                            yOffset = 16
                            if i == gameVars["pauseMenuRow"] and j == gameVars["pauseMenuCol"]:
                                yOffset = 0
                            
                            text = font.render(f"{pauseMenuWeaponNames[i][j]}", False, (255, 255, 255))
                            
                            if pauseMenuWeapons[i][j] in gameVars["currentLevel"].player.weaponOwned:
                                screen.blit(icons[0], (16 + j * 112, 48 + i * 24), (16 * pauseMenuWeapons[i][j], yOffset, 16, 16))
                                screen.blit(text, (32 + j * 112, 48 + i * 24))
                                screen.blit(bars[10], (32 + j * 112, 58 + i * 24), (0, 0, 71, 2))

                                for k in range(1, gameVars["currentLevel"].player.weaponEnergies[pauseMenuWeapons[i][j]] + 1):
                                    x = 16 + 2 * (k - 1)
                                    screen.blit(bars[pauseMenuWeapons[i][j]], (16 + j * 112 + x, 56 + i * 24))
                    
                    # split the lines into an array of itself because font.render doesn't know how to deal with \n for some reason
                    tempString = weaponDesc[gameVars['pauseMenuRow']][gameVars['pauseMenuCol']]
                    tempData = tempString.split("\n")

                    for i, val in enumerate(tempData):
                        descText = font.render(f"{val}", False, (255, 255, 255))
                        screen.blit(descText, (24, 160 + i * 8))
                    
                    weaponName = font.render(f"{weaponDescHeader[gameVars['pauseMenuRow']][gameVars['pauseMenuCol']]}", False, (0, 239, 222))
                    screen.blit(weaponName, (24, 152))
                    
                    if gameData["hasFlashDash"]:
                        screen.blit(icons[1], (168, 120), (0, 0, 16, 16))
                    
                    if gameData["hasWallCling"]:
                        screen.blit(icons[1], (192, 120), (16, 0, 16, 16))

                    if gameData["hasPowerPlasma"]:
                        screen.blit(icons[1], (216, 120), (32, 0, 16, 16))
                else:
                    gameVars["pauseMenuTimer"] += 1
                    screen.blit(pauseMenuHuds[2], (0, 0))

                    if gameVars["keyDelay"] > 0:
                        gameVars["keyDelay"] -= 1

                    if gameVars["pauseMenuScreen"] == 1:
                        headers = ["AUDIO", "CONTROLS", "DATA"]
                        options = ["BGM VOLUME", "SFX VOLUME", "CHANGE BUTTONS", "AUTOSAVE"]

                        for i, text in enumerate(options):
                            renderedText = font.render(f"{text}", False, (255, 255, 255))

                            x = 24
                            y = 40 + i * 16

                            if i == 2:
                                y = 88
                            elif i == 3:
                                y = 120
                            
                            screen.blit(renderedText, (x, y))

                            if gameVars["pauseMenuRow"] == i:
                                cursor = font.render("> ", False, (247, 189, 57))
                                screen.blit(cursor, (16, y))

                        for i, text in enumerate(headers): # OPTIONS MENU
                            renderedText = font.render(f"{text}", False, (247, 189, 57))

                            x = 104
                            y = 24

                            if i == 1:
                                x = 96
                                y = 72
                            elif i == 2:
                                x = 112
                                y = 104
                            
                            screen.blit(renderedText, (x, y))
                        
                        leftCursor = font.render("<", False, (255, 255, 255))
                        rightCursor = font.render(">", False, (255, 255, 255))

                        for i in range(2):
                            y = 40 + i * 16
                            if settings[setting_names[i]] != 0.0:
                                screen.blit(leftCursor, (184, y))
                            if settings[setting_names[i]] != 1.0:
                                screen.blit(rightCursor, (224, y))

                        bgmValue = font.render(f"{int(settings['BGM_volume'] * 100)}", False, (255, 255, 255))
                        sfxValue = font.render(f"{int(settings['SFX_volume'] * 100)}", False, (255, 255, 255))

                        screen.blit(bgmValue, (200, 40))
                        screen.blit(sfxValue, (200, 56))

                        checkBoxWidth = 1
                        if settings["autosaves"]:
                            checkBoxWidth = 10
                        pygame.draw.rect(screen, (255, 255, 255), (224, 120, 7, 7), checkBoxWidth)
                    elif gameVars["pauseMenuScreen"] == 2: # FORFEIT MENU
                        header = font.render("FORFEIT MENU", False, (247, 189, 57))

                        options = ["RETURN TO MAIN MENU", "EXIT TO WINDOWS"]

                        for i, text in enumerate(options):
                            renderedText = font.render(f"{text}", False, (255, 255, 255))

                            x = 24
                            y = 40 + i * 16

                            screen.blit(renderedText, (x, y))

                            if gameVars["pauseMenuRow"] == i:
                                cursor = font.render("> ", False, (247, 189, 57))
                                screen.blit(cursor, (16, y))
                        screen.blit(header, (80, 24))
                    elif gameVars["pauseMenuScreen"] == 3: #CHANGE CONTROLS
                        header = font.render("CHANGE BUTTON CONFIGURATION", False, (247, 189, 57))
                        text1 = font.render("NEW CONTROL SCHEMES ONLY", False, (255, 255, 255))
                        text2 = font.render("APPLY AFTER CONFIRMING", False, (255, 255, 255))
                        text3 = font.render("CHANGES.", False, (255, 255, 255))
                        screen.blit(header, (16, 32))
                        screen.blit(text1, (32, 48))
                        screen.blit(text2, (40, 56))
                        screen.blit(text3, (96, 64))

                        for k, v in enumerate(new_controls):
                            color = (255, 255, 255)

                            if k == gameVars["pauseMenuRow"] and gameVars["pauseMenuTakesChanges"]:
                                color = (247, 189, 57)
                            keyName = pygame.key.name(new_controls[v])
                            
                            text = font.render(control_names[k].upper(), False, color)
                            screen.blit(text, (24, 80 + (8 * k)))

                            text2 = font.render(keyName.upper(), False, color)
                            screen.blit(text2, (112, 80 + (8 * k)))

                            if gameVars["pauseMenuRow"] == k:
                                cursor = font.render("> ", False, (247, 189, 57))

                                screen.blit(cursor, (16, 80 + (8 * gameVars["pauseMenuRow"])))

                            if new_controls[v] != controls[v]:
                                old_color = (100, 100, 100)
                                keyName_old = pygame.key.name(controls[v])
                                text3 = font.render(f"({keyName_old.upper()})", False, old_color)
                                screen.blit(text3, (112 + (8 * (len(keyName) + 1)), 80 + (8 * k)))
                        
                        confirmColor, backColor = (255, 255, 255), (255, 255, 255)

                        if gameVars["pauseMenuRow"] == len(new_controls):
                            confirmColor = (245, 200, 66)
                        elif gameVars["pauseMenuRow"] == len(new_controls) + 1:
                            backColor = (245, 200, 66)

                        confirmText = font.render("CONFIRM", False, confirmColor)
                        backText = font.render("BACK", False, backColor)

                        screen.blit(confirmText, (24, 168))
                        screen.blit(backText, (24, 176))

                        if gameVars["pauseMenuTakesChanges"]:
                            saveText = font.render("PRESS ANY VALID KEY", False, (245, 200, 66))
                            screen.blit(saveText, (48, 192))
                        if gameVars["pauseSavingTextTimer"] > 0:
                            saveText = font.render("SAVING CONTROLS...", False, (245, 200, 66))
                            screen.blit(saveText, (56, 192))

                            gameVars["pauseSavingTextTimer"] -= 1

                            if gameVars["pauseSavingTextTimer"] % 8 == 0:
                                if keyIdx < len(controls):
                                    controls[control_names[keyIdx]] = new_controls[control_names[keyIdx]]
                            
                                keyIdx += 1
                        else:
                            keyIdx = 0

                # selection
                if gameVars["pauseMenuScreen"] < 4:
                    screen.blit(pauseMenuHuds[1], (0, 200), (0, 24 * gameVars["pauseMenuScreen"], 256, 24))

            if gameVars["currentLevel"].transitionTimer > 0 or gameVars["menuTransitionTimer"] > 0:
                pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height), width)
            
        if gameVars["menuTransitionTimer"] > 0:
            gameVars["menuTransitionTimer"] -= 1
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()