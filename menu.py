import pygame

class Menu:
    def __init__(self, screen, click_sound=None, music_end_event=None, play_next_func=None):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.play_button = self.font.render("Play", True, (255, 255, 255))
        self.exit_button = self.font.render("Exit", True, (255, 255, 255))
        self.resume_button = self.font.render("Resume", True, (255, 255, 255))
        self.restart_button = self.font.render("Restart", True, (255, 255, 255))
        self.game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        self.menu_rect = pygame.Rect(400, 200, 480, 300)
        self.click_sound = click_sound
        self.music_end_event = music_end_event
        self.play_next_func = play_next_func

    def show_initial_menu(self):
        """Show Play/Exit menu at game start"""
        self._show_menu("initial", None)

    def show_pause_menu(self):
        """Show Resume/Exit menu when ESC is pressed"""
        background = self.screen.copy()
        self._show_menu("pause", background)

    def show_game_over_menu(self):
        """Show Restart/Exit menu when game ends"""
        background = self.screen.copy()
        self._show_menu("game_over", background)

    def _show_menu(self, menu_type, background=None):
        
        waiting = True
        clock = pygame.time.Clock()  # Local clock for menu
        while waiting:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif self.music_end_event and event.type == self.music_end_event:
                    # Handle music transitions even while in menu
                    if self.play_next_func:
                        self.play_next_func(loop=True)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Allow ESC to unpause from pause menu
                    if menu_type == "pause":
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Determine buttons based on menu type
                    if menu_type == "initial":
                        buttons = [self.play_button, self.exit_button]
                        y_start = 100
                    elif menu_type == "pause":
                        buttons = [self.resume_button, self.exit_button]
                        y_start = 100
                    else:  # game_over
                        buttons = [self.restart_button, self.exit_button]
                        y_start = 140
                    
                    button_rects = []
                    for i, button in enumerate(buttons):
                        button_rect = button.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + y_start + i * 80))
                        button_rects.append(button_rect)
                    
                    # Check clicks
                    for i, button_rect in enumerate(button_rects):
                        if button_rect.collidepoint(mouse_pos):
                            if self.click_sound:
                                try:
                                    self.click_sound.play()
                                except Exception:
                                    pass
                            if i == 0:  # First button (Play/Resume/Restart)
                                waiting = False
                            elif i == 1:  # Exit button
                                pygame.quit()
                                exit()

            # Draw menu
            if background:
                self.screen.blit(background, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            
            # Overlay transparency
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))

            # Draw menu background
            pygame.draw.rect(self.screen, (50, 50, 50), self.menu_rect)

            # Prepare button positions
            if menu_type == "initial":
                buttons = [self.play_button, self.exit_button]
                y_start = 100
            elif menu_type == "pause":
                buttons = [self.resume_button, self.exit_button]
                y_start = 100
            else:  # game_over
                # Draw game over text
                text_rect = self.game_over_text.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 60))
                self.screen.blit(self.game_over_text, text_rect)
                buttons = [self.restart_button, self.exit_button]
                y_start = 140

            button_rects = []
            for i, button in enumerate(buttons):
                button_rect = button.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + y_start + i * 80))
                button_rects.append(button_rect)

            # Highlight on hover
            mouse_pos = pygame.mouse.get_pos()
            for button_rect in button_rects:
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (100, 100, 100), button_rect.inflate(20, 20), border_radius=5)

            # Draw button text
            for i, button in enumerate(buttons):
                self.screen.blit(button, button_rects[i])

            pygame.display.flip()
            clock.tick(60)  # Use local clock, not creating new one each frame