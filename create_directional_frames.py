#!/usr/bin/env python3
"""
Script to create directional animation frames for the elf warrior.
This will create frames for up, down, left, right directions from existing frames.
"""

import pygame
import os
import sys

def create_directional_frames():
    """Create directional animation frames from existing frames."""
    # Initialize pygame with dummy display
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))  # Create minimal display
    
    # Paths
    assets_dir = os.path.join('assets', 'sprites', 'player')
    
    # Animation types and directions
    animation_types = ['idle', 'walk']
    directions = ['up', 'down', 'left', 'right']
    
    print("🎨 Creating Directional Animation Frames")
    print("=" * 45)
    
    for anim_type in animation_types:
        print(f"\n📽️  Processing {anim_type} animations...")
        
        # Load base frames (currently all the same)
        base_frames = []
        for i in range(1, 5):
            frame_path = os.path.join(assets_dir, f"{anim_type}_{i}.png")
            if os.path.exists(frame_path):
                try:
                    frame = pygame.image.load(frame_path).convert_alpha()
                    base_frames.append(frame)
                except pygame.error as e:
                    print(f"❌ Error loading {frame_path}: {e}")
                    return False
            else:
                print(f"❌ Base frame not found: {frame_path}")
                return False
        
        if len(base_frames) != 4:
            print(f"❌ Expected 4 frames for {anim_type}, found {len(base_frames)}")
            continue
            
        # Create directional variations
        for direction in directions:
            print(f"   Creating {direction} frames...")
            
            for i, frame in enumerate(base_frames):
                # Apply transformations based on direction
                if direction == 'down':
                    # Down is the original direction
                    transformed_frame = frame.copy()
                elif direction == 'up':
                    # Flip vertically for up
                    transformed_frame = pygame.transform.flip(frame, False, True)
                elif direction == 'left':
                    # Flip horizontally for left
                    transformed_frame = pygame.transform.flip(frame, True, False)
                elif direction == 'right':
                    # Right uses original (assuming character naturally faces forward/down)
                    # You might want to flip horizontally if the character faces left naturally
                    transformed_frame = frame.copy()
                
                # Save the directional frame
                filename = f"{anim_type}_{direction}_{i + 1}.png"
                filepath = os.path.join(assets_dir, filename)
                
                try:
                    pygame.image.save(transformed_frame, filepath)
                    print(f"   ✅ Created {filename}")
                except pygame.error as e:
                    print(f"   ❌ Error saving {filename}: {e}")
    
    print(f"\n🎉 Directional animation frames created!")
    print("\n📁 New frame structure:")
    print("   idle_down_1.png to idle_down_4.png")
    print("   idle_up_1.png to idle_up_4.png")
    print("   idle_left_1.png to idle_left_4.png")
    print("   idle_right_1.png to idle_right_4.png")
    print("   walk_down_1.png to walk_down_4.png")
    print("   walk_up_1.png to walk_up_4.png")
    print("   walk_left_1.png to walk_left_4.png")
    print("   walk_right_1.png to walk_right_4.png")
    
    return True

def update_sprite_loader():
    """Update the sprite loading to use directional frames."""
    print("\n💡 To use these directional frames, update your sprite loader to:")
    print("   1. Look for frames named: {animation}_{direction}_{number}.png")
    print("   2. Group them by animation and direction")
    print("   3. Create separate Animation objects for each direction")
    
    print("\n🎮 Controls:")
    print("   WASD or Arrow Keys - Character will face the movement direction")
    print("   Different walking animations for up, down, left, right")

if __name__ == "__main__":
    if create_directional_frames():
        update_sprite_loader()
        print("\n🚀 Ready to test directional animations!")
    else:
        print("\n❌ Failed to create directional frames")
        print("💡 Make sure the base animation frames exist in assets/sprites/player/")
    
    pygame.quit() 