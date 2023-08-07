import pygame as pg
import time
import sys
import math
from abc import ABC, abstractmethod

pg.init()

class Score:
    errors: int
    chars_per_minute: int




class SceneManager:
    pass


class Scene(ABC):
    manager: SceneManager

    def __init__(self, manager:SceneManager) -> None:
        self.manager = manager

    @abstractmethod
    def render(self, screen:pg.Surface) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def handle_events(self, events:list[pg.event.Event]) -> None:
        raise NotImplementedError


class IngameScene(Scene):
    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)




class A(pg.surface.Surface):
    def __init__(self, size: tuple[int,int]):
        super().__init__(size)




class GameOptions:
    def __init__(
        self,
        COLOR_TEXT_NORMAL: pg.Color = pg.Color('black'),
        COLOR_TEXT_ACTIVE: pg.Color = pg.Color('green4'),
        COLOR_TEXT_MISTYPED: pg.Color = pg.Color('red'),
        COLOR_RECT: pg.Color = pg.Color('black'),

        PADDING_X: int = 40,
        PADDING_Y: int = 5,
        CPM_COOLDOWN: int = 1,

        LEN_TEXT_DISPLAYED: int = 41,
        FONT_LARGE: pg.font.Font = pg.font.SysFont('monospace', 32, bold=False),
        FONT_SMALL: pg.font.Font = pg.font.SysFont('monospace', 18),
    ) -> None:
        self.COLOR_TEXT_NORMAL = COLOR_TEXT_NORMAL
        self.COLOR_TEXT_ACTIVE = COLOR_TEXT_ACTIVE
        self.COLOR_TEXT_MISTYPED = COLOR_TEXT_MISTYPED
        self.COLOR_RECT = COLOR_RECT

        self.PADDING_X = PADDING_X
        self.PADDING_Y = PADDING_Y
        self.CPM_COOLDOWN = CPM_COOLDOWN

        # LEN_TEXT_DISPLAYED must be odd so that the cursor letter is always in the middle
        self.LEN_TEXT_DISPLAYED = LEN_TEXT_DISPLAYED
        assert self.LEN_TEXT_DISPLAYED % 2 == 1

        self.FONT_LARGE = FONT_LARGE
        self.FONT_SMALL = FONT_SMALL



class TextSurface:
    parts: tuple[pg.Surface]

    def __init__(self, *parts: pg.Surface) -> None:
        self.parts = parts

    def draw(self, surface: pg.Surface, dest: tuple[int,int]):
        x = dest[0]
        y = dest[1]
        for part in self.parts:
            surface.blit(part, (x,y))
            x += part.get_width()


# represents a rectangle that contains text
class TextBox:
    text: str
    rect: pg.Rect
    options: GameOptions

    def __init__(self, text:str, rect:pg.Rect, options:GameOptions) -> None:
        self.text = ' ' * options.LEN_TEXT_DISPLAYED + text
        self.cursor = options.LEN_TEXT_DISPLAYED + 1
        self.rect = rect
        self.options = options

    def draw(self, on_surface:pg.Surface, from_surface:TextSurface) -> None:
        # draw rectange
        pg.draw.rect(on_surface, self.options.COLOR_RECT, self.rect, 2)
        # draw text
        dest = (self.rect.x + self.options.PADDING_X, self.rect.y + self.options.PADDING_Y)
        from_surface.draw(on_surface, dest)

    def render_normal(self, text:str) -> TextSurface:
        surface = self.options.FONT_LARGE.render(text, True, self.options.COLOR_TEXT_NORMAL)
        return TextSurface(surface)

    def render_exercise(self, cursor:int) -> TextSurface:
        surfaces: list[pg.Surface] = []

        # parse left part
        length = math.floor((self.options.LEN_TEXT_DISPLAYED + 1) / 2) - 1
        index_left = cursor - length
        index_right = cursor - 1

        # 4: length = floor((4+1)/2) - 1 = floor(2.5) - 1 = 2-1 = 1
        # 5: length = floor((5+1)/2) - 1 = floor(3) - 1 = 3-1 = 2
        # 6: length = floor((6+1)/2) - 1 = floor(3.5) - 1 = 3-1 = 2
        surface = self.options.FONT_LARGE.render(self.text[index_left : index_right+1], True, self.options.COLOR_TEXT_NORMAL)
        surfaces.append(surface)

        # parse center part

        surface = self.options.FONT_LARGE.render(self.text[cursor], True, self.options.COLOR_TEXT_NORMAL)
        surfaces.append(surface)


        # parse right part
        length = math.floor((self.options.LEN_TEXT_DISPLAYED + 1) / 2)
        index_left = cursor + 1
        index_right = cursor + length

        surface = self.options.FONT_LARGE.render(self.text[index_left : index_right+1], True, self.options.COLOR_TEXT_NORMAL)
        surfaces.append(surface)

        # 4: length = floor((4+1)/2) = floor(2.5) = 2
        # 5: length = floor((5+1)/2) = floor(3) = 3
        # 6: length = floor((6+1)/2) = floor(3.5) = 3

        return TextSurface(*surfaces)





class Game:

    options: GameOptions
    text_exercise: str
    clock: pg.time.Clock

    TEXT_START = r'Press <Space> to start'
    TEXT_FINISH = 'Exercise finished'

    time_start: float
    cursor = 0
    errors = 0
    chars_per_minute: int = 0
    is_mistyped: bool = False
    has_started: bool = False
    last_cpm_refresh = 0


    def __init__(self, text:str, screen:pg.Surface, options:GameOptions):
        self.options = options
        self.text_exercise = text
        self.screen = screen

        self.clock = pg.time.Clock()
        
        # the rectange where the text should appear

        SIZE_TEXT = self.options.FONT_LARGE.size('a'*self.options.LEN_TEXT_DISPLAYED)
        RECT_WIDTH = SIZE_TEXT[0] + 2*self.options.PADDING_X
        RECT_HEIGHT = SIZE_TEXT[1] + 2*self.options.PADDING_Y

        WIN_WIDTH, WIN_HEIGHT = screen.get_size()

        rect = pg.Rect(
            int((WIN_WIDTH-RECT_WIDTH)/2),          # horizonal axis: centered
            int((WIN_HEIGHT-RECT_HEIGHT)/2)-50,     # vertical axis: little bit above center
            RECT_WIDTH,
            RECT_HEIGHT
        )

        self.textbox = TextBox(self.text_exercise, rect, options)
    

    def start(self):
        ## event loop
        while True:
            self.screen.fill(pg.Color('white'))
            self.update()
            
            #self.screen.blit(self.options.FONT_SMALL.render('Errors: %d' % self.errors, True, self.options.COLOR_TEXT_NORMAL), (self.rect.x, game.RECT.bottom+50))
            #self.screen.blit(self.options.FONT_SMALL.render('Characters per minute: %s' % self.chars_per_minute, True, game.options.COLOR_TEXT_NORMAL), (game.RECT.x + 160, game.RECT.bottom+50))
            
            pg.display.flip()
            self.clock.tick(60)
        

    def update(self):
        def is_quit(event: pg.event.Event):
            return event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
        
        def is_start(event: pg.event.Event):
            return (not self.has_started) and event.type == pg.KEYDOWN and event.key == pg.K_SPACE
        
        def is_char(event: pg.event.Event):
            return self.has_started and event.type == pg.KEYDOWN and event.unicode != ""

        for event in pg.event.get():
            if is_quit(event):
                pg.quit()
                sys.exit()
            elif is_start(event):
                self.start_exercise()
            elif is_char(event):
                self.handle_char_key(event.unicode)

        # refresh chars_per_minute
        if self.has_started and time.time() - self.last_cpm_refresh > self.options.CPM_COOLDOWN:
            self.last_cpm_refresh = time.time()
            # calculate chars per minute
            delta_t = time.time() - self.time_start
            self.chars_per_minute = 0 if delta_t == 0 else int( self.cursor / (delta_t/60) )

        #print("get_mods", pg.key.get_mods() & pg.KMOD_NUM)
        #print("self.is_mistyped", self.is_mistyped)
            
        
        if self.has_started:
            surface = self.textbox.render_exercise(self.cursor) 
        else:
            surface = self.textbox.render_normal(self.TEXT_START)
        self.textbox.draw(self.screen, surface)


    def handle_char_key(self, char: str):
        if char == self.text_exercise[self.cursor]:
            # correct key
            if self.cursor == len(self.text_exercise) - 1:
                self.textbox.render_normal(self.TEXT_FINISH)
                self.has_started = False
            self.cursor += 1
            self.is_mistyped = False
        else:
            # mistyped
            self.is_mistyped = True
            self.errors += 1

    def start_exercise(self):
        self.has_started = True
        self.text_exercise = self.text_exercise
        self.time_start = time.time()
    


def main():
    exercise_text = r'Returns the dimensions needed to render the text. This can be used to help determine the positioning needed for text before it is rendered. It can also be used for wordwrapping and other layout effects.'

    options = GameOptions()
    screen = pg.display.set_mode((1200, 640))
    game = Game(exercise_text, screen, options)
    game.start()

if __name__ == '__main__':
    main()
