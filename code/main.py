from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import *

class Game:
    def __init__(self):
        pygame.init()
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Super Steve')
        self.clock = pygame.time.Clock()
        self.import_assets()
        
        self.tmx_maps = {0: load_pygame(join('.', 'data', 'levels', 'omni.tmx'))}        
        self.current_stage = Level(self.tmx_maps[0], self.level_frames)

    def import_assets(self):
        self.level_frames = {
            'floor spike': import_folder('.', 'graphics', 'enemies', 'floor_spikes'),
            'torch': import_folder('.', 'graphics', 'level', 'torch'),
            'torch_light': import_folder('.', 'graphics', 'level', 'torch_light'),
            'player': import_sub_folders('.', 'graphics', 'player'),
            'spike trap': import_image('.', 'graphics', 'enemies', 'spike_trap', 'trap'),
            'zombie': import_folder('.', 'graphics', 'enemies', 'zombie'),
            'shell': import_sub_folders('.', 'graphics', 'enemies', 'shell'),
            'pearl': import_image('.', 'graphics', 'enemies', 'bullets', 'pearl'),
            'items': import_sub_folders('.', 'graphics', 'items'),
            'particle': import_folder('.', 'graphics', 'effects', 'particle'),
            
        }
        # print(self.level_frames)
        
    def run(self):
        while True:
            delta_time = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.current_stage.run(delta_time)
                    
            pygame.display.update()

if __name__ =='__main__':            
    game = Game()
    game.run()
    