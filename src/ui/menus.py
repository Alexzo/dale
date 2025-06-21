"""
Menu classes for game menus.
"""

import pygame
import math
from typing import Tuple, Optional

from ..game.settings import *

class MainMenu:
    """Main menu for the game."""
    
    def __init__(self, character_progression=None, sprite_manager=None, database=None):
        """Initialize the main menu."""
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE * 2)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_tiny = pygame.font.Font(None, max(16, FONT_SIZE_SMALL - 4))
        
        # Character progression system
        self.character_progression = character_progression
        self.sprite_manager = sprite_manager
        self.database = database
        
        # Menu state
        self.animation_timer = 0.0
        
        # Name editing state
        self.editing_name = False
        self.name_input = ""
        self.name_cursor_timer = 0.0
        
    def update(self, dt: float):
        """Update menu state."""
        self.animation_timer += dt
        self.name_cursor_timer += dt
        
    def handle_event(self, event):
        """Handle input events for the main menu."""
        if not self.character_progression:
            return None
            
        # Handle name editing
        if self.editing_name:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Save name and exit editing
                    if self.name_input.strip():
                        self.character_progression.set_character_name(self.name_input.strip())
                    self.editing_name = False
                    return None
                elif event.key == pygame.K_ESCAPE:
                    # Cancel editing
                    self.editing_name = False
                    self.name_input = ""
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                    return None
                elif event.unicode.isprintable() and len(self.name_input) < 20:
                    self.name_input += event.unicode
                    return None
        else:
            # Check for menu actions
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:  # Press 'N' to edit name
                    self.editing_name = True
                    self.name_input = self.character_progression.get_character_name()
                    return None
                elif event.key == pygame.K_c:  # Press 'C' to continue game
                    if self.database and self.database.has_saved_game():
                        return "continue_game"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "new_game"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
                    
        return None
        
    def render(self, screen: pygame.Surface):
        """Render the main menu."""
        # Background
        screen.fill((20, 40, 20))  # Dark green background
        
        # Title
        title_text = "Dale"
        title_surface = self.font_large.render(title_text, True, GOLD)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Medieval Fantasy Tower Defense"
        subtitle_surface = self.font_medium.render(subtitle_text, True, WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Character info panel (left side)
        if self.character_progression:
            self._render_character_panel(screen)
        
        # Instructions (right side)
        self._render_instructions(screen)
        
        # Animated prompt
        alpha = int(128 + 127 * abs(math.sin(self.animation_timer * 3)))
        prompt_surface = self.font_medium.render("Press ENTER to Start", True, WHITE)
        prompt_surface.set_alpha(alpha)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(prompt_surface, prompt_rect)
        
    def _render_character_panel(self, screen: pygame.Surface):
        """Render character progression panel on the left side."""
        if not self.character_progression:
            return
            
        char_info = self.character_progression.get_character_display_info()
        
        # Panel background (increased height to fit all content)
        panel_x = 50
        panel_y = 180
        panel_width = 300
        panel_height = 480  # Increased from 400 to 480
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 60, 40), panel_rect)
        pygame.draw.rect(screen, GOLD, panel_rect, 3)
        
        # Character sprite (if available)
        sprite_y = panel_y + 20
        if self.sprite_manager:
            char_sprite = self.sprite_manager.get_sprite('player')
            if char_sprite:
                # Scale sprite for display
                display_sprite = pygame.transform.scale(char_sprite, (80, 80))
                sprite_rect = display_sprite.get_rect()
                sprite_rect.centerx = panel_x + panel_width // 2
                sprite_rect.y = sprite_y
                screen.blit(display_sprite, sprite_rect)
                sprite_y += 90
        
        # Character title
        if self.editing_name:
            # Show name input field
            input_text = self.name_input
            cursor_visible = (self.name_cursor_timer % 1.0) < 0.5
            if cursor_visible:
                input_text += "|"
            
            title_surface = self.font_medium.render(input_text, True, (255, 255, 100))
            
            # Input instructions
            instruction_text = "Enter name, ENTER to save, ESC to cancel"
            instruction_surface = self.font_tiny.render(instruction_text, True, (200, 200, 200))
            instruction_rect = instruction_surface.get_rect()
            instruction_rect.centerx = panel_x + panel_width // 2
            instruction_rect.y = sprite_y + 25
            screen.blit(instruction_surface, instruction_rect)
        else:
            # Show character name
            title_text = char_info['name']
            title_surface = self.font_medium.render(title_text, True, GOLD)
            
            # Edit instruction
            edit_text = "Press N to edit name"
            edit_surface = self.font_tiny.render(edit_text, True, (150, 150, 150))
            edit_rect = edit_surface.get_rect()
            edit_rect.centerx = panel_x + panel_width // 2
            edit_rect.y = sprite_y + 25
            screen.blit(edit_surface, edit_rect)
        
        title_rect = title_surface.get_rect()
        title_rect.centerx = panel_x + panel_width // 2
        title_rect.y = sprite_y
        screen.blit(title_surface, title_rect)
        
        # Class subtitle
        class_text = "Elvish Warrior"
        class_surface = self.font_small.render(class_text, True, (200, 200, 200))
        class_rect = class_surface.get_rect()
        class_rect.centerx = panel_x + panel_width // 2
        class_rect.y = sprite_y + 45
        screen.blit(class_surface, class_rect)
        
        # Character stats (adjusted spacing)
        stats_y = sprite_y + 75
        stats = [
            f"Level: {char_info['level']}",
            f"Health: {char_info['health']}",
            f"Attack: {char_info['attack']}",
            "",
            f"Experience:",
            f"  {char_info['current_exp']} / {char_info['exp_for_next_level']}",
            f"  Progress: {char_info['exp_progress_percent']:.1f}%",
            "",
            f"Career Stats:",
            f"  Games: {char_info['games_played']}",
            f"  Enemies: {char_info['total_enemies_killed']}",
            f"  Waves: {char_info['total_waves_completed']}",
            f"  Towers: {char_info['total_towers_built']}"
        ]
        
        current_y = stats_y
        for stat in stats:
            if stat == "":
                current_y += 10
                continue
                
            # Choose color based on stat type
            if stat.startswith("Level:"):
                color = GOLD
            elif stat.startswith("Experience:") or stat.startswith("Career Stats:"):
                color = YELLOW
            elif stat.startswith("  "):
                color = (200, 200, 200)  # Light gray for indented stats
            else:
                color = WHITE
            
            text_surface = self.font_small.render(stat, True, color)
            text_rect = text_surface.get_rect()
            text_rect.x = panel_x + 20
            text_rect.y = current_y
            screen.blit(text_surface, text_rect)
            current_y += 18
        
        # Experience progress bar (positioned after all stats with proper spacing)
        if char_info['exp_for_next_level'] > 0:
            bar_x = panel_x + 20
            bar_y = current_y + 15  # Add spacing after stats
            bar_width = panel_width - 40
            bar_height = 12
            
            # Ensure the bar fits within the panel
            if bar_y + bar_height + 20 > panel_y + panel_height:
                # Adjust panel height if needed
                new_panel_height = bar_y + bar_height + 20 - panel_y
                panel_rect = pygame.Rect(panel_x, panel_y, panel_width, new_panel_height)
                pygame.draw.rect(screen, (40, 60, 40), panel_rect)
                pygame.draw.rect(screen, GOLD, panel_rect, 3)
            
            # Background
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            
            # Progress
            progress = char_info['exp_progress_percent'] / 100.0
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, progress_width, bar_height))
            
            # Border
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # "EXP" label above the bar
            exp_label = self.font_tiny.render("EXP Progress", True, WHITE)
            screen.blit(exp_label, (bar_x, bar_y - 18))
        
    def _render_instructions(self, screen: pygame.Surface):
        """Render game instructions on the right side."""
        instructions_x = SCREEN_WIDTH - 350
        instructions_y = 180
        
        # Check if there's a saved game
        has_saved_game = self.database and self.database.has_saved_game()
        saved_game_info = None
        if has_saved_game and self.database:
            saved_game_info = self.database.get_saved_game_info()
        
        instructions = []
        
        # Add continue game section if available
        if has_saved_game and saved_game_info:
            instructions.extend([
                "Continue Game Available:",
                f"• Wave {saved_game_info['wave_number']} - Score: {saved_game_info['score']}",
                f"• {saved_game_info['essence']} Essence - Castle: {saved_game_info['castle_health']} HP",
                f"• Time: {saved_game_info['time_elapsed']:.1f}s",
                "",
                "Press C to Continue Game",
                "Press ENTER for New Game",
                "",
            ])
        else:
            instructions.extend([
                "Press ENTER to Start New Game",
                "",
            ])
        
        instructions.extend([
            "How to Play:",
            "",
            "• Defend your castle from enemy waves",
            "• Move freely around the battlefield",
            "• Attack enemies with your sword",
            "• Collect essence from defeated enemies",
            "• Summon elvish warrior allies",
            "• Build arrow towers for defense",
            "• Gain experience and level up!",
            "",
            "Controls:",
            "• WASD / Arrow Keys - Move",
            "• F / Shift - Attack",
            "• Space - Summon ally",
            "• E - Build tower near player",
            "• Mouse - Click to build tower",
            "• B - Toggle build zones",
            "• N - Edit character name",
            "",
            "Character Progression:",
            "• Gain EXP from killing enemies",
            "• Level up for +2 Health, +1 Attack",
            "• Progress persists between games",
            "• Customize your character name",
            "",
            "ESC to quit"
        ])
        
        for i, instruction in enumerate(instructions):
            if instruction == "":
                continue
                
            # Choose color based on instruction type
            if instruction.endswith(":"):
                if "Continue Game Available" in instruction:
                    color = (100, 255, 100)  # Bright green for continue option
                else:
                    color = GOLD
            elif instruction.startswith("•"):
                if "Wave" in instruction or "Essence" in instruction or "Time:" in instruction:
                    color = (200, 255, 200)  # Light green for saved game details
                else:
                    color = WHITE
            elif instruction.startswith("Press"):
                if "Continue" in instruction:
                    color = (0, 255, 0)  # Bright green for continue
                elif "New Game" in instruction:
                    color = GREEN
                else:
                    color = GREEN
            else:
                color = (200, 200, 200)
                
            text_surface = self.font_small.render(instruction, True, color)
            text_rect = text_surface.get_rect()
            text_rect.x = instructions_x
            text_rect.y = instructions_y + i * 20
            screen.blit(text_surface, text_rect)

class GameOverMenu:
    """Game over menu."""
    
    def __init__(self, character_progression=None):
        """Initialize the game over menu."""
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE * 2)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Character progression system
        self.character_progression = character_progression
        
        # Menu state
        self.animation_timer = 0.0
        
    def update(self, dt: float):
        """Update menu state."""
        self.animation_timer += dt
        
    def render(self, screen: pygame.Surface):
        """Render the game over menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Game Over title
        title_text = "GAME OVER"
        title_surface = self.font_large.render(title_text, True, RED)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title_surface, title_rect)
        
        # Personalized message
        if self.character_progression:
            char_name = self.character_progression.get_character_name()
            message_text = f"{char_name}'s castle has been destroyed!"
            
            # Show session summary
            session = self.character_progression.get_session_summary()
            if session['exp_gained'] > 0:
                exp_text = f"You gained {session['exp_gained']} experience!"
                exp_surface = self.font_small.render(exp_text, True, (100, 255, 100))
                exp_rect = exp_surface.get_rect(center=(SCREEN_WIDTH // 2, 310))
                screen.blit(exp_surface, exp_rect)
                
            if session['levels_gained'] > 0:
                level_text = f"Congratulations! You gained {session['levels_gained']} level(s)!"
                level_surface = self.font_small.render(level_text, True, GOLD)
                level_rect = level_surface.get_rect(center=(SCREEN_WIDTH // 2, 330))
                screen.blit(level_surface, level_rect)
        else:
            message_text = "Your castle has been destroyed!"
        
        message_surface = self.font_medium.render(message_text, True, WHITE)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, 260))
        screen.blit(message_surface, message_rect)
        
        # Instructions
        instructions = [
            "",
            "Press ENTER or SPACE to play again",
            "Press ESC to return to main menu"
        ]
        
        y_start = 380
        for i, instruction in enumerate(instructions):
            if instruction == "":
                continue
                
            color = GREEN if "ENTER" in instruction else WHITE
            text_surface = self.font_small.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 30))
            screen.blit(text_surface, text_rect)
            
        # Animated prompt
        alpha = int(128 + 127 * abs(math.sin(self.animation_timer * 3)))
        prompt_surface = self.font_medium.render("Try Again?", True, WHITE)
        prompt_surface.set_alpha(alpha)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
        screen.blit(prompt_surface, prompt_rect)

class PauseMenu:
    """Pause menu with save/quit options."""
    
    def __init__(self):
        """Initialize the pause menu."""
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Menu options
        self.menu_options = [
            {"text": "Resume Game", "action": "resume"},
            {"text": "Save & Quit to Menu", "action": "save_quit"},
            {"text": "Quit to Menu (No Save)", "action": "quit_no_save"}
        ]
        
        # Menu state
        self.selected_index = 0
        self.animation_timer = 0.0
        
    def update(self, dt: float):
        """Update menu state."""
        self.animation_timer += dt
        
    def handle_event(self, event):
        """Handle input events for the pause menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"  # ESC resumes the game
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                # Move selection up
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                return None
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                # Move selection down
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select current option
                return self.menu_options[self.selected_index]["action"]
                
        return None
        
    def render(self, screen: pygame.Surface):
        """Render the pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Menu background panel
        panel_width = 400
        panel_height = 300
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(screen, GOLD, panel_rect, 3)
        
        # Paused title
        title_text = "GAME PAUSED"
        title_surface = self.font_large.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 60))
        screen.blit(title_surface, title_rect)
        
        # Menu options
        option_start_y = panel_y + 120
        option_spacing = 45
        
        for i, option in enumerate(self.menu_options):
            option_y = option_start_y + i * option_spacing
            
            # Highlight selected option
            is_selected = (i == self.selected_index)
            
            if is_selected:
                # Draw selection highlight
                highlight_rect = pygame.Rect(panel_x + 20, option_y - 8, panel_width - 40, 32)
                pygame.draw.rect(screen, (80, 80, 120), highlight_rect)
                pygame.draw.rect(screen, WHITE, highlight_rect, 2)
                
                # Add animated glow effect
                glow_alpha = int(100 + 50 * abs(math.sin(self.animation_timer * 4)))
                glow_surface = pygame.Surface((highlight_rect.width, highlight_rect.height))
                glow_surface.set_alpha(glow_alpha)
                glow_surface.fill((255, 255, 100))
                screen.blit(glow_surface, highlight_rect.topleft, special_flags=pygame.BLEND_ADD)
            
            # Render option text
            color = GOLD if is_selected else WHITE
            option_surface = self.font_medium.render(option["text"], True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, option_y + 8))
            screen.blit(option_surface, option_rect)
        
        # Controls hint
        controls_y = panel_y + panel_height - 40
        controls_text = "↑↓ Navigate • ENTER Select • ESC Resume"
        controls_surface = self.font_small.render(controls_text, True, (180, 180, 180))
        controls_rect = controls_surface.get_rect(center=(SCREEN_WIDTH // 2, controls_y))
        screen.blit(controls_surface, controls_rect) 