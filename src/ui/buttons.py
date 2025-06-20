"""
UI button classes for interactive elements.
"""

import pygame
from typing import Tuple, Callable, Optional

from ..game.settings import *

class Button:
    """Basic button class."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None, 
                 color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = WHITE):
        """Initialize button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # State
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
        
        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, FONT_SIZE_SMALL)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events."""
        if not self.enabled:
            return False
            
        mouse_pos = pygame.mouse.get_pos()
        
        # Check hover
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left click
                self.is_pressed = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.is_hovered:
                self.is_pressed = False
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
            
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the button."""
        if not self.enabled:
            color = (60, 60, 60)
        elif self.is_pressed:
            color = (80, 80, 80)
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
            
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw border
        border_color = WHITE if self.enabled else (100, 100, 100)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def set_enabled(self, enabled: bool):
        """Set button enabled state."""
        self.enabled = enabled
        
    def set_text(self, text: str):
        """Set button text."""
        self.text = text

class IconButton(Button):
    """Button with an icon instead of text."""
    
    def __init__(self, x: int, y: int, width: int, height: int, icon_surface: pygame.Surface,
                 callback: Optional[Callable] = None,
                 color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150)):
        """Initialize icon button."""
        super().__init__(x, y, width, height, "", callback, color, hover_color)
        self.icon = icon_surface
        
    def render(self, screen: pygame.Surface):
        """Render the icon button."""
        if not self.enabled:
            color = (60, 60, 60)
        elif self.is_pressed:
            color = (80, 80, 80)
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
            
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw border
        border_color = WHITE if self.enabled else (100, 100, 100)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw icon
        if self.icon:
            icon_rect = self.icon.get_rect(center=self.rect.center)
            screen.blit(self.icon, icon_rect)

class ToggleButton(Button):
    """Button that can be toggled on/off."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 callback: Optional[Callable] = None,
                 on_color: Tuple[int, int, int] = GREEN,
                 off_color: Tuple[int, int, int] = RED):
        """Initialize toggle button."""
        super().__init__(x, y, width, height, text, callback)
        self.on_color = on_color
        self.off_color = off_color
        self.is_on = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle button events."""
        result = super().handle_event(event)
        if result and event.type == pygame.MOUSEBUTTONUP:
            self.is_on = not self.is_on
        return result
        
    def render(self, screen: pygame.Surface):
        """Render the toggle button."""
        # Override color based on toggle state
        self.color = self.on_color if self.is_on else self.off_color
        super().render(screen)
        
    def set_state(self, is_on: bool):
        """Set the toggle state."""
        self.is_on = is_on 