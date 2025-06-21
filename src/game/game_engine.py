"""
Main game engine for Dale.
"""

import pygame
import sys
from typing import Dict, Any, Optional

from .settings import *
from .constants import *
from .game_state import GameStateManager, GameState
from .character_progression import CharacterProgression
from ..entities.player import Player
from ..entities.enemies import EnemyManager
from ..entities.towers import TowerManager
from ..entities.allies import AllyManager
from ..entities.projectiles import ProjectileManager
from ..ui.hud import HUD
from ..ui.menus import MainMenu, GameOverMenu, PauseMenu
from ..utils.sprites import SpriteManager
from ..backend.database import GameDatabase

class GameEngine:
    """Main game engine class."""
    
    def __init__(self):
        """Initialize the game engine."""
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dale")
        
        # Set up clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Initialize game systems
        self.state_manager = GameStateManager()
        self.sprite_manager = SpriteManager()
        self.database = GameDatabase()
        self.character_progression = CharacterProgression(self.database)
        
        # Initialize game objects (will be set in _initialize_game_objects)
        self.player: Optional[Player] = None
        self.enemy_manager: Optional[EnemyManager] = None
        self.tower_manager: Optional[TowerManager] = None
        self.ally_manager: Optional[AllyManager] = None
        self.projectile_manager: Optional[ProjectileManager] = None
        
        # Initialize UI (will be set in _initialize_game_objects)
        self.hud: Optional[HUD] = None
        self.main_menu: Optional[MainMenu] = None
        self.game_over_menu: Optional[GameOverMenu] = None
        self.pause_menu: Optional[PauseMenu] = None
        
        # Game timing
        self.last_wave_time = 0.0
        self.wave_timer = 0.0
        
        # UI state
        self.show_build_zones = True  # Show no-build zones by default
        
        # Running flag
        self.running = True
        
        self._initialize_game_objects()
        
    def _initialize_game_objects(self):
        """Initialize all game objects."""
        # Initialize player with level-based stats
        player_health = self.character_progression.get_character_health()
        player_attack = self.character_progression.get_character_attack()
        
        self.player = Player(
            self.state_manager.player_data['x'],
            self.state_manager.player_data['y'],
            self.sprite_manager,
            health=player_health,
            attack_damage=player_attack
        )
        
        # Initialize managers
        self.enemy_manager = EnemyManager(self.sprite_manager, self.state_manager)
        self.tower_manager = TowerManager(self.sprite_manager, self.state_manager)
        self.ally_manager = AllyManager(self.sprite_manager, self.state_manager)
        self.projectile_manager = ProjectileManager(self.sprite_manager)
        
        # Initialize UI with character progression
        self.hud = HUD(self.state_manager)
        self.main_menu = MainMenu(self.character_progression, self.sprite_manager, self.database)
        self.game_over_menu = GameOverMenu(self.character_progression)
        self.pause_menu = PauseMenu()
        
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self._handle_events()
            self._update(dt)
            self._render()
            
        self._cleanup()
        
    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle different game states
            if self.state_manager.is_state(GameState.MENU):
                self._handle_menu_events(event)
            elif self.state_manager.is_state(GameState.PLAYING):
                self._handle_game_events(event)
            elif self.state_manager.is_state(GameState.PAUSED):
                self._handle_pause_events(event)
            elif self.state_manager.is_state(GameState.GAME_OVER):
                self._handle_game_over_events(event)
                
    def _handle_menu_events(self, event):
        """Handle events in menu state."""
        # Let main menu handle events first (for name editing)
        if self.main_menu:
            action = self.main_menu.handle_event(event)
            if action == "new_game":
                self._start_new_game()
            elif action == "continue_game":
                self._continue_saved_game()
            elif action == "quit":
                self.running = False
                
    def _handle_game_events(self, event):
        """Handle events during gameplay."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.PAUSED)
            elif event.key in KEY_SUMMON_ALLY:
                self._try_summon_ally()
            elif event.key in KEY_BUILD_TOWER:
                self._try_build_tower()
            elif event.key in KEY_TOGGLE_BUILD_ZONES:
                self.show_build_zones = not self.show_build_zones
                status = "ON" if self.show_build_zones else "OFF"
                print(f"🔧 No-build zones visibility: {status}")
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_left_click(event.pos)
                
    def _handle_game_over_events(self, event):
        """Handle events in game over state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._start_new_game()
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.MENU)
                
    def _handle_pause_events(self, event):
        """Handle events in paused state."""
        if self.pause_menu:
            action = self.pause_menu.handle_event(event)
            
            if action == "resume":
                self.state_manager.change_state(GameState.PLAYING)
            elif action == "save_quit":
                self._save_and_quit_to_menu()
            elif action == "quit_no_save":
                self._quit_to_menu_no_save()
                
    def _handle_left_click(self, pos):
        """Handle left mouse click during gameplay."""
        # Check if clicking on UI elements first
        if self.hud.handle_click(pos):  # type: ignore
            return
            
        # Otherwise, try to build tower at position
        grid_x = pos[0] // TILE_SIZE
        grid_y = pos[1] // TILE_SIZE
        
        # Try to build tower and provide feedback
        if not self.tower_manager.try_build_tower(grid_x, grid_y):  # type: ignore
            # Tower couldn't be built - could be due to path, castle, or essence
            tower_x = grid_x * TILE_SIZE + TILE_SIZE // 2
            tower_y = grid_y * TILE_SIZE + TILE_SIZE // 2
            
            # Check specific reason for failure to provide better feedback
            if self.tower_manager._is_too_close_to_path(tower_x, tower_y):  # type: ignore
                print("❌ Cannot build tower: Too close to enemy path!")
            elif not self.state_manager.player_data['essence'] >= ARROW_TOWER_COST:
                print("❌ Cannot build tower: Not enough essence!")
            else:
                print("❌ Cannot build tower: Invalid location!")
        
    def _try_summon_ally(self):
        """Try to summon an ally near the player."""
        if self.state_manager.spend_essence(ALLY_COST):
            self.ally_manager.spawn_ally_near_player(self.player.x, self.player.y)  # type: ignore
            self.state_manager.game_data['allies_summoned'] += 1
            
    def _try_build_tower(self):
        """Try to build a tower near the player."""
        if self.state_manager.spend_essence(ARROW_TOWER_COST):
            grid_x = int(self.player.x // TILE_SIZE)  # type: ignore
            grid_y = int(self.player.y // TILE_SIZE)  # type: ignore
            if self.tower_manager.try_build_tower(grid_x, grid_y):  # type: ignore
                self.state_manager.game_data['towers_built'] += 1
            else:
                # Refund essence if tower couldn't be built
                self.state_manager.add_essence(ARROW_TOWER_COST)
                
    def _update(self, dt):
        """Update game logic."""
        if self.state_manager.is_state(GameState.PLAYING):
            self._update_gameplay(dt)
        elif self.state_manager.is_state(GameState.PAUSED):
            if self.pause_menu:
                self.pause_menu.update(dt)
        elif self.state_manager.is_state(GameState.MENU):
            self.main_menu.update(dt)  # type: ignore
        elif self.state_manager.is_state(GameState.GAME_OVER):
            self.game_over_menu.update(dt)  # type: ignore
            
    def _update_gameplay(self, dt):
        """Update gameplay logic."""
        # Update game timer
        self.state_manager.game_data['time_elapsed'] += dt
        
        # Handle input for player movement
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, dt)  # type: ignore
        
        # Update entities
        self.player.update(dt)  # type: ignore
        self.enemy_manager.update(dt, self.state_manager.castle_data)  # type: ignore
        self.tower_manager.update(dt)  # type: ignore
        self.ally_manager.update(dt)  # type: ignore
        self.projectile_manager.update(dt, self.state_manager.entities['projectiles'])  # type: ignore
        
        # Handle combat
        self._handle_combat()
        
        # Handle wave spawning
        self._handle_wave_spawning(dt)
        
        # Check win/lose conditions
        self._check_game_conditions()
        
    def _handle_combat(self):
        """Handle combat between entities."""
        enemies = self.state_manager.entities['enemies']
        towers = self.state_manager.entities['towers']
        allies = self.state_manager.entities['allies']
        projectiles = self.state_manager.entities['projectiles']
        
        # Player attacks
        if self.player.is_attacking:  # type: ignore
            hit_enemies = self.player.attack_enemies(enemies)  # type: ignore
            for enemy in hit_enemies:
                # Check if enemy is dead from player attack
                if enemy.health <= 0:
                    if enemy in enemies:
                        enemies.remove(enemy)
                        self._on_enemy_killed(enemy)
        
        # Tower attacks
        for tower in towers:
            target = tower.find_target(enemies)
            if target and tower.can_fire():
                projectile = tower.fire_at(target)
                if projectile:
                    projectiles.append(projectile)
                    
        # Ally attacks
        for ally in allies:
            target = ally.find_target(enemies)
            if target and ally.can_attack():
                ally.attack(target)
                
        # Projectile hits
        for projectile in projectiles[:]:  # Use slice copy for safe iteration
            hit_enemy = projectile.check_collision(enemies)
            if hit_enemy:
                hit_enemy.take_damage(projectile.damage)
                projectiles.remove(projectile)
                
                # Check if enemy is dead
                if hit_enemy.health <= 0:
                    enemies.remove(hit_enemy)
                    self._on_enemy_killed(hit_enemy)
                    
        # Clean up any remaining dead enemies (from ally attacks, etc.)
        for enemy in enemies[:]:  # Use slice copy for safe iteration
            if enemy.health <= 0:
                enemies.remove(enemy)
                self._on_enemy_killed(enemy)
        
    def _handle_wave_spawning(self, dt):
        """Handle spawning of enemy waves."""
        self.wave_timer += dt
        
        # Spawn first wave immediately, then use delay for subsequent waves
        if len(self.state_manager.entities['enemies']) == 0:
            if self.state_manager.game_data['current_wave'] == 1 or (self.wave_timer - self.last_wave_time) >= WAVE_DELAY:
                self._spawn_wave()
                self.last_wave_time = self.wave_timer
                
    def _spawn_wave(self):
        """Spawn a new wave of enemies."""
        wave_num = self.state_manager.game_data['current_wave']
        enemy_count = int(WAVE_ENEMY_COUNT_BASE * (WAVE_ENEMY_COUNT_MULTIPLIER ** (wave_num - 1)))
        
        self.enemy_manager.spawn_wave(enemy_count)  # type: ignore
        self.state_manager.next_wave()
        
    def _on_enemy_killed(self, enemy):
        """Handle when an enemy is killed."""
        self.state_manager.game_data['enemies_killed'] += 1
        self.state_manager.add_score(POINTS_PER_ENEMY_KILL * enemy.max_health)
        
        # Drop essence
        essence_amount = ESSENCE_PER_ENEMY
        self.state_manager.add_essence(essence_amount)
        
        # Give EXP for enemy kill
        level_up_info = self.character_progression.add_enemy_kill_exp()
        if level_up_info['level_up']:
            self._handle_level_up(level_up_info)
            
    def _handle_level_up(self, level_up_info):
        """Handle character level up."""
        if level_up_info['levels_gained'] > 0:
            new_level = level_up_info['new_level']
            health_gained = level_up_info['levels_gained'] * CHARACTER_HEALTH_PER_LEVEL
            attack_gained = level_up_info['levels_gained'] * CHARACTER_ATTACK_PER_LEVEL
            
            # Update player stats
            if self.player:
                # Update max health and heal to full
                self.player.max_health = self.character_progression.get_character_health()
                self.player.health = self.player.max_health  # Full heal on level up
                self.player.attack_damage = self.character_progression.get_character_attack()
                
            # Show level up message
            message = self.character_progression.get_level_up_message(new_level)
            print(f"🎉 {message}")
            print(f"💪 Gained: +{health_gained} Health, +{attack_gained} Attack!")
        
    def _check_game_conditions(self):
        """Check for win/lose conditions."""
        if self.state_manager.is_castle_destroyed():
            self._game_over()
            
    def _game_over(self):
        """Handle game over."""
        self.state_manager.change_state(GameState.GAME_OVER)
        
        # Delete saved game since the game is over
        self.database.delete_saved_game()
        
        # Add session summary to save data
        session_summary = self.character_progression.get_session_summary()
        save_data = self.state_manager.get_save_data()
        save_data.update({
            'exp_gained': session_summary['exp_gained'],
            'character_level_start': session_summary['starting_level'],
            'character_level_end': session_summary['ending_level']
        })
        
        # Save game data to backend
        self.database.save_game_session(save_data)
        
    def _start_new_game(self):
        """Start a new game."""
        # Delete any existing saved game
        self.database.delete_saved_game()
        
        # Reset character progression session tracking
        self.character_progression.reset_session()
        
        self.state_manager.reset_game()
        self.state_manager.change_state(GameState.PLAYING)
        self.last_wave_time = 0.0
        self.wave_timer = 0.0
        
        # Reinitialize game objects with fresh state and current character level
        self._initialize_game_objects()
        
    def _continue_saved_game(self):
        """Continue from a saved game."""
        saved_game = self.database.load_saved_game()
        if not saved_game:
            print("❌ No saved game found!")
            return
            
        # Reset character progression session tracking
        self.character_progression.reset_session()
        
        # Load the saved game state
        self.state_manager.load_game_state(saved_game)
        self.state_manager.change_state(GameState.PLAYING)
        
        # Set wave timer state
        self.wave_timer = saved_game['time_elapsed']
        self.last_wave_time = self.wave_timer
        
        # Reinitialize game objects with saved state
        self._initialize_game_objects()
        
        print(f"🎮 Continuing game from wave {saved_game['wave_number']}!")
        
    def _render(self):
        """Render the game."""
        self.screen.fill(DARK_GREEN)  # Background color
        
        if self.state_manager.is_state(GameState.MENU):
            self.main_menu.render(self.screen)  # type: ignore
        elif self.state_manager.is_state(GameState.PLAYING):
            self._render_gameplay()
        elif self.state_manager.is_state(GameState.PAUSED):
            self._render_gameplay()  # Show game state in background
            if self.pause_menu:
                self.pause_menu.render(self.screen)
        elif self.state_manager.is_state(GameState.GAME_OVER):
            self._render_gameplay()  # Show game state
            self.game_over_menu.render(self.screen)  # type: ignore
            
        pygame.display.flip()
        
    def _render_gameplay(self):
        """Render gameplay elements."""
        # Render enemy path first (so it appears under other elements)
        self._render_enemy_path()
        
        # Render no-build zones around path (if enabled)
        if self.show_build_zones:
            self._render_path_no_build_zones()
        
        # Render castle (now much larger)
        castle_rect = pygame.Rect(
            self.state_manager.castle_data['x'] - CASTLE_WIDTH//2,
            self.state_manager.castle_data['y'] - CASTLE_HEIGHT//2,
            CASTLE_WIDTH,
            CASTLE_HEIGHT
        )
        
        # Draw main castle walls
        pygame.draw.rect(self.screen, BROWN, castle_rect)
        
        # Add castle details
        # Main keep (center tower)
        keep_width = CASTLE_WIDTH // 3
        keep_height = CASTLE_HEIGHT // 2
        keep_rect = pygame.Rect(
            castle_rect.centerx - keep_width//2,
            castle_rect.centery - keep_height//2,
            keep_width,
            keep_height
        )
        pygame.draw.rect(self.screen, (101, 67, 33), keep_rect)  # Darker brown
        
        # Side towers
        tower_width = CASTLE_WIDTH // 6
        tower_height = CASTLE_HEIGHT // 3
        
        # Left tower
        left_tower = pygame.Rect(
            castle_rect.left + 10,
            castle_rect.centery - tower_height//2,
            tower_width,
            tower_height
        )
        pygame.draw.rect(self.screen, (101, 67, 33), left_tower)
        
        # Right tower  
        right_tower = pygame.Rect(
            castle_rect.right - tower_width - 10,
            castle_rect.centery - tower_height//2,
            tower_width,
            tower_height
        )
        pygame.draw.rect(self.screen, (101, 67, 33), right_tower)
        
        # Castle outline
        pygame.draw.rect(self.screen, BLACK, castle_rect, 3)
        pygame.draw.rect(self.screen, BLACK, keep_rect, 2)
        pygame.draw.rect(self.screen, BLACK, left_tower, 2)
        pygame.draw.rect(self.screen, BLACK, right_tower, 2)
        
        # Render entities
        for tower in self.state_manager.entities['towers']:
            tower.render(self.screen)
            
        for enemy in self.state_manager.entities['enemies']:
            enemy.render(self.screen)
            
        for ally in self.state_manager.entities['allies']:
            ally.render(self.screen)
            
        for projectile in self.state_manager.entities['projectiles']:
            projectile.render(self.screen)
            
        # Render player
        self.player.render(self.screen)  # type: ignore
        
        # Render UI
        self.hud.render(self.screen)  # type: ignore
        
    def _render_enemy_path(self):
        """Render the enemy path on the game map."""
        if len(ENEMY_PATH) < 2:
            return
            
        # Draw path lines connecting waypoints
        for i in range(len(ENEMY_PATH) - 1):
            start_pos = ENEMY_PATH[i]
            end_pos = ENEMY_PATH[i + 1]
            
            # Draw thick yellow line for the path
            pygame.draw.line(self.screen, (255, 255, 0), start_pos, end_pos, PATH_WIDTH)
            # Draw thinner dark outline for better visibility
            pygame.draw.line(self.screen, (180, 180, 0), start_pos, end_pos, 2)
            
        # Draw waypoint circles
        for i, waypoint in enumerate(ENEMY_PATH):
            if i == 0:
                # Start point - green circle
                pygame.draw.circle(self.screen, (0, 255, 0), waypoint, WAYPOINT_RADIUS + 2)
                pygame.draw.circle(self.screen, (0, 180, 0), waypoint, WAYPOINT_RADIUS + 2, 2)
            elif i == len(ENEMY_PATH) - 1:
                # End point (castle) - red circle
                pygame.draw.circle(self.screen, (255, 0, 0), waypoint, WAYPOINT_RADIUS + 2)
                pygame.draw.circle(self.screen, (180, 0, 0), waypoint, WAYPOINT_RADIUS + 2, 2)
            else:
                # Regular waypoints - yellow circles
                pygame.draw.circle(self.screen, (255, 255, 0), waypoint, WAYPOINT_RADIUS)
                pygame.draw.circle(self.screen, (180, 180, 0), waypoint, WAYPOINT_RADIUS, 2)
        
    def _render_path_no_build_zones(self):
        """Render semi-transparent no-build zones around the enemy path."""
        if len(ENEMY_PATH) < 2:
            return
            
        # Create a surface for the no-build zones with alpha transparency
        no_build_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Define no-build zone width (same as tower placement logic)
        no_build_width = PATH_WIDTH // 2 + TOWER_SIZE // 2 + 10  # Same as tower placement check
        
        # Draw no-build zones for each path segment
        for i in range(len(ENEMY_PATH) - 1):
            start_pos = ENEMY_PATH[i]
            end_pos = ENEMY_PATH[i + 1]
            
            # Calculate the vector along the path segment
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
                # Normalize the direction vector
                dx_norm = dx / length
                dy_norm = dy / length
                
                # Calculate perpendicular vector for width
                perp_x = -dy_norm * no_build_width
                perp_y = dx_norm * no_build_width
                
                # Create rectangle points for the no-build zone
                points = [
                    (start_pos[0] + perp_x, start_pos[1] + perp_y),
                    (start_pos[0] - perp_x, start_pos[1] - perp_y),
                    (end_pos[0] - perp_x, end_pos[1] - perp_y),
                    (end_pos[0] + perp_x, end_pos[1] + perp_y)
                ]
                
                # Draw semi-transparent red zone
                pygame.draw.polygon(no_build_surface, (255, 0, 0, 60), points)
        
        # Blit the no-build zones to the main screen
        self.screen.blit(no_build_surface, (0, 0))
        
    def _cleanup(self):
        """Clean up resources."""
        pygame.quit()
        sys.exit()
        
    def _save_and_quit_to_menu(self):
        """Save current game progress and return to main menu."""
        # Save complete game state for continuation
        game_state_data = {
            'game_state': self.state_manager.get_saveable_game_state(),
            'wave_number': self.state_manager.game_data['current_wave'],
            'score': self.state_manager.game_data['score'],
            'essence': self.state_manager.player_data['essence'],
            'castle_health': self.state_manager.castle_data['health'],
            'time_elapsed': self.state_manager.game_data['time_elapsed']
        }
        
        # Save game state to database
        if self.database.save_game_state(game_state_data):
            print("💾 Game saved successfully!")
        else:
            print("❌ Failed to save game!")
        
        # Also save session data to game_sessions table
        session_summary = self.character_progression.get_session_summary()
        save_data = self.state_manager.get_save_data()
        save_data.update({
            'exp_gained': session_summary['exp_gained'],
            'character_level_start': session_summary['starting_level'],
            'character_level_end': session_summary['ending_level']
        })
        
        # Save game session data
        self.database.save_game_session(save_data)
        
        # Return to main menu
        self.state_manager.change_state(GameState.MENU)
        print("🏠 Returned to main menu!")
        
    def _quit_to_menu_no_save(self):
        """Return to main menu without saving progress."""
        # Reset character progression session (lose progress)
        self.character_progression.reset_session()
        
        # Return to main menu
        self.state_manager.change_state(GameState.MENU)
        print("🚪 Returned to menu without saving.") 