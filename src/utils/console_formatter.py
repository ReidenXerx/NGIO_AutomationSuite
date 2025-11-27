#!/usr/bin/env python3
"""
Console Formatter - Enhanced Output Formatting (v1.4.0+)
Beautiful console output with boxes, tables, and formatting
"""

from typing import List, Dict, Optional
from enum import Enum


class BoxStyle(Enum):
    """Box drawing styles"""
    SINGLE = {
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'h': '─', 'v': '│', 'cross': '┼',
        'left': '├', 'right': '┤', 'top': '┬', 'bottom': '┴'
    }
    DOUBLE = {
        'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
        'h': '═', 'v': '║', 'cross': '╬',
        'left': '╠', 'right': '╣', 'top': '╦', 'bottom': '╩'
    }
    ROUNDED = {
        'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
        'h': '─', 'v': '│', 'cross': '┼',
        'left': '├', 'right': '┤', 'top': '┬', 'bottom': '┴'
    }
    ASCII = {
        'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
        'h': '-', 'v': '|', 'cross': '+',
        'left': '+', 'right': '+', 'top': '+', 'bottom': '+'
    }


class ConsoleFormatter:
    """
    Enhanced console formatting utilities
    
    Features:
    - Boxes and borders
    - Tables
    - Progress indicators
    - Aligned text
    - Status badges
    """
    
    @staticmethod
    def box(text: str, width: int = 70, style: BoxStyle = BoxStyle.SINGLE, 
            title: Optional[str] = None, padding: int = 1) -> str:
        """
        Create a box around text
        
        Args:
            text: Content
            width: Box width
            style: Box drawing style
            title: Optional title
            padding: Internal padding
            
        Returns:
            Formatted box
        """
        chars = style.value
        lines = text.split('\n')
        
        # Calculate content width
        content_width = width - 2 - (padding * 2)
        
        result = []
        
        # Top border
        if title:
            title_str = f" {title} "
            title_len = len(title_str)
            left_pad = (width - 2 - title_len) // 2
            right_pad = width - 2 - title_len - left_pad
            result.append(f"{chars['tl']}{chars['h'] * left_pad}{title_str}{chars['h'] * right_pad}{chars['tr']}")
        else:
            result.append(f"{chars['tl']}{chars['h'] * (width - 2)}{chars['tr']}")
        
        # Padding
        for _ in range(padding):
            result.append(f"{chars['v']}{' ' * (width - 2)}{chars['v']}")
        
        # Content
        for line in lines:
            # Word wrap if needed
            if len(line) > content_width:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= content_width:
                        current_line += (word + " ")
                    else:
                        result.append(f"{chars['v']}{' ' * padding}{current_line.ljust(content_width)}{' ' * padding}{chars['v']}")
                        current_line = word + " "
                if current_line:
                    result.append(f"{chars['v']}{' ' * padding}{current_line.ljust(content_width)}{' ' * padding}{chars['v']}")
            else:
                result.append(f"{chars['v']}{' ' * padding}{line.ljust(content_width)}{' ' * padding}{chars['v']}")
        
        # Padding
        for _ in range(padding):
            result.append(f"{chars['v']}{' ' * (width - 2)}{chars['v']}")
        
        # Bottom border
        result.append(f"{chars['bl']}{chars['h'] * (width - 2)}{chars['br']}")
        
        return '\n'.join(result)
    
    @staticmethod
    def table(headers: List[str], rows: List[List[str]], 
             style: BoxStyle = BoxStyle.SINGLE) -> str:
        """
        Create a formatted table
        
        Args:
            headers: Column headers
            rows: Data rows
            style: Box style
            
        Returns:
            Formatted table
        """
        chars = style.value
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Add padding
        col_widths = [w + 2 for w in col_widths]
        
        result = []
        
        # Top border
        top = chars['tl']
        for i, width in enumerate(col_widths):
            top += chars['h'] * width
            top += chars['top'] if i < len(col_widths) - 1 else chars['tr']
        result.append(top)
        
        # Headers
        header_line = chars['v']
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            header_line += f" {header.ljust(width - 1)}{chars['v']}"
        result.append(header_line)
        
        # Header separator
        sep = chars['left']
        for i, width in enumerate(col_widths):
            sep += chars['h'] * width
            sep += chars['cross'] if i < len(col_widths) - 1 else chars['right']
        result.append(sep)
        
        # Data rows
        for row in rows:
            row_line = chars['v']
            for i, (cell, width) in enumerate(zip(row, col_widths)):
                row_line += f" {str(cell).ljust(width - 1)}{chars['v']}"
            result.append(row_line)
        
        # Bottom border
        bottom = chars['bl']
        for i, width in enumerate(col_widths):
            bottom += chars['h'] * width
            bottom += chars['bottom'] if i < len(col_widths) - 1 else chars['br']
        result.append(bottom)
        
        return '\n'.join(result)
    
    @staticmethod
    def status_badge(status: str, width: int = 10) -> str:
        """
        Create a status badge
        
        Args:
            status: Status text
            width: Badge width
            
        Returns:
            Formatted badge
        """
        status_map = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'pending': '⏳',
            'running': '🔄',
            'complete': '🎉'
        }
        
        icon = status_map.get(status.lower(), '•')
        return f"{icon} {status.upper().ljust(width)}"
    
    @staticmethod
    def progress_indicator(current: int, total: int, width: int = 40, 
                          fill: str = '█', empty: str = '░') -> str:
        """
        Create a progress bar
        
        Args:
            current: Current progress
            total: Total amount
            width: Bar width
            fill: Fill character
            empty: Empty character
            
        Returns:
            Progress bar string
        """
        if total == 0:
            percent = 0
        else:
            percent = (current / total) * 100
        
        filled_width = int((current / total) * width) if total > 0 else 0
        bar = fill * filled_width + empty * (width - filled_width)
        
        return f"[{bar}] {percent:5.1f}% ({current}/{total})"
    
    @staticmethod
    def separator(width: int = 70, char: str = '─') -> str:
        """Create a separator line"""
        return char * width
    
    @staticmethod
    def center_text(text: str, width: int = 70, fill: str = ' ') -> str:
        """Center text in given width"""
        text_len = len(text)
        if text_len >= width:
            return text
        
        left_pad = (width - text_len) // 2
        right_pad = width - text_len - left_pad
        return f"{fill * left_pad}{text}{fill * right_pad}"
    
    @staticmethod
    def align_columns(left: str, right: str, width: int = 70) -> str:
        """Align text in two columns"""
        left_len = len(left)
        right_len = len(right)
        
        if left_len + right_len >= width:
            return f"{left} {right}"
        
        spacing = width - left_len - right_len
        return f"{left}{' ' * spacing}{right}"
    
    @staticmethod
    def banner(text: str, width: int = 70, style: BoxStyle = BoxStyle.DOUBLE) -> str:
        """
        Create a banner with centered text
        
        Args:
            text: Banner text
            width: Banner width
            style: Box style
            
        Returns:
            Formatted banner
        """
        chars = style.value
        
        lines = text.split('\n')
        result = []
        
        # Top border
        result.append(f"{chars['tl']}{chars['h'] * (width - 2)}{chars['tr']}")
        
        # Content (centered)
        for line in lines:
            centered = ConsoleFormatter.center_text(line, width - 4)
            result.append(f"{chars['v']} {centered} {chars['v']}")
        
        # Bottom border
        result.append(f"{chars['bl']}{chars['h'] * (width - 2)}{chars['br']}")
        
        return '\n'.join(result)
    
    @staticmethod
    def list_with_icons(items: List[tuple], icon_width: int = 3) -> str:
        """
        Create a list with icons
        
        Args:
            items: List of (icon, text) tuples
            icon_width: Width for icon column
            
        Returns:
            Formatted list
        """
        lines = []
        for icon, text in items:
            lines.append(f"{icon.ljust(icon_width)} {text}")
        return '\n'.join(lines)


# === HELPER FUNCTIONS ===

def print_box(text: str, title: Optional[str] = None, style: BoxStyle = BoxStyle.SINGLE):
    """Quick helper to print a box"""
    print(ConsoleFormatter.box(text, title=title, style=style))


def print_table(headers: List[str], rows: List[List[str]], style: BoxStyle = BoxStyle.SINGLE):
    """Quick helper to print a table"""
    print(ConsoleFormatter.table(headers, rows, style))


def print_banner(text: str, style: BoxStyle = BoxStyle.DOUBLE):
    """Quick helper to print a banner"""
    print(ConsoleFormatter.banner(text, style=style))


if __name__ == "__main__":
    # Example usage
    print("Console Formatter - Examples\n")
    
    # Example 1: Simple box
    print("Example 1: Simple Box")
    print_box("This is a message in a box!", title="Information")
    
    print("\n" + "="*70 + "\n")
    
    # Example 2: Table
    print("Example 2: Table")
    headers = ["Season", "Status", "Time", "Files"]
    rows = [
        ["Winter", "✅ Complete", "42.3 min", "1,524"],
        ["Spring", "🔄 Running", "12.5 min", "485"],
        ["Summer", "⏳ Pending", "-", "-"],
        ["Autumn", "⏳ Pending", "-", "-"]
    ]
    print_table(headers, rows)
    
    print("\n" + "="*70 + "\n")
    
    # Example 3: Banner
    print("Example 3: Banner")
    print_banner("🌱 NGIO AUTOMATION SUITE 🌱\nVersion 1.4.0")
    
    print("\n" + "="*70 + "\n")
    
    # Example 4: Progress
    print("Example 4: Progress Bar")
    print(ConsoleFormatter.progress_indicator(75, 100, width=50))
    
    print("\n" + "="*70 + "\n")
    
    # Example 5: List with icons
    print("Example 5: List with Icons")
    items = [
        ("✅", "Skyrim installation found"),
        ("✅", "SKSE64 detected"),
        ("❌", "NGIO mod not found"),
        ("⚠️", "Low disk space (8.5 GB)")
    ]
    print(ConsoleFormatter.list_with_icons(items))

