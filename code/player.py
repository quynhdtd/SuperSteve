from settings import *
from timer import Timer
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_colli_sprites, frames):
        # general setup
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        
        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]
        
        
        # rects
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-152, -72)
        self.old_rect = self.hitbox_rect.copy()
        
        # movement
        self.direction = vector(0,0)
        self.speed = 300
        self.gravity = 1350
        self.jump = False
        self.jump_height = 630
        self.attacking = False
        
        # collision
        self.collision_sprites = collision_sprites
        self.semi_colli_sprites = semi_colli_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}
        self.platform = None
        
        # timer
        self.timers = {
            'platform skip': Timer(100),
            'attack block': Timer(500)
        }
        
    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0,0)
        
        if keys[pygame.K_RIGHT]:
            input_vector.x += 1
            self.facing_right = True
        
        if keys[pygame.K_LEFT]:
            input_vector.x -= 1     
            self.facing_right = False
        self.direction.x = input_vector.normalize().x if input_vector.x else input_vector.x
        
        if keys[pygame.K_DOWN]:
            self.timers['platform skip'].activate()
        
        if keys[pygame.K_x]:
            self.jump = True
            
        if keys[pygame.K_z]:
            self.attack()
    
    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()
        
    def move(self, dt):
        # horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        
        # vertical
        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                self.hitbox_rect.bottom -= 1
            self.jump = False
            
        self.direction.y += self.gravity / 2 * dt
        self.hitbox_rect.y += self.direction.y * dt
        self.direction.y += self.gravity / 2 * dt
        
           
        self.collision('vertical')
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center
       
    def platform_move(self, dt):
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt
            
    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width, 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_colli_rects = [sprite.rect for sprite in self.semi_colli_sprites]
        
        # collision
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_colli_rects) >=0 and self.direction.y >= 0 else False 
        
        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_colli_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite
        
    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    # left
                    
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    
                    # right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                    
                else:
                    # top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'):
                            self.hitbox_rect.top += 6
                        
                    # bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top 

                    self.direction.y = 0
    
    def semi_collision(self):
        if not self.timers['platform skip'].active:
            for sprite in self.semi_colli_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0
                      
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
            
    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames[self.state]):
            self.state = 'idle'
            
            
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False
            
    def get_state(self):
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'attack'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.attacking:
                self.state = 'air_attack'
            else:
                self.state = 'jump' if self.direction.y <0 else 'fall'
    
    def get_damage(self):
        print('player dam')
    
    def update(self, dt):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        
        self.input()
        self.move(dt)
        
        self.check_contact()
        self.platform_move(dt)
        
        self.get_state()
        self.animate(dt)
        