import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.play_button = self.font.render("play", True, (255, 255, 255))
        self.exit_button = self.font.render("exit", True, (255, 255, 255))
        self.restart_button = self.font.render("restart", True, (255, 255, 255))
        self.game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        self.menu_rect = pygame.Rect(400, 200, 480, 300)


    def show_main_menu(self):
        self._show_menu("main")

    def show_game_over_menu(self):
        self._show_menu("game_over")


    def _show_menu(self, menu_type):
        self.screen.fill((0, 0, 0))

        # overlay transparency for menu
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0,)) # semi-transparent black
        overlay.set_alpha(170) # transparency level
        self.screen.blit(overlay, (0, 0))

        # dray rect for menu
        pygame.draw.rect(self.screen, (50, 50, 50), self.menu_rect)

        # draw buttons
        buttons = [self.play_button, self.exit_button] if menu_type == "main" else [self.restart_button, self.exit_button]
        button_rects = []
        for i, button in enumerate(buttons):
            button_rect = button.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 100 + i * 80))
            button_rects.append(button_rect)
            self.screen.blit(button, button_rect)

        # highlight effect on hover for buttons
        mouse_pos = pygame.mouse.get_pos()
        for button_rect in button_rects:
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), button_rect.inflate(20, 20), border_radius=5) # highlight
                break
        
        pygame.display.flip()


        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, button_rect in enumerate(button_rects):
                        if button_rect.collidepoint(mouse_pos):
                            if menu_type == "main":
                                if i == 0:
                                    waiting = False # play button
                                elif i == 1:
                                    pygame.quit()
                                    exit() # exit button
                            else: # game over menu
                                if i == 0:
                                    waiting = False # restart button
                                elif i == 1:
                                    pygame.quit()
                                    exit()

        # draw menu (with hover effect, redrawn on frame refresh)
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0,))
        overlay.set_alpha(170) # transparency again
        self.screen.blit(overlay, (0, 0))


        # draw rect for menu
        pygame.draw.rect(self.screen, (50, 50, 50), self.menu_rect)

        # button prep
        buttons = [self.play_button, self.exit_button] if menu_type == "main" else [self.game_over_text, self.restart_button, self.exit_button]
        button_rects = []

        if menu_type == "game_over":
            text_rect = self.game_over_text.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 60))
            self.screen.blit(self.game_over_text, text_rect)
            # button offset for game over text
            for i, button in enumerate(buttons[1:]):
                button_rect = button.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 140 + i * 80))
                button_rects.append(button_rect)
                self.screen.blit(button, button_rect)
            else:
                for i, button in enumerate(buttons):
                    button_rect = button.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 100 + i * 80))
                    button_rects.append(button_rect)
                    self.screen.blit(button, button_rect)

            # highlight effect on hover for buttons
            mouse_pos = pygame.mouse.get_pos()
            for button_rect in button_rects:
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (100, 100, 100), button_rect.inflate(20, 20), border_radius=5) # highlight
            

            # draw button text
            if menu_type == "game_over":
                for i, button in enumerate([self.restart_button, self.exit_button]):
                    self.screen.blit(button, button_rects[i])
            else:
                for i, button in enumerate(buttons):
                    self.screen.blit(button, button_rects[i])

            pygame.display.flip()
            pygame.time.Clock().tick(60) # limit menu to 60 FPS