import pygame
from constants import *
from game_states import load_game_data, save_game_data


class ShipSelectMenu:
    def __init__(self, menu_background=None, click_sound=None):
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.medium_font = pygame.font.Font(None, 32)
        self.save_data = load_game_data()
        self.selected_index = 0
        self.ships = list(SHIP_UNLOCKS.keys())
        self.menu_background = menu_background
        self.click_sound = click_sound
        
        # Ensure current ship index is selected
        if self.save_data['current_ship'] in self.ships:
            self.selected_index = self.ships.index(self.save_data['current_ship'])


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.ships)
                if self.click_sound:
                    self.click_sound.play()
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.ships)
                if self.click_sound:
                    self.click_sound.play()
            elif event.key == pygame.K_RETURN:
                selected_ship = self.ships[self.selected_index]
                if selected_ship in self.save_data['unlocked_ships']:
                    self.save_data['current_ship'] = selected_ship
                    save_game_data(self.save_data)
                    if self.click_sound:
                        self.click_sound.play()
                    return 'start_game'
            elif event.key == pygame.K_ESCAPE:
                if self.click_sound:
                    self.click_sound.play()
                return 'main_menu'
        
        # Mouse support
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            y_offset = 200
            
            for i, ship in enumerate(self.ships):
                ship_rect = pygame.Rect(100, y_offset, SCREEN_WIDTH - 200, 120)
                if ship_rect.collidepoint(mouse_pos):
                    if ship in self.save_data['unlocked_ships']:
                        self.selected_index = i
                        self.save_data['current_ship'] = ship
                        save_game_data(self.save_data)
                        if self.click_sound:
                            self.click_sound.play()
                        return 'start_game'
                    break
                y_offset += 140
            
            # Back button
            back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                if self.click_sound:
                    self.click_sound.play()
                return 'main_menu'
        
        return None
    

    def draw(self, screen):
        # Draw background
        if self.menu_background:
            self.menu_background.draw(screen)
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Title
        title = self.font.render("SELECT YOUR SHIP", True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        # Ship options
        y_offset = 200
        mouse_pos = pygame.mouse.get_pos()
        
        for i, ship in enumerate(self.ships):
            is_unlocked = ship in self.save_data['unlocked_ships']
            is_selected = (i == self.selected_index)
            is_current = (ship == self.save_data['current_ship'])

            # Background panel
            panel_rect = pygame.Rect(100, y_offset, SCREEN_WIDTH - 200, 120)
            
            # Hover effect
            if panel_rect.collidepoint(mouse_pos) and is_unlocked:
                pygame.draw.rect(screen, (60, 60, 60), panel_rect, border_radius=10)
            elif is_selected:
                pygame.draw.rect(screen, (50, 50, 70), panel_rect, border_radius=10)
            else:
                pygame.draw.rect(screen, (40, 40, 40), panel_rect, border_radius=10)
            
            # Border - highlight current ship
            border_color = (100, 255, 100) if is_current else (100, 100, 150)
            border_width = 3 if is_current else 2
            pygame.draw.rect(screen, border_color, panel_rect, border_width, border_radius=10)

            # Ship Name
            name_color = (100, 255, 100) if is_current else (255, 255, 100) if is_selected else (255, 255, 255) if is_unlocked else (100, 100, 100)
            name_text = self.font.render(ship.upper(), True, name_color)
            screen.blit(name_text, (120, y_offset + 15))

            # Current ship indicator
            if is_current:
                equipped_text = self.small_font.render("(EQUIPPED)", True, (100, 255, 100))
                screen.blit(equipped_text, (120 + name_text.get_width() + 20, y_offset + 25))

            if not is_unlocked:
                # Locked status
                required = SHIP_UNLOCKS[ship]
                lock_text = self.medium_font.render(f"Locked - Score {required} to unlock", True, (150, 150, 150))
                screen.blit(lock_text, (120, y_offset + 65))
                
                # Lock icon
                pygame.draw.circle(screen, (150, 150, 150), (SCREEN_WIDTH - 180, y_offset + 60), 20, 3)
                pygame.draw.rect(screen, (150, 150, 150), (SCREEN_WIDTH - 190, y_offset + 60, 20, 25), 3)
            else:
                # Display stats
                stats = SHIP_STATS[ship]
                stats_x = 120
                stats_y = y_offset + 65
                
                # Format stats with icons/bars
                stat_names = {
                    'max_speed': 'Speed',
                    'acceleration': 'Accel',
                    'shot_speed': 'Shot Spd'
                }
                
                stat_values = {
                    'max_speed': stats['max_speed'] / 5.0,  # Normalize to ~0-1 range
                    'acceleration': stats['acceleration'] / 0.3,
                    'shot_speed': stats['shot_speed'] / 15.0
                }
                
                stat_offset = 0
                for stat_key, stat_label in stat_names.items():
                    # Stat label
                    label_text = self.small_font.render(f"{stat_label}:", True, (200, 200, 200))
                    screen.blit(label_text, (stats_x + stat_offset, stats_y))
                    
                    # Stat bar (visual representation)
                    bar_x = stats_x + stat_offset + label_text.get_width() + 5
                    bar_width = int(50 * min(1.0, stat_values[stat_key]))
                    bar_rect = pygame.Rect(bar_x, stats_y + 5, 50, 12)
                    pygame.draw.rect(screen, (80, 80, 80), bar_rect, border_radius=3)
                    if bar_width > 0:
                        fill_rect = pygame.Rect(bar_x, stats_y + 5, bar_width, 12)
                        pygame.draw.rect(screen, (100, 200, 255), fill_rect, border_radius=3)
                    
                    stat_offset += 200
                
                # Ship preview
                preview_x = SCREEN_WIDTH - 180
                preview_y = y_offset + 60
                preview_pos = pygame.Vector2(preview_x, preview_y)
                
                # Draw ship preview using shape data
                from player import Player
                temp_player = type('obj', (object,), {
                    'position': preview_pos,
                    'rotation': 0,
                    'radius': 20,
                    'ship_stats': stats,
                    'shape': stats['shape'],
                    'color': stats['color']
                })()
                Player.draw_ship_preview(screen, temp_player)

            y_offset += 140

        # Back button
        back_text = self.medium_font.render("Back (ESC)", True, (200, 200, 200))
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        
        button_rect = back_rect.inflate(40, 20)
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 100, 100), button_rect, border_radius=10)
        
        screen.blit(back_text, back_rect)