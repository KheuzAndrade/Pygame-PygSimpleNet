import pygame
from pygame.locals import *
from PygameNetworking import ClientManager

# Constantes
WINDOW_SIZE = (640,480)
WINDOW_TITLE = "Multiplayer Tutorial"

FPS = 60

CLIENT = ClientManager(
    host = "localhost",
    port = 12750
)

#-----------

class Player(pygame.sprite.Sprite):
    def __init__(self, group, x=0, y=0):
        super().__init__(group)
        self.image = pygame.Surface((32,32))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.position = pygame.math.Vector2(x, y)
        self.speed = 2

    def update(self):
        self.rect.x = self.position.x
        self.rect.y = self.position.y

        pressed = pygame.key.get_pressed()

        if pressed[K_w]:
            self.position.y -= self.speed
        elif pressed[K_s]:
            self.position.y += self.speed
        if pressed[K_a]:
            self.position.x -= self.speed
        elif pressed[K_d]:
            self.position.x += self.speed

class GameApp():
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.work = True

        self.group = pygame.sprite.Group()
        self.player = Player(self.group, (WINDOW_SIZE[0]/2)-16, (WINDOW_SIZE[1]/2)-16)

        self.run()

    def draw_players(self):
        for player in CLIENT.players:
            try:
                img = pygame.Surface((32,32))
                img.fill((255,0,0))
                self.display.blit(img, [CLIENT.players[player]["Dict"]["position"][0], CLIENT.players[player]["Dict"]["position"][1]])
            except:
                pass

    def run(self):
        CLIENT.connect()
        while self.work:
            self.clock.tick(FPS)

            CLIENT.send_dict["position"] = [self.player.rect.x, self.player.rect.y]
            CLIENT.receive_data()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.work = False

            self.display.fill([0,0,0])

            self.group.update()
            self.group.draw(self.display)
            self.draw_players()

            pygame.display.update()

GameApp()
