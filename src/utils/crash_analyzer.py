#!/usr/bin/env python3
"""
Crash Analyzer - Enhanced Crash Analytics (v1.3.0+)
Tracks and analyzes crash patterns for better diagnostics
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter

from .logger import Logger


@dataclass
class CrashEvent:
    """Single crash event record"""
    timestamp: float
    season: str
    worldspace: Optional[str]
    retry_number: int
    crash_type: str  # 'hang', 'crash', 'no_progress'
    duration_seconds: float
    files_generated: int
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CrashEvent':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class CrashPattern:
    """Identified crash pattern"""
    pattern_type: str  # 'frequent_worldspace', 'timeout_issue', 'consistent_failure'
    description: str
    occurrences: int
    suggested_fix: str
    severity: str  # 'low', 'medium', 'high'


class CrashAnalyzer:
    """
    Analyzes crash patterns and provides diagnostics
    
    Features:
    - Track crash events
    - Identify patterns
    - Suggest fixes
    - Generate reports
    - Detect problematic worldspaces
    """
    
    CRASH_LOG_FILE = ".ngio_crash_log.json"
    MAX_LOG_ENTRIES = 1000  # Keep last 1000 crashes
    
    def __init__(self, log_directory: str = "."):
        self.logger = Logger("CrashAnalyzer")
        self.log_directory = Path(log_directory)
        self.log_file = self.log_directory / self.CRASH_LOG_FILE
        self.crash_history: List[CrashEvent] = []
        
        # Load existing history
        self._load_history()
    
    def record_crash(self, 
                    season: str,
                    crash_type: str,
                    duration_seconds: float,
                    files_generated: int,
                    retry_number: int = 0,
                    worldspace: Optional[str] = None,
                    error_message: Optional[str] = None):
        """
        Record a crash event
        
        Args:
            season: Season being generated
            crash_type: Type of crash (hang, crash, no_progress)
            duration_seconds: How long before crash
            files_generated: Files generated before crash
            retry_number: Which retry attempt
            worldspace: Current worldspace if known
            error_message: Error message if available
        """
        event = CrashEvent(
            timestamp=time.time(),
            season=season,
            worldspace=worldspace,
            retry_number=retry_number,
            crash_type=crash_type,
            duration_seconds=duration_seconds,
            files_generated=files_generated,
            error_message=error_message
        )
        
        self.crash_history.append(event)
        self._save_history()
        
        self.logger.debug(f"Recorded {crash_type} event: {season} (retry {retry_number})")
    
    def analyze_patterns(self) -> List[CrashPattern]:
        """
        Analyze crash history for patterns
        
        Returns:
            List of identified patterns
        """
        patterns = []
        
        if not self.crash_history:
            return patterns
        
        # Pattern 1: Frequent timeouts
        timeout_crashes = [c for c in self.crash_history if c.crash_type == 'hang']
        if len(timeout_crashes) > 5:
            patterns.append(CrashPattern(
                pattern_type='timeout_issue',
                description=f"Frequent timeout/hang crashes ({len(timeout_crashes)} times)",
                occurrences=len(timeout_crashes),
                suggested_fix="Increase 'no_progress_timeout_minutes' in config (try 20-30 minutes for large load orders)",
                severity='high'
            ))
        
        # Pattern 2: Consistent no-progress
        no_progress = [c for c in self.crash_history if c.crash_type == 'no_progress' and c.files_generated == 0]
        if len(no_progress) > 3:
            patterns.append(CrashPattern(
                pattern_type='no_files_generated',
                description=f"Multiple attempts with no files generated ({len(no_progress)} times)",
                occurrences=len(no_progress),
                suggested_fix="Check: 1) NGIO mod enabled, 2) SKSE working, 3) Load order not conflicting",
                severity='critical'
            ))
        
        # Pattern 3: Specific worldspace issues
        worldspace_crashes = [c for c in self.crash_history if c.worldspace]
        if worldspace_crashes:
            worldspace_counts = Counter(c.worldspace for c in worldspace_crashes)
            for worldspace, count in worldspace_counts.items():
                if count >= 3:
                    patterns.append(CrashPattern(
                        pattern_type='problematic_worldspace',
                        description=f"Worldspace '{worldspace}' crashes frequently ({count} times)",
                        occurrences=count,
                        suggested_fix=f"Possible mod conflict in {worldspace} - try disabling landscape mods for that area",
                        severity='medium'
                    ))
        
        # Pattern 4: Quick crashes (< 1 minute)
        quick_crashes = [c for c in self.crash_history if c.duration_seconds < 60]
        if len(quick_crashes) > 5:
            patterns.append(CrashPattern(
                pattern_type='startup_crash',
                description=f"Frequent quick crashes (<1 min) ({len(quick_crashes)} times)",
                occurrences=len(quick_crashes),
                suggested_fix="Likely mod load order issue or missing master files - check LOOT and mod dependencies",
                severity='high'
            ))
        
        # Pattern 5: Season-specific issues
        season_crashes = Counter(c.season for c in self.crash_history)
        for season, count in season_crashes.items():
            if count > 10:
                patterns.append(CrashPattern(
                    pattern_type='season_specific',
                    description=f"{season} season crashes frequently ({count} times)",
                    occurrences=count,
                    suggested_fix=f"Check seasonal mods configuration for {season} - possible grass conflict",
                    severity='medium'
                ))
        
        # Pattern 6: Retry failures
        high_retries = [c for c in self.crash_history if c.retry_number > 5]
        if len(high_retries) > 5:
            patterns.append(CrashPattern(
                pattern_type='persistent_failure',
                description=f"Multiple high-retry attempts ({len(high_retries)} times)",
                occurrences=len(high_retries),
                suggested_fix="System may be unstable - try: 1) Close background apps, 2) Update GPU drivers, 3) Verify Skyrim files",
                severity='high'
            ))
        
        return patterns
    
    def get_crash_statistics(self) -> Dict[str, any]:
        """
        Get crash statistics
        
        Returns:
            Dictionary of statistics
        """
        if not self.crash_history:
            return {
                "total_crashes": 0,
                "avg_duration": 0,
                "avg_files_generated": 0,
                "most_common_type": None,
                "most_problematic_season": None
            }
        
        total = len(self.crash_history)
        avg_duration = sum(c.duration_seconds for c in self.crash_history) / total
        avg_files = sum(c.files_generated for c in self.crash_history) / total
        
        crash_types = Counter(c.crash_type for c in self.crash_history)
        most_common_type = crash_types.most_common(1)[0] if crash_types else (None, 0)
        
        seasons = Counter(c.season for c in self.crash_history)
        most_problematic_season = seasons.most_common(1)[0] if seasons else (None, 0)
        
        return {
            "total_crashes": total,
            "avg_duration": avg_duration,
            "avg_files_generated": avg_files,
            "most_common_type": most_common_type,
            "most_problematic_season": most_problematic_season,
            "crash_type_breakdown": dict(crash_types),
            "season_breakdown": dict(seasons)
        }
    
    def generate_report(self) -> str:
        """
        Generate comprehensive crash report
        
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("🔍 CRASH ANALYSIS REPORT")
        lines.append("=" * 60)
        
        stats = self.get_crash_statistics()
        
        # Statistics section
        lines.append(f"\n📊 STATISTICS:")
        lines.append(f"   Total Crashes: {stats['total_crashes']}")
        if stats['total_crashes'] > 0:
            lines.append(f"   Average Duration: {stats['avg_duration']/60:.1f} minutes")
            lines.append(f"   Average Files Generated: {stats['avg_files_generated']:.0f}")
            
            if stats['most_common_type'][0]:
                lines.append(f"   Most Common Type: {stats['most_common_type'][0]} ({stats['most_common_type'][1]} times)")
            
            if stats['most_problematic_season'][0]:
                lines.append(f"   Most Problematic Season: {stats['most_problematic_season'][0]} ({stats['most_problematic_season'][1]} times)")
        
        # Patterns section
        patterns = self.analyze_patterns()
        if patterns:
            lines.append(f"\n⚠️  IDENTIFIED PATTERNS ({len(patterns)}):")
            for i, pattern in enumerate(patterns, 1):
                severity_icon = "🔴" if pattern.severity == 'critical' else "🟠" if pattern.severity == 'high' else "🟡"
                lines.append(f"\n{i}. {severity_icon} {pattern.description}")
                lines.append(f"   Suggestion: {pattern.suggested_fix}")
        else:
            lines.append("\n✅ No problematic patterns identified")
        
        # Recent crashes
        recent = self.crash_history[-5:]
        if recent:
            lines.append(f"\n📋 RECENT CRASHES (last {len(recent)}):")
            for i, crash in enumerate(reversed(recent), 1):
                timestamp = datetime.fromtimestamp(crash.timestamp).strftime("%Y-%m-%d %H:%M")
                lines.append(f"   {i}. [{timestamp}] {crash.season} - {crash.crash_type} (retry {crash.retry_number})")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def get_recommendations(self) -> List[str]:
        """
        Get actionable recommendations based on crash history
        
        Returns:
            List of recommendations
        """
        recommendations = []
        patterns = self.analyze_patterns()
        
        # Sort by severity
        critical = [p for p in patterns if p.severity == 'critical']
        high = [p for p in patterns if p.severity == 'high']
        medium = [p for p in patterns if p.severity == 'medium']
        
        if critical:
            recommendations.append("🔴 CRITICAL: Fix these issues immediately:")
            for pattern in critical:
                recommendations.append(f"   • {pattern.suggested_fix}")
        
        if high:
            recommendations.append("🟠 HIGH PRIORITY:")
            for pattern in high:
                recommendations.append(f"   • {pattern.suggested_fix}")
        
        if medium:
            recommendations.append("🟡 CONSIDER:")
            for pattern in medium:
                recommendations.append(f"   • {pattern.suggested_fix}")
        
        if not recommendations:
            recommendations.append("✅ No specific issues identified - system seems stable")
        
        return recommendations
    
    def clear_history(self):
        """Clear crash history"""
        self.crash_history = []
        self._save_history()
        self.logger.info("Crash history cleared")
    
    def _load_history(self):
        """Load crash history from file"""
        try:
            if not self.log_file.exists():
                return
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.crash_history = [CrashEvent.from_dict(event) for event in data]
            
            # Trim if too large
            if len(self.crash_history) > self.MAX_LOG_ENTRIES:
                self.crash_history = self.crash_history[-self.MAX_LOG_ENTRIES:]
                self._save_history()
            
            self.logger.debug(f"Loaded {len(self.crash_history)} crash events")
            
        except Exception as e:
            self.logger.warning(f"Failed to load crash history: {e}")
            self.crash_history = []
    
    def _save_history(self):
        """Save crash history to file"""
        try:
            # Ensure directory exists
            self.log_directory.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict list
            data = [event.to_dict() for event in self.crash_history]
            
            # Write atomically
            temp_file = self.log_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            temp_file.replace(self.log_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save crash history: {e}")


# === HELPER FUNCTIONS ===

def analyze_crashes(log_directory: str = ".") -> str:
    """
    Quick crash analysis helper
    
    Args:
        log_directory: Directory containing crash logs
        
    Returns:
        Formatted report
    """
    analyzer = CrashAnalyzer(log_directory)
    return analyzer.generate_report()


if __name__ == "__main__":
    # Example usage
    print("Crash Analyzer - Testing")
    print("=" * 60)
    
    analyzer = CrashAnalyzer()
    
    # Simulate some crashes
    analyzer.record_crash("Winter", "hang", 300, 50, retry_number=1)
    analyzer.record_crash("Winter", "hang", 350, 75, retry_number=2)
    analyzer.record_crash("Winter", "crash", 120, 20, retry_number=3)
    analyzer.record_crash("Spring", "no_progress", 0, 0, retry_number=1)
    analyzer.record_crash("Spring", "hang", 400, 100, retry_number=1)
    
    # Generate report
    print(analyzer.generate_report())
    
    # Get recommendations
    print("\n💡 RECOMMENDATIONS:")
    for rec in analyzer.get_recommendations():
        print(rec)

