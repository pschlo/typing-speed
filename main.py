import pygame as pg
import time
import sys

pg.init()
WIN = pg.display.set_mode((1200, 640))
FONT_LARGE = pg.font.SysFont('monospace', 32, bold=False)
FONT_SMALL = pg.font.SysFont('monospace', 18)

exercise_text = r'Returns the dimensions needed to render the text. This can be used to help determine the positioning needed for text before it is rendered. It can also be used for wordwrapping and other layout effects.'


class TextBox:
    def __init__(self, exercise_text):
        self.COLOR_TEXT_NORMAL = pg.Color('black')
        self.COLOR_TEXT_ACTIVE = pg.Color('green4')
        self.COLOR_TEXT_MISTYPED = pg.Color('red')
        self.COLOR_RECT = pg.Color('black')
        self.PADDING_X = 40
        self.PADDING_Y = 5
        self.CPM_COOLDOWN = 1
        
        # LEN_TEXT_DISPLAYED must be odd so that the cursor letter is always in the middle
        self.LEN_TEXT_DISPLAYED = 41
        assert self.LEN_TEXT_DISPLAYED % 2 == 1
        
        SIZE_TEXT = FONT_LARGE.size('a'*self.LEN_TEXT_DISPLAYED)
        RECT_WIDTH = SIZE_TEXT[0] + 2*self.PADDING_X
        RECT_HEIGHT = SIZE_TEXT[1] + 2*self.PADDING_Y
        WIN_WIDTH, WIN_HEIGHT = WIN.get_size()
        
        self.RECT = pg.Rect(
            int((WIN_WIDTH-RECT_WIDTH)/2),
            int((WIN_HEIGHT-RECT_HEIGHT)/2)-50,
            RECT_WIDTH,
            RECT_HEIGHT
        )
        
        self.EXERCISE_TEXT = exercise_text
        
        self.text = r'Press <Space> to start'
        self.list_surf_text = []
        self.cursor = 0
        self.errors = 0
        self.cpm = None
        self.is_mistyped = False
        self.has_started = False
        self.time_start = None
        self.last_cpm_refresh = 0
        
        
    def update(self, events):

        if self.has_started and time.time() - self.last_cpm_refresh > self.CPM_COOLDOWN:
            self.last_cpm_refresh = time.time()
            # calculate clicks per minute
            delta_t = time.time() - self.time_start
            self.cpm = int( self.cursor / (delta_t/60) )

        print("get_mods =", pg.key.get_mods())
        print("self.is_mistyped", self.is_mistyped)
            
        for event in events:
            if event.type == pg.KEYDOWN:
                if not self.has_started:
                    if event.key == pg.K_SPACE:
                        # start exercise
                        self.has_started = True
                        self.text = self.EXERCISE_TEXT
                        self.time_start = time.time()
                else:   
                    if event.unicode == self.text[self.cursor]:
                        # correct key
                        if self.cursor == len(self.EXERCISE_TEXT) - 1:
                            self.text = 'Exercise finished'
                            self.has_started = False
                        self.cursor += 1
                        self.is_mistyped = False
                    elif not (pg.key.get_mods() or event.unicode == '' or self.is_mistyped):
                        # mistyped
                        self.is_mistyped = True
                        self.errors += 1
        
        
        if self.has_started:
            self.list_surf_text = self.seperate_text()
        else:
            self.list_surf_text = [
                FONT_LARGE.render(self.text, True, self.COLOR_TEXT_NORMAL)
            ]
            
    
    def seperate_text(self):
        list_surf_text = []
        
        ### LEFT TEXT SURFACE
        # index_left_left describes the index of the most left char of the left side text
        # Right at the beginning, that index would be negative, since index 0 is in the center
        
        index_left_left_theoretical = self.cursor - int(self.LEN_TEXT_DISPLAYED/2)
        # if too far at the beginning, add placeholder spaces to the text
        spaces = ' ' * max(0, -index_left_left_theoretical)
        
        index_left_left = max(0, index_left_left_theoretical)
        index_left_right = self.cursor - 1
        list_surf_text.append(
            FONT_LARGE.render(spaces + self.text[index_left_left:index_left_right+1], True, self.COLOR_TEXT_NORMAL)
        )
        
        ### CENTER TEXT SURFACE
        FONT_LARGE.set_underline(True)
        list_surf_text.append(
            FONT_LARGE.render(self.text[self.cursor], True, self.COLOR_TEXT_ACTIVE if not self.is_mistyped else self.COLOR_TEXT_MISTYPED)
        )
        FONT_LARGE.set_underline(False)
        
        ### RIGHT TEXT SURFACE
        index_right_left = self.cursor+1
        index_right_right = self.cursor+int(self.LEN_TEXT_DISPLAYED/2)
        list_surf_text.append(
            FONT_LARGE.render(self.text[index_right_left:index_right_right+1], True, self.COLOR_TEXT_NORMAL)
        )
        
        return list_surf_text
    
    
    def draw(self, surf):
        # draw all surfaces from list_surf_text one after another
        width = self.PADDING_X
        for surf_text in self.list_surf_text:
            surf.blit(surf_text, (self.RECT.x+width, self.RECT.y+self.PADDING_Y))
            width += surf_text.get_width()
        pg.draw.rect(surf, self.COLOR_RECT, self.RECT, 2)


def main():
    clock = pg.time.Clock()
    textbox = TextBox(exercise_text)
    
    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
        
        textbox.update(events)
        WIN.fill(pg.Color('white'))
        textbox.draw(WIN)
        
        WIN.blit(FONT_SMALL.render('Errors: %d' % textbox.errors, True, textbox.COLOR_TEXT_NORMAL), (textbox.RECT.x, textbox.RECT.bottom+50))
        WIN.blit(FONT_SMALL.render('Cpm: %s' % textbox.cpm, True, textbox.COLOR_TEXT_NORMAL), (textbox.RECT.x + 160, textbox.RECT.bottom+50))
        
        pg.display.update()
        
        clock.tick(60)

if __name__ == '__main__':
    main()
