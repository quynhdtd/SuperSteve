from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite
from player import Player
from groups import AllSprites

class Level:
    def __init__(self, tmx_map, level_frames):
        self.display_surf = pygame.display.get_surface()
        
        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_colli_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.setup(tmx_map, level_frames)
    
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
                    if obj.name == 'floor_spike': groups.append(self.damage_sprites)
                    
                    # z index
                    z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']
                    
                    
                    AnimatedSprite((obj.x, obj.y), frames, groups, z)
        # moving objects
        for obj in tmx_map.get_layer_by_name('Moving Objects'):
            if obj.name == 'helicopter':
                if obj.width > obj.height:  # horizontal
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height/2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height/2)
                    
                else:   # vertical
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width/2, obj.y)
                    end_pos = (obj.x + obj.width/2, obj.y + obj.height)
                    
                speed = obj.properties['speed']
                MovingSprite((self.all_sprites, self.semi_colli_sprites), start_pos, end_pos, move_dir, speed)
        
        
    def run(self, dt):
        self.all_sprites.update(dt)
        self.display_surf.fill('black')
        self.all_sprites.draw(self.player.hitbox_rect.center)