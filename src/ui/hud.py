"""
Heads-up display (HUD) for the game.
"""

import pygame
from typing import Tuple

from ..game.settings import *
from ..game.game_state import GameStateManager

class HUD:
    """Heads-up display showing game information."""
    
    def __init__(self, state_manager: GameStateManager):
        """Initialize the HUD."""
        self.state_manager = state_manager
        
        # Initialize fonts
        pygame.font.init()
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        
        # HUD area
        self.hud_rect = pygame.Rect(0, SCREEN_HEIGHT - HUD_HEIGHT, SCREEN_WIDTH, HUD_HEIGHT)
        
        # Button areas
        self.summon_button_rect = pygame.Rect(10, SCREEN_HEIGHT - HUD_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.tower_button_rect = pygame.Rect(140, SCREEN_HEIGHT - HUD_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse clicks on HUD elements."""
        # Check if click is in HUD area
        if not self.hud_rect.collidepoint(pos):
            return False
            
        # Check summon button
        if self.summon_button_rect.collidepoint(pos):
            if self.state_manager.spend_essence(ALLY_COST):
                # Signal to summon ally (handled by game engine)
                return True
                
        # Check tower button
        if self.tower_button_rect.collidepoint(pos):
            if self.state_manager.spend_essence(ARROW_TOWER_COST):
                # Signal to build tower (handled by game engine)
                return True
                
        return True  # Consumed the click even if no action taken
        
    def render(self, screen: pygame.Surface):
        """Render the HUD."""
        # Draw HUD background
        pygame.draw.rect(screen, (40, 40, 40), self.hud_rect)
        pygame.draw.rect(screen, WHITE, self.hud_rect, 2)
        
        # Render game information
        self._render_player_info(screen)
        self._render_castle_info(screen)
        self._render_game_info(screen)
        self._render_buttons(screen)
        
    def _render_player_info(self, screen: pygame.Surface):
        """Render player information."""
        y_start = SCREEN_HEIGHT - HUD_HEIGHT + 5
        
        # Player health
        health_text = f"Health: {self.state_manager.player_data['health']}"
        health_surface = self.font_small.render(health_text, True, WHITE)
        screen.blit(health_surface, (280, y_start))
        
        # Essence
        essence_text = f"Essence: {self.state_manager.player_data['essence']}"
        essence_surface = self.font_small.render(essence_text, True, GOLD)
        screen.blit(essence_surface, (280, y_start + 20))
        
    def _render_castle_info(self, screen: pygame.Surface):
        """Render castle information."""
        y_start = SCREEN_HEIGHT - HUD_HEIGHT + 5
        
        # Castle health
        castle_health = self.state_manager.castle_data['health']
        castle_max_health = self.state_manager.castle_data['max_health']
        castle_text = f"Castle: {castle_health}/{castle_max_health}"
        castle_surface = self.font_small.render(castle_text, True, RED if castle_health < castle_max_health * 0.3 else WHITE)
        screen.blit(castle_surface, (400, y_start))
        
        # Castle health bar
        bar_width = 100
        bar_height = 8
        bar_x = 400
        bar_y = y_start + 20
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_percentage = castle_health / castle_max_health
        health_width = int(health_percentage * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
    def _render_game_info(self, screen: pygame.Surface):
        """Render game information."""
        y_start = SCREEN_HEIGHT - HUD_HEIGHT + 5
        
        # Wave number
        wave_text = f"Wave: {self.state_manager.game_data['current_wave']}"
        wave_surface = self.font_medium.render(wave_text, True, WHITE)
        screen.blit(wave_surface, (SCREEN_WIDTH - 200, y_start))
        
        # Score
        score_text = f"Score: {self.state_manager.game_data['score']}"
        score_surface = self.font_small.render(score_text, True, WHITE)
        screen.blit(score_surface, (SCREEN_WIDTH - 200, y_start + 25))
        
        # Enemies killed
        kills_text = f"Kills: {self.state_manager.game_data['enemies_killed']}"
        kills_surface = self.font_small.render(kills_text, True, WHITE)
        screen.blit(kills_surface, (SCREEN_WIDTH - 200, y_start + 45))
        
    def _render_buttons(self, screen: pygame.Surface):
        """Render action buttons."""
        # Summon ally button
        summon_color = GREEN if self.state_manager.player_data['essence'] >= ALLY_COST else (60, 60, 60)
        pygame.draw.rect(screen, summon_color, self.summon_button_rect)
        pygame.draw.rect(screen, WHITE, self.summon_button_rect, 2)
        
        summon_text = f"Summon ({ALLY_COST})"
        summon_surface = self.font_small.render(summon_text, True, WHITE)
        text_rect = summon_surface.get_rect(center=self.summon_button_rect.center)
        screen.blit(summon_surface, text_rect)
        
        # Build tower button
        tower_color = BROWN if self.state_manager.player_data['essence'] >= ARROW_TOWER_COST else (60, 60, 60)
        pygame.draw.rect(screen, tower_color, self.tower_button_rect)
        pygame.draw.rect(screen, WHITE, self.tower_button_rect, 2)
        
        tower_text = f"Tower ({ARROW_TOWER_COST})"
        tower_surface = self.font_small.render(tower_text, True, WHITE)
        text_rect = tower_surface.get_rect(center=self.tower_button_rect.center)
        screen.blit(tower_surface, text_rect)
        
        # Controls info
        controls_y = SCREEN_HEIGHT - HUD_HEIGHT + 55
        controls_text = "WASD: Move | Space: Summon | E: Build Tower | Mouse: Click to build"
        controls_surface = self.font_small.render(controls_text, True, (180, 180, 180))
        screen.blit(controls_surface, (10, controls_y)) 