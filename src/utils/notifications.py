#!/usr/bin/env python3
"""
Notifications Module - Windows Toast Notifications and Sounds

Provides user-friendly notifications for completion, errors, and progress.

Design notes (v1.5.2 hotfix):
- Replaced `win10toast` with `winotify` because `win10toast` is unmaintained and
  triggers `pkg_resources.DistributionNotFound` inside the bundled PyInstaller EXE
  on many Windows 11 setups. `winotify` is pure-Python, has no `pkg_resources`
  runtime lookup, and bundles cleanly.
- Triple-layered defense so a broken/missing notification backend NEVER blocks
  the actual grass cache generation:
    1. Import guard         -> ImportError gracefully disables toasts.
    2. Instantiation guard  -> any error constructing Notification() disables toasts.
    3. Per-call guard       -> show() failures are swallowed and logged at debug.
- Auto-detects Wine / Proton (Steam Deck) and disables toasts there since the
  PowerShell shim winotify uses is unreliable under Wine.
- `winsound` is stdlib, so sound paths only need a single try/except.
"""

import os
import sys
from typing import Optional

try:
    import winsound
    _WINSOUND_AVAILABLE = True
except ImportError:
    _WINSOUND_AVAILABLE = False

# Layer 1: import guard for the toast backend
try:
    from winotify import Notification as _WinotifyNotification, audio as _winotify_audio
    _TOAST_BACKEND = "winotify"
    _TOAST_AVAILABLE = True
except Exception:
    _TOAST_BACKEND = None
    _TOAST_AVAILABLE = False

from .logger import Logger


def _running_under_wine_or_proton() -> bool:
    """
    Detect Wine / Proton (Steam Deck) environments.

    Wine sets WINELOADER and/or WINEPREFIX. Proton inherits those from Wine.
    Toast notifications via PowerShell are unreliable under Wine, so we
    silently disable them rather than spamming errors.
    """
    return bool(os.environ.get("WINELOADER") or os.environ.get("WINEPREFIX"))


class Notifier:
    """
    User notifications via Windows toast notifications and sounds.

    Public API is stable across backend swaps:
        notify_completion(season_name, duration_minutes)
        notify_error(error_message)
        notify_progress(message, season_name=None)
        play_completion_sound() / play_error_sound() / play_warning_sound()

    All methods are guaranteed to be non-throwing.
    """

    APP_ID = "NGIO Automation Suite"

    def __init__(self, enable_toast: bool = True, enable_sound: bool = True):
        self.logger = Logger("Notifier")

        # Sound subsystem (winsound is stdlib so it's basically always available
        # on Windows, but we still gate on import success).
        self.enable_sound = bool(enable_sound) and _WINSOUND_AVAILABLE

        # Toast subsystem - apply user preference + auto-detect failure modes.
        self.enable_toast = bool(enable_toast)

        if self.enable_toast and not _TOAST_AVAILABLE:
            # Import failed. Don't crash, just disable toasts.
            self.enable_toast = False
            self.logger.debug(
                "Toast backend not importable - notifications via toast disabled"
            )

        if self.enable_toast and _running_under_wine_or_proton():
            # Wine / Proton: PowerShell-based toasts are unreliable here.
            self.enable_toast = False
            self.logger.info(
                "Wine/Proton detected - toast notifications disabled (sounds still active)"
            )

        # Layer 2: instantiation-time guard. winotify constructs notifications
        # lazily per-call, so there's nothing to construct here, but if a future
        # backend needs an instance we'd put the guard here. Probe the API
        # surface once so a broken install is caught now, not on first toast.
        if self.enable_toast:
            try:
                # Cheap probe: build (but do not show) a Notification.
                _WinotifyNotification(
                    app_id=self.APP_ID, title="probe", msg="probe"
                )
            except Exception as exc:
                self.enable_toast = False
                self.logger.warning(
                    f"Toast backend probe failed - notifications via toast disabled ({exc})"
                )

        self.logger.debug(
            f"Notifier ready: toast={'on' if self.enable_toast else 'off'}"
            f"{f' [{_TOAST_BACKEND}]' if self.enable_toast else ''}, "
            f"sound={'on' if self.enable_sound else 'off'}"
        )

    def _show_toast(self, title: str, message: str) -> None:
        """
        Layer 3: per-call guard. Never raises, never blocks generation.
        """
        if not self.enable_toast:
            return
        try:
            toast = _WinotifyNotification(
                app_id=self.APP_ID,
                title=title,
                msg=message,
            )
            toast.show()
        except Exception as exc:
            self.logger.debug(f"Toast show failed (suppressed): {exc}")

    def notify_completion(self, season_name: str, duration_minutes: float) -> None:
        message = (
            f"{season_name} grass cache generation completed!\n"
            f"Time: {duration_minutes:.1f} minutes"
        )
        self._show_toast("NGIO Automation Suite", message)
        if self.enable_sound:
            self.play_completion_sound()

    def notify_error(self, error_message: str) -> None:
        if len(error_message) > 200:
            error_message = error_message[:197] + "..."
        self._show_toast("NGIO Automation Suite - Error", error_message)
        if self.enable_sound:
            self.play_error_sound()

    def notify_progress(
        self, message: str, season_name: Optional[str] = None
    ) -> None:
        title = (
            f"NGIO - {season_name}" if season_name else "NGIO Automation Suite"
        )
        self._show_toast(title, message)

    def play_completion_sound(self) -> None:
        if not self.enable_sound:
            return
        try:
            winsound.MessageBeep(winsound.MB_OK)
        except Exception as exc:
            self.logger.debug(f"Completion sound failed (suppressed): {exc}")

    def play_error_sound(self) -> None:
        if not self.enable_sound:
            return
        try:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception as exc:
            self.logger.debug(f"Error sound failed (suppressed): {exc}")

    def play_warning_sound(self) -> None:
        if not self.enable_sound:
            return
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as exc:
            self.logger.debug(f"Warning sound failed (suppressed): {exc}")


def notify_user(message: str, is_error: bool = False) -> None:
    """Quick one-shot notification helper."""
    notifier = Notifier()
    if is_error:
        notifier.notify_error(message)
    else:
        notifier.notify_progress(message)


if __name__ == "__main__":
    print("Testing notifications...")
    notifier = Notifier()

    print("1. Completion notification")
    notifier.notify_completion("Winter", 45.5)

    import time
    time.sleep(2)

    print("2. Error notification")
    notifier.notify_error("Test error message")

    time.sleep(2)

    print("3. Progress notification")
    notifier.notify_progress("Generation started", "Spring")

    print("Notifications test complete")
