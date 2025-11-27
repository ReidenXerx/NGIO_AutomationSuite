#!/usr/bin/env python3
"""
Progress Estimator - Time Estimates (v1.4.0+)
Provides accurate ETA calculations based on historical data
"""

import time
import json
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from statistics import mean, median

from .logger import Logger


@dataclass
class GenerationTiming:
    """Timing data for a single generation"""
    season: str
    duration_seconds: float
    files_generated: int
    timestamp: float
    mod_count: Optional[int] = None
    worldspace_count: Optional[int] = None


class ProgressEstimator:
    """
    Estimates completion time based on historical data
    
    Features:
    - Learns from past generations
    - Accounts for season differences
    - Considers mod list size
    - Provides confidence intervals
    """
    
    HISTORY_FILE = ".ngio_timing_history.json"
    MAX_HISTORY_ENTRIES = 100
    
    def __init__(self, history_directory: str = "."):
        self.logger = Logger("ProgressEstimator")
        self.history_directory = Path(history_directory)
        self.history_file = self.history_directory / self.HISTORY_FILE
        self.history: List[GenerationTiming] = []
        
        self._load_history()
    
    def record_generation(self, 
                         season: str,
                         duration_seconds: float,
                         files_generated: int,
                         mod_count: Optional[int] = None):
        """
        Record a completed generation
        
        Args:
            season: Season name
            duration_seconds: How long it took
            files_generated: Number of files created
            mod_count: Number of mods (if known)
        """
        timing = GenerationTiming(
            season=season,
            duration_seconds=duration_seconds,
            files_generated=files_generated,
            timestamp=time.time(),
            mod_count=mod_count
        )
        
        self.history.append(timing)
        self._save_history()
        
        self.logger.debug(f"Recorded timing: {season} - {duration_seconds/60:.1f} min")
    
    def estimate_season_time(self, season: str) -> Optional[float]:
        """
        Estimate time for a specific season
        
        Args:
            season: Season name
            
        Returns:
            Estimated seconds, or None if no data
        """
        # Get recent timings for this season (last 10)
        season_timings = [t for t in self.history if t.season == season][-10:]
        
        if not season_timings:
            # No historical data - use defaults
            return self._get_default_estimate()
        
        # Use median to avoid outliers
        durations = [t.duration_seconds for t in season_timings]
        return median(durations)
    
    def estimate_total_time(self, seasons: List[str]) -> Dict[str, any]:
        """
        Estimate total time for multiple seasons
        
        Args:
            seasons: List of season names
            
        Returns:
            Dictionary with estimates
        """
        estimates = {}
        total = 0
        
        for season in seasons:
            estimate = self.estimate_season_time(season)
            if estimate:
                estimates[season] = estimate
                total += estimate
            else:
                # Use default
                default = self._get_default_estimate()
                estimates[season] = default
                total += default
        
        return {
            "per_season": estimates,
            "total_seconds": total,
            "total_minutes": total / 60,
            "total_hours": total / 3600,
            "confidence": self._calculate_confidence(seasons)
        }
    
    def get_eta(self, start_time: float, completed_seasons: List[str], 
                remaining_seasons: List[str]) -> Dict[str, any]:
        """
        Calculate ETA for remaining work
        
        Args:
            start_time: When generation started
            completed_seasons: Already completed
            remaining_seasons: Still to do
            
        Returns:
            ETA information
        """
        elapsed = time.time() - start_time
        
        # Estimate remaining time
        remaining_estimate = self.estimate_total_time(remaining_seasons)
        
        # Calculate completion time
        eta_seconds = remaining_estimate['total_seconds']
        eta_timestamp = time.time() + eta_seconds
        
        return {
            "elapsed_seconds": elapsed,
            "elapsed_minutes": elapsed / 60,
            "remaining_seconds": eta_seconds,
            "remaining_minutes": eta_seconds / 60,
            "eta_timestamp": eta_timestamp,
            "total_estimated_seconds": elapsed + eta_seconds,
            "total_estimated_minutes": (elapsed + eta_seconds) / 60,
            "confidence": remaining_estimate['confidence']
        }
    
    def format_time(self, seconds: float) -> str:
        """
        Format seconds as human-readable time
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted string like "2h 34m" or "45m"
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    def format_eta_message(self, eta_info: Dict) -> str:
        """
        Format ETA as user-friendly message
        
        Args:
            eta_info: ETA dictionary from get_eta()
            
        Returns:
            Formatted message
        """
        elapsed = self.format_time(eta_info['elapsed_seconds'])
        remaining = self.format_time(eta_info['remaining_seconds'])
        total = self.format_time(eta_info['total_estimated_seconds'])
        
        confidence = eta_info['confidence']
        confidence_emoji = "🎯" if confidence == "high" else "📊" if confidence == "medium" else "❓"
        
        eta_time = time.strftime("%I:%M %p", time.localtime(eta_info['eta_timestamp']))
        
        return (
            f"⏱️  Elapsed: {elapsed} | "
            f"Remaining: ~{remaining} | "
            f"Total: ~{total} | "
            f"ETA: {eta_time} {confidence_emoji}"
        )
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get timing statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.history:
            return {
                "total_generations": 0,
                "average_time_minutes": 0,
                "fastest_generation": None,
                "slowest_generation": None
            }
        
        durations = [t.duration_seconds for t in self.history]
        
        fastest = min(self.history, key=lambda t: t.duration_seconds)
        slowest = max(self.history, key=lambda t: t.duration_seconds)
        
        return {
            "total_generations": len(self.history),
            "average_time_minutes": mean(durations) / 60,
            "median_time_minutes": median(durations) / 60,
            "fastest_generation": {
                "season": fastest.season,
                "time_minutes": fastest.duration_seconds / 60,
                "files": fastest.files_generated
            },
            "slowest_generation": {
                "season": slowest.season,
                "time_minutes": slowest.duration_seconds / 60,
                "files": slowest.files_generated
            }
        }
    
    def _get_default_estimate(self) -> float:
        """Get default time estimate when no history available"""
        # Conservative estimate: 45 minutes per season
        return 45 * 60
    
    def _calculate_confidence(self, seasons: List[str]) -> str:
        """
        Calculate confidence level in estimates
        
        Args:
            seasons: Seasons to estimate
            
        Returns:
            "high", "medium", or "low"
        """
        # Count how many seasons we have data for
        data_count = sum(1 for s in seasons if any(t.season == s for t in self.history))
        
        if data_count == len(seasons) and len(self.history) >= 5:
            return "high"
        elif data_count > 0:
            return "medium"
        else:
            return "low"
    
    def _load_history(self):
        """Load timing history from file"""
        try:
            if not self.history_file.exists():
                return
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.history = [GenerationTiming(**entry) for entry in data]
            
            # Trim if too large
            if len(self.history) > self.MAX_HISTORY_ENTRIES:
                self.history = self.history[-self.MAX_HISTORY_ENTRIES:]
                self._save_history()
            
            self.logger.debug(f"Loaded {len(self.history)} timing entries")
            
        except Exception as e:
            self.logger.warning(f"Failed to load timing history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save timing history to file"""
        try:
            self.history_directory.mkdir(parents=True, exist_ok=True)
            
            data = [asdict(entry) for entry in self.history]
            
            temp_file = self.history_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            temp_file.replace(self.history_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save timing history: {e}")


# === HELPER FUNCTIONS ===

def estimate_time(seasons: List[str], history_dir: str = ".") -> Dict:
    """
    Quick helper to estimate time
    
    Args:
        seasons: List of season names
        history_dir: Directory with history file
        
    Returns:
        Estimate dictionary
    """
    estimator = ProgressEstimator(history_dir)
    return estimator.estimate_total_time(seasons)


if __name__ == "__main__":
    # Example usage
    print("Progress Estimator - Testing")
    print("=" * 60)
    
    estimator = ProgressEstimator()
    
    # Simulate some past generations
    estimator.record_generation("Winter", 2400, 1500)  # 40 min
    estimator.record_generation("Spring", 2700, 1600)  # 45 min
    estimator.record_generation("Summer", 2100, 1400)  # 35 min
    
    # Estimate for new generation
    print("\n1. Estimating time for all seasons:")
    estimate = estimator.estimate_total_time(["Winter", "Spring", "Summer", "Autumn"])
    print(f"   Total time: ~{estimate['total_minutes']:.0f} minutes ({estimate['total_hours']:.1f} hours)")
    print(f"   Confidence: {estimate['confidence']}")
    
    # Calculate ETA
    print("\n2. Calculating ETA:")
    start_time = time.time() - 1200  # Started 20 min ago
    eta = estimator.get_eta(start_time, ["Winter"], ["Spring", "Summer", "Autumn"])
    print(f"   {estimator.format_eta_message(eta)}")
    
    # Statistics
    print("\n3. Statistics:")
    stats = estimator.get_statistics()
    print(f"   Total generations: {stats['total_generations']}")
    print(f"   Average time: {stats['average_time_minutes']:.1f} minutes")
    print(f"   Fastest: {stats['fastest_generation']['season']} - {stats['fastest_generation']['time_minutes']:.1f} min")

