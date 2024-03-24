from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((84, 116))
        self.image.fill('red')
        
        # rects
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()
        
        # movement
        self.direction = vector(0,0)
        self.speed = 200
        self.gravity = 1300
        self.jump = False
        self.jump_height = 900
        
        # collision
        self.collision_sprites = collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}
        
    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0,0)
        
        if keys[pygame.K_RIGHT]:
            input_vector.x += 1
        if keys[pygame.K_LEFT]:
            input_vector.x -= 1     
        self.direction.x = input_vector.normalize().x if input_vector.x else input_vector.x

        if keys[pygame.K_SPACE]:
            self.jump = True
            
    def move(self, dt):
        # horizontal
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        
        # vertical
        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
            self.jump = False
            
        self.direction.y += self.gravity / 2 * dt
        self.rect.y += self.direction.y * dt
        self.direction.y += self.gravity / 2 * dt
        
           
        self.collision('vertical')
       
    
    def check_contact(self):
        floor_rect = pygame.Rect(self.rect.bottomleft,(self.rect.width, 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        
        # collision
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 else False 
        
    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == 'horizontal':
                    # left
                    
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                    
                    # right
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                    
                else:
                    # top
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        
                    # bottom
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top 

                    self.direction.y = 0
    
    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.input()
        self.move(dt)
        self.check_contact()