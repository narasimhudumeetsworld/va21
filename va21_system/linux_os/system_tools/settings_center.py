#!/usr/bin/env python3
"""
VA21 Research OS - Settings & Control Center
==============================================

Complete system settings and control for VA21 Desktop OS.
This replaces traditional desktop environment settings with
VA21's own advanced interface.

Features:
- WiFi/Network Management
- Date & Time Settings
- Display & Appearance
- Sound & Audio
- Power Management
- Security & Privacy
- Keyboard & Shortcuts
- Language & Region
- Storage Management
- User Accounts
- System Updates

Om Vinayaka - Complete control, elegant simplicity.
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WiFiNetwork:
    """WiFi network information."""
    ssid: str
    signal_strength: int  # 0-100
    security: str  # WPA2, WPA3, WEP, Open
    frequency: str  # 2.4GHz or 5GHz
    connected: bool = False
    saved: bool = False
    bssid: str = ""


@dataclass
class AudioDevice:
    """Audio device information."""
    name: str
    device_type: str  # sink, source
    is_default: bool
    volume: int  # 0-100
    muted: bool
    description: str = ""


@dataclass
class Display:
    """Display/monitor information."""
    name: str
    resolution: str
    refresh_rate: int
    is_primary: bool
    position: Tuple[int, int] = (0, 0)
    scale: float = 1.0


class ThemeMode(Enum):
    """Theme modes."""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


# ═══════════════════════════════════════════════════════════════════════════════
# WIFI MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class WiFiManager:
    """
    VA21 WiFi Manager
    
    Manages WiFi connections using NetworkManager (nmcli) or wpa_supplicant.
    """
    
    def __init__(self):
        self.backend = self._detect_backend()
        
    def _detect_backend(self) -> str:
        """Detect available WiFi backend."""
        if os.path.exists("/usr/bin/nmcli"):
            return "nmcli"
        elif os.path.exists("/sbin/wpa_supplicant"):
            return "wpa_supplicant"
        elif os.path.exists("/sbin/iwconfig"):
            return "wireless-tools"
        return "none"
    
    def is_available(self) -> bool:
        """Check if WiFi is available."""
        return self.backend != "none"
    
    def get_status(self) -> Dict:
        """Get WiFi status."""
        status = {
            "enabled": False,
            "connected": False,
            "ssid": None,
            "ip_address": None,
            "signal": 0,
            "backend": self.backend
        }
        
        if self.backend == "nmcli":
            try:
                # Check if WiFi is enabled
                result = subprocess.run(
                    ["nmcli", "radio", "wifi"],
                    capture_output=True, text=True, timeout=5
                )
                status["enabled"] = "enabled" in result.stdout.lower()
                
                # Get current connection
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL", "dev", "wifi"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.strip().split('\n'):
                    if line.startswith("yes:"):
                        parts = line.split(':')
                        if len(parts) >= 3:
                            status["connected"] = True
                            status["ssid"] = parts[1]
                            status["signal"] = int(parts[2]) if parts[2].isdigit() else 0
                
                # Get IP address
                if status["connected"]:
                    result = subprocess.run(
                        ["nmcli", "-t", "-f", "IP4.ADDRESS", "dev", "show", "wlan0"],
                        capture_output=True, text=True, timeout=5
                    )
                    for line in result.stdout.strip().split('\n'):
                        if "IP4.ADDRESS" in line:
                            status["ip_address"] = line.split(':')[1].split('/')[0]
                            break
                            
            except Exception as e:
                status["error"] = str(e)
        
        return status
    
    def scan_networks(self) -> List[WiFiNetwork]:
        """Scan for available WiFi networks."""
        networks = []
        
        if self.backend == "nmcli":
            try:
                # Rescan
                subprocess.run(
                    ["nmcli", "dev", "wifi", "rescan"],
                    capture_output=True, timeout=10
                )
                
                # List networks
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,FREQ,BSSID,IN-USE", "dev", "wifi", "list"],
                    capture_output=True, text=True, timeout=10
                )
                
                seen_ssids = set()
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split(':')
                    if len(parts) >= 5:
                        ssid = parts[0]
                        if ssid and ssid not in seen_ssids:
                            seen_ssids.add(ssid)
                            networks.append(WiFiNetwork(
                                ssid=ssid,
                                signal_strength=int(parts[1]) if parts[1].isdigit() else 0,
                                security=parts[2] or "Open",
                                frequency="5GHz" if "5" in parts[3] else "2.4GHz",
                                bssid=parts[4] if len(parts) > 4 else "",
                                connected="*" in parts[5] if len(parts) > 5 else False
                            ))
                
                # Sort by signal strength
                networks.sort(key=lambda n: n.signal_strength, reverse=True)
                
            except Exception as e:
                pass
        
        return networks
    
    def connect(self, ssid: str, password: str = None) -> Tuple[bool, str]:
        """Connect to a WiFi network."""
        if self.backend == "nmcli":
            try:
                cmd = ["nmcli", "dev", "wifi", "connect", ssid]
                if password:
                    cmd.extend(["password", password])
                
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    return True, f"Connected to {ssid}"
                else:
                    return False, result.stderr or "Connection failed"
                    
            except subprocess.TimeoutExpired:
                return False, "Connection timeout"
            except Exception as e:
                return False, str(e)
        
        return False, "WiFi backend not available"
    
    def disconnect(self) -> Tuple[bool, str]:
        """Disconnect from current WiFi network."""
        if self.backend == "nmcli":
            try:
                result = subprocess.run(
                    ["nmcli", "dev", "disconnect", "wlan0"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return True, "Disconnected"
                return False, result.stderr
            except Exception as e:
                return False, str(e)
        
        return False, "WiFi backend not available"
    
    def toggle_wifi(self, enable: bool) -> Tuple[bool, str]:
        """Enable or disable WiFi."""
        if self.backend == "nmcli":
            try:
                state = "on" if enable else "off"
                result = subprocess.run(
                    ["nmcli", "radio", "wifi", state],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return True, f"WiFi {'enabled' if enable else 'disabled'}"
                return False, result.stderr
            except Exception as e:
                return False, str(e)
        
        return False, "WiFi backend not available"
    
    def forget_network(self, ssid: str) -> Tuple[bool, str]:
        """Forget a saved network."""
        if self.backend == "nmcli":
            try:
                result = subprocess.run(
                    ["nmcli", "connection", "delete", ssid],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return True, f"Forgot network: {ssid}"
                return False, result.stderr
            except Exception as e:
                return False, str(e)
        
        return False, "WiFi backend not available"
    
    def get_saved_networks(self) -> List[str]:
        """Get list of saved networks."""
        networks = []
        
        if self.backend == "nmcli":
            try:
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
                    capture_output=True, text=True, timeout=10
                )
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(':')
                    if len(parts) >= 2 and "wireless" in parts[1].lower():
                        networks.append(parts[0])
            except:
                pass
        
        return networks


# ═══════════════════════════════════════════════════════════════════════════════
# DATE & TIME MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class DateTimeManager:
    """
    VA21 Date & Time Manager
    
    Manages system date, time, timezone, and NTP synchronization.
    """
    
    def get_current_datetime(self) -> Dict:
        """Get current date and time information."""
        now = datetime.now()
        utc_now = datetime.now(timezone.utc)
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "datetime": now.isoformat(),
            "utc_datetime": utc_now.isoformat(),
            "timezone": self.get_timezone(),
            "timestamp": int(now.timestamp()),
            "day_of_week": now.strftime("%A"),
            "formatted": now.strftime("%A, %B %d, %Y %I:%M %p")
        }
    
    def get_timezone(self) -> str:
        """Get current timezone."""
        try:
            result = subprocess.run(
                ["timedatectl", "show", "-p", "Timezone", "--value"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or "UTC"
        except:
            # Fallback
            if os.path.exists("/etc/timezone"):
                with open("/etc/timezone", 'r') as f:
                    return f.read().strip()
            return "UTC"
    
    def get_available_timezones(self) -> List[str]:
        """Get list of available timezones."""
        try:
            result = subprocess.run(
                ["timedatectl", "list-timezones"],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip().split('\n')
        except:
            # Fallback to common timezones
            return [
                "UTC", "America/New_York", "America/Los_Angeles", "America/Chicago",
                "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo",
                "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai", "Australia/Sydney",
                "Pacific/Auckland"
            ]
    
    def set_timezone(self, timezone: str) -> Tuple[bool, str]:
        """Set system timezone."""
        try:
            result = subprocess.run(
                ["timedatectl", "set-timezone", timezone],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, f"Timezone set to {timezone}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def set_datetime(self, date_str: str, time_str: str) -> Tuple[bool, str]:
        """Set system date and time manually."""
        try:
            datetime_str = f"{date_str} {time_str}"
            result = subprocess.run(
                ["timedatectl", "set-time", datetime_str],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, f"Date/time set to {datetime_str}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def get_ntp_status(self) -> Dict:
        """Get NTP synchronization status."""
        status = {
            "enabled": False,
            "synchronized": False,
            "ntp_server": None
        }
        
        try:
            result = subprocess.run(
                ["timedatectl", "show"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split('\n'):
                if "NTP=" in line:
                    status["enabled"] = "yes" in line.lower()
                elif "NTPSynchronized=" in line:
                    status["synchronized"] = "yes" in line.lower()
        except:
            pass
        
        return status
    
    def toggle_ntp(self, enable: bool) -> Tuple[bool, str]:
        """Enable or disable NTP synchronization."""
        try:
            state = "true" if enable else "false"
            result = subprocess.run(
                ["timedatectl", "set-ntp", state],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, f"NTP {'enabled' if enable else 'disabled'}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def sync_time(self) -> Tuple[bool, str]:
        """Force NTP time synchronization."""
        try:
            # Try chronyd first
            result = subprocess.run(
                ["chronyc", "makestep"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Time synchronized with chrony"
            
            # Try ntpdate as fallback
            result = subprocess.run(
                ["ntpdate", "-u", "pool.ntp.org"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return True, "Time synchronized with ntpdate"
            
            return False, "Time sync failed"
        except Exception as e:
            return False, str(e)


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class DisplayManager:
    """
    VA21 Display Manager
    
    Manages display settings, resolution, brightness, etc.
    """
    
    def get_displays(self) -> List[Display]:
        """Get list of connected displays."""
        displays = []
        
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True, text=True, timeout=10
            )
            
            current_display = None
            for line in result.stdout.strip().split('\n'):
                if " connected" in line:
                    parts = line.split()
                    name = parts[0]
                    is_primary = "primary" in line
                    
                    # Find current resolution
                    resolution = "unknown"
                    for part in parts:
                        if 'x' in part and '+' in part:
                            resolution = part.split('+')[0]
                            break
                    
                    displays.append(Display(
                        name=name,
                        resolution=resolution,
                        refresh_rate=60,
                        is_primary=is_primary
                    ))
        except:
            pass
        
        return displays
    
    def get_available_resolutions(self, display_name: str = None) -> List[str]:
        """Get available resolutions for a display."""
        resolutions = []
        
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True, text=True, timeout=10
            )
            
            in_display = False
            for line in result.stdout.strip().split('\n'):
                if " connected" in line:
                    if display_name:
                        in_display = line.startswith(display_name)
                    else:
                        in_display = True
                elif line.startswith("   ") and in_display:
                    parts = line.split()
                    if parts:
                        resolutions.append(parts[0])
                elif not line.startswith("   "):
                    in_display = False
        except:
            pass
        
        return resolutions
    
    def set_resolution(self, display_name: str, resolution: str) -> Tuple[bool, str]:
        """Set display resolution."""
        try:
            result = subprocess.run(
                ["xrandr", "--output", display_name, "--mode", resolution],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, f"Resolution set to {resolution}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def get_brightness(self) -> int:
        """Get current screen brightness (0-100)."""
        try:
            # Try xrandr
            result = subprocess.run(
                ["xrandr", "--verbose", "--current"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if "Brightness:" in line:
                    brightness = float(line.split(':')[1].strip())
                    return int(brightness * 100)
        except:
            pass
        
        try:
            # Try backlight
            brightness_file = "/sys/class/backlight/intel_backlight/brightness"
            max_file = "/sys/class/backlight/intel_backlight/max_brightness"
            
            if os.path.exists(brightness_file) and os.path.exists(max_file):
                with open(brightness_file) as f:
                    current = int(f.read().strip())
                with open(max_file) as f:
                    maximum = int(f.read().strip())
                return int((current / maximum) * 100)
        except:
            pass
        
        return 100
    
    def set_brightness(self, level: int) -> Tuple[bool, str]:
        """Set screen brightness (0-100)."""
        level = max(10, min(100, level))  # Clamp between 10-100
        
        try:
            # Try xrandr first
            brightness = level / 100.0
            result = subprocess.run(
                ["xrandr", "--output", "eDP-1", "--brightness", str(brightness)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, f"Brightness set to {level}%"
        except:
            pass
        
        try:
            # Try backlight
            brightness_file = "/sys/class/backlight/intel_backlight/brightness"
            max_file = "/sys/class/backlight/intel_backlight/max_brightness"
            
            if os.path.exists(brightness_file) and os.path.exists(max_file):
                with open(max_file) as f:
                    maximum = int(f.read().strip())
                new_value = int((level / 100.0) * maximum)
                with open(brightness_file, 'w') as f:
                    f.write(str(new_value))
                return True, f"Brightness set to {level}%"
        except:
            pass
        
        return False, "Could not set brightness"


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class AudioManager:
    """
    VA21 Audio Manager
    
    Manages audio devices, volume, and sound settings using PulseAudio/PipeWire.
    """
    
    def __init__(self):
        self.backend = self._detect_backend()
    
    def _detect_backend(self) -> str:
        """Detect audio backend."""
        if os.path.exists("/usr/bin/pactl"):
            return "pulseaudio"
        elif os.path.exists("/usr/bin/amixer"):
            return "alsa"
        return "none"
    
    def get_volume(self) -> int:
        """Get current volume (0-100)."""
        if self.backend == "pulseaudio":
            try:
                result = subprocess.run(
                    ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                    capture_output=True, text=True, timeout=5
                )
                match = re.search(r'(\d+)%', result.stdout)
                if match:
                    return int(match.group(1))
            except:
                pass
        
        elif self.backend == "alsa":
            try:
                result = subprocess.run(
                    ["amixer", "get", "Master"],
                    capture_output=True, text=True, timeout=5
                )
                match = re.search(r'\[(\d+)%\]', result.stdout)
                if match:
                    return int(match.group(1))
            except:
                pass
        
        return 50
    
    def set_volume(self, level: int) -> Tuple[bool, str]:
        """Set volume (0-100)."""
        level = max(0, min(100, level))
        
        if self.backend == "pulseaudio":
            try:
                result = subprocess.run(
                    ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return True, f"Volume set to {level}%"
                return False, result.stderr
            except Exception as e:
                return False, str(e)
        
        elif self.backend == "alsa":
            try:
                result = subprocess.run(
                    ["amixer", "set", "Master", f"{level}%"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return True, f"Volume set to {level}%"
                return False, result.stderr
            except Exception as e:
                return False, str(e)
        
        return False, "Audio backend not available"
    
    def is_muted(self) -> bool:
        """Check if audio is muted."""
        if self.backend == "pulseaudio":
            try:
                result = subprocess.run(
                    ["pactl", "get-sink-mute", "@DEFAULT_SINK@"],
                    capture_output=True, text=True, timeout=5
                )
                return "yes" in result.stdout.lower()
            except:
                pass
        
        return False
    
    def toggle_mute(self) -> Tuple[bool, str]:
        """Toggle audio mute."""
        if self.backend == "pulseaudio":
            try:
                result = subprocess.run(
                    ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    muted = self.is_muted()
                    return True, f"Audio {'muted' if muted else 'unmuted'}"
                return False, result.stderr
            except Exception as e:
                return False, str(e)
        
        return False, "Audio backend not available"
    
    def get_audio_devices(self) -> List[AudioDevice]:
        """Get list of audio devices."""
        devices = []
        
        if self.backend == "pulseaudio":
            try:
                # Get sinks (output devices)
                result = subprocess.run(
                    ["pactl", "list", "sinks", "short"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices.append(AudioDevice(
                                name=parts[1],
                                device_type="sink",
                                is_default=False,
                                volume=50,
                                muted=False
                            ))
                
                # Get sources (input devices)
                result = subprocess.run(
                    ["pactl", "list", "sources", "short"],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.strip().split('\n'):
                    if line and "monitor" not in line.lower():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices.append(AudioDevice(
                                name=parts[1],
                                device_type="source",
                                is_default=False,
                                volume=50,
                                muted=False
                            ))
            except:
                pass
        
        return devices


# ═══════════════════════════════════════════════════════════════════════════════
# APPEARANCE SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

class AppearanceSettings:
    """
    VA21 Appearance Settings
    
    Manages themes, fonts, and visual customization.
    """
    
    def __init__(self, config_path: str = "/va21/config"):
        self.config_path = config_path
        self.settings_file = os.path.join(config_path, "appearance.json")
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict:
        """Load appearance settings."""
        defaults = {
            "theme": "dark",
            "accent_color": "#00D4AA",
            "font_family": "DejaVu Sans",
            "font_size": 14,
            "icon_theme": "Adwaita",
            "cursor_theme": "default",
            "animations": True,
            "transparency": 0.95,
            "blur": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    saved = json.load(f)
                defaults.update(saved)
        except:
            pass
        
        return defaults
    
    def save_settings(self) -> bool:
        """Save appearance settings."""
        try:
            os.makedirs(self.config_path, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except:
            return False
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self.settings.get("theme", "dark")
    
    def set_theme(self, theme: str) -> Tuple[bool, str]:
        """Set theme (dark, light, auto)."""
        if theme not in ["dark", "light", "auto"]:
            return False, "Invalid theme"
        
        self.settings["theme"] = theme
        self.save_settings()
        return True, f"Theme set to {theme}"
    
    def get_accent_color(self) -> str:
        """Get accent color."""
        return self.settings.get("accent_color", "#00D4AA")
    
    def set_accent_color(self, color: str) -> Tuple[bool, str]:
        """Set accent color (hex)."""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return False, "Invalid color format"
        
        self.settings["accent_color"] = color
        self.save_settings()
        return True, f"Accent color set to {color}"
    
    def get_all_settings(self) -> Dict:
        """Get all appearance settings."""
        return self.settings.copy()
    
    def update_settings(self, settings: Dict) -> Tuple[bool, str]:
        """Update multiple settings."""
        self.settings.update(settings)
        self.save_settings()
        return True, "Settings updated"


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SETTINGS CENTER
# ═══════════════════════════════════════════════════════════════════════════════

class VA21SettingsCenter:
    """
    VA21 Settings Center
    
    Central hub for all system settings, replacing traditional
    desktop environment settings with VA21's unified interface.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config_path: str = "/va21/config"):
        self.config_path = config_path
        
        # Initialize managers
        self.wifi = WiFiManager()
        self.datetime = DateTimeManager()
        self.display = DisplayManager()
        self.audio = AudioManager()
        self.appearance = AppearanceSettings(config_path)
        
        # General settings
        self.settings_file = os.path.join(config_path, "settings.json")
        self.general_settings = self._load_general_settings()
        
        print(f"[Settings] VA21 Settings Center v{self.VERSION} initialized")
    
    def _load_general_settings(self) -> Dict:
        """Load general settings."""
        defaults = {
            "language": "en_US",
            "keyboard_layout": "us",
            "auto_updates": True,
            "telemetry": False,
            "developer_mode": False,
            "hints_enabled": True,
            "sound_effects": True,
            "notifications": True,
            "screen_lock_timeout": 300,
            "suspend_timeout": 900
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    saved = json.load(f)
                defaults.update(saved)
        except:
            pass
        
        return defaults
    
    def save_general_settings(self) -> bool:
        """Save general settings."""
        try:
            os.makedirs(self.config_path, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.general_settings, f, indent=2)
            return True
        except:
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UNIFIED INTERFACE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_all_status(self) -> Dict:
        """Get status of all system components."""
        return {
            "wifi": self.wifi.get_status(),
            "datetime": self.datetime.get_current_datetime(),
            "displays": [d.__dict__ for d in self.display.get_displays()],
            "audio": {
                "volume": self.audio.get_volume(),
                "muted": self.audio.is_muted()
            },
            "appearance": self.appearance.get_all_settings(),
            "general": self.general_settings
        }
    
    def get_quick_settings(self) -> Dict:
        """Get quick settings for the status bar / panel."""
        wifi_status = self.wifi.get_status()
        
        return {
            "wifi": {
                "connected": wifi_status.get("connected", False),
                "ssid": wifi_status.get("ssid"),
                "signal": wifi_status.get("signal", 0)
            },
            "time": datetime.now().strftime("%H:%M"),
            "date": datetime.now().strftime("%a %b %d"),
            "volume": self.audio.get_volume(),
            "muted": self.audio.is_muted(),
            "brightness": self.display.get_brightness(),
            "battery": self._get_battery_status(),
            "theme": self.appearance.get_theme()
        }
    
    def _get_battery_status(self) -> Optional[Dict]:
        """Get battery status if available."""
        if PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    return {
                        "percent": battery.percent,
                        "charging": battery.power_plugged,
                        "time_left": battery.secsleft if battery.secsleft > 0 else None
                    }
            except:
                pass
        return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SETTINGS CATEGORIES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_settings_categories(self) -> List[Dict]:
        """Get all settings categories for navigation."""
        return [
            {
                "id": "wifi",
                "name": "WiFi & Network",
                "icon": "📶",
                "description": "Manage WiFi connections and network settings"
            },
            {
                "id": "datetime",
                "name": "Date & Time",
                "icon": "🕐",
                "description": "Set date, time, timezone, and synchronization"
            },
            {
                "id": "display",
                "name": "Display",
                "icon": "🖥️",
                "description": "Resolution, brightness, and multi-monitor setup"
            },
            {
                "id": "audio",
                "name": "Sound",
                "icon": "🔊",
                "description": "Volume, audio devices, and sound effects"
            },
            {
                "id": "appearance",
                "name": "Appearance",
                "icon": "🎨",
                "description": "Themes, colors, fonts, and visual effects"
            },
            {
                "id": "keyboard",
                "name": "Keyboard",
                "icon": "⌨️",
                "description": "Keyboard layouts and shortcuts"
            },
            {
                "id": "privacy",
                "name": "Privacy & Security",
                "icon": "🔒",
                "description": "Security settings and privacy controls"
            },
            {
                "id": "power",
                "name": "Power",
                "icon": "🔋",
                "description": "Battery, power profiles, and sleep settings"
            },
            {
                "id": "storage",
                "name": "Storage",
                "icon": "💾",
                "description": "Disk usage and storage management"
            },
            {
                "id": "about",
                "name": "About",
                "icon": "ℹ️",
                "description": "System information and updates"
            }
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # KEYBOARD SETTINGS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_keyboard_layouts(self) -> List[str]:
        """Get available keyboard layouts."""
        try:
            result = subprocess.run(
                ["localectl", "list-x11-keymap-layouts"],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip().split('\n')[:50]  # Limit to 50
        except:
            return ["us", "gb", "de", "fr", "es", "it", "ru", "jp", "kr", "in"]
    
    def set_keyboard_layout(self, layout: str) -> Tuple[bool, str]:
        """Set keyboard layout."""
        try:
            result = subprocess.run(
                ["setxkbmap", layout],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.general_settings["keyboard_layout"] = layout
                self.save_general_settings()
                return True, f"Keyboard layout set to {layout}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ABOUT / SYSTEM INFO
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_about_info(self) -> Dict:
        """Get system information for About page."""
        import platform
        
        info = {
            "os_name": "VA21 Research OS",
            "version": self.VERSION,
            "codename": "Vinayaka",
            "base": os.environ.get("VA21_BASE", "Unknown"),
            "kernel": platform.release(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }
        
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            info["memory_total"] = f"{mem.total / (1024**3):.1f} GB"
            info["cpu_cores"] = psutil.cpu_count()
            
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            info["uptime"] = f"{hours}h {minutes}m"
        
        return info
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TEXT-BASED UI
    # ═══════════════════════════════════════════════════════════════════════════
    
    def render_status_panel(self) -> str:
        """Render a text-based status panel."""
        status = self.get_quick_settings()
        
        lines = []
        lines.append("┌" + "─" * 40 + "┐")
        lines.append("│" + " VA21 SYSTEM STATUS ".center(40) + "│")
        lines.append("├" + "─" * 40 + "┤")
        
        # WiFi
        wifi_icon = "📶" if status["wifi"]["connected"] else "📵"
        wifi_text = status["wifi"]["ssid"] or "Not connected"
        lines.append(f"│ {wifi_icon} WiFi: {wifi_text:<28} │")
        
        # Date & Time
        lines.append(f"│ 🕐 {status['date']} {status['time']:<21} │")
        
        # Volume
        vol_icon = "🔇" if status["muted"] else "🔊"
        lines.append(f"│ {vol_icon} Volume: {status['volume']}%{' (muted)' if status['muted'] else '':<18} │")
        
        # Brightness
        lines.append(f"│ 🔆 Brightness: {status['brightness']}%{'':<18} │")
        
        # Battery
        if status["battery"]:
            bat = status["battery"]
            bat_icon = "🔌" if bat["charging"] else "🔋"
            lines.append(f"│ {bat_icon} Battery: {bat['percent']}%{' (charging)' if bat['charging'] else '':<14} │")
        
        # Theme
        theme_icon = "🌙" if status["theme"] == "dark" else "☀️"
        lines.append(f"│ {theme_icon} Theme: {status['theme'].capitalize():<26} │")
        
        lines.append("└" + "─" * 40 + "┘")
        
        return "\n".join(lines)
    
    def render_settings_menu(self) -> str:
        """Render text-based settings menu."""
        categories = self.get_settings_categories()
        
        lines = []
        lines.append("╔" + "═" * 50 + "╗")
        lines.append("║" + " VA21 SETTINGS ".center(50) + "║")
        lines.append("╠" + "═" * 50 + "╣")
        
        for i, cat in enumerate(categories, 1):
            lines.append(f"║ {i:2}. {cat['icon']} {cat['name']:<40} ║")
        
        lines.append("╠" + "═" * 50 + "╣")
        lines.append("║  Q. Exit Settings                                ║")
        lines.append("╚" + "═" * 50 + "╝")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_settings_instance = None

def get_settings() -> VA21SettingsCenter:
    """Get the Settings Center singleton."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = VA21SettingsCenter()
    return _settings_instance


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN / TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    settings = get_settings()
    
    print(settings.render_status_panel())
    print()
    print(settings.render_settings_menu())
    print()
    print("About:")
    print(json.dumps(settings.get_about_info(), indent=2))
