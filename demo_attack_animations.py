#!/usr/bin/env python3
"""
Demo script showing attack animation system for Dale.
"""

import pygame
import math
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.animations import DirectionalAnimationManager, Animation

def create_sample_character_sprite(size=64):
    """Create a simple character sprite for demonstration."""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Body (ellipse)
    pygame.draw.ellipse(sprite, (0, 100, 200), (size//4, size//3, size//2, size//2))
    
    # Head (circle)
    pygame.draw.circle(sprite, (255, 220, 177), (size//2, size//4), size//8)
    
    # Simple face
    pygame.draw.circle(sprite, (0, 0, 0), (size//2 - 6, size//4 - 3), 2)  # Left eye
    pygame.draw.circle(sprite, (0, 0, 0), (size//2 + 6, size//4 - 3), 2)  # Right eye
    
    return sprite

def create_attack_frames(base_frame):
    """Create attack animation frames by adding sword effect."""
    frames = []
    
    for i in range(4):
        frame = base_frame.copy()
        
        # Create sword overlay
        sword_surface = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        
        progress = i / 3.0  # 0.0 to 1.0
        
        # Sword position and rotation
        center_x = base_frame.get_width() // 2
        center_y = base_frame.get_height() // 2
        
        # Sword swing angle (-60 to +60 degrees)
        angle = -60 + progress * 120
        sword_length = 20
        sword_width = 3
        
        # Calculate sword tip position
        end_x = center_x + int(sword_length * math.cos(math.radians(angle)))
        end_y = center_y + int(sword_length * math.sin(math.radians(angle)))
        
        # Draw sword blade
        pygame.draw.line(sword_surface, (200, 200, 220), 
                        (center_x, center_y), (end_x, end_y), sword_width)
        
        # Draw sword hilt
        hilt_x = center_x - int(5 * math.cos(math.radians(angle)))
        hilt_y = center_y - int(5 * math.sin(math.radians(angle)))
        pygame.draw.circle(sword_surface, (139, 69, 19), (hilt_x, hilt_y), 3)
        
        # Add energy effect around sword at peak of swing
        if i == 1 or i == 2:
            for j in range(3):
                effect_radius = 8 + j * 4
                effect_alpha = 80 - j * 25
                effect_color = (255, 255, 100, effect_alpha)
                
                # Create temporary surface for alpha blending
                effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, effect_color[:3], 
                                 (effect_radius, effect_radius), effect_radius)
                
                # Position effect at sword tip
                effect_rect = effect_surface.get_rect()
                effect_rect.center = (end_x, end_y)
                sword_surface.blit(effect_surface, effect_rect)
        
        # Combine character with sword
        frame.blit(sword_surface, (0, 0))
        frames.append(frame)
        
    return frames

def demo_attack_animations():
    """Demonstrate the attack animation system."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dale - Attack Animation Demo")
    clock = pygame.time.Clock()
    
    # Create sample character sprite
    base_sprite = create_sample_character_sprite(64)
    
    # Create attack frames
    attack_frames = create_attack_frames(base_sprite)
    
    # Create directional animation manager
    anim_manager = DirectionalAnimationManager()
    
    # Create animations for each direction
    directions = ['down', 'up', 'left', 'right']
    for direction in directions:
        # Create directional variations of attack frames
        if direction == 'down':
            frames = attack_frames
        elif direction == 'up':
            frames = [pygame.transform.flip(frame, False, True) for frame in attack_frames]
        elif direction == 'left':
            frames = [pygame.transform.flip(frame, True, False) for frame in attack_frames]
        elif direction == 'right':
            frames = attack_frames  # Use same as down for this demo
            
        # Add attack animation for this direction
        attack_anim = Animation(frames, 0.08, False)  # Fast, non-looping
        anim_manager.add_directional_animation('attack', direction, attack_anim)
        
        # Add idle animation (just the base sprite)
        idle_anim = Animation([base_sprite], 0.5, True)
        anim_manager.add_directional_animation('idle', direction, idle_anim)
    
    # Demo state
    current_direction = 'down'
    is_attacking = False
    attack_timer = 0.0
    font = pygame.font.Font(None, 36)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_attacking:
                    # Start attack
                    is_attacking = True
                    attack_timer = 0.32  # Attack duration
                    anim_manager.set_animation('attack', current_direction, force_restart=True)
                elif event.key == pygame.K_UP:
                    current_direction = 'up'
                elif event.key == pygame.K_DOWN:
                    current_direction = 'down'
                elif event.key == pygame.K_LEFT:
                    current_direction = 'left'
                elif event.key == pygame.K_RIGHT:
                    current_direction = 'right'
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update attack timer
        if is_attacking:
            attack_timer -= dt
            if attack_timer <= 0:
                is_attacking = False
                anim_manager.set_animation('idle', current_direction)
        
        # Update animation
        anim_manager.update(dt)
        
        # Render
        screen.fill((50, 100, 50))  # Dark green background
        
        # Draw character in center
        current_frame = anim_manager.get_current_frame()
        if current_frame:
            char_rect = current_frame.get_rect()
            char_rect.center = (400, 300)
            screen.blit(current_frame, char_rect)
        
        # Draw instructions
        instructions = [
            "Attack Animation Demo",
            "",
            "SPACE: Attack",
            "Arrow Keys: Change Direction",
            "ESC: Exit",
            "",
            f"Current Direction: {current_direction.upper()}",
            f"Animation: {'ATTACK' if is_attacking else 'IDLE'}",
        ]
        
        y_offset = 50
        for instruction in instructions:
            if instruction:
                text = font.render(instruction, True, (255, 255, 255))
                screen.blit(text, (50, y_offset))
            y_offset += 35
        
        # Draw direction indicator
        direction_text = font.render(f"Facing: {current_direction.upper()}", True, (255, 255, 0))
        screen.blit(direction_text, (400, 150))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    print("🎮 Dale - Attack Animation Demo")
    print("=" * 40)
    print("This demo shows the attack animation system:")
    print("• Directional attack animations")
    print("• Sword swing effects with energy")
    print("• Non-looping attack animations")
    print("• Smooth transitions between idle and attack")
    print("")
    print("Controls:")
    print("• SPACE: Trigger attack animation")
    print("• Arrow Keys: Change facing direction")
    print("• ESC: Exit demo")
    print("")
    print("Starting demo...")
    
    try:
        demo_attack_animations()
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc() 