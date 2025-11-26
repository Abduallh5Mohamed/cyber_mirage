"""
Elite Attacker Profiler for Cyber Mirage
Creates comprehensive profiles for threat actors with behavioral analysis.
"""

import logging
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import json

logger = logging.getLogger(__name__)


class AttackerProfile:
    """
    Comprehensive attacker profile with behavioral analysis.
    """
    
    def __init__(self, attacker_ip: str, first_seen: datetime = None):
        self.attacker_ip = attacker_ip
        self.attacker_id = self._generate_attacker_id(attacker_ip)
        self.first_seen = first_seen or datetime.utcnow()
        self.last_seen = datetime.utcnow()
        
        # Identity information
        self.aliases = []
        self.known_usernames = []
        self.known_passwords = []
        
        # Attack history
        self.total_attacks = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
        self.total_commands = 0
        self.unique_commands = set()
        
        # Targeting
        self.targeted_services = []
        self.targeted_ports = []
        self.honeypot_types_hit = []
        
        # Behavioral patterns
        self.attack_times = []  # Timestamps
        self.session_durations = []
        self.command_sequences = []
        
        # MITRE ATT&CK
        self.mitre_tactics = []
        self.mitre_techniques = []
        
        # Tools and techniques
        self.tools_used = []
        self.exploits_attempted = []
        self.zero_days_used = []
        
        # Device fingerprinting
        self.ssh_banners = []
        self.user_agents = []
        self.ttl_values = []
        self.tcp_window_sizes = []
        
        # Geolocation
        self.locations = []
        self.countries = []
        self.isps = []
        self.asns = []
        
        # Threat intelligence
        self.threat_score = 0
        self.skill_level = "Unknown"
        self.motivation = "Unknown"
        self.attribution = []
        
        # Data exfiltration
        self.data_collected_bytes = 0
        self.files_accessed = []
        self.sensitive_data_types = []
    
    def _generate_attacker_id(self, ip: str) -> str:
        """Generate unique attacker ID."""
        return f"ATK-{hashlib.md5(ip.encode()).hexdigest()[:12].upper()}"
    
    def update_from_session(self, session_data: Dict):
        """Update profile with data from an attack session."""
        try:
            self.last_seen = datetime.utcnow()
            self.total_attacks += 1
            
            if session_data.get('detected'):
                self.failed_attacks += 1
            else:
                self.successful_attacks += 1
            
            # Update commands
            if 'commands' in session_data:
                commands = session_data['commands']
                self.total_commands += len(commands)
                self.unique_commands.update(commands)
                
                # Track command sequences
                if len(commands) > 0:
                    self.command_sequences.append(commands)
            
            # Update services and ports
            if 'service' in session_data:
                self.targeted_services.append(session_data['service'])
            if 'port' in session_data:
                self.targeted_ports.append(session_data['port'])
            if 'honeypot_type' in session_data:
                self.honeypot_types_hit.append(session_data['honeypot_type'])
            
            # Update timing
            if 'start_time' in session_data and 'end_time' in session_data:
                self.attack_times.append(session_data['start_time'])
                duration = (session_data['end_time'] - session_data['start_time']).total_seconds()
                self.session_durations.append(duration)
            
            # Update MITRE tactics
            if 'mitre_tactics' in session_data:
                tactics = session_data['mitre_tactics']
                if isinstance(tactics, str):
                    try:
                        tactics = json.loads(tactics)
                    except:
                        tactics = [tactics]
                self.mitre_tactics.extend(tactics)
            
            # Update tools and exploits
            if 'tools_used' in session_data:
                self.tools_used.extend(session_data['tools_used'])
            if 'exploits' in session_data:
                self.exploits_attempted.extend(session_data['exploits'])
            if 'zero_days' in session_data:
                self.zero_days_used.extend(session_data['zero_days'])
            
            # Update data collection
            if 'data_collected' in session_data:
                self.data_collected_bytes += session_data['data_collected']
            
            # Update skill level
            self._assess_skill_level()
            
        except Exception as e:
            logger.error(f"Error updating profile from session: {e}")
    
    def _assess_skill_level(self):
        """Assess attacker skill level based on behavior."""
        try:
            score = 0
            
            # Advanced command usage
            advanced_commands = {'wget', 'curl', 'nc', 'python', 'perl', 'bash', 'chmod', 'chown'}
            if any(cmd in str(self.unique_commands) for cmd in advanced_commands):
                score += 20
            
            # Multiple service targeting
            if len(set(self.targeted_services)) > 3:
                score += 15
            
            # Long session durations (persistence)
            if self.session_durations and max(self.session_durations) > 300:
                score += 10
            
            # MITRE tactics diversity
            unique_tactics = len(set(self.mitre_tactics))
            score += min(unique_tactics * 5, 25)
            
            # Zero-day usage
            if len(self.zero_days_used) > 0:
                score += 30
            
            # Success rate
            if self.total_attacks > 0:
                success_rate = self.successful_attacks / self.total_attacks
                score += int(success_rate * 20)
            
            # Classify
            if score >= 80:
                self.skill_level = "Elite/APT"
            elif score >= 60:
                self.skill_level = "Advanced"
            elif score >= 40:
                self.skill_level = "Intermediate"
            elif score >= 20:
                self.skill_level = "Beginner"
            else:
                self.skill_level = "Script Kiddie"
            
            self.threat_score = min(score, 100)
            
        except Exception as e:
            logger.error(f"Error assessing skill level: {e}")
            self.skill_level = "Unknown"
    
    def get_attack_timeline(self) -> List[Dict]:
        """Get chronological attack timeline."""
        timeline = []
        
        for i, timestamp in enumerate(sorted(self.attack_times)):
            event = {
                "timestamp": timestamp,
                "event_type": "Attack Session",
                "session_number": i + 1,
                "duration": self.session_durations[i] if i < len(self.session_durations) else 0
            }
            
            if i < len(self.command_sequences):
                event["commands"] = len(self.command_sequences[i])
            
            timeline.append(event)
        
        return timeline
    
    def get_behavioral_patterns(self) -> Dict:
        """Analyze behavioral patterns."""
        patterns = {
            "attack_frequency": self._calculate_attack_frequency(),
            "preferred_time": self._get_preferred_attack_time(),
            "avg_session_duration": self._get_avg_session_duration(),
            "command_complexity": self._assess_command_complexity(),
            "persistence_level": self._assess_persistence(),
            "evasion_techniques": self._detect_evasion_techniques()
        }
        
        return patterns
    
    def _calculate_attack_frequency(self) -> str:
        """Calculate attack frequency pattern."""
        if len(self.attack_times) < 2:
            return "Insufficient data"
        
        # Calculate intervals
        sorted_times = sorted(self.attack_times)
        intervals = []
        for i in range(1, len(sorted_times)):
            delta = (sorted_times[i] - sorted_times[i-1]).total_seconds() / 3600  # hours
            intervals.append(delta)
        
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval < 1:
            return "Very High (< 1 hour)"
        elif avg_interval < 24:
            return f"High (~{int(avg_interval)} hours)"
        elif avg_interval < 168:
            return f"Medium (~{int(avg_interval/24)} days)"
        else:
            return "Low (weekly+)"
    
    def _get_preferred_attack_time(self) -> str:
        """Determine preferred attack time (timezone analysis)."""
        if not self.attack_times:
            return "Unknown"
        
        hours = [t.hour for t in self.attack_times]
        hour_counts = Counter(hours)
        most_common_hour = hour_counts.most_common(1)[0][0]
        
        if 0 <= most_common_hour < 6:
            return f"Night ({most_common_hour:02d}:00 UTC)"
        elif 6 <= most_common_hour < 12:
            return f"Morning ({most_common_hour:02d}:00 UTC)"
        elif 12 <= most_common_hour < 18:
            return f"Afternoon ({most_common_hour:02d}:00 UTC)"
        else:
            return f"Evening ({most_common_hour:02d}:00 UTC)"
    
    def _get_avg_session_duration(self) -> float:
        """Get average session duration in seconds."""
        if not self.session_durations:
            return 0.0
        return sum(self.session_durations) / len(self.session_durations)
    
    def _assess_command_complexity(self) -> str:
        """Assess complexity of commands used."""
        if not self.unique_commands:
            return "None"
        
        # Look for advanced patterns
        advanced_patterns = [
            'pipe', '|', '&&', '||', ';', 'for', 'while', 'if', 
            'base64', 'encode', 'decode', 'wget', 'curl', 'nc'
        ]
        
        command_str = ' '.join(self.unique_commands)
        complexity_score = sum(1 for pattern in advanced_patterns if pattern in command_str.lower())
        
        if complexity_score >= 5:
            return "Very High"
        elif complexity_score >= 3:
            return "High"
        elif complexity_score >= 1:
            return "Medium"
        else:
            return "Low"
    
    def _assess_persistence(self) -> str:
        """Assess attacker persistence."""
        if not self.session_durations:
            return "Unknown"
        
        # Check for long sessions and multiple attempts
        max_duration = max(self.session_durations)
        
        if max_duration > 600 and self.total_attacks > 5:
            return "Very High"
        elif max_duration > 300 or self.total_attacks > 3:
            return "High"
        elif self.total_attacks > 1:
            return "Medium"
        else:
            return "Low"
    
    def _detect_evasion_techniques(self) -> List[str]:
        """Detect evasion techniques used."""
        techniques = []
        
        command_str = ' '.join(self.unique_commands).lower()
        
        if 'encoding' in command_str or 'base64' in command_str:
            techniques.append("Command Obfuscation")
        
        if len(set(self.targeted_ports)) > 5:
            techniques.append("Port Hopping")
        
        if len(set(self.countries)) > 2:
            techniques.append("Geographic Shifting")
        
        if 'sleep' in command_str or 'wait' in command_str:
            techniques.append("Timing Manipulation")
        
        return techniques if techniques else ["None Detected"]
    
    def get_mitre_mapping(self) -> Dict:
        """Get MITRE ATT&CK framework mapping."""
        # Count tactic frequencies
        tactic_counts = Counter(self.mitre_tactics)
        
        # Map to MITRE matrix
        mitre_matrix = {
            "Reconnaissance": tactic_counts.get("reconnaissance", 0),
            "Initial Access": tactic_counts.get("initial_access", 0),
            "Execution": tactic_counts.get("execution", 0),
            "Persistence": tactic_counts.get("persistence", 0),
            "Privilege Escalation": tactic_counts.get("privilege_escalation", 0),
            "Defense Evasion": tactic_counts.get("defense_evasion", 0),
            "Credential Access": tactic_counts.get("credential_access", 0),
            "Discovery": tactic_counts.get("discovery", 0),
            "Lateral Movement": tactic_counts.get("lateral_movement", 0),
            "Collection": tactic_counts.get("collection", 0),
            "Exfiltration": tactic_counts.get("exfiltration", 0),
            "Impact": tactic_counts.get("impact", 0)
        }
        
        return {
            "tactics_used": len([v for v in mitre_matrix.values() if v > 0]),
            "total_tactic_instances": sum(mitre_matrix.values()),
            "matrix": mitre_matrix,
            "primary_tactic": max(mitre_matrix, key=mitre_matrix.get) if any(mitre_matrix.values()) else "None"
        }
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        return {
            "attacker_id": self.attacker_id,
            "attacker_ip": self.attacker_ip,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "total_attacks": self.total_attacks,
            "successful_attacks": self.successful_attacks,
            "failed_attacks": self.failed_attacks,
            "success_rate": f"{(self.successful_attacks / self.total_attacks * 100):.1f}%" if self.total_attacks > 0 else "0%",
            "threat_score": self.threat_score,
            "skill_level": self.skill_level,
            "total_commands": self.total_commands,
            "unique_commands": len(self.unique_commands),
            "targeted_services": list(set(self.targeted_services)),
            "honeypot_types": list(set(self.honeypot_types_hit)),
            "data_collected_mb": round(self.data_collected_bytes / 1024 / 1024, 2),
            "behavioral_patterns": self.get_behavioral_patterns(),
            "mitre_analysis": self.get_mitre_mapping(),
            "locations": list(set(self.countries)),
            "isps": list(set(self.isps))
        }


class EliteAttackerProfiler:
    """
    Advanced attacker profiling system with behavioral analysis and threat intelligence.
    """
    
    def __init__(self):
        self.profiles = {}  # IP -> AttackerProfile
        
    def get_or_create_profile(self, attacker_ip: str) -> AttackerProfile:
        """Get existing profile or create new one."""
        if attacker_ip not in self.profiles:
            self.profiles[attacker_ip] = AttackerProfile(attacker_ip)
        
        return self.profiles[attacker_ip]
    
    def update_profile(self, attacker_ip: str, session_data: Dict):
        """Update attacker profile with new session data."""
        try:
            profile = self.get_or_create_profile(attacker_ip)
            profile.update_from_session(session_data)
            
            logger.info(f"Updated profile for {attacker_ip}: {profile.skill_level}, Threat Score: {profile.threat_score}")
            
        except Exception as e:
            logger.error(f"Error updating profile for {attacker_ip}: {e}")
    
    def get_profile(self, attacker_ip: str) -> Optional[AttackerProfile]:
        """Get profile for specific attacker."""
        return self.profiles.get(attacker_ip)
    
    def get_all_profiles(self) -> List[AttackerProfile]:
        """Get all attacker profiles."""
        return list(self.profiles.values())
    
    def get_top_attackers(self, limit: int = 10, sort_by: str = "threat_score") -> List[AttackerProfile]:
        """
        Get top attackers sorted by criteria.
        
        Args:
            limit: Number of profiles to return
            sort_by: Sort criteria (threat_score, total_attacks, success_rate)
        """
        profiles = list(self.profiles.values())
        
        if sort_by == "threat_score":
            profiles.sort(key=lambda p: p.threat_score, reverse=True)
        elif sort_by == "total_attacks":
            profiles.sort(key=lambda p: p.total_attacks, reverse=True)
        elif sort_by == "success_rate":
            profiles.sort(key=lambda p: p.successful_attacks / max(p.total_attacks, 1), reverse=True)
        
        return profiles[:limit]
    
    def get_elite_attackers(self) -> List[AttackerProfile]:
        """Get all Elite/APT level attackers."""
        return [p for p in self.profiles.values() if p.skill_level == "Elite/APT"]
    
    def get_threat_landscape(self) -> Dict:
        """Get comprehensive threat landscape analysis."""
        if not self.profiles:
            return {}
        
        profiles = list(self.profiles.values())
        
        # Skill distribution
        skill_distribution = Counter([p.skill_level for p in profiles])
        
        # Service targeting
        all_services = []
        for p in profiles:
            all_services.extend(p.targeted_services)
        service_distribution = Counter(all_services)
        
        # Geographic distribution
        all_countries = []
        for p in profiles:
            all_countries.extend(p.countries)
        country_distribution = Counter(all_countries)
        
        # MITRE tactics
        all_tactics = []
        for p in profiles:
            all_tactics.extend(p.mitre_tactics)
        tactic_distribution = Counter(all_tactics)
        
        return {
            "total_attackers": len(profiles),
            "elite_attackers": len([p for p in profiles if p.skill_level == "Elite/APT"]),
            "avg_threat_score": sum(p.threat_score for p in profiles) / len(profiles),
            "skill_distribution": dict(skill_distribution),
            "most_targeted_services": dict(service_distribution.most_common(5)),
            "top_source_countries": dict(country_distribution.most_common(10)),
            "common_tactics": dict(tactic_distribution.most_common(10)),
            "total_attacks": sum(p.total_attacks for p in profiles),
            "successful_breaches": sum(p.successful_attacks for p in profiles)
        }
    
    def export_profile(self, attacker_ip: str, format: str = "json") -> str:
        """Export attacker profile in specified format."""
        profile = self.get_profile(attacker_ip)
        
        if not profile:
            return ""
        
        if format == "json":
            return json.dumps(profile.to_dict(), indent=2)
        elif format == "text":
            return self._format_profile_text(profile)
        else:
            return ""
    
    def _format_profile_text(self, profile: AttackerProfile) -> str:
        """Format profile as readable text."""
        data = profile.to_dict()
        
        text = f"""
═══════════════════════════════════════════════════════════════
ATTACKER PROFILE REPORT
═══════════════════════════════════════════════════════════════

IDENTITY
  Attacker ID:      {data['attacker_id']}
  IP Address:       {data['attacker_ip']}
  First Seen:       {data['first_seen']}
  Last Seen:        {data['last_seen']}

THREAT ASSESSMENT
  Skill Level:      {data['skill_level']}
  Threat Score:     {data['threat_score']}/100
  Total Attacks:    {data['total_attacks']}
  Success Rate:     {data['success_rate']}

ATTACK STATISTICS
  Successful:       {data['successful_attacks']}
  Failed:           {data['failed_attacks']}
  Total Commands:   {data['total_commands']}
  Unique Commands:  {data['unique_commands']}
  Data Collected:   {data['data_collected_mb']} MB

TARGETING
  Services:         {', '.join(data['targeted_services'])}
  Honeypots:        {', '.join(data['honeypot_types'])}

BEHAVIORAL ANALYSIS
  Attack Frequency: {data['behavioral_patterns']['attack_frequency']}
  Preferred Time:   {data['behavioral_patterns']['preferred_time']}
  Persistence:      {data['behavioral_patterns']['persistence_level']}
  Evasion:          {', '.join(data['behavioral_patterns']['evasion_techniques'])}

MITRE ATT&CK MAPPING
  Tactics Used:     {data['mitre_analysis']['tactics_used']}/12
  Primary Tactic:   {data['mitre_analysis']['primary_tactic']}

GEOLOCATION
  Countries:        {', '.join(data['locations'])}
  ISPs:             {', '.join(data['isps'])}

═══════════════════════════════════════════════════════════════
"""
        return text


# Singleton instance
_attacker_profiler = None

def get_attacker_profiler() -> EliteAttackerProfiler:
    """Get singleton attacker profiler instance."""
    global _attacker_profiler
    if _attacker_profiler is None:
        _attacker_profiler = EliteAttackerProfiler()
    return _attacker_profiler
