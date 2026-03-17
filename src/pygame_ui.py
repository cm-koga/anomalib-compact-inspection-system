import pygame

class Button:
    def __init__(self,
                 rect,
                 text,
                 callback,
                 args=None,
                 font_size=12,
                 bg_color=[0x19, 0x76, 0xd2],
                 bg_hover_color=[0x15, 0x65, 0xc0],
                 bg_clicked_color=[0x0d, 0x47, 0xa1],
        ):
        self.font_size = font_size
        self.font = pygame.font.SysFont(None, font_size)
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.args = args
        self.bg_color = bg_color
        self.bg_hover_color = bg_hover_color
        self.bg_clicked_color = bg_clicked_color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed[0]:
                color = self.bg_clicked_color
            else:
                color = self.bg_hover_color
        else:
            color = self.bg_color

        pygame.draw.rect(screen, color, self.rect)

        screen.blit(self._render_text, self._text_rect)

    @property
    def text(self):
        return self.___text
    
    @text.setter
    def text(self, value):
        self.__text = value

        self._render_text = self.font.render(self.__text, True, (255, 255, 255))
        self._text_rect = self._render_text.get_rect(center=self.rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback is not None:
                    self.callback(self.args)
