#!/usr/bin/env python3
"""
Notifications Module - Windows Toast Notifications and Sounds
Provides user-friendly notifications for completion and errors
"""

import sys
import winsound
from typing import Optional

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False

from .logger import Logger


class Notifier:
    """
    Handles user notifications via Windows toast notifications and sounds
    
    Features:
    - Windows 10/11 toast notifications
    - System sounds for events
    - Graceful fallback if dependencies missing
    """
    
    def __init__(self, enable_toast=True, enable_sound=True):
        self.logger = Logger("Notifier")
        self.enable_toast = enable_toast and TOAST_AVAILABLE
        self.enable_sound = enable_sound
        
        if self.enable_toast:
            try:
                self.toaster = ToastNotifier()
            except Exception as e:
                self.logger.warning(f"⚠️ Toast notifications unavailable: {e}")
                self.enable_toast = False
        else:
            if enable_toast and not TOAST_AVAILABLE:
                self.logger.debug("ℹ️ win10toast not installed - toast notifications disabled")
    
    def notify_completion(self, season_name: str, duration_minutes: float) -> None:
        """
        Notify user of successful generation completion
        
        Args:
            season_name: Name of completed season
            duration_minutes: Time taken in minutes
        """
        title = "NGIO Automation Suite"
        message = f"✅ {season_name} grass cache generation completed!\nTime: {duration_minutes:.1f} minutes"
        
        if self.enable_toast:
            try:
                self.toaster.show_toast(
                    title,
                    message,
                    duration=10,
                    icon_path=None,  # Use default icon
                    threaded=True
                )
            except Exception as e:
                self.logger.debug(f"Toast notification failed: {e}")
        
        if self.enable_sound:
            self.play_completion_sound()
    
    def notify_error(self, error_message: str) -> None:
        """
        Notify user of error
        
        Args:
            error_message: Description of error
        """
        title = "NGIO Automation Suite - Error"
        
        # Truncate message if too long for toast
        if len(error_message) > 200:
            error_message = error_message[:197] + "..."
        
        if self.enable_toast:
            try:
                self.toaster.show_toast(
                    title,
                    f"❌ {error_message}",
                    duration=15,
                    icon_path=None,
                    threaded=True
                )
            except Exception as e:
                self.logger.debug(f"Toast notification failed: {e}")
        
        if self.enable_sound:
            self.play_error_sound()
    
    def notify_progress(self, message: str, season_name: Optional[str] = None) -> None:
        """
        Notify user of progress milestone
        
        Args:
            message: Progress message
            season_name: Current season (optional)
        """
        title = f"NGIO - {season_name}" if season_name else "NGIO Automation Suite"
        
        if self.enable_toast:
            try:
                self.toaster.show_toast(
                    title,
                    message,
                    duration=5,
                    icon_path=None,
                    threaded=True
                )
            except Exception as e:
                self.logger.debug(f"Toast notification failed: {e}")
    
    def play_completion_sound(self) -> None:
        """Play Windows completion sound"""
        if sys.platform == 'win32':
            try:
                # MB_OK sound (asterisk/information sound)
                winsound.MessageBeep(winsound.MB_OK)
            except Exception as e:
                self.logger.debug(f"Sound playback failed: {e}")
    
    def play_error_sound(self) -> None:
        """Play Windows error sound"""
        if sys.platform == 'win32':
            try:
                # MB_ICONHAND sound (critical stop/error sound)
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception as e:
                self.logger.debug(f"Sound playback failed: {e}")
    
    def play_warning_sound(self) -> None:
        """Play Windows warning sound"""
        if sys.platform == 'win32':
            try:
                # MB_ICONEXCLAMATION sound (exclamation/warning sound)
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception as e:
                self.logger.debug(f"Sound playback failed: {e}")


# Convenience function for quick notifications
def notify_user(message: str, is_error=False) -> None:
    """
    Quick notification helper
    
    Args:
        message: Message to display
        is_error: Whether this is an error notification
    """
    notifier = Notifier()
    if is_error:
        notifier.notify_error(message)
    else:
        notifier.notify_progress(message)


if __name__ == "__main__":
    # Test notifications
    print("Testing notifications...")
    notifier = Notifier()
    
    print("1. Testing completion notification")
    notifier.notify_completion("Winter", 45.5)
    
    import time
    time.sleep(2)
    
    print("2. Testing error notification")
    notifier.notify_error("Test error message")
    
    time.sleep(2)
    
    print("3. Testing progress notification")
    notifier.notify_progress("Generation started", "Spring")
    
    print("Notifications test complete")

