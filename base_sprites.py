from init import *
# модуль с важными классами спрайтов


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, x, y, sheet, columns, rows, framerate, *aux_groups):
        super().__init__(all_sprites, *aux_groups)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.framerate = framerate
        self.iteration = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pg.Rect(frame_location, self.rect.size)))

    def update(self):
        self.iteration += 1
        if self.iteration % (FPS // self.framerate) == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        if self.tile_type != 'empty':
            collidable_group.add(self)
        if self.tile_type == 'bricks':
            breakable_group.add(self)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def kill(self):
        super().kill()
        breaking_sound.play()
        if self.tile_type == 'bricks':
            Tile('empty', self.rect.x // tile_width, self.rect.y // tile_height)
