from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Zombie, Shell, Pearl

class Level:
    def __init__(self, tmx_map, level_frames):
        self.display_surf = pygame.display.get_surface()
        
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_colli_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.zombie_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        
        
        self.setup(tmx_map, level_frames)
        
        # frames
        self.pearl_surf = level_frames['pearl']
        self.particle_frames = level_frames['particle']
        
    def setup(self, tmx_map, level_frames):
        # tiles
        for layer in ['BG', 'Terrain', 'Platforms']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'Terrain': groups.append(self.collision_sprites)
                if layer == 'Platforms': groups.append(self.semi_colli_sprites)
                
                match layer:
                    case 'BG': z = Z_LAYERS['bg tiles']
                    case _: z = Z_LAYERS['main']
                Sprite((x*TILE_SIZE, y*TILE_SIZE), surf, groups, z)
        
        # bg details
        for obj in tmx_map.get_layer_by_name('BG Details'):
            if obj.name == 'static':
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z=Z_LAYERS['bg tiles'])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, Z_LAYERS['bg tiles'])
                if obj.name == 'torch':
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames['torch_light'], self.all_sprites, Z_LAYERS['bg tiles'])
        
        # objects    
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'player':
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    groups = self.all_sprites, 
                    collision_sprites = self.collision_sprites, 
                    semi_colli_sprites = self.semi_colli_sprites,
                    frames = level_frames['player'])
            else:
                if obj.name in ('barrel', 'crate'):
                    Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
                else:
                    # frames
                    # if obj.name in ('floor_spike'):
                    #     frames =  level_frames[obj.name] 
                    
                    frames =  level_frames[obj.name] 
                    # groups
                    groups = [self.all_sprites]
                    if obj.name == 'floor spike': groups.append(self.damage_sprites)
                    
                    # z index
                    z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']
                    
                    
                    AnimatedSprite((obj.x, obj.y), frames, groups, z)
        
        # moving objects
        for obj in tmx_map.get_layer_by_name('Moving Objects'):
            frames = level_frames[obj.name]
            groups = (self.all_sprites, self.semi_colli_sprites, self.damage_sprites)
            
            if obj.width > obj.height:  # horizontal
                move_dir = 'x'
                start_pos = (obj.x, obj.y + obj.height/2)
                end_pos = (obj.x + obj.width, obj.y + obj.height/2)
                
            else:   # vertical
                move_dir = 'y'
                start_pos = (obj.x + obj.width/2, obj.y)
                end_pos = (obj.x + obj.width/2, obj.y + obj.height)
                    
            speed = obj.properties['speed']
            trap = obj.properties['trap']
            MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, trap)
        
        # enemies
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'zombie':
                Zombie((obj.x, obj.y), level_frames['zombie'], (self.all_sprites, self.damage_sprites, self.zombie_sprites), self.collision_sprites)

            if obj.name == 'shell':
                Shell(
                    pos = (obj.x, obj.y), 
                    frames = level_frames['shell'], 
                    groups = (self.all_sprites, self.collision_sprites), 
                    reverse = obj.properties['reverse'], 
                    player = self.player, 
                    create_pearl = self.create_pearl)
        
        # items
        for obj in tmx_map.get_layer_by_name('Items'):
            Item(obj.name, (obj.x + TILE_SIZE/2, obj.y), level_frames['items'][obj.name], (self.all_sprites, self.item_sprites))
        
    def create_pearl(self, pos, direction):
        Pearl(pos, (self.all_sprites, self.damage_sprites, self.pearl_sprites), self.pearl_surf, direction, 150)
    
    def pearl_collision(self):
        for sprite in self.collision_sprites:
            sprite = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True)
            if sprite:
                ParticleEffectSprite((sprite[0].rect.center), self.particle_frames, self.all_sprites)
    
    def hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.get_damage()
                
                if hasattr(sprite, 'pearl'):
                    sprite.kill()
                    ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)
                         
    def item_collision(self):
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                ParticleEffectSprite((item_sprites[0].rect.center), self.particle_frames, self.all_sprites)
                
    def attack_collision(self):
        for target in self.pearl_sprites.sprites() + self.zombie_sprites.sprites():
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
                            
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.reverse()
    
    def run(self, dt):
        self.all_sprites.update(dt)
        self.pearl_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.display_surf.fill('blue')
        
        self.all_sprites.draw(self.player.hitbox_rect.center)