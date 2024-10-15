import sys, pygame
pygame.init()

size = width, height = 256, 224
screen = pygame.display.set_mode(size)
black = (0, 0, 0)

player = pygame.image.load("pygame project\\test.png")
playerRect = player.get_rect()
clock = pygame.time.Clock()
speed = [0, 0]

blockGFXs = [pygame.image.load("pygame project\\block-1.png")]
blockRects = [blockGFXs[0].get_rect(), blockGFXs[0].get_rect(), blockGFXs[0].get_rect(), blockGFXs[0].get_rect(), blockGFXs[0].get_rect(), blockGFXs[0].get_rect(), blockGFXs[0].get_rect()]
playerStates = [False, 0]

blockRects[0].y = 192
blockRects[1].x, blockRects[1].y = 16, 192
blockRects[2].x, blockRects[2].y = 32, 192
blockRects[3].x, blockRects[3].y = 48, 160
blockRects[4].x, blockRects[4].y = 64, 192
blockRects[5].x, blockRects[5].y = 80, 192
blockRects[6].x, blockRects[6].y = 96, 192

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    if pygame.key.get_pressed():
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            speed[0] = 1
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            speed[0] = -1
        if (not pygame.key.get_pressed()[pygame.K_RIGHT]) and (not pygame.key.get_pressed()[pygame.K_LEFT]):
            speed[0] = 0
        
        if pygame.key.get_pressed()[pygame.K_z] and playerRect.collideobjectsall(blockRects):
            playerStates[0] = True
    
    if not playerRect.collideobjectsall(blockRects):
        speed[1] = 3
    else:
        speed[1] = 0
    
    if playerStates[0] and playerStates[1] < 25:
        speed[1] = -2.2

        playerStates[1] = playerStates[1] + 1
    else:
        playerStates[0] = False
        playerStates[1] = 0
    
    playerRect = playerRect.move(speed)

    screen.fill(black)
    screen.blit(player, playerRect)

    for k, v in enumerate(blockRects):
        screen.blit(blockGFXs[0], blockRects[k])
    pygame.display.flip()
    clock.tick(60)