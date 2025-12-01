#!/usr/bin/env python3
"""
State Manager - Resume from Interruption (v1.3.0+)
Saves and restores automation state for crash recovery
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

from .logger import Logger


@dataclass
class AutomationState:
    """
    Represents the current state of automation
    
    Allows resuming from interruption without losing progress
    """
    # Current execution
    current_season: Optional[str] = None
    completed_seasons: List[str] = None
    failed_seasons: List[str] = None
    
    # Progress tracking
    retry_count: int = 0
    total_retries: int = 0
    files_processed: int = 0
    
    # Timing
    start_time: float = 0.0
    last_updated: float = 0.0
    season_start_time: float = 0.0
    
    # Configuration snapshot
    skyrim_path: str = ""
    output_directory: str = ""
    seasons_to_generate: List[str] = None
    
    # Status flags
    is_running: bool = False
    is_paused: bool = False
    interrupted: bool = False
    
    def __post_init__(self):
        if self.completed_seasons is None:
            self.completed_seasons = []
        if self.failed_seasons is None:
            self.failed_seasons = []
        if self.seasons_to_generate is None:
            self.seasons_to_generate = []


class StateManager:
    """
    Manages automation state for crash recovery and resumption
    
    Features:
    - Automatic state saving
    - State restoration after crashes
    - Progress preservation
    - Interrupt detection
    - Atomic file operations
    """
    
    STATE_FILE = ".ngio_automation_state.json"
    BACKUP_FILE = ".ngio_automation_state.backup.json"
    
    def __init__(self, state_directory: str = "."):
        self.logger = Logger("StateManager")
        self.state_directory = Path(state_directory)
        self.state_file = self.state_directory / self.STATE_FILE
        self.backup_file = self.state_directory / self.BACKUP_FILE
        
        # Ensure directory exists
        self.state_directory.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, state: AutomationState) -> bool:
        """
        Save current automation state to disk
        
        Args:
            state: AutomationState to save
            
        Returns:
            True if successful
        """
        try:
            # Update timestamp
            state.last_updated = time.time()
            
            # Convert to dict
            state_dict = asdict(state)
            
            # Create backup of existing state first
            if self.state_file.exists():
                try:
                    self.state_file.replace(self.backup_file)
                except Exception as e:
                    self.logger.warning(f"Failed to create backup: {e}")
            
            # Write new state atomically
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2)
            
            # Atomic replace
            temp_file.replace(self.state_file)
            
            self.logger.debug(f"💾 State saved: {state.current_season or 'idle'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False
    
    def load_state(self) -> Optional[AutomationState]:
        """
        Load saved automation state from disk
        
        Returns:
            AutomationState if found and valid, None otherwise
        """
        try:
            if not self.state_file.exists():
                self.logger.debug("No saved state found")
                return None
            
            # Try loading main state file
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_dict = json.load(f)
                
                state = AutomationState(**state_dict)
                
                # Check if state is recent (< 7 days old)
                age_days = (time.time() - state.last_updated) / 86400
                if age_days > 7:
                    self.logger.warning(f"⚠️ Saved state is {age_days:.1f} days old - ignoring")
                    return None
                
                self.logger.info(f"📂 Loaded saved state: {state.current_season or 'idle'}")
                return state
                
            except json.JSONDecodeError:
                self.logger.warning("State file corrupted, trying backup...")
                
                # Try backup
                if self.backup_file.exists():
                    with open(self.backup_file, 'r', encoding='utf-8') as f:
                        state_dict = json.load(f)
                    
                    state = AutomationState(**state_dict)
                    self.logger.info("✅ Restored from backup")
                    return state
                else:
                    self.logger.error("No valid backup found")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return None
    
    def has_saved_state(self) -> bool:
        """
        Check if there's a saved state file
        
        Returns:
            True if state file exists
        """
        return self.state_file.exists()
    
    def clear_state(self) -> bool:
        """
        Clear saved state (after successful completion)
        
        Returns:
            True if successful
        """
        try:
            if self.state_file.exists():
                self.state_file.unlink()
                self.logger.debug("🗑️ State file cleared")
            
            if self.backup_file.exists():
                self.backup_file.unlink()
                self.logger.debug("🗑️ Backup file cleared")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear state: {e}")
            return False
    
    def check_for_interruption(self) -> Optional[AutomationState]:
        """
        Check if there was a previous interrupted session
        
        Returns:
            AutomationState if interruption detected, None otherwise
        """
        state = self.load_state()
        
        if state is None:
            return None
        
        # Check if was running but not properly closed
        if state.is_running and not state.interrupted:
            self.logger.warning("⚠️ Detected abnormal termination (crash/force quit)")
            state.interrupted = True
            return state
        
        # Check if was paused
        if state.is_paused:
            self.logger.info("⏸️ Detected paused session")
            return state
        
        # Normal completion - no need to resume
        if not state.is_running:
            return None
        
        return state
    
    def mark_interrupted(self) -> bool:
        """
        Mark current state as interrupted (for emergency shutdown)
        
        Returns:
            True if successful
        """
        state = self.load_state()
        if state:
            state.interrupted = True
            state.is_running = False
            return self.save_state(state)
        return False
    
    def get_resumable_seasons(self, state: AutomationState) -> List[str]:
        """
        Get list of seasons that still need to be generated
        
        Args:
            state: Current automation state
            
        Returns:
            List of season names to generate
        """
        if not state.seasons_to_generate:
            return []
        
        # Remove completed and failed seasons
        remaining = [
            season for season in state.seasons_to_generate
            if season not in state.completed_seasons 
            and season not in state.failed_seasons
        ]
        
        # If current season was in progress, include it
        if state.current_season and state.current_season not in state.completed_seasons:
            if state.current_season not in remaining:
                remaining.insert(0, state.current_season)
        
        return remaining
    
    def create_state_from_config(self, config) -> AutomationState:
        """
        Create initial automation state from config
        
        Args:
            config: AutomationConfig instance
            
        Returns:
            New AutomationState
        """
        state = AutomationState(
            start_time=time.time(),
            last_updated=time.time(),
            skyrim_path=config.skyrim_path,
            output_directory=config.output_directory,
            seasons_to_generate=[s.display_name for s in config.seasons_to_generate],
            is_running=True,
            is_paused=False,
            interrupted=False
        )
        
        return state
    
    def format_state_summary(self, state: AutomationState) -> str:
        """
        Generate human-readable state summary
        
        Args:
            state: AutomationState to summarize
            
        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("📊 SAVED STATE SUMMARY")
        lines.append("=" * 60)
        
        # Current progress
        if state.current_season:
            lines.append(f"Current Season: {state.current_season}")
        
        lines.append(f"Completed: {', '.join(state.completed_seasons) if state.completed_seasons else 'None'}")
        lines.append(f"Failed: {', '.join(state.failed_seasons) if state.failed_seasons else 'None'}")
        
        # Remaining seasons
        remaining = self.get_resumable_seasons(state)
        if remaining:
            lines.append(f"Remaining: {', '.join(remaining)}")
        
        # Timing
        if state.start_time:
            elapsed = time.time() - state.start_time
            lines.append(f"Elapsed Time: {elapsed/60:.1f} minutes")
        
        # Last update
        if state.last_updated:
            last_update_time = datetime.fromtimestamp(state.last_updated)
            lines.append(f"Last Updated: {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Status
        status = "Running" if state.is_running else "Stopped"
        if state.is_paused:
            status = "Paused"
        if state.interrupted:
            status = "Interrupted"
        lines.append(f"Status: {status}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# === HELPER FUNCTIONS ===

def create_state_manager(state_directory: str = ".") -> StateManager:
    """
    Create StateManager instance
    
    Args:
        state_directory: Directory for state files
        
    Returns:
        StateManager instance
    """
    return StateManager(state_directory)


if __name__ == "__main__":
    # Example usage and testing
    print("State Manager - Testing")
    print("=" * 60)
    
    manager = StateManager()
    
    # Create test state
    state = AutomationState(
        current_season="Winter",
        completed_seasons=["Summer"],
        seasons_to_generate=["Summer", "Winter", "Spring", "Autumn"],
        start_time=time.time() - 3600,  # 1 hour ago
        is_running=True
    )
    
    # Save state
    print("\n1. Saving test state...")
    if manager.save_state(state):
        print("   ✅ State saved")
    
    # Load state
    print("\n2. Loading state...")
    loaded_state = manager.load_state()
    if loaded_state:
        print("   ✅ State loaded")
        print(manager.format_state_summary(loaded_state))
    
    # Check for interruption
    print("\n3. Checking for interruption...")
    interrupted = manager.check_for_interruption()
    if interrupted:
        print(f"   ⚠️ Interrupted session detected")
        remaining = manager.get_resumable_seasons(interrupted)
        print(f"   Remaining seasons: {remaining}")
    
    # Clear state
    print("\n4. Clearing state...")
    if manager.clear_state():
        print("   ✅ State cleared")

