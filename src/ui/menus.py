"""
Menu classes for game menus.
"""

import pygame
import math
from typing import Tuple

from ..game.settings import *

class MainMenu:
    """Main menu for the game."""
    
    def __init__(self):
        """Initialize the main menu."""
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE * 2)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Menu state
        self.animation_timer = 0.0
        
    def update(self, dt: float):
        """Update menu state."""
        self.animation_timer += dt
        
    def render(self, screen: pygame.Surface):
        """Render the main menu."""
        # Background
        screen.fill((20, 40, 20))  # Dark green background
        
        # Title
        title_text = "Dale"
        title_surface = self.font_large.render(title_text, True, GOLD)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Last Stand of the Five Armies"
        subtitle_surface = self.font_medium.render(subtitle_text, True, WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Instructions
        instructions = [
            "Defend your magical castle from waves of enemies",
            "Move freely around the battlefield",
            "Collect essence from defeated enemies",
            "Summon elvish warrior allies",
            "Build arrow towers for defense",
            "",
            "Controls:",
            "WASD / Arrow Keys - Move character",
            "Space - Summon ally (costs essence)",
            "E - Build tower near player (costs essence)",
            "Mouse - Click to build tower at position",
            "",
            "Press ENTER or SPACE to start playing",
            "Press ESC to quit"
        ]
        
        y_start = 280
        for i, instruction in enumerate(instructions):
            if instruction == "":
                y_start += 10
                continue
                
            color = YELLOW if instruction.startswith("Controls:") else WHITE
            if instruction.startswith("Press"):
                color = GREEN
                
            text_surface = self.font_small.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 22))
            screen.blit(text_surface, text_rect)
            
        # Animated prompt
        alpha = int(128 + 127 * abs(math.sin(self.animation_timer * 3)))
        prompt_surface = self.font_medium.render("Press ENTER to Start", True, WHITE)
        prompt_surface.set_alpha(alpha)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(prompt_surface, prompt_rect)

class GameOverMenu:
    """Game over menu."""
    
    def __init__(self):
        """Initialize the game over menu."""
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE * 2)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
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
        
        # Castle destroyed message
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
        
        y_start = 350
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
    """Pause menu."""
    
    def __init__(self):
        """Initialize the pause menu."""
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
    def render(self, screen: pygame.Surface):
        """Render the pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Paused title
        title_text = "PAUSED"
        title_surface = self.font_large.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title_surface, title_rect)
        
        # Resume instruction
        resume_text = "Press ESC to resume"
        resume_surface = self.font_medium.render(resume_text, True, GREEN)
        resume_rect = resume_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(resume_surface, resume_rect) 