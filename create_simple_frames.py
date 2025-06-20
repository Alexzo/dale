#!/usr/bin/env python3
"""
Simple script to create basic animation frames by copying the existing elf warrior sprite.
"""

import os
import shutil

def create_basic_animation_frames():
    """Create basic animation frames by copying the existing sprite."""
    
    # Paths
    assets_dir = os.path.join('assets', 'sprites', 'player')
    elf_warrior_path = os.path.join(assets_dir, 'elf_warrior.png')
    
    # Check if the main sprite exists
    if not os.path.exists(elf_warrior_path):
        print(f"❌ Elf warrior sprite not found at {elf_warrior_path}")
        print("Please make sure the elf warrior sprite is in the correct location.")
        return False
    
    try:
        print(f"✅ Found elf warrior sprite at {elf_warrior_path}")
        
        # Create idle animation frames (4 copies)
        for i in range(1, 5):
            idle_filename = f"idle_{i}.png"
            idle_path = os.path.join(assets_dir, idle_filename)
            shutil.copy2(elf_warrior_path, idle_path)
            print(f"✅ Created {idle_filename}")
        
        # Create walking animation frames (4 copies)
        for i in range(1, 5):
            walk_filename = f"walk_{i}.png"
            walk_path = os.path.join(assets_dir, walk_filename)
            shutil.copy2(elf_warrior_path, walk_path)
            print(f"✅ Created {walk_filename}")
        
        print(f"\n🎉 Successfully created 8 animation frames!")
        print(f"📁 Animation frames saved in: {assets_dir}")
        print("\nAnimation frames created:")
        print("🚶 Walking: walk_1.png, walk_2.png, walk_3.png, walk_4.png")
        print("😌 Idle: idle_1.png, idle_2.png, idle_3.png, idle_4.png")
        print("\n💡 Note: These are basic copies. For more advanced animation,")
        print("   you can create custom frames using a pixel art editor like Aseprite.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating frames: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Simple Elf Warrior Animation Frame Creator")
    print("=" * 45)
    
    if create_basic_animation_frames():
        print("\n🎮 You can now run the game to see the animation system!")
        print("💡 The elf warrior will now use the animation system with:")
        print("   - Idle animation when standing still")
        print("   - Walking animation when moving")
    else:
        print("\n❌ Failed to create animation frames")
        print("💡 Make sure the elf warrior sprite exists in assets/sprites/player/elf_warrior.png") 