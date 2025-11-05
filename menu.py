import pygame
import math
from background import Background

class Menu:
    def __init__(self, screen, click_sound=None, music_end_event=None, play_next_func=None):
        self.screen = screen
        
        # Fonts
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self.medium_font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)
        self.title_font = pygame.font.Font(None, 120)
        
        # Menu state
        self.menu_rect = pygame.Rect(400, 200, 480, 400)
        self.selected_resolution = (1280, 720)
        self.title_time = 0
        
        # Volume settings (0.0 to 1.0)
        self.shot_volume = 0.5
        self.music_volume = 0.5
        self.effects_volume = 0.5
        
        # Sound references for live updates
        self.laser_sound = None
        self.rapid_fire_sound = None
        self.shotgun_sound = None
        self.asteroid_sounds = None
        
        # Audio playback
        self.click_sound = click_sound
        self.music_end_event = music_end_event
        self.play_next_func = play_next_func
        
        # Background
        self.menu_background = None
        self._init_menu_background()

    def _draw_title_banner(self, screen, time_elapsed):
        """Draw animated PYSTEROIDS title with neon glow and cosmic effects"""
        import math
        
        self.title_time += time_elapsed
        
        # Gentle pulsing effect for glow (much slower and subtler)
        pulse = 0.85 + 0.15 * math.sin(self.title_time * 0.8)
        
        center_x = screen.get_width() // 2
        title_y = 80
        
        title_text = "PYSTEROIDS"
        
        # Create multiple layers for neon glow effect (softer colors)
        # Outer glow layers (muted cyan/magenta)
        glow_colors = [
            (180, 100, 200, int(30 * pulse)),  # Muted purple outer glow
            (100, 180, 220, int(45 * pulse)),  # Muted cyan mid glow
            (120, 160, 200, int(70 * pulse))   # Soft blue inner glow
        ]
        
        for i, (r, g, b, alpha) in enumerate(glow_colors):
            offset = (len(glow_colors) - i) * 3
            glow_surf = self.title_font.render(title_text, True, (r, g, b))
            glow_surf.set_alpha(alpha)
            
            # Create expanded glow by rendering multiple times with offsets
            for dx in range(-offset, offset + 1, 2):
                for dy in range(-offset, offset + 1, 2):
                    glow_rect = glow_surf.get_rect(center=(center_x + dx, title_y + dy))
                    screen.blit(glow_surf, glow_rect)
        
        # Main title with softer gradient effect (muted purple to cyan)
        # Top half - softer cyan
        main_surf_top = self.title_font.render(title_text, True, (120, 180, 220))
        main_rect = main_surf_top.get_rect(center=(center_x, title_y))
        
        # Bottom half - softer purple
        main_surf_bottom = self.title_font.render(title_text, True, (170, 120, 200))
        
        # Draw bottom half
        screen.blit(main_surf_bottom, main_rect)
        
        # Clip and draw top half to create gradient
        clip_rect = pygame.Rect(main_rect.x, main_rect.y, main_rect.width, main_rect.height // 2)
        screen.set_clip(clip_rect)
        screen.blit(main_surf_top, main_rect)
        screen.set_clip(None)
        
        # Add gentle sparkle particles around title (slower, softer)
        for i in range(5):
            angle = (self.title_time * 0.3 + i * (3.14159 * 2 / 5)) % (3.14159 * 2)
            radius = 180 + 15 * math.sin(self.title_time * 1.5 + i)
            sparkle_x = center_x + int(radius * math.cos(angle))
            sparkle_y = title_y + int(radius * 0.3 * math.sin(angle))
            
            # Gentle twinkling sparkles
            sparkle_brightness = 0.6 + 0.4 * math.sin(self.title_time * 2 + i * 0.8)
            sparkle_size = int(2 + 1.5 * math.sin(self.title_time * 1.8 + i))
            
            # Softer sparkle color (muted cyan-white)
            base_brightness = int(140 + 60 * sparkle_brightness)
            sparkle_color = (base_brightness, base_brightness + 20, base_brightness + 40)
            pygame.draw.circle(screen, sparkle_color, (sparkle_x, sparkle_y), sparkle_size)

    def _init_menu_background(self):
        """Initialize a menu background with slower, dimmer effects"""
        self.menu_background = Background()
        for star in self.menu_background.stars:
            star.alpha = int(star.alpha * 0.5)
            star.twinkle_speed *= 0.3
        for nebula in self.menu_background.nebulae:
            nebula.alpha = int(nebula.alpha * 0.6)
            nebula.drift_speed *= 0.2
            nebula.color = tuple(int(c * 0.6) for c in nebula.color)
            nebula.secondary_color = tuple(int(c * 0.6) for c in nebula.secondary_color)
    
    def _play_click(self):
        """Play click sound if available"""
        if self.click_sound:
            try:
                self.click_sound.play()
            except Exception:
                pass
    
    def _handle_common_events(self, event):
        """Handle events common to all menus"""
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif self.music_end_event and event.type == self.music_end_event:
            if self.play_next_func:
                self.play_next_func(loop=True)
    
    def _draw_overlay(self, alpha=170):
        """Draw dark overlay over background"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))
    
    def _draw_asteroid_icon(self, x, y, size=25, selected=False):
        """Draw an asteroid-shaped icon (irregular polygon)"""
        # Asteroid shape points (8-sided irregular polygon)
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        radii = [1.0, 0.7, 0.9, 0.6, 0.8, 0.75, 0.95, 0.65]  # Irregular radii
        
        points = []
        for angle, radius_mult in zip(angles, radii):
            rad = math.radians(angle)
            px = x + int(math.cos(rad) * size * radius_mult)
            py = y + int(math.sin(rad) * size * radius_mult)
            points.append((px, py))
        
        if selected:
            # Filled asteroid (cyan)
            pygame.draw.polygon(self.screen, (100, 200, 255), points)
            pygame.draw.polygon(self.screen, (150, 220, 255), points, 2)
        else:
            # Outline only (gray)
            pygame.draw.polygon(self.screen, (100, 100, 100), points, 3)

    
    def set_sound_references(self, laser_sound=None, rapid_fire_sound=None, shotgun_sound=None, asteroid_sounds=None):
        """Store references to game sounds for live volume updates"""
        self.laser_sound = laser_sound
        self.rapid_fire_sound = rapid_fire_sound
        self.shotgun_sound = shotgun_sound
        self.asteroid_sounds = asteroid_sounds
    
    def _apply_volume_live(self):
        """Apply volume changes immediately to all sounds"""
        # Apply shot volume
        if self.laser_sound:
            self.laser_sound.set_volume(0.20 * self.shot_volume)
        if self.rapid_fire_sound:
            self.rapid_fire_sound.set_volume(0.20 * self.shot_volume)
        if self.shotgun_sound:
            self.shotgun_sound.set_volume(0.70 * self.shot_volume)
        
        # Apply effects volume
        if self.asteroid_sounds:
            for key, base_vol in [("bossteroid", 1.0), ("asteroid_large", 0.4), 
                                  ("asteroid_medium", 0.25), ("asteroid_small", 0.15)]:
                if key in self.asteroid_sounds:
                    self.asteroid_sounds[key].set_volume(base_vol * self.effects_volume)
        
        if self.click_sound:
            self.click_sound.set_volume(1.0 * self.effects_volume)
        
        # Apply music volume
        pygame.mixer.music.set_volume(self.music_volume)

    def get_shot_volume(self):
        """Get the shot volume setting (0.0 to 1.0)"""
        return self.shot_volume
    
    def get_music_volume(self):
        """Get the music volume setting (0.0 to 1.0)"""
        return self.music_volume
    
    def get_effects_volume(self):
        """Get the effects volume setting (0.0 to 1.0)"""
        return self.effects_volume
    
    def apply_volumes(self, laser_sound=None, rapid_fire_sound=None, shotgun_sound=None, 
                     asteroid_sounds=None, click_sound=None):
        """Apply current volume settings to all game sounds (called from main.py)"""
        # Store references if provided
        if laser_sound:
            self.laser_sound = laser_sound
        if rapid_fire_sound:
            self.rapid_fire_sound = rapid_fire_sound
        if shotgun_sound:
            self.shotgun_sound = shotgun_sound
        if asteroid_sounds:
            self.asteroid_sounds = asteroid_sounds
        if click_sound:
            self.click_sound = click_sound
        
        # Apply volumes
        self._apply_volume_live()

    def show_initial_menu(self, background=None):
        """Show Play/Settings/Controls/Exit menu at game start"""
        return self._show_menu("initial", background)

    def show_pause_menu(self, background=None):
        """Show Resume/Settings/Controls/Exit menu when ESC is pressed"""
        self._show_menu("pause", background)

    def show_game_over_menu(self, background=None):
        """Show Restart/Settings/Controls/Exit menu when game ends"""
        self._show_menu("game_over", background)
    
    def _show_display_settings(self):
        """Display settings submenu with resolution options"""
        import constants as const
        
        waiting = True
        clock = pygame.time.Clock()
        resolutions = [(1280, 720), (1920, 1080)]
        selected_res_index = resolutions.index(self.selected_resolution) if self.selected_resolution in resolutions else 0
        
        while waiting:
            for event in pygame.event.get():
                self._handle_common_events(event)
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.screen.get_width() // 2
                    
                    # Check resolution options
                    res_y_start = 250
                    for i, res in enumerate(resolutions):
                        res_text = f"{res[0]} x {res[1]}"
                        res_surf = self.large_font.render(res_text, True, (255, 255, 255))
                        res_rect = res_surf.get_rect(center=(center_x, res_y_start + i * 100))
                        
                        if res_rect.inflate(40, 20).collidepoint(mouse_pos):
                            selected_res_index = i
                            self.selected_resolution = resolutions[i]
                            
                            # Apply resolution immediately
                            const.set_resolution(self.selected_resolution[0], self.selected_resolution[1])
                            self.screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
                            self._init_menu_background()
                            self._play_click()
                            break
                    
                    # Back button
                    back_text = self.font.render("Back", True, (255, 255, 255))
                    back_rect = back_text.get_rect(center=(center_x, 500))
                    if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                        self._play_click()
                        waiting = False
            
            dt = clock.tick(60) / 1000.0
            self.menu_background.update(dt)
            
            self.screen.fill((0, 0, 0))
            self.menu_background.draw(self.screen)
            self._draw_overlay(200)
            
            # Title
            title = self.large_font.render("DISPLAY", True, (100, 200, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
            self.screen.blit(title, title_rect)
            
            # Resolution label
            res_label = self.font.render("Resolution:", True, (200, 200, 200))
            res_label_rect = res_label.get_rect(center=(self.screen.get_width() // 2, 180))
            self.screen.blit(res_label, res_label_rect)
            
            # Resolution options
            center_x = self.screen.get_width() // 2
            res_y_start = 250
            mouse_pos = pygame.mouse.get_pos()
            
            for i, res in enumerate(resolutions):
                res_text = f"{res[0]} x {res[1]}"
                color = (100, 255, 100) if i == selected_res_index else (200, 200, 200)
                
                res_surf = self.large_font.render(res_text, True, color)
                res_rect = res_surf.get_rect(center=(center_x, res_y_start + i * 100))
                
                # Hover highlight
                if res_rect.inflate(40, 20).collidepoint(mouse_pos) or i == selected_res_index:
                    pygame.draw.rect(self.screen, (80, 80, 80), res_rect.inflate(40, 20), border_radius=10)
                
                self.screen.blit(res_surf, res_rect)
                
                # Asteroid icon indicator
                asteroid_x = center_x - 220
                asteroid_y = res_y_start + i * 100
                self._draw_asteroid_icon(asteroid_x, asteroid_y, size=20, selected=(i == selected_res_index))
            
            # Back button
            back_text = self.font.render("Back", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(center_x, 500))
            if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), back_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(back_text, back_rect)
            
            # Instructions
            instruction = self.small_font.render("Press ESC to return", True, (150, 150, 150))
            instruction_rect = instruction.get_rect(center=(center_x, 580))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
        
        return self.selected_resolution
    
    def show_controls_menu(self, background=None):
        """Show controls submenu"""
        self._show_controls(background)

    def _show_controls(self, background=None):
        """Controls submenu displaying game controls"""
        waiting = True
        clock = pygame.time.Clock()
        
        while waiting:
            for event in pygame.event.get():
                self._handle_common_events(event)
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.screen.get_width() // 2
                    back_text = self.font.render("Back", True, (255, 255, 255))
                    back_rect = back_text.get_rect(center=(center_x, 600))
                    if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                        self._play_click()
                        waiting = False
            
            dt = clock.tick(60) / 1000.0
            self.menu_background.update(dt)
            
            self.screen.fill((0, 0, 0))
            self.menu_background.draw(self.screen)
            self._draw_overlay(180)
            
            # Title
            title = self.large_font.render("CONTROLS", True, (100, 200, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
            self.screen.blit(title, title_rect)
            
            # Left side - Controls list
            left_x = self.screen.get_width() // 3
            controls_y_start = 180
            
            controls = [
                ("WASD", "Move Ship"),
                ("Mouse/Click", "Aim & Fire"),
                ("SPACE", "Fire"),
                ("Left Shift", "Dash"),
                ("R", "Ring Blast"),
                ("ESC", "Pause Game")
            ]
            
            y_offset = controls_y_start
            for key, description in controls:
                key_text = self.medium_font.render(key, True, (100, 255, 100))
                key_rect = key_text.get_rect(midright=(left_x - 20, y_offset))
                self.screen.blit(key_text, key_rect)
                
                separator = self.medium_font.render("-", True, (150, 150, 150))
                sep_rect = separator.get_rect(center=(left_x, y_offset))
                self.screen.blit(separator, sep_rect)
                
                desc_text = self.medium_font.render(description, True, (200, 200, 200))
                desc_rect = desc_text.get_rect(midleft=(left_x + 20, y_offset))
                self.screen.blit(desc_text, desc_rect)
                
                y_offset += 60
            
            # Right side - Tips panel
            right_x = self.screen.get_width() * 2 // 3
            tips_y_start = 200
            
            tips_title = self.font.render("TIPS", True, (255, 200, 100))
            tips_title_rect = tips_title.get_rect(center=(right_x, tips_y_start - 40))
            self.screen.blit(tips_title, tips_title_rect)
            
            tips = [
                "Collect power-ups for",
                "rapid fire & shotgun",
                "",
                "Ring charges drop at",
                "score milestones",
                "",
                "Dash makes you",
                "invincible briefly"
            ]
            
            tips_y = tips_y_start
            for tip in tips:
                if tip:
                    tip_text = self.small_font.render(tip, True, (200, 200, 220))
                    tip_rect = tip_text.get_rect(center=(right_x, tips_y))
                    self.screen.blit(tip_text, tip_rect)
                tips_y += 30
            
            # Back button
            center_x = self.screen.get_width() // 2
            mouse_pos = pygame.mouse.get_pos()
            back_text = self.font.render("Back", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(center_x, 600))
            if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), back_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(back_text, back_rect)
            
            instruction = self.small_font.render("Press ESC to return", True, (150, 150, 150))
            instruction_rect = instruction.get_rect(center=(center_x, 650))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()

    def show_settings_menu(self, background=None, drawable_objects=None, player=None):
        """Settings hub menu - gateway to Display and Sound submenus"""
        waiting = True
        clock = pygame.time.Clock()
        
        while waiting:
            for event in pygame.event.get():
                self._handle_common_events(event)
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.screen.get_width() // 2
                    
                    # Display button
                    display_text = self.font.render("Display", True, (255, 255, 255))
                    display_rect = display_text.get_rect(center=(center_x, 250))
                    if display_rect.inflate(40, 20).collidepoint(mouse_pos):
                        self._play_click()
                        self._show_display_settings()
                    
                    # Sound button
                    sound_text = self.font.render("Sound", True, (255, 255, 255))
                    sound_rect = sound_text.get_rect(center=(center_x, 350))
                    if sound_rect.inflate(40, 20).collidepoint(mouse_pos):
                        self._play_click()
                        self._show_sound_settings()
                    
                    # Back button
                    back_text = self.font.render("Back", True, (255, 255, 255))
                    back_rect = back_text.get_rect(center=(center_x, 450))
                    if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                        self._play_click()
                        waiting = False
            
            dt = clock.tick(60) / 1000.0
            self.menu_background.update(dt)
            
            self.screen.fill((0, 0, 0))
            self.menu_background.draw(self.screen)
            self._draw_overlay(200)
            
            # Title
            title = self.large_font.render("SETTINGS", True, (100, 200, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
            self.screen.blit(title, title_rect)
            
            # Menu buttons
            center_x = self.screen.get_width() // 2
            mouse_pos = pygame.mouse.get_pos()
            
            # Display button
            display_text = self.font.render("Display", True, (255, 255, 255))
            display_rect = display_text.get_rect(center=(center_x, 250))
            if display_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), display_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(display_text, display_rect)
            
            # Sound button
            sound_text = self.font.render("Sound", True, (255, 255, 255))
            sound_rect = sound_text.get_rect(center=(center_x, 350))
            if sound_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), sound_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(sound_text, sound_rect)
            
            # Back button
            back_text = self.font.render("Back", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(center_x, 450))
            if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), back_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(back_text, back_rect)
            
            # Instructions
            instruction = self.small_font.render("Press ESC to return", True, (150, 150, 150))
            instruction_rect = instruction.get_rect(center=(center_x, 530))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
        
        return self.selected_resolution

    def _show_sound_settings(self):
        """Sound settings submenu with live volume sliders"""
        waiting = True
        clock = pygame.time.Clock()
        dragging_slider = None
        
        while waiting:
            for event in pygame.event.get():
                self._handle_common_events(event)
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.screen.get_width() // 2
                    
                    # Check sliders
                    slider_data = [
                        (250, 'shot', self.shot_volume),
                        (350, 'music', self.music_volume),
                        (450, 'effects', self.effects_volume)
                    ]
                    
                    for slider_y, slider_name, _ in slider_data:
                        slider_rect = pygame.Rect(center_x - 150, slider_y - 10, 300, 20)
                        if slider_rect.collidepoint(mouse_pos):
                            dragging_slider = slider_name
                            # Update volume immediately
                            rel_x = mouse_pos[0] - (center_x - 150)
                            volume = max(0.0, min(1.0, rel_x / 300))
                            self._update_volume(slider_name, volume)
                            break
                    
                    # Back button
                    back_text = self.font.render("Back", True, (255, 255, 255))
                    back_rect = back_text.get_rect(center=(center_x, 550))
                    if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                        self._play_click()
                        waiting = False
                
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_slider = None
                
                elif event.type == pygame.MOUSEMOTION and dragging_slider:
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.screen.get_width() // 2
                    rel_x = mouse_pos[0] - (center_x - 150)
                    volume = max(0.0, min(1.0, rel_x / 300))
                    self._update_volume(dragging_slider, volume)
            
            dt = clock.tick(60) / 1000.0
            self.menu_background.update(dt)
            
            self.screen.fill((0, 0, 0))
            self.menu_background.draw(self.screen)
            self._draw_overlay(200)
            
            # Title
            title = self.large_font.render("SOUND", True, (100, 200, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
            self.screen.blit(title, title_rect)
            
            # Draw sliders
            self._draw_volume_slider("Shot Volume", self.shot_volume, 250)
            self._draw_volume_slider("Music Volume", self.music_volume, 350)
            self._draw_volume_slider("Effects Volume", self.effects_volume, 450)
            
            # Back button
            center_x = self.screen.get_width() // 2
            mouse_pos = pygame.mouse.get_pos()
            back_text = self.font.render("Back", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(center_x, 550))
            if back_rect.inflate(40, 20).collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 100), back_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(back_text, back_rect)
            
            # Instructions
            instruction = self.small_font.render("Press ESC to return", True, (150, 150, 150))
            instruction_rect = instruction.get_rect(center=(center_x, 630))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
    
    def _update_volume(self, volume_type, value):
        """Update a specific volume and apply it live"""
        if volume_type == 'shot':
            self.shot_volume = value
        elif volume_type == 'music':
            self.music_volume = value
        elif volume_type == 'effects':
            self.effects_volume = value
        
        # Apply immediately
        self._apply_volume_live()
    
    def _draw_volume_slider(self, label, volume, y_pos):
        """Draw a volume slider with label and percentage"""
        center_x = self.screen.get_width() // 2
        
        # Label
        label_text = self.medium_font.render(label, True, (200, 200, 200))
        label_rect = label_text.get_rect(center=(center_x, y_pos - 40))
        self.screen.blit(label_text, label_rect)
        
        # Slider background
        slider_bg_rect = pygame.Rect(center_x - 150, y_pos - 10, 300, 20)
        pygame.draw.rect(self.screen, (80, 80, 80), slider_bg_rect, border_radius=10)
        
        # Slider fill
        fill_width = int(300 * volume)
        if fill_width > 0:
            slider_fill_rect = pygame.Rect(center_x - 150, y_pos - 10, fill_width, 20)
            pygame.draw.rect(self.screen, (100, 200, 255), slider_fill_rect, border_radius=10)
        
        # Slider handle
        handle_x = center_x - 150 + int(300 * volume)
        pygame.draw.circle(self.screen, (150, 220, 255), (handle_x, y_pos), 15)
        pygame.draw.circle(self.screen, (100, 180, 235), (handle_x, y_pos), 12)
        
        # Volume percentage
        volume_text = self.small_font.render(f"{int(volume * 100)}%", True, (150, 150, 150))
        volume_rect = volume_text.get_rect(center=(center_x + 200, y_pos))
        self.screen.blit(volume_text, volume_rect)

    def _show_menu(self, menu_type, background=None):
        """Unified menu display logic for initial/pause/game over menus"""
        waiting = True
        clock = pygame.time.Clock()
        
        # Define menu structure
        if menu_type == "initial":
            buttons = ["Play", "Settings", "Controls", "Exit"]
            y_start = 80
            show_title = True
        elif menu_type == "pause":
            buttons = ["Resume", "Settings", "Controls", "Exit"]
            y_start = 80
            show_title = False
        else:  # game_over
            buttons = ["Restart", "Settings", "Controls", "Exit"]
            y_start = 120
            show_title = False
        
        while waiting:
            for event in pygame.event.get():
                self._handle_common_events(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and menu_type == "pause":
                        waiting = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    center_x = self.screen.get_width() // 2
                    
                    for i, button_text in enumerate(buttons):
                        button_surf = self.font.render(button_text, True, (255, 255, 255))
                        button_rect = button_surf.get_rect(center=(center_x, self.menu_rect.top + y_start + i * 70))
                        
                        if button_rect.collidepoint(mouse_pos):
                            self._play_click()
                            
                            if i == 0:  # Play/Resume/Restart
                                waiting = False
                            elif i == 1:  # Settings
                                self.show_settings_menu(background)
                            elif i == 2:  # Controls
                                self.show_controls_menu(background)
                            elif i == 3:  # Exit
                                pygame.quit()
                                exit()
                            break
            
            dt = clock.tick(60) / 1000.0
            self.menu_background.update(dt)
            
            self.screen.fill((0, 0, 0))
            self.menu_background.draw(self.screen)
            self._draw_overlay(170)
            
            # Draw animated title banner on initial menu
            if show_title:
                self._draw_title_banner(self.screen, dt)
            
            # Menu box
            menu_rect = self.menu_rect.copy()
            menu_rect.centerx = self.screen.get_width() // 2
            pygame.draw.rect(self.screen, (50, 50, 50), menu_rect, border_radius=15)
            pygame.draw.rect(self.screen, (100, 100, 150), menu_rect, 3, border_radius=15)
            
            # Game over text
            if menu_type == "game_over":
                game_over_text = self.font.render("Game Over", True, (255, 0, 0))
                text_rect = game_over_text.get_rect(center=(menu_rect.centerx, menu_rect.top + 50))
                self.screen.blit(game_over_text, text_rect)
            
            # Draw buttons
            center_x = self.screen.get_width() // 2
            mouse_pos = pygame.mouse.get_pos()
            
            for i, button_text in enumerate(buttons):
                button_surf = self.font.render(button_text, True, (255, 255, 255))
                button_rect = button_surf.get_rect(center=(center_x, self.menu_rect.top + y_start + i * 70))
                
                # Hover effect
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (100, 100, 100), button_rect.inflate(20, 20), border_radius=5)
                
                self.screen.blit(button_surf, button_rect)
            
            pygame.display.flip()
        
        if menu_type == "initial":
            return self.selected_resolution
        return None
