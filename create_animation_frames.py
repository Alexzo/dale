#!/usr/bin/env python3
"""
Utility script to create basic animation frames for the elf warrior.
This script will create simple animation frames by applying transformations to the existing sprite.
"""

import pygame
import os
import sys

# Add the src directory to the path
sys.path.append('src')

def create_simple_animations():
    """Create simple animation frames from the existing elf warrior sprite."""
    # Initialize pygame without display
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    
    # Paths
    assets_dir = os.path.join('assets', 'sprites', 'player')
    elf_warrior_path = os.path.join(assets_dir, 'elf_warrior.png')
    
    # Check if the main sprite exists
    if not os.path.exists(elf_warrior_path):
        print(f"❌ Elf warrior sprite not found at {elf_warrior_path}")
        print("Please make sure the elf warrior sprite is in the correct location.")
        return False
    
    try:
        # Load the main sprite
        main_sprite = pygame.image.load(elf_warrior_path).convert_alpha()
        original_size = main_sprite.get_size()
        print(f"✅ Loaded elf warrior sprite: {original_size[0]}x{original_size[1]}")
        
        # Create idle animation frames (4 frames with slight variations)
        idle_frames = []
        for i in range(4):
            frame = main_sprite.copy()
            
            # Add slight brightness variation for breathing effect
            brightness_offset = int(10 * (1 + 0.2 * (i % 2)))
            
            # Create a slight brightness overlay
            overlay = pygame.Surface(original_size, pygame.SRCALPHA)
            overlay.fill((brightness_offset, brightness_offset, brightness_offset, 20))
            frame.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            idle_frames.append(frame)
            
            # Save idle frame
            idle_filename = f"idle_{i + 1}.png"
            idle_path = os.path.join(assets_dir, idle_filename)
            pygame.image.save(frame, idle_path)
            print(f"✅ Created {idle_filename}")
        
        # Create walking animation frames (4 frames with slight position shifts)
        walk_frames = []
        for i in range(4):
            frame_surface = pygame.Surface(original_size, pygame.SRCALPHA)
            
            # Create slight horizontal movement effect
            x_offset = int(2 * (i % 2 - 0.5))  # -1, 0, 1, 0 pattern
            y_offset = int(1 * (i // 2 % 2))   # slight bounce
            
            # Blit the main sprite with offset
            frame_surface.blit(main_sprite, (x_offset, y_offset))
            
            # Add slight color tint for movement effect
            if i % 2 == 1:
                tint = pygame.Surface(original_size, pygame.SRCALPHA)
                tint.fill((10, 5, 0, 15))  # Slight brown tint
                frame_surface.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            walk_frames.append(frame_surface)
            
            # Save walking frame
            walk_filename = f"walk_{i + 1}.png"
            walk_path = os.path.join(assets_dir, walk_filename)
            pygame.image.save(frame_surface, walk_path)
            print(f"✅ Created {walk_filename}")
        
        print(f"\n🎉 Successfully created 8 animation frames!")
        print(f"📁 Animation frames saved in: {assets_dir}")
        print("\nAnimation frames created:")
        print("🚶 Walking: walk_1.png, walk_2.png, walk_3.png, walk_4.png")
        print("😌 Idle: idle_1.png, idle_2.png, idle_3.png, idle_4.png")
        
        return True
        
    except pygame.error as e:
        print(f"❌ Error processing sprite: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_spritesheet():
    """Create a spritesheet from individual frames (optional)."""
    assets_dir = os.path.join('assets', 'sprites', 'player')
    
    # Check if individual frames exist
    frames = []
    for anim_type in ['idle', 'walk']:
        for i in range(1, 5):
            frame_path = os.path.join(assets_dir, f"{anim_type}_{i}.png")
            if os.path.exists(frame_path):
                frame = pygame.image.load(frame_path).convert_alpha()
                frames.append(frame)
            else:
                print(f"⚠️  Frame not found: {frame_path}")
                return False
    
    if len(frames) == 8:
        # Assuming all frames are the same size
        frame_size = frames[0].get_size()
        spritesheet_width = frame_size[0] * 4  # 4 frames per row
        spritesheet_height = frame_size[1] * 2  # 2 rows (idle + walk)
        
        spritesheet = pygame.Surface((spritesheet_width, spritesheet_height), pygame.SRCALPHA)
        
        # Arrange frames: idle on top row, walk on bottom row
        for i, frame in enumerate(frames):
            row = i // 4
            col = i % 4
            x = col * frame_size[0]
            y = row * frame_size[1]
            spritesheet.blit(frame, (x, y))
        
        # Save spritesheet
        spritesheet_path = os.path.join(assets_dir, 'elf_warrior_spritesheet.png')
        pygame.image.save(spritesheet, spritesheet_path)
        print(f"✅ Created spritesheet: {spritesheet_path}")
        return True
    
    return False

if __name__ == "__main__":
    print("🎨 Elf Warrior Animation Frame Creator")
    print("=" * 40)
    
    if create_simple_animations():
        print("\n📋 Creating optional spritesheet...")
        if create_spritesheet():
            print("✅ Spritesheet created successfully!")
        else:
            print("⚠️  Could not create spritesheet (individual frames will be used)")
        
        print("\n🎮 You can now run the game to see the animated elf warrior!")
        print("💡 The animation system will automatically switch between idle and walking animations.")
    else:
        print("\n❌ Failed to create animation frames")
        print("💡 Make sure the elf warrior sprite exists in assets/sprites/player/elf_warrior.png")
    
    pygame.quit() 