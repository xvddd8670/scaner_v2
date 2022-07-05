import pygame
import pygame_gui



class Button:
    def __init__(self, coord_x, coord_y, btn_width, btn_height, btn_text, manager):
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.btn_width = btn_width
        self.btn_height = btn_height
        self.btn_text = btn_text
        ##
        self.button_rectangle = pygame.Rect((self.coord_x, self.coord_y), (self.btn_width, self.btn_height))
        self.button = pygame_gui.elements.UIButton(
            relative_rect=self.button_rectangle,
            text=self.btn_text,
            manager=manager)
        self.hide_show = True
