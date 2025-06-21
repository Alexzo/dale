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
        
        # Environment decorations
        self.decorations = []
        
        # Running flag
        self.running = True
        
        self._initialize_game_objects()
        # self._generate_environment_decorations()  # DISABLED FOR NOW - focusing on path textures only
        
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
        
    def _generate_environment_decorations(self):
        """Generate environment decorations like trees and rocks."""
        import random
        
        print("🌲 Generating environment decorations...")
        
        # Define decoration types and their spawn counts
        decoration_types = {
            'tree_oak': {'count': 8, 'size': (48, 64)},
            'tree_pine': {'count': 6, 'size': (40, 72)}, 
            'tree_birch': {'count': 5, 'size': (44, 68)},
            'rock_small': {'count': 12, 'size': (24, 20)},
            'rock_medium': {'count': 8, 'size': (36, 30)},
            'rock_large': {'count': 4, 'size': (48, 40)},
            'boulder': {'count': 3, 'size': (60, 50)}
        }
        
        # Generate decorations for each type
        for decoration_name, config in decoration_types.items():
            sprite = self.sprite_manager.get_sprite(decoration_name)
            if not sprite:
                continue
                
            attempts = 0
            placed = 0
            max_attempts = config['count'] * 20  # Prevent infinite loops
            
            while placed < config['count'] and attempts < max_attempts:
                attempts += 1
                
                # Random position on the battlefield
                x = random.randint(50, SCREEN_WIDTH - 100)
                y = random.randint(50, SCREEN_HEIGHT - HUD_HEIGHT - 50)
                
                # Check if position is valid (not blocking gameplay areas)
                if self._is_valid_decoration_position(x, y, config['size']):
                    decoration = {
                        'type': decoration_name,
                        'x': x,
                        'y': y, 
                        'sprite': sprite,
                        'size': config['size']
                    }
                    self.decorations.append(decoration)
                    placed += 1
                    
        print(f"🎨 Placed {len(self.decorations)} environment decorations")
        
    def _is_valid_decoration_position(self, x: int, y: int, size: tuple) -> bool:
        """Check if a decoration can be placed at the given position."""
        decoration_width, decoration_height = size
        decoration_radius = max(decoration_width, decoration_height) // 2
        
        # Check distance from castle
        castle_data = self.state_manager.castle_data
        castle_distance = ((x - castle_data['x'])**2 + (y - castle_data['y'])**2)**0.5
        if castle_distance < CASTLE_WIDTH // 2 + decoration_radius + 30:
            return False
            
        # Check distance from all enemy paths
        min_path_distance = PATH_WIDTH // 2 + decoration_radius + 20
        
        for enemy_path in ENEMY_PATHS:
            for i in range(len(enemy_path) - 1):
                start_pos = enemy_path[i]
                end_pos = enemy_path[i + 1]
                
                # Calculate distance from decoration center to path segment
                distance = self._point_to_line_segment_distance(
                    x, y, start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                )
                
                if distance < min_path_distance:
                    return False
        
        # Check distance from other decorations (prevent clustering)
        for other_decoration in self.decorations:
            other_x = other_decoration['x']
            other_y = other_decoration['y']
            distance = ((x - other_x)**2 + (y - other_y)**2)**0.5
            
            # Minimum distance based on decoration sizes
            min_distance = decoration_radius + max(other_decoration['size']) // 2 + 15
            if distance < min_distance:
                return False
                
        return True
        
    def _point_to_line_segment_distance(self, px: float, py: float, 
                                      x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate the shortest distance from a point to a line segment."""
        import math
        
        # Vector from start to end of line segment
        dx = x2 - x1
        dy = y2 - y1
        
        # If the segment has zero length, return distance to start point
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Calculate parameter t that represents position along the line segment
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        
        # Clamp t to [0, 1] to stay within the line segment
        t = max(0, min(1, t))
        
        # Find the closest point on the line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Return distance from point to closest point on segment
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
        
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
            elif event.key == pygame.K_u:  # U key for upgrade
                self._try_upgrade_selected_tower()
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
        hud_action = self.hud.handle_click(pos)  # type: ignore
        if hud_action == "summon_ally":
            self._try_summon_ally()
            return
        elif hud_action == "build_tower":
            self._try_build_tower()
            return
        elif hud_action == "upgrade_tower":
            self._upgrade_selected_tower()
            return
        elif hud_action is True:  # Clicked in HUD but no action
            return
            
        # Check if clicking on a tower to select it
        tower = self.tower_manager.get_tower_near_position(pos[0], pos[1])  # type: ignore
        if tower:
            self.hud.set_selected_tower(tower)  # type: ignore
            print(f"🏗️ Selected Level {tower.level} Tower (Health: {tower.health}/{tower.max_health})")
            return
            
        # Clear tower selection if clicking elsewhere
        self.hud.clear_tower_selection()  # type: ignore
            
        # Try to build tower at position
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
        else:
            # Clear tower selection after building
            self.hud.clear_tower_selection()  # type: ignore
        
    def _try_summon_ally(self):
        """Try to summon an ally near the player."""
        if self.state_manager.player_data['essence'] >= ALLY_COST:
            if self.state_manager.spend_essence(ALLY_COST):
                self.ally_manager.spawn_ally_near_player(self.player.x, self.player.y)  # type: ignore
                self.state_manager.game_data['allies_summoned'] += 1
                print(f"🧝 Summoned ally! Essence: {self.state_manager.player_data['essence']}")
            
    def _try_build_tower(self):
        """Try to build a tower near the player."""
        grid_x = int(self.player.x // TILE_SIZE)  # type: ignore
        grid_y = int(self.player.y // TILE_SIZE)  # type: ignore
        
        # Let tower manager handle essence spending
        if self.tower_manager.try_build_tower(grid_x, grid_y):  # type: ignore
            print(f"🏗️ Tower built! Essence: {self.state_manager.player_data['essence']}")
        else:
            print("❌ Cannot build tower at this location!")
                
    def _try_upgrade_selected_tower(self):
        """Try to upgrade the currently selected tower using U key."""
        selected_tower = self.hud.selected_tower  # type: ignore
        if selected_tower is None:
            print("❌ No tower selected! Click on a tower first.")
            return
            
        if not selected_tower.can_upgrade():
            print("❌ Tower is already at maximum level!")
            return
            
        upgrade_cost = selected_tower.get_upgrade_cost()
        if self.state_manager.player_data['essence'] < upgrade_cost:
            print(f"❌ Not enough essence! Need {upgrade_cost}, have {self.state_manager.player_data['essence']}")
            return
            
        # Perform the upgrade
        if self.tower_manager.try_upgrade_tower(selected_tower):  # type: ignore
            print(f"✅ Tower upgraded to level {selected_tower.level}!")
        else:
            print("❌ Tower upgrade failed!")
            
    def _upgrade_selected_tower(self):
        """Upgrade the currently selected tower (called from HUD button)."""
        selected_tower = self.hud.selected_tower  # type: ignore
        if selected_tower and self.tower_manager.try_upgrade_tower(selected_tower):  # type: ignore
            print(f"✅ Tower upgraded to level {selected_tower.level}!")
                
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
        
        # Recreate saved entities with correct levels
        saved_entity_data = self.state_manager.get_saved_entity_data()
        if saved_entity_data:
            self._recreate_saved_entities(saved_entity_data)
        
        print(f"🎮 Continuing game from wave {saved_game['wave_number']}!")
        
    def _recreate_saved_entities(self, saved_data: Dict[str, Any]):
        """Recreate towers and allies from saved data with correct levels."""
        from ..entities.towers import ArrowTower
        from ..entities.allies import ElfWarrior
        
        # Clear existing entities first
        self.state_manager.entities['towers'].clear()
        self.state_manager.entities['allies'].clear()
        self.tower_manager.occupied_positions.clear()  # type: ignore
        
        # Recreate towers with correct levels
        for tower_data in saved_data.get('towers', []):
            # Use grid position and level from saved data
            tower_level = tower_data.get('level', 1)
            tower = ArrowTower(tower_data['grid_x'], tower_data['grid_y'], self.sprite_manager, level=tower_level)
            tower.health = tower_data.get('health', tower.health)
            self.state_manager.entities['towers'].append(tower)
            self.tower_manager.occupied_positions.add((tower.grid_x, tower.grid_y))  # type: ignore
            
        # Recreate allies
        for ally_data in saved_data.get('allies', []):
            ally = ElfWarrior(ally_data['x'], ally_data['y'], self.sprite_manager)
            ally.health = ally_data.get('health', ally.health)
            self.state_manager.entities['allies'].append(ally)
            
        print(f"🏗️ Recreated {len(saved_data.get('towers', []))} towers and {len(saved_data.get('allies', []))} allies from save")
        
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
        # Render terrain background first (appears behind everything)
        self._render_terrain_background()
        
        # Render enemy path first (so it appears under other elements)
        self._render_enemy_path()
        
        # Render no-build zones around path (if enabled)
        if self.show_build_zones:
            self._render_path_no_build_zones()
            
        # Render environment decorations (behind gameplay elements) - DISABLED FOR NOW
        # self._render_environment_decorations()
        
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
        """Render all enemy paths on the game map with environment textures."""
        if not ENEMY_PATHS:
            return
            
        # Draw all paths with different textures and colors
        for path_index, enemy_path in enumerate(ENEMY_PATHS):
            if len(enemy_path) < 2:
                continue
                
            # Get texture and color for this path
            texture_name = PATH_TEXTURES[path_index] if path_index < len(PATH_TEXTURES) else 'path_dirt'
            path_color = PATH_COLORS[path_index] if path_index < len(PATH_COLORS) else (255, 255, 255)
            path_color_dark = tuple(int(c * 0.7) for c in path_color)  # Darker outline
            
            # Get texture from sprite manager
            path_texture = self.sprite_manager.get_sprite(texture_name)
            
            # Debug: Print texture info for first time only
            if not hasattr(self, '_texture_debug_printed'):
                print(f"🎨 Route {path_index + 1}: Using texture '{texture_name}' - {'Found' if path_texture else 'NOT FOUND'}")
                if path_texture:
                    print(f"   Texture size: {path_texture.get_width()}x{path_texture.get_height()}")
                if path_index == len(ENEMY_PATHS) - 1:  # Last path
                    self._texture_debug_printed = True
            
            # Draw textured path segments
            for i in range(len(enemy_path) - 1):
                start_pos = enemy_path[i]
                end_pos = enemy_path[i + 1]
                
                if path_texture:
                    # Render simple textured path segment
                    self._render_simple_textured_path(start_pos, end_pos, path_texture, PATH_WIDTH)
                else:
                    # Fallback to colored lines if texture not available
                    pygame.draw.line(self.screen, path_color, start_pos, end_pos, PATH_WIDTH)
        
    def _render_simple_textured_path(self, start_pos, end_pos, texture, path_width):
        """Render a simple textured path segment by tiling texture rectangles."""
        import math
        
        # Calculate segment direction and length
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1] 
        segment_length = math.sqrt(dx**2 + dy**2)
        
        if segment_length == 0:
            return
            
        # Get texture dimensions
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        
        # Scale texture to match path width
        scale_factor = path_width / texture_height
        scaled_width = max(1, int(texture_width * scale_factor))
        scaled_height = max(1, int(texture_height * scale_factor))
        
        # Scale texture
        scaled_texture = pygame.transform.scale(texture, (scaled_width, scaled_height))
        
        # Calculate step size (use scaled width for continuous tiling)
        step_size = scaled_width * 0.9  # Slight overlap to prevent gaps
        
        # Calculate number of steps needed
        num_steps = max(1, int(segment_length / step_size) + 1)
        
        # Render texture tiles along the path with continuous coverage
        for i in range(num_steps):
            # Calculate position along the path using step size
            distance_along_path = i * step_size
            
            # Don't go beyond the segment
            if distance_along_path > segment_length:
                distance_along_path = segment_length
                
            # Calculate position
            progress = distance_along_path / segment_length if segment_length > 0 else 0
            tile_x = start_pos[0] + progress * dx
            tile_y = start_pos[1] + progress * dy
            
            # Position the tile
            tile_rect = scaled_texture.get_rect()
            tile_rect.center = (int(tile_x), int(tile_y))
            
            # Blit the textured tile
            self.screen.blit(scaled_texture, tile_rect)
        
    def _render_path_no_build_zones(self):
        """Render semi-transparent no-build zones around all enemy paths."""
        if not ENEMY_PATHS:
            return
            
        # Create a surface for the no-build zones with alpha transparency
        no_build_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Define no-build zone width (same as tower placement logic)
        no_build_width = PATH_WIDTH // 2 + TOWER_SIZE // 2 + 10  # Same as tower placement check
        
        # Draw no-build zones for each path
        for path_index, enemy_path in enumerate(ENEMY_PATHS):
            if len(enemy_path) < 2:
                continue
                
            # Use different alpha values for different paths to distinguish them
            alpha_values = [60, 50, 40]  # Different transparency for each path
            alpha = alpha_values[path_index] if path_index < len(alpha_values) else 45
            
            # Draw no-build zones for each path segment
            for i in range(len(enemy_path) - 1):
                start_pos = enemy_path[i]
                end_pos = enemy_path[i + 1]
                
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
                    pygame.draw.polygon(no_build_surface, (255, 0, 0, alpha), points)
        
        # Blit the no-build zones to the main screen
        self.screen.blit(no_build_surface, (0, 0))
        
    def _render_environment_decorations(self):
        """Render environment decorations like trees and rocks."""
        for decoration in self.decorations:
            sprite = decoration['sprite']
            x = decoration['x']
            y = decoration['y']
            
            # Draw the decoration sprite
            if sprite:
                sprite_rect = sprite.get_rect()
                sprite_rect.center = (x, y)
                self.screen.blit(sprite, sprite_rect)
        
    def _render_terrain_background(self):
        """Render the terrain background using grass and dirt tiles."""
        import random
        
        # Get terrain textures
        grass_texture = self.sprite_manager.get_sprite('grass_tile')
        dirt_texture = self.sprite_manager.get_sprite('dirt_tile')
        
        # If textures don't exist, create simple procedural ones
        if not grass_texture:
            grass_texture = self.sprite_manager.get_sprite('path_grass')
        if not dirt_texture:
            dirt_texture = self.sprite_manager.get_sprite('path_dirt')
            
        if not grass_texture and not dirt_texture:
            return  # No textures available
            
        # Use a reasonable tile size for terrain
        tile_size = 64
        
        # Calculate how many tiles we need
        tiles_x = (SCREEN_WIDTH // tile_size) + 2
        tiles_y = ((SCREEN_HEIGHT - HUD_HEIGHT) // tile_size) + 2
        
        # Castle area for avoiding terrain rendering
        castle_data = self.state_manager.castle_data
        castle_left = castle_data['x'] - CASTLE_WIDTH//2 - 20
        castle_right = castle_data['x'] + CASTLE_WIDTH//2 + 20
        castle_top = castle_data['y'] - CASTLE_HEIGHT//2 - 20
        castle_bottom = castle_data['y'] + CASTLE_HEIGHT//2 + 20
        
        # Set random seed for consistent terrain pattern
        random.seed(42)  # Fixed seed for consistent terrain
        
        # Render terrain tiles
        for tile_x in range(tiles_x):
            for tile_y in range(tiles_y):
                # Calculate tile position
                x = tile_x * tile_size
                y = tile_y * tile_size
                
                # Skip if in castle area
                if (x >= castle_left and x <= castle_right and 
                    y >= castle_top and y <= castle_bottom):
                    continue
                    
                # Skip if below HUD area
                if y >= SCREEN_HEIGHT - HUD_HEIGHT:
                    continue
                
                # Choose texture based on position and some randomness
                # Create natural patches of grass and dirt
                noise_value = self._simple_noise(tile_x, tile_y)
                
                # Bias towards grass (70% grass, 30% dirt for natural look)
                if noise_value > 0.3:
                    current_texture = grass_texture
                else:
                    current_texture = dirt_texture
                    
                # Use fallback if texture not available
                if not current_texture:
                    current_texture = dirt_texture if grass_texture else grass_texture
                    
                if current_texture:
                    # Scale texture to tile size
                    scaled_texture = pygame.transform.scale(current_texture, (tile_size, tile_size))
                    
                    # Position the tile
                    tile_rect = scaled_texture.get_rect()
                    tile_rect.topleft = (x, y)
                    
                    # Render the terrain tile
                    self.screen.blit(scaled_texture, tile_rect)
        
        # Reset random seed
        random.seed()
        
    def _simple_noise(self, x: int, y: int) -> float:
        """Generate simple noise for terrain variation."""
        import math
        
        # Simple pseudo-noise function for natural terrain patterns
        value = math.sin(x * 0.3) * math.cos(y * 0.3)
        value += math.sin(x * 0.1 + y * 0.1) * 0.5
        value += math.sin(x * 0.05) * math.cos(y * 0.07) * 0.3
        
        # Normalize to 0-1 range
        return (value + 2) / 4
        
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