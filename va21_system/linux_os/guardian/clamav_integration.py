#!/usr/bin/env python3
"""
VA21 Research OS - ClamAV Integration
======================================

Integrates ClamAV (Open Source Antivirus) with the Guardian AI
for active threat defense using community-maintained virus databases.

ClamAV provides:
- Virus/Malware signature database
- File scanning capabilities
- Real-time threat detection
- Regular database updates

Om Vinayaka - Protection through open knowledge.
"""

import os
import subprocess
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ScanResult:
    """Result of a ClamAV scan."""
    path: str
    infected: bool
    threat_name: Optional[str] = None
    scan_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ClamAVIntegration:
    """
    ClamAV Integration for VA21 Guardian AI
    
    This module integrates ClamAV's open-source antivirus capabilities
    with the Guardian AI system, providing:
    
    1. File Scanning - Scan files for known threats
    2. Directory Scanning - Recursive directory scanning
    3. Memory Scanning - Scan process memory (limited)
    4. Database Updates - Keep signatures current
    5. Real-time Integration - Works with Guardian AI
    
    ClamAV Database Sources:
    - main.cvd - Main virus database
    - daily.cvd - Daily updates
    - bytecode.cvd - Bytecode signatures
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.clamscan_path = self._find_clamscan()
        self.freshclam_path = self._find_freshclam()
        self.clamdscan_path = self._find_clamdscan()
        
        self.is_available = self.clamscan_path is not None
        self.database_path = "/var/lib/clamav"
        self.quarantine_path = "/va21/quarantine"
        
        # Scan history
        self.scan_history: List[ScanResult] = []
        self.threats_found: List[ScanResult] = []
        
        # Statistics
        self.stats = {
            "total_scans": 0,
            "files_scanned": 0,
            "threats_detected": 0,
            "last_db_update": None,
            "database_version": None
        }
        
        # Ensure quarantine directory exists
        os.makedirs(self.quarantine_path, exist_ok=True)
        
        if self.is_available:
            self._get_database_info()
            print(f"[ClamAV] Initialized v{self.VERSION}")
            print(f"[ClamAV] Database: {self.stats.get('database_version', 'Unknown')}")
        else:
            print("[ClamAV] Not available - running in simulation mode")
    
    def _find_clamscan(self) -> Optional[str]:
        """Find the clamscan binary."""
        paths = ["/usr/bin/clamscan", "/usr/local/bin/clamscan", "clamscan"]
        for path in paths:
            try:
                result = subprocess.run([path, "--version"], 
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return None
    
    def _find_freshclam(self) -> Optional[str]:
        """Find the freshclam binary for database updates."""
        paths = ["/usr/bin/freshclam", "/usr/local/bin/freshclam", "freshclam"]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_clamdscan(self) -> Optional[str]:
        """Find clamdscan for daemon-based scanning (faster)."""
        paths = ["/usr/bin/clamdscan", "/usr/local/bin/clamdscan", "clamdscan"]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def _get_database_info(self):
        """Get ClamAV database information."""
        try:
            result = subprocess.run(
                [self.clamscan_path, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.stats["database_version"] = result.stdout.strip()
        except Exception as e:
            print(f"[ClamAV] Could not get database info: {e}")
    
    def update_database(self) -> Tuple[bool, str]:
        """
        Update ClamAV virus database.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.freshclam_path:
            return False, "freshclam not available"
        
        print("[ClamAV] Updating virus database...")
        
        try:
            result = subprocess.run(
                [self.freshclam_path, "--quiet"],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                self.stats["last_db_update"] = datetime.now().isoformat()
                self._get_database_info()
                return True, "Database updated successfully"
            else:
                return False, f"Update failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Update timed out"
        except Exception as e:
            return False, f"Update error: {e}"
    
    def scan_file(self, filepath: str, quarantine: bool = False) -> ScanResult:
        """
        Scan a single file for threats.
        
        Args:
            filepath: Path to file to scan
            quarantine: Move infected files to quarantine
            
        Returns:
            ScanResult object
        """
        if not os.path.exists(filepath):
            return ScanResult(
                path=filepath,
                infected=False,
                threat_name="File not found"
            )
        
        if not self.is_available:
            # Simulation mode - basic pattern check
            return self._simulate_scan(filepath)
        
        start_time = time.time()
        
        try:
            cmd = [self.clamscan_path, "--no-summary", filepath]
            if quarantine:
                cmd.extend(["--move", self.quarantine_path])
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=60
            )
            
            scan_time = time.time() - start_time
            self.stats["total_scans"] += 1
            self.stats["files_scanned"] += 1
            
            # Parse result
            infected = result.returncode == 1
            threat_name = None
            
            if infected:
                # Extract threat name from output
                # Format: /path/to/file: ThreatName FOUND
                for line in result.stdout.split('\n'):
                    if 'FOUND' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            threat_name = parts[1].replace('FOUND', '').strip()
                
                self.stats["threats_detected"] += 1
            
            scan_result = ScanResult(
                path=filepath,
                infected=infected,
                threat_name=threat_name,
                scan_time=scan_time
            )
            
            self.scan_history.append(scan_result)
            if infected:
                self.threats_found.append(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            return ScanResult(path=filepath, infected=False, threat_name="Scan timed out")
        except Exception as e:
            return ScanResult(path=filepath, infected=False, threat_name=f"Scan error: {e}")
    
    def scan_directory(self, dirpath: str, recursive: bool = True, 
                       quarantine: bool = False) -> List[ScanResult]:
        """
        Scan a directory for threats.
        
        Args:
            dirpath: Path to directory
            recursive: Scan subdirectories
            quarantine: Move infected files to quarantine
            
        Returns:
            List of ScanResult objects
        """
        results = []
        
        if not os.path.isdir(dirpath):
            return [ScanResult(path=dirpath, infected=False, threat_name="Not a directory")]
        
        if not self.is_available:
            # Simulation mode
            for root, dirs, files in os.walk(dirpath):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    results.append(self._simulate_scan(filepath))
                if not recursive:
                    break
            return results
        
        print(f"[ClamAV] Scanning directory: {dirpath}")
        start_time = time.time()
        
        try:
            cmd = [self.clamscan_path]
            if recursive:
                cmd.append("-r")
            if quarantine:
                cmd.extend(["--move", self.quarantine_path])
            cmd.append(dirpath)
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=300
            )
            
            scan_time = time.time() - start_time
            self.stats["total_scans"] += 1
            
            # Parse results
            for line in result.stdout.split('\n'):
                if ':' in line and ('OK' in line or 'FOUND' in line):
                    parts = line.split(':')
                    filepath = parts[0].strip()
                    
                    if 'FOUND' in line:
                        threat_name = parts[1].replace('FOUND', '').strip() if len(parts) > 1 else "Unknown"
                        scan_result = ScanResult(
                            path=filepath,
                            infected=True,
                            threat_name=threat_name,
                            scan_time=scan_time
                        )
                        self.threats_found.append(scan_result)
                        self.stats["threats_detected"] += 1
                    else:
                        scan_result = ScanResult(
                            path=filepath,
                            infected=False,
                            scan_time=scan_time
                        )
                    
                    results.append(scan_result)
                    self.stats["files_scanned"] += 1
            
            return results
            
        except subprocess.TimeoutExpired:
            return [ScanResult(path=dirpath, infected=False, threat_name="Scan timed out")]
        except Exception as e:
            return [ScanResult(path=dirpath, infected=False, threat_name=f"Scan error: {e}")]
    
    def scan_data(self, data: bytes, filename: str = "memory_data") -> ScanResult:
        """
        Scan raw data/bytes for threats.
        
        Args:
            data: Bytes to scan
            filename: Name for logging purposes
            
        Returns:
            ScanResult object
        """
        # Write to temp file, scan, then delete
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            
            result = self.scan_file(tmp_path)
            result.path = filename  # Replace temp path with meaningful name
            
            os.unlink(tmp_path)
            return result
            
        except Exception as e:
            return ScanResult(path=filename, infected=False, threat_name=f"Scan error: {e}")
    
    def _simulate_scan(self, filepath: str) -> ScanResult:
        """Simulate a scan when ClamAV is not available."""
        # Check for obviously suspicious patterns
        suspicious_extensions = ['.exe', '.dll', '.scr', '.bat', '.cmd', '.vbs', '.js']
        suspicious_names = ['virus', 'malware', 'trojan', 'hack', 'crack', 'keygen']
        
        filename = os.path.basename(filepath).lower()
        
        # Check extension
        for ext in suspicious_extensions:
            if filename.endswith(ext):
                return ScanResult(
                    path=filepath,
                    infected=False,
                    threat_name=f"[SIMULATED] Suspicious extension: {ext}"
                )
        
        # Check name
        for name in suspicious_names:
            if name in filename:
                return ScanResult(
                    path=filepath,
                    infected=True,
                    threat_name=f"[SIMULATED] Suspicious filename pattern: {name}"
                )
        
        return ScanResult(path=filepath, infected=False)
    
    def get_quarantine_contents(self) -> List[Dict]:
        """Get list of quarantined files."""
        quarantined = []
        
        if os.path.exists(self.quarantine_path):
            for filename in os.listdir(self.quarantine_path):
                filepath = os.path.join(self.quarantine_path, filename)
                stat = os.stat(filepath)
                quarantined.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "quarantined_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return quarantined
    
    def delete_quarantined(self, filename: str) -> bool:
        """Delete a quarantined file."""
        filepath = os.path.join(self.quarantine_path, filename)
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                return True
        except Exception as e:
            print(f"[ClamAV] Could not delete quarantined file: {e}")
        return False
    
    def get_stats(self) -> Dict:
        """Get scanning statistics."""
        return {
            **self.stats,
            "quarantined_files": len(self.get_quarantine_contents()),
            "recent_threats": [
                {
                    "path": t.path,
                    "threat": t.threat_name,
                    "time": t.timestamp.isoformat()
                }
                for t in self.threats_found[-10:]
            ]
        }
    
    def get_status(self) -> Dict:
        """Get ClamAV status."""
        return {
            "available": self.is_available,
            "version": self.stats.get("database_version", "Unknown"),
            "last_update": self.stats.get("last_db_update"),
            "total_scans": self.stats["total_scans"],
            "threats_detected": self.stats["threats_detected"]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_clamav_instance = None

def get_clamav() -> ClamAVIntegration:
    """Get the ClamAV integration singleton."""
    global _clamav_instance
    if _clamav_instance is None:
        _clamav_instance = ClamAVIntegration()
    return _clamav_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for ClamAV integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VA21 ClamAV Integration")
    parser.add_argument("action", choices=["scan", "update", "status", "quarantine"],
                       help="Action to perform")
    parser.add_argument("path", nargs="?", help="Path to scan")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive scan")
    parser.add_argument("-q", "--quarantine", action="store_true", help="Quarantine threats")
    
    args = parser.parse_args()
    
    clamav = get_clamav()
    
    if args.action == "status":
        status = clamav.get_status()
        print(json.dumps(status, indent=2))
        
    elif args.action == "update":
        success, message = clamav.update_database()
        print(f"{'✅' if success else '❌'} {message}")
        
    elif args.action == "quarantine":
        contents = clamav.get_quarantine_contents()
        if contents:
            print("Quarantined files:")
            for item in contents:
                print(f"  - {item['filename']} ({item['size']} bytes)")
        else:
            print("Quarantine is empty")
            
    elif args.action == "scan":
        if not args.path:
            print("Error: Path required for scan")
            return
        
        if os.path.isdir(args.path):
            results = clamav.scan_directory(args.path, args.recursive, args.quarantine)
        else:
            results = [clamav.scan_file(args.path, args.quarantine)]
        
        threats = [r for r in results if r.infected]
        print(f"\nScanned: {len(results)} files")
        print(f"Threats: {len(threats)}")
        
        if threats:
            print("\n⚠️ THREATS FOUND:")
            for t in threats:
                print(f"  - {t.path}: {t.threat_name}")


if __name__ == "__main__":
    main()
