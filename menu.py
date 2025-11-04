import pygame

class Menu:
    def __init__(self, screen, click_sound=None, music_end_event=None, play_next_func=None):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self.medium_font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)
        self.play_button = self.font.render("Play", True, (255, 255, 255))
        self.exit_button = self.font.render("Exit", True, (255, 255, 255))
        self.resume_button = self.font.render("Resume", True, (255, 255, 255))
        self.restart_button = self.font.render("Restart", True, (255, 255, 255))
        self.settings_button = self.font.render("Settings", True, (255, 255, 255))
        self.back_button = self.font.render("Back", True, (255, 255, 255))
        self.menu_rect = pygame.Rect(400, 200, 480, 300)
        self.game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        self.click_sound = click_sound
        self.music_end_event = music_end_event
        self.play_next_func = play_next_func
        self.selected_resolution = (1280, 720)  # Default resolution
        self.in_settings = False

    def show_initial_menu(self, background=None):
        """Show Play/Exit menu at game start with controls display"""
        return self._show_menu("initial", background)

    def show_pause_menu(self, background=None):
        """Show Resume/Exit menu when ESC is pressed"""
        self._show_menu("pause", background)

    def show_game_over_menu(self, background=None):
        """Show Restart/Exit menu when game ends"""
        self._show_menu("game_over", background)
    
    def show_settings_menu(self, background=None, drawable_objects=None, player=None):
        """Show settings menu with live resolution preview"""
        return self._show_settings(background, drawable_objects, player)
    
    def _show_settings(self, background=None, drawable_objects=None, player=None):
        """Settings menu with live resolution updates"""
        import constants as const
        
        waiting = True
        clock = pygame.time.Clock()
        resolutions = [(1280, 720), (1920, 1080)]
        selected_res_index = resolutions.index(self.selected_resolution) if self.selected_resolution in resolutions else 0
        
        while waiting:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif self.music_end_event and event.type == self.music_end_event:
                    if self.play_next_func:
                        self.play_next_func(loop=True)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_y:
                        # Exit settings
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check resolution selection (use current screen size for click detection)
                    center_x = self.screen.get_width() // 2
                    res_y_start = 250
                    for i, res in enumerate(resolutions):
                        res_text = f"{res[0]} x {res[1]}"
                        res_surf = self.large_font.render(res_text, True, (255, 255, 255))
                        res_rect = res_surf.get_rect(center=(center_x, res_y_start + i * 100))
                        if res_rect.inflate(40, 20).collidepoint(mouse_pos):
                            # Always allow clicking, even if same resolution
                            selected_res_index = i
                            self.selected_resolution = resolutions[i]
                            
                            # Apply resolution immediately and update screen
                            const.set_resolution(self.selected_resolution[0], self.selected_resolution[1])
                            self.screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
                            
                            if self.click_sound:
                                try:
                                    self.click_sound.play()
                                except Exception:
                                    pass
                            # Continue loop to stay in settings with new resolution
                            break
                    
                    # Check Back button (recalculate position based on current screen size)
                    center_x = self.screen.get_width() // 2
                    back_rect = self.back_button.get_rect(center=(center_x, 500))
                    if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                        if self.click_sound:
                            try:
                                self.click_sound.play()
                            except Exception:
                                pass
                        waiting = False
            
            # Draw game background if available
            if background:
                self.screen.fill((0, 0, 0))
                background.draw(self.screen)
                
                # Draw game objects if available
                if drawable_objects and player:
                    for obj in drawable_objects:
                        if obj != player:  # Don't draw player in settings menu
                            obj.draw(self.screen)
            else:
                self.screen.fill((0, 0, 0))
            
            # Overlay
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            # Title
            title = self.large_font.render("SETTINGS", True, (100, 200, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
            self.screen.blit(title, title_rect)
            
            # Resolution label
            res_label = self.font.render("Resolution:", True, (200, 200, 200))
            res_label_rect = res_label.get_rect(center=(self.screen.get_width() // 2, 180))
            self.screen.blit(res_label, res_label_rect)
            
            # Draw resolution options (large and centered)
            center_x = self.screen.get_width() // 2
            res_y_start = 250
            mouse_pos = pygame.mouse.get_pos()
            
            for i, res in enumerate(resolutions):
                res_text = f"{res[0]} x {res[1]}"
                
                # Color based on selection
                if i == selected_res_index:
                    color = (100, 255, 100)  # Green for selected
                else:
                    color = (200, 200, 200)  # Gray for unselected
                
                res_surf = self.large_font.render(res_text, True, color)
                res_rect = res_surf.get_rect(center=(center_x, res_y_start + i * 100))
                
                # Highlight on hover or if selected
                if res_rect.inflate(40, 20).collidepoint(mouse_pos) or i == selected_res_index:
                    pygame.draw.rect(self.screen, (80, 80, 80), res_rect.inflate(40, 20), border_radius=10)
                
                self.screen.blit(res_surf, res_rect)
                
                # Show checkbox for selected resolution
                if i == selected_res_index:
                    # Draw checkbox circle background
                    checkbox_x = center_x - 220
                    checkbox_y = res_y_start + i * 100
                    pygame.draw.circle(self.screen, (100, 255, 100), (checkbox_x, checkbox_y), 25)
                    pygame.draw.circle(self.screen, (0, 0, 0), (checkbox_x, checkbox_y), 23)
                    
                    # Draw checkmark
                    check = self.large_font.render("✓", True, (100, 255, 100))
                    check_rect = check.get_rect(center=(checkbox_x, checkbox_y))
                    self.screen.blit(check, check_rect)
                else:
                    # Draw empty checkbox circle for unselected
                    checkbox_x = center_x - 220
                    checkbox_y = res_y_start + i * 100
                    pygame.draw.circle(self.screen, (100, 100, 100), (checkbox_x, checkbox_y), 25, 3)
            
            # Back button
            back_rect = self.back_button.get_rect(center=(center_x, 500))
            if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), back_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(self.back_button, back_rect)
            
            # Instructions
            instruction = self.small_font.render("Press Y or ESC to return", True, (150, 150, 150))
            instruction_rect = instruction.get_rect(center=(center_x, 580))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        return self.selected_resolution

    def _show_menu(self, menu_type, background=None):
        
        waiting = True
        clock = pygame.time.Clock()
        resolutions = [(1280, 720), (1920, 1080)]
        selected_res_index = resolutions.index(self.selected_resolution) if self.selected_resolution in resolutions else 0
        
        while waiting:
            # Determine buttons based on menu type (calculate once per frame)
            if menu_type == "initial":
                buttons = [self.play_button, self.settings_button, self.exit_button]
                y_start = 100
                menu_x_offset = 280
            elif menu_type == "pause":
                buttons = [self.resume_button, self.settings_button, self.exit_button]
                y_start = 80
                menu_x_offset = 0
            else:  # game_over
                buttons = [self.restart_button, self.settings_button, self.exit_button]
                y_start = 140
                menu_x_offset = 0
            
            adjusted_menu_rect = self.menu_rect.copy()
            adjusted_menu_rect.x += menu_x_offset
            
            button_rects = []
            for i, button in enumerate(buttons):
                button_rect = button.get_rect(center=(adjusted_menu_rect.centerx, adjusted_menu_rect.top + y_start + i * 70))
                button_rects.append(button_rect)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif self.music_end_event and event.type == self.music_end_event:
                    # Handle music transitions even while in menu
                    if self.play_next_func:
                        self.play_next_func(loop=True)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Allow ESC to unpause from pause menu
                        if menu_type == "pause":
                            waiting = False
                    elif event.key == pygame.K_y:
                        # Open settings menu with background
                        new_resolution = self.show_settings_menu(background)
                        if new_resolution:
                            self.selected_resolution = new_resolution
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check button clicks
                    for i, button_rect in enumerate(button_rects):
                        if button_rect.collidepoint(mouse_pos):
                            if self.click_sound:
                                try:
                                    self.click_sound.play()
                                except Exception:
                                    pass
                            if i == 0:  # First button (Play/Resume/Restart)
                                waiting = False
                            elif i == 1:  # Settings button
                                new_resolution = self.show_settings_menu(background)
                                if new_resolution:
                                    self.selected_resolution = new_resolution
                            elif i == 2:  # Exit button
                                pygame.quit()
                                exit()

            # Draw menu
            if background:
                self.screen.fill((0, 0, 0))
                background.draw(self.screen)
            else:
                self.screen.fill((0, 0, 0))
            
            # Overlay transparency
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))

            # Draw controls on the left side (for initial menu only)
            if menu_type == "initial":
                controls_x = 200
                controls_y = 250
                
                title = self.font.render("CONTROLS", True, (100, 200, 255))
                title_rect = title.get_rect(center=(controls_x, controls_y - 30))
                self.screen.blit(title, title_rect)
                
                controls = [
                    "WASD - Move",
                    "Mouse/Click - Aim & Fire",
                    "SPACE - Fire",
                    "Left Shift - Dash",
                    "R - Ring Blast",
                    "ESC - Pause"
                ]
                
                y_offset = controls_y + 10
                for control in controls:
                    text = self.small_font.render(control, True, (200, 200, 200))
                    text_rect = text.get_rect(center=(controls_x, y_offset))
                    self.screen.blit(text, text_rect)
                    y_offset += 30
                
                # Add hint about settings
                hint_y = y_offset + 20
                hint = self.small_font.render("Press Y for Settings", True, (100, 200, 255))
                hint_rect = hint.get_rect(center=(controls_x, hint_y))
                self.screen.blit(hint, hint_rect)

            # Draw menu background (offset to the right for initial menu)
            pygame.draw.rect(self.screen, (50, 50, 50), adjusted_menu_rect)

            # Draw game over text if applicable
            if menu_type == "game_over":
                text_rect = self.game_over_text.get_rect(center=(adjusted_menu_rect.centerx, adjusted_menu_rect.top + 60))
                self.screen.blit(self.game_over_text, text_rect)

            # Highlight on hover
            mouse_pos = pygame.mouse.get_pos()
            for button_rect in button_rects:
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (100, 100, 100), button_rect.inflate(20, 20), border_radius=5)

            
            # Draw button text
            for i, button in enumerate(buttons):
                self.screen.blit(button, button_rects[i])

            pygame.display.flip()
            clock.tick(60)
        
        # Return selected resolution for initial menu
        if menu_type == "initial":
            return self.selected_resolution
        return None
