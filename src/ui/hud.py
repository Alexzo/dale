"""
Heads-up display (HUD) for the game.
"""

import pygame
from typing import Tuple

from ..game.settings import *
from ..game.game_state import GameStateManager
from ..game.constants import *

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
        self.upgrade_button_rect = pygame.Rect(270, SCREEN_HEIGHT - HUD_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        # Selected tower (for upgrades)
        self.selected_tower = None
        
    def handle_click(self, pos: Tuple[int, int], action_type=None):
        """Handle mouse clicks on HUD elements."""
        # Check if click is in HUD area
        if not self.hud_rect.collidepoint(pos):
            return False
            
        # Check summon button
        if self.summon_button_rect.collidepoint(pos):
            if self.state_manager.spend_essence(ALLY_COST):
                # Signal to summon ally (handled by game engine)
                return "summon_ally"
                
        # Check tower button
        if self.tower_button_rect.collidepoint(pos):
            if self.state_manager.spend_essence(ARROW_TOWER_COST):
                # Signal to build tower (handled by game engine)
                return "build_tower"
                
        # Check upgrade button
        if self.upgrade_button_rect.collidepoint(pos) and self.selected_tower:
            if self.selected_tower.can_upgrade():
                upgrade_cost = self.selected_tower.get_upgrade_cost()
                if self.state_manager.spend_essence(upgrade_cost):
                    # Signal to upgrade tower (handled by game engine)
                    return "upgrade_tower"
                
        return True  # Consumed the click even if no action taken
        
    def set_selected_tower(self, tower):
        """Set the currently selected tower."""
        self.selected_tower = tower
        
    def clear_tower_selection(self):
        """Clear tower selection."""
        self.selected_tower = None
        
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
        self._render_tower_info(screen)
        
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
        
        # Upgrade tower button (only show if a tower is selected)
        if self.selected_tower:
            if self.selected_tower.can_upgrade():
                upgrade_cost = self.selected_tower.get_upgrade_cost()
                can_afford = self.state_manager.player_data['essence'] >= upgrade_cost
                upgrade_color = GOLD if can_afford else (60, 60, 60)
                pygame.draw.rect(screen, upgrade_color, self.upgrade_button_rect)
                pygame.draw.rect(screen, WHITE, self.upgrade_button_rect, 2)
                
                upgrade_text = f"Upgrade ({upgrade_cost})"
                upgrade_surface = self.font_small.render(upgrade_text, True, WHITE)
                text_rect = upgrade_surface.get_rect(center=self.upgrade_button_rect.center)
                screen.blit(upgrade_surface, text_rect)
            else:
                # Tower at max level
                pygame.draw.rect(screen, (40, 40, 40), self.upgrade_button_rect)
                pygame.draw.rect(screen, WHITE, self.upgrade_button_rect, 2)
                
                max_text = "MAX LEVEL"
                max_surface = self.font_small.render(max_text, True, WHITE)
                text_rect = max_surface.get_rect(center=self.upgrade_button_rect.center)
                screen.blit(max_surface, text_rect)
        
        # Controls info
        controls_y = SCREEN_HEIGHT - HUD_HEIGHT + 55
        controls_text = [
            "WASD/Arrows: Move",
            f"Space: Summon Ally ({ALLY_COST} essence)",
            f"E: Build Tower ({ARROW_TOWER_COST} essence)",
            "F/Shift: Attack",
            "U: Upgrade Tower (select first)",
            "B: Toggle Build Zones"
        ]
        
        y_offset = 5
        for text in controls_text:
            text_surface = self.font_small.render(text, True, WHITE)
            screen.blit(text_surface, (10, controls_y + y_offset))
            y_offset += 22
            
    def _render_tower_info(self, screen: pygame.Surface):
        """Render selected tower information."""
        if not self.selected_tower:
            return
            
        # Tower info panel (top right of screen)
        info_x = SCREEN_WIDTH - 250
        info_y = 10
        info_width = 240
        info_height = 120
        
        # Background
        info_rect = pygame.Rect(info_x, info_y, info_width, info_height)
        pygame.draw.rect(screen, (40, 40, 40, 180), info_rect)
        pygame.draw.rect(screen, WHITE, info_rect, 2)
        
        # Tower title
        title_text = f"Tower Level {self.selected_tower.level}"
        title_surface = self.font_medium.render(title_text, True, TOWER_LEVEL_COLORS[self.selected_tower.level])
        screen.blit(title_surface, (info_x + 10, info_y + 5))
        
        # Tower stats
        stats_y = info_y + 30
        stats = [
            f"Health: {self.selected_tower.health}/{self.selected_tower.max_health}",
            f"Damage: {self.selected_tower.damage}",
            f"Fire Rate: {self.selected_tower.fire_rate:.1f}/sec",
            f"Range: {self.selected_tower.range}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font_small.render(stat, True, WHITE)
            screen.blit(stat_surface, (info_x + 10, stats_y + i * 18))
            
        # Next level preview (if can upgrade)
        if self.selected_tower.can_upgrade():
            next_level = self.selected_tower.level + 1
            preview_y = stats_y + len(stats) * 18 + 5
            
            preview_text = f"→ Level {next_level}:"
            preview_surface = self.font_small.render(preview_text, True, GOLD)
            screen.blit(preview_surface, (info_x + 10, preview_y))
            
            # Calculate next level stats
            next_damage = TOWER_BASE_DAMAGE + (next_level - 1) * TOWER_DAMAGE_BONUS_PER_LEVEL
            next_health = TOWER_BASE_HEALTH + (next_level - 1) * TOWER_HEALTH_PER_LEVEL
            next_fire_rate = TOWER_BASE_ATTACK_SPEED + ((next_level - 1) // 2) * TOWER_ATTACK_SPEED_BONUS_EVERY_2_LEVELS
            
            next_stats = f"DMG:{next_damage} HP:{next_health} FR:{next_fire_rate:.1f}"
            next_surface = self.font_small.render(next_stats, True, GREEN)
            screen.blit(next_surface, (info_x + 75, preview_y)) 