from init import *
from base_sprites import AnimatedSprite
# модуль с классами эффектов


class Explosion(AnimatedSprite):
    def __init__(self, center):
        super().__init__(0, 0, explosion_sheet, 11, 1, 20, top_layer_group, effects_group)
        self.rect.center = center

    def update(self):
        super().update()
        if self.iteration == len(self.frames) * (FPS // self.framerate):
            self.kill()  # при конце анимации умирает


class SmallExplosion(AnimatedSprite):
    def __init__(self, center):
        super().__init__(0, 0, small_explosion_sheet, 8, 1, 20, top_layer_group, effects_group)
        self.rect.center = center

    def update(self):
        super().update()
        if self.iteration == len(self.frames) * (FPS // self.framerate):
            self.kill()  # при конце анимации умирает


class SpawningEffect(AnimatedSprite):
    def __init__(self, coords, duration):
        super().__init__(coords[0], coords[1], spawning_eff_sheet, 2, 1, 4,
                         top_layer_group, effects_group, collidable_group)
        self.duration = duration

    def update(self):
        super().update()
        if self.iteration == int(self.duration / 1000 * FPS):
            self.kill()
