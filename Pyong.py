import pygame
import sys
import time
from debug import debug


class Shield(pygame.sprite.Sprite):
    def __init__(self, groups, pos, bot):
        super().__init__(groups)
        self.image = pygame.Surface((10, 80))
        self.image.fill("white")
        # Player pos = (980, 300)
        self.rect = self.image.get_rect(topleft=(pos))
        self.old_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2()
        self.speed = 400
        self.bot = bot

    def screen_colission(self):
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.y
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.pos.y = self.rect.y
    
    def input(self):
        keys = pygame.key.get_pressed()
        if self.bot == False:
            if keys[pygame.K_w]:
                self.direction.y = -1
            elif keys[pygame.K_s]:
                self.direction.y = 1
            else:
                self.direction.y = 0
        else:
            if keys[pygame.K_i]:
                self.direction.y = -1
            elif keys[pygame.K_k]:
                self.direction.y = 1
            else:
                self.direction.y = 0

    def update(self, dt):
        self.old_rect = self.rect.copy()
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.input()

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.screen_colission()


class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, colsprite, player, enemy):
        super().__init__(groups)
        self.image = pygame.Surface((20, 20))
        self.image.fill("white")
        self.rect = self.image.get_rect(center=(512, 300))
        self.old_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(1,1)
        self.speed = 400
        self.colsprite = colsprite
        self.player = player
        self.enemy = enemy

    def colission(self, direction):
        colission_sprites = pygame.sprite.spritecollide(self, self.colsprite, False)
        if self.rect.colliderect(self.player.rect):
            colission_sprites.append(self.player)
        if self.rect.colliderect(self.enemy.rect):
            colission_sprites.append(self.enemy)
        
        if colission_sprites:
            if direction == "horizontal":
                for sprite in colission_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.speed += 10
                        
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.speed += 10
            
            if direction == "vertical":
                for sprite in colission_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.speed += 10
                        
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.speed += 10
    
    def screen_colission(self, direction):
        if direction == "horizontal":
            if self.rect.right > 1024:
                self.rect.center = (512,300)
                self.pos = self.rect
                self.direction.x *= -1
                self.speed = 400
            if self.rect.left < 0:
                self.rect.center = (512,300)
                self.pos = self.rect
                self.direction.x *= -1
                self.speed = 400
        if direction == "vertical":
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direction.y *= -1
                self.speed += 20
            if self.rect.bottom > 600:
                self.rect.bottom = 600
                self.pos.y = self.rect.y
                self.direction.y *= -1
                self.speed += 20
    
    def update(self,dt):
        self.old_rect = self.rect.copy()
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.colission("horizontal")
        self.colission("vertical")
        self.screen_colission("horizontal")
        self.screen_colission("vertical")

class Game:
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = 1024
        self.WINDOW_HEIGHT = 600
        self.FRAMERATE = 60
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Pyong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.font_big = pygame.font.Font(None, 150)
        
        self.main_menu = True
        self.debug = False
        
        self.all_sprites = pygame.sprite.Group()
        self.colission_sprites = pygame.sprite.Group()
        
        self.line = pygame.Surface((5,600))
        self.line.fill("white")
        self.player = Shield(self.all_sprites, (self.WINDOW_WIDTH - 30,280), False)
        self.player1 = Shield(self.all_sprites, (self.WINDOW_WIDTH / 42,280), True)
        self.ball = Ball(self.all_sprites, self.colission_sprites, self.player, self.player1)
        
        self.playerscore = 0
        self.enemyscore = 0
        self.delay = 0
    
    def text_maker(self, font, text, color, xy):
        text_surf = font.render(str(text), True, color)
        text_rect = text_surf.get_rect(midtop = xy)
        self.screen.blit(text_surf, text_rect)
    
    def score_system(self, dt):
        self.delay -= 1 * dt
        if self.delay <= 0:
            if self.ball.rect.right >= 1010:
                self.enemyscore += 1
                self.delay = 1
            if self.ball.rect.left <= 14:
                self.playerscore += 1
                self.delay = 1
        
        self.text_maker(self.font, self.playerscore, "white", (self.WINDOW_WIDTH / 1.315, 50))
        self.text_maker(self.font, self.enemyscore, "white", (self.WINDOW_WIDTH / 4, 50))
    
    def run(self):
        last_time = time.time()
        while True:
            dt = time.time() - last_time
            last_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_7:
                        if self.debug == False:
                            self.debug = True
                        else:
                            self.debug = False
                    if self.main_menu:
                        if event.key == pygame.K_SPACE:
                            self.main_menu = False
            
            self.screen.fill("black")
            
            if self.main_menu:
                self.text_maker(self.font_big, "Py  ng", "white", (self.WINDOW_WIDTH / 2, 50))
                pygame.draw.circle(self.screen, "white", (self.WINDOW_WIDTH / 2 - 4, 105), 30)
                self.text_maker(self.font, "Tekan Space untuk memulai gamenya", "white", (self.WINDOW_WIDTH / 2, 450))
            else:
                self.screen.blit(self.line, (512,0))
                
                self.score_system(dt)
                
                self.all_sprites.update(dt)
                self.all_sprites.draw(self.screen)
            
            if self.debug:
                debug(f"{self.clock}")
            
            pygame.display.update()
            self.clock.tick(self.FRAMERATE)

if __name__ == "__main__":
    game = Game()
    game.run()