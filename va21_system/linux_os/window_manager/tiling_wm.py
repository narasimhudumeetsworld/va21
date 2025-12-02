#!/usr/bin/env python3
"""
VA21 Research OS - Tiling Window Manager
=========================================

A keyboard-driven tiling window manager for VA21 OS.
Inspired by i3wm, dwm, and Amethyst.

Features:
- Automatic window tiling
- Multiple layouts (columns, rows, grid, monocle)
- Keyboard-driven operation
- Workspaces/virtual desktops
- Focus follows keyboard
- Split and resize panes

Om Vinayaka - Organized as the cosmos, efficient as thought.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Layout(Enum):
    """Window layout types."""
    TALL = "tall"           # Master on left, stack on right
    WIDE = "wide"           # Master on top, stack on bottom  
    COLUMNS = "columns"     # Equal columns
    ROWS = "rows"           # Equal rows
    GRID = "grid"           # Grid layout
    MONOCLE = "monocle"     # Single fullscreen window
    FLOATING = "floating"   # Traditional floating windows


class Direction(Enum):
    """Navigation directions."""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


@dataclass
class Window:
    """Represents a window/pane."""
    id: str
    title: str
    app_id: str
    x: int = 0
    y: int = 0
    width: int = 80
    height: int = 24
    is_focused: bool = False
    is_floating: bool = False
    is_fullscreen: bool = False
    is_minimized: bool = False
    workspace: int = 1
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Workspace:
    """A virtual desktop/workspace."""
    id: int
    name: str
    layout: Layout = Layout.TALL
    windows: List[str] = field(default_factory=list)  # Window IDs
    master_count: int = 1
    master_ratio: float = 0.55
    gap: int = 2


class TilingWindowManager:
    """
    VA21 Tiling Window Manager
    
    A keyboard-driven window manager that automatically tiles
    windows for efficient screen usage.
    
    Layouts:
    - Tall: Master on left, stack on right (like i3's default)
    - Wide: Master on top, stack on bottom
    - Columns: Equal-width columns
    - Rows: Equal-height rows
    - Grid: Automatic grid arrangement
    - Monocle: Single fullscreen window
    - Floating: Traditional overlapping windows
    """
    
    VERSION = "1.0.0"
    
    # Default keybindings
    KEYBINDINGS = {
        # Focus
        "focus_left": ["ctrl+h", "cmd+left"],
        "focus_right": ["ctrl+l", "cmd+right"],
        "focus_up": ["ctrl+k", "cmd+up"],
        "focus_down": ["ctrl+j", "cmd+down"],
        "focus_next": ["ctrl+tab", "alt+tab"],
        "focus_prev": ["ctrl+shift+tab", "alt+shift+tab"],
        
        # Move windows
        "move_left": ["ctrl+shift+h", "cmd+shift+left"],
        "move_right": ["ctrl+shift+l", "cmd+shift+right"],
        "move_up": ["ctrl+shift+k", "cmd+shift+up"],
        "move_down": ["ctrl+shift+j", "cmd+shift+down"],
        "swap_main": ["ctrl+return", "cmd+return"],
        
        # Resize
        "grow_main": ["ctrl+=", "cmd+="],
        "shrink_main": ["ctrl+-", "cmd+-"],
        "reset_size": ["ctrl+0", "cmd+0"],
        
        # Layout
        "cycle_layout": ["ctrl+space"],
        "layout_tall": ["ctrl+alt+t"],
        "layout_wide": ["ctrl+alt+w"],
        "layout_columns": ["ctrl+alt+c"],
        "layout_grid": ["ctrl+alt+g"],
        "layout_monocle": ["ctrl+alt+m"],
        
        # Windows
        "close_window": ["ctrl+q", "cmd+w"],
        "toggle_float": ["ctrl+shift+space"],
        "toggle_fullscreen": ["ctrl+f", "cmd+f", "f11"],
        
        # Workspaces
        "workspace_1": ["ctrl+1", "cmd+1"],
        "workspace_2": ["ctrl+2", "cmd+2"],
        "workspace_3": ["ctrl+3", "cmd+3"],
        "workspace_4": ["ctrl+4", "cmd+4"],
        "workspace_next": ["ctrl+]", "cmd+]"],
        "workspace_prev": ["ctrl+[", "cmd+["],
        "move_to_workspace_1": ["ctrl+shift+1"],
        "move_to_workspace_2": ["ctrl+shift+2"],
        "move_to_workspace_3": ["ctrl+shift+3"],
        "move_to_workspace_4": ["ctrl+shift+4"],
    }
    
    def __init__(self, screen_width: int = 120, screen_height: int = 40,
                 config_path: str = "/va21/config"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config_path = config_path
        
        # Windows
        self.windows: Dict[str, Window] = {}
        self.focused_window: Optional[str] = None
        
        # Workspaces (default 4)
        self.workspaces: Dict[int, Workspace] = {}
        self.current_workspace = 1
        self._init_workspaces()
        
        # Settings
        self.gap = 1  # Gap between windows
        self.border = 1  # Border width
        self.bar_height = 2  # Status bar height
        
        # Effective screen area
        self.work_area = {
            "x": 0,
            "y": self.bar_height,
            "width": screen_width,
            "height": screen_height - self.bar_height
        }
        
        print(f"[WM] Tiling Window Manager v{self.VERSION} initialized")
        print(f"[WM] Screen: {screen_width}x{screen_height}")
    
    def _init_workspaces(self):
        """Initialize default workspaces."""
        workspace_names = ["Main", "Research", "Terminal", "Notes"]
        for i, name in enumerate(workspace_names, 1):
            self.workspaces[i] = Workspace(id=i, name=name)
    
    def create_window(self, title: str, app_id: str) -> Window:
        """
        Create a new window.
        
        Args:
            title: Window title
            app_id: Application ID
            
        Returns:
            Created Window object
        """
        window_id = f"win_{datetime.now().strftime('%H%M%S%f')}"
        
        window = Window(
            id=window_id,
            title=title,
            app_id=app_id,
            workspace=self.current_workspace
        )
        
        self.windows[window_id] = window
        
        # Add to current workspace
        workspace = self.workspaces[self.current_workspace]
        workspace.windows.append(window_id)
        
        # Focus the new window
        self.focus_window(window_id)
        
        # Re-tile
        self.tile()
        
        print(f"[WM] Created window: {title} ({window_id})")
        return window
    
    def close_window(self, window_id: str = None) -> bool:
        """
        Close a window.
        
        Args:
            window_id: Window to close (or focused window)
            
        Returns:
            Success status
        """
        if window_id is None:
            window_id = self.focused_window
        
        if window_id not in self.windows:
            return False
        
        window = self.windows.pop(window_id)
        
        # Remove from workspace
        for workspace in self.workspaces.values():
            if window_id in workspace.windows:
                workspace.windows.remove(window_id)
        
        # Focus next window
        if self.focused_window == window_id:
            workspace = self.workspaces[self.current_workspace]
            if workspace.windows:
                self.focus_window(workspace.windows[-1])
            else:
                self.focused_window = None
        
        # Re-tile
        self.tile()
        
        print(f"[WM] Closed window: {window.title}")
        return True
    
    def focus_window(self, window_id: str) -> bool:
        """
        Focus a window.
        
        Args:
            window_id: Window to focus
            
        Returns:
            Success status
        """
        if window_id not in self.windows:
            return False
        
        # Unfocus current
        if self.focused_window and self.focused_window in self.windows:
            self.windows[self.focused_window].is_focused = False
        
        # Focus new
        self.windows[window_id].is_focused = True
        self.focused_window = window_id
        
        # Switch to window's workspace if needed
        window = self.windows[window_id]
        if window.workspace != self.current_workspace:
            self.switch_workspace(window.workspace)
        
        return True
    
    def focus_direction(self, direction: Direction) -> bool:
        """
        Focus the window in a direction.
        
        Args:
            direction: Direction to focus
            
        Returns:
            Success status
        """
        if not self.focused_window:
            return False
        
        workspace = self.workspaces[self.current_workspace]
        if len(workspace.windows) < 2:
            return False
        
        current_idx = workspace.windows.index(self.focused_window)
        current_window = self.windows[self.focused_window]
        
        # Find window in direction
        best_candidate = None
        best_distance = float('inf')
        
        for win_id in workspace.windows:
            if win_id == self.focused_window:
                continue
            
            win = self.windows[win_id]
            
            # Check if window is in the right direction
            dx = win.x - current_window.x
            dy = win.y - current_window.y
            
            is_in_direction = False
            distance = abs(dx) + abs(dy)
            
            if direction == Direction.LEFT and dx < 0:
                is_in_direction = True
            elif direction == Direction.RIGHT and dx > 0:
                is_in_direction = True
            elif direction == Direction.UP and dy < 0:
                is_in_direction = True
            elif direction == Direction.DOWN and dy > 0:
                is_in_direction = True
            
            if is_in_direction and distance < best_distance:
                best_distance = distance
                best_candidate = win_id
        
        if best_candidate:
            return self.focus_window(best_candidate)
        
        return False
    
    def focus_next(self) -> bool:
        """Focus the next window in the stack."""
        workspace = self.workspaces[self.current_workspace]
        if len(workspace.windows) < 2:
            return False
        
        if self.focused_window:
            idx = workspace.windows.index(self.focused_window)
            next_idx = (idx + 1) % len(workspace.windows)
            return self.focus_window(workspace.windows[next_idx])
        
        return False
    
    def focus_prev(self) -> bool:
        """Focus the previous window in the stack."""
        workspace = self.workspaces[self.current_workspace]
        if len(workspace.windows) < 2:
            return False
        
        if self.focused_window:
            idx = workspace.windows.index(self.focused_window)
            prev_idx = (idx - 1) % len(workspace.windows)
            return self.focus_window(workspace.windows[prev_idx])
        
        return False
    
    def swap_with_main(self) -> bool:
        """Swap the focused window with the main window."""
        workspace = self.workspaces[self.current_workspace]
        if len(workspace.windows) < 2 or not self.focused_window:
            return False
        
        idx = workspace.windows.index(self.focused_window)
        if idx == 0:
            return False  # Already main
        
        workspace.windows[0], workspace.windows[idx] = workspace.windows[idx], workspace.windows[0]
        self.tile()
        return True
    
    def move_window(self, window_id: str, direction: Direction) -> bool:
        """
        Move a window in a direction (swap positions).
        
        Args:
            window_id: Window to move
            direction: Direction to move
            
        Returns:
            Success status
        """
        workspace = self.workspaces[self.current_workspace]
        if window_id not in workspace.windows:
            return False
        
        idx = workspace.windows.index(window_id)
        
        if direction == Direction.LEFT or direction == Direction.UP:
            if idx > 0:
                workspace.windows[idx], workspace.windows[idx-1] = \
                    workspace.windows[idx-1], workspace.windows[idx]
                self.tile()
                return True
        elif direction == Direction.RIGHT or direction == Direction.DOWN:
            if idx < len(workspace.windows) - 1:
                workspace.windows[idx], workspace.windows[idx+1] = \
                    workspace.windows[idx+1], workspace.windows[idx]
                self.tile()
                return True
        
        return False
    
    def set_layout(self, layout: Layout) -> bool:
        """
        Set the layout for the current workspace.
        
        Args:
            layout: New layout
            
        Returns:
            Success status
        """
        workspace = self.workspaces[self.current_workspace]
        workspace.layout = layout
        self.tile()
        print(f"[WM] Layout: {layout.value}")
        return True
    
    def cycle_layout(self) -> Layout:
        """Cycle to the next layout."""
        workspace = self.workspaces[self.current_workspace]
        layouts = list(Layout)
        idx = layouts.index(workspace.layout)
        new_layout = layouts[(idx + 1) % len(layouts)]
        self.set_layout(new_layout)
        return new_layout
    
    def grow_main(self, amount: float = 0.05):
        """Increase main area ratio."""
        workspace = self.workspaces[self.current_workspace]
        workspace.master_ratio = min(0.9, workspace.master_ratio + amount)
        self.tile()
    
    def shrink_main(self, amount: float = 0.05):
        """Decrease main area ratio."""
        workspace = self.workspaces[self.current_workspace]
        workspace.master_ratio = max(0.1, workspace.master_ratio - amount)
        self.tile()
    
    def reset_size(self):
        """Reset main ratio to default."""
        workspace = self.workspaces[self.current_workspace]
        workspace.master_ratio = 0.55
        self.tile()
    
    def toggle_float(self, window_id: str = None) -> bool:
        """Toggle floating state of a window."""
        if window_id is None:
            window_id = self.focused_window
        
        if window_id not in self.windows:
            return False
        
        window = self.windows[window_id]
        window.is_floating = not window.is_floating
        self.tile()
        return True
    
    def toggle_fullscreen(self, window_id: str = None) -> bool:
        """Toggle fullscreen state of a window."""
        if window_id is None:
            window_id = self.focused_window
        
        if window_id not in self.windows:
            return False
        
        window = self.windows[window_id]
        window.is_fullscreen = not window.is_fullscreen
        self.tile()
        return True
    
    def switch_workspace(self, workspace_id: int) -> bool:
        """
        Switch to a workspace.
        
        Args:
            workspace_id: Workspace to switch to
            
        Returns:
            Success status
        """
        if workspace_id not in self.workspaces:
            return False
        
        self.current_workspace = workspace_id
        workspace = self.workspaces[workspace_id]
        
        # Focus first window if available
        if workspace.windows:
            self.focus_window(workspace.windows[0])
        else:
            self.focused_window = None
        
        self.tile()
        print(f"[WM] Workspace: {workspace.name}")
        return True
    
    def move_to_workspace(self, window_id: str, workspace_id: int) -> bool:
        """
        Move a window to another workspace.
        
        Args:
            window_id: Window to move
            workspace_id: Target workspace
            
        Returns:
            Success status
        """
        if window_id not in self.windows:
            return False
        if workspace_id not in self.workspaces:
            return False
        
        window = self.windows[window_id]
        
        # Remove from current workspace
        for ws in self.workspaces.values():
            if window_id in ws.windows:
                ws.windows.remove(window_id)
        
        # Add to new workspace
        self.workspaces[workspace_id].windows.append(window_id)
        window.workspace = workspace_id
        
        # Focus next window in current workspace
        if self.focused_window == window_id:
            current_ws = self.workspaces[self.current_workspace]
            if current_ws.windows:
                self.focus_window(current_ws.windows[-1])
            else:
                self.focused_window = None
        
        self.tile()
        return True
    
    def tile(self):
        """
        Tile all windows according to the current layout.
        """
        workspace = self.workspaces[self.current_workspace]
        
        # Get visible windows (not minimized, in current workspace)
        visible_windows = [
            self.windows[wid] for wid in workspace.windows
            if wid in self.windows and not self.windows[wid].is_minimized
        ]
        
        # Handle fullscreen
        fullscreen_windows = [w for w in visible_windows if w.is_fullscreen]
        if fullscreen_windows:
            win = fullscreen_windows[0]
            win.x = 0
            win.y = 0
            win.width = self.screen_width
            win.height = self.screen_height
            return
        
        # Separate floating windows
        tiled_windows = [w for w in visible_windows if not w.is_floating]
        
        if not tiled_windows:
            return
        
        # Calculate work area with gaps
        x = self.work_area["x"] + self.gap
        y = self.work_area["y"] + self.gap
        w = self.work_area["width"] - (self.gap * 2)
        h = self.work_area["height"] - (self.gap * 2)
        
        # Apply layout
        if workspace.layout == Layout.MONOCLE:
            self._layout_monocle(tiled_windows, x, y, w, h)
        elif workspace.layout == Layout.TALL:
            self._layout_tall(tiled_windows, x, y, w, h, workspace.master_ratio)
        elif workspace.layout == Layout.WIDE:
            self._layout_wide(tiled_windows, x, y, w, h, workspace.master_ratio)
        elif workspace.layout == Layout.COLUMNS:
            self._layout_columns(tiled_windows, x, y, w, h)
        elif workspace.layout == Layout.ROWS:
            self._layout_rows(tiled_windows, x, y, w, h)
        elif workspace.layout == Layout.GRID:
            self._layout_grid(tiled_windows, x, y, w, h)
    
    def _layout_monocle(self, windows: List[Window], x: int, y: int, w: int, h: int):
        """Full screen layout - only show focused window."""
        for win in windows:
            win.x = x
            win.y = y
            win.width = w
            win.height = h
    
    def _layout_tall(self, windows: List[Window], x: int, y: int, w: int, h: int, ratio: float):
        """Master-stack layout (master on left)."""
        if len(windows) == 1:
            windows[0].x = x
            windows[0].y = y
            windows[0].width = w
            windows[0].height = h
            return
        
        master_width = int(w * ratio)
        stack_width = w - master_width - self.gap
        
        # Master window
        windows[0].x = x
        windows[0].y = y
        windows[0].width = master_width
        windows[0].height = h
        
        # Stack windows
        stack_count = len(windows) - 1
        stack_height = (h - (self.gap * (stack_count - 1))) // stack_count
        
        for i, win in enumerate(windows[1:]):
            win.x = x + master_width + self.gap
            win.y = y + (stack_height + self.gap) * i
            win.width = stack_width
            win.height = stack_height
    
    def _layout_wide(self, windows: List[Window], x: int, y: int, w: int, h: int, ratio: float):
        """Master-stack layout (master on top)."""
        if len(windows) == 1:
            windows[0].x = x
            windows[0].y = y
            windows[0].width = w
            windows[0].height = h
            return
        
        master_height = int(h * ratio)
        stack_height = h - master_height - self.gap
        
        # Master window
        windows[0].x = x
        windows[0].y = y
        windows[0].width = w
        windows[0].height = master_height
        
        # Stack windows
        stack_count = len(windows) - 1
        stack_width = (w - (self.gap * (stack_count - 1))) // stack_count
        
        for i, win in enumerate(windows[1:]):
            win.x = x + (stack_width + self.gap) * i
            win.y = y + master_height + self.gap
            win.width = stack_width
            win.height = stack_height
    
    def _layout_columns(self, windows: List[Window], x: int, y: int, w: int, h: int):
        """Equal columns layout."""
        col_count = len(windows)
        col_width = (w - (self.gap * (col_count - 1))) // col_count
        
        for i, win in enumerate(windows):
            win.x = x + (col_width + self.gap) * i
            win.y = y
            win.width = col_width
            win.height = h
    
    def _layout_rows(self, windows: List[Window], x: int, y: int, w: int, h: int):
        """Equal rows layout."""
        row_count = len(windows)
        row_height = (h - (self.gap * (row_count - 1))) // row_count
        
        for i, win in enumerate(windows):
            win.x = x
            win.y = y + (row_height + self.gap) * i
            win.width = w
            win.height = row_height
    
    def _layout_grid(self, windows: List[Window], x: int, y: int, w: int, h: int):
        """Automatic grid layout."""
        count = len(windows)
        
        # Calculate grid dimensions
        cols = 1
        while cols * cols < count:
            cols += 1
        rows = (count + cols - 1) // cols
        
        cell_width = (w - (self.gap * (cols - 1))) // cols
        cell_height = (h - (self.gap * (rows - 1))) // rows
        
        for i, win in enumerate(windows):
            row = i // cols
            col = i % cols
            
            win.x = x + (cell_width + self.gap) * col
            win.y = y + (cell_height + self.gap) * row
            win.width = cell_width
            win.height = cell_height
    
    def render_status_bar(self) -> str:
        """Render the status bar."""
        parts = []
        
        # Workspaces
        for ws_id, ws in self.workspaces.items():
            if ws_id == self.current_workspace:
                parts.append(f"[{ws.name}]")
            elif ws.windows:
                parts.append(f"({ws.name})")
            else:
                parts.append(f" {ws.name} ")
        
        workspace_str = " ".join(parts)
        
        # Current layout
        workspace = self.workspaces[self.current_workspace]
        layout_str = workspace.layout.value.upper()
        
        # Window count
        win_count = len([w for w in self.windows.values() 
                         if w.workspace == self.current_workspace and not w.is_minimized])
        
        # Build status bar
        left = f" {workspace_str} │ {layout_str} │ {win_count} windows"
        right = datetime.now().strftime("%H:%M:%S")
        
        padding = self.screen_width - len(left) - len(right) - 2
        
        return f"{left}{' ' * padding}{right} "
    
    def get_status(self) -> Dict:
        """Get window manager status."""
        workspace = self.workspaces[self.current_workspace]
        
        return {
            "current_workspace": self.current_workspace,
            "workspace_name": workspace.name,
            "layout": workspace.layout.value,
            "window_count": len([w for w in self.windows.values() 
                                 if w.workspace == self.current_workspace]),
            "focused_window": self.focused_window,
            "workspaces": {
                ws_id: {
                    "name": ws.name,
                    "windows": len(ws.windows),
                    "layout": ws.layout.value
                }
                for ws_id, ws in self.workspaces.items()
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_wm_instance = None

def get_window_manager() -> TilingWindowManager:
    """Get the window manager singleton."""
    global _wm_instance
    if _wm_instance is None:
        _wm_instance = TilingWindowManager()
    return _wm_instance


if __name__ == "__main__":
    wm = get_window_manager()
    
    # Create some test windows
    wm.create_window("Terminal 1", "terminal")
    wm.create_window("Browser", "browser")
    wm.create_window("Notes", "vault")
    
    # Test layouts
    print("\nStatus:", json.dumps(wm.get_status(), indent=2))
    print("\nStatus bar:", wm.render_status_bar())
    
    # Cycle layouts
    wm.cycle_layout()
    print("After cycle:", wm.workspaces[wm.current_workspace].layout.value)
