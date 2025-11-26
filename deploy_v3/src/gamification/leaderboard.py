"""
🎮 Gamification & Leaderboard System
Make security fun and competitive!
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import json


@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    icon: str
    points: int
    rarity: str  # common, rare, epic, legendary


@dataclass
class PlayerStats:
    """Player statistics"""
    username: str
    level: int
    xp: int
    total_attacks_detected: int
    total_data_collected: float
    detection_rate: float
    avg_response_time: float
    achievements: List[str]
    badges: List[str]


class GamificationSystem:
    """
    Gamification system for security analysts
    """
    
    def __init__(self):
        self.players = {}
        self.achievements = self._define_achievements()
        self.leaderboard = []
    
    def _define_achievements(self) -> List[Achievement]:
        """Define all achievements"""
        return [
            # Detection Achievements
            Achievement(
                "first_blood",
                "First Blood",
                "Detect your first attack",
                "🎯",
                100,
                "common"
            ),
            Achievement(
                "sharp_eye",
                "Sharp Eye",
                "Detect 100 attacks",
                "👁️",
                500,
                "rare"
            ),
            Achievement(
                "guardian",
                "Guardian",
                "Detect 1000 attacks",
                "🛡️",
                2000,
                "epic"
            ),
            Achievement(
                "cyber_sentinel",
                "Cyber Sentinel",
                "Detect 10,000 attacks",
                "⚔️",
                10000,
                "legendary"
            ),
            
            # Skill Achievements
            Achievement(
                "apt_hunter",
                "APT Hunter",
                "Detect 10 APT attacks",
                "🎖️",
                1000,
                "epic"
            ),
            Achievement(
                "nation_state_defender",
                "Nation-State Defender",
                "Detect attacks from all major threat actors",
                "🌍",
                5000,
                "legendary"
            ),
            
            # Speed Achievements
            Achievement(
                "quick_response",
                "Quick Response",
                "Detect attack in under 30 seconds",
                "⚡",
                300,
                "rare"
            ),
            Achievement(
                "instant_guardian",
                "Instant Guardian",
                "Detect attack in under 10 seconds",
                "🚀",
                1000,
                "epic"
            ),
            
            # Accuracy Achievements
            Achievement(
                "perfectionist",
                "Perfectionist",
                "Achieve 100% detection rate in 10 consecutive sessions",
                "💯",
                3000,
                "legendary"
            ),
            Achievement(
                "data_collector",
                "Data Collector",
                "Collect over 10GB of attack data",
                "💾",
                1500,
                "epic"
            ),
            
            # Special Achievements
            Achievement(
                "night_owl",
                "Night Owl",
                "Detect attack between 2AM-5AM",
                "🦉",
                500,
                "rare"
            ),
            Achievement(
                "weekend_warrior",
                "Weekend Warrior",
                "Detect 50 attacks on weekends",
                "⚔️",
                800,
                "epic"
            ),
            Achievement(
                "hacker_vs_hacker",
                "Hacker vs Hacker",
                "Defeat APT28, Lazarus, and APT29",
                "🥷",
                5000,
                "legendary"
            )
        ]
    
    def register_player(self, username: str) -> PlayerStats:
        """Register new player"""
        player = PlayerStats(
            username=username,
            level=1,
            xp=0,
            total_attacks_detected=0,
            total_data_collected=0.0,
            detection_rate=0.0,
            avg_response_time=0.0,
            achievements=[],
            badges=[]
        )
        
        self.players[username] = player
        print(f"🎮 Welcome, {username}! Your journey begins...")
        
        return player
    
    def record_detection(
        self,
        username: str,
        detected: bool,
        attacker: str,
        skill: float,
        data_collected: float,
        response_time: float
    ):
        """Record attack detection and update stats"""
        if username not in self.players:
            self.register_player(username)
        
        player = self.players[username]
        
        # Update stats
        player.total_attacks_detected += 1 if detected else 0
        player.total_data_collected += data_collected
        
        # Calculate detection rate
        total_sessions = player.total_attacks_detected + \
                        (1 if not detected else 0)
        player.detection_rate = (
            player.total_attacks_detected / total_sessions * 100
            if total_sessions > 0 else 0
        )
        
        # Update avg response time
        player.avg_response_time = (
            (player.avg_response_time * (player.total_attacks_detected - 1) + response_time)
            / player.total_attacks_detected
            if player.total_attacks_detected > 0 else response_time
        )
        
        # Award XP
        xp_gained = self._calculate_xp(detected, skill, data_collected)
        player.xp += xp_gained
        
        # Level up check
        old_level = player.level
        player.level = self._calculate_level(player.xp)
        
        if player.level > old_level:
            print(f"🎉 LEVEL UP! {username} is now level {player.level}!")
        
        # Check achievements
        self._check_achievements(username, attacker, detected, response_time)
        
        # Update leaderboard
        self._update_leaderboard()
        
        print(f"✅ {username} gained {xp_gained} XP! "
              f"(Total: {player.xp} XP, Level {player.level})")
    
    def _calculate_xp(
        self,
        detected: bool,
        skill: float,
        data_collected: float
    ) -> int:
        """Calculate XP earned"""
        base_xp = 100
        
        if not detected:
            return 10  # Consolation XP
        
        # Bonus for skill level
        skill_bonus = int(skill * 200)
        
        # Bonus for data collected
        data_bonus = int(data_collected / 10)
        
        total_xp = base_xp + skill_bonus + data_bonus
        
        return total_xp
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP"""
        # Level formula: XP = 100 * level^2
        level = int((xp / 100) ** 0.5) + 1
        return level
    
    def _check_achievements(
        self,
        username: str,
        attacker: str,
        detected: bool,
        response_time: float
    ):
        """Check and award achievements"""
        player = self.players[username]
        
        # First Blood
        if player.total_attacks_detected == 1:
            self._award_achievement(username, "first_blood")
        
        # Sharp Eye (100 detections)
        if player.total_attacks_detected == 100:
            self._award_achievement(username, "sharp_eye")
        
        # Guardian (1000 detections)
        if player.total_attacks_detected == 1000:
            self._award_achievement(username, "guardian")
        
        # Quick Response
        if detected and response_time < 30:
            self._award_achievement(username, "quick_response")
        
        # Instant Guardian
        if detected and response_time < 10:
            self._award_achievement(username, "instant_guardian")
        
        # APT Hunter (detect APT attacks)
        if detected and "APT" in attacker:
            apt_count = sum(
                1 for a in player.badges
                if a.startswith("APT_")
            )
            if apt_count >= 10:
                self._award_achievement(username, "apt_hunter")
    
    def _award_achievement(self, username: str, achievement_id: str):
        """Award achievement to player"""
        player = self.players[username]
        
        if achievement_id in player.achievements:
            return  # Already has it
        
        achievement = next(
            (a for a in self.achievements if a.id == achievement_id),
            None
        )
        
        if not achievement:
            return
        
        player.achievements.append(achievement_id)
        player.xp += achievement.points
        
        print(f"\n🏆 ACHIEVEMENT UNLOCKED!")
        print(f"   {achievement.icon} {achievement.name}")
        print(f"   {achievement.description}")
        print(f"   +{achievement.points} XP ({achievement.rarity})\n")
    
    def _update_leaderboard(self):
        """Update global leaderboard"""
        self.leaderboard = sorted(
            self.players.values(),
            key=lambda p: (p.xp, p.detection_rate),
            reverse=True
        )
    
    def display_leaderboard(self, top_n: int = 10):
        """Display top players"""
        print("\n" + "="*80)
        print("🏆 LEADERBOARD - TOP CYBER DEFENDERS")
        print("="*80)
        
        for i, player in enumerate(self.leaderboard[:top_n], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            print(f"\n{medal} {player.username}")
            print(f"   Level: {player.level} | XP: {player.xp:,}")
            print(f"   Detections: {player.total_attacks_detected:,} "
                  f"({player.detection_rate:.1f}% rate)")
            print(f"   Achievements: {len(player.achievements)}")
    
    def display_player_profile(self, username: str):
        """Display detailed player profile"""
        if username not in self.players:
            print(f"❌ Player '{username}' not found")
            return
        
        player = self.players[username]
        
        print("\n" + "="*80)
        print(f"👤 PLAYER PROFILE: {player.username}")
        print("="*80)
        
        print(f"\n📊 Statistics:")
        print(f"   Level: {player.level}")
        print(f"   XP: {player.xp:,}")
        print(f"   Total Detections: {player.total_attacks_detected:,}")
        print(f"   Detection Rate: {player.detection_rate:.1f}%")
        print(f"   Data Collected: {player.total_data_collected:,.2f} MB")
        print(f"   Avg Response Time: {player.avg_response_time:.1f}s")
        
        print(f"\n🏆 Achievements ({len(player.achievements)}):")
        for achievement_id in player.achievements:
            achievement = next(
                (a for a in self.achievements if a.id == achievement_id),
                None
            )
            if achievement:
                print(f"   {achievement.icon} {achievement.name} "
                      f"({achievement.rarity})")


# Example usage
if __name__ == "__main__":
    print("🎮 Gamification System Demo")
    print("="*80)
    
    # Create gamification system
    game = GamificationSystem()
    
    # Register players
    game.register_player("Alice")
    game.register_player("Bob")
    game.register_player("Charlie")
    
    # Simulate detections
    print("\n🎯 Simulating attack detections...\n")
    
    # Alice - Expert player
    for _ in range(150):
        game.record_detection(
            "Alice",
            detected=True,
            attacker="APT28",
            skill=0.85,
            data_collected=125.5,
            response_time=15.3
        )
    
    # Bob - Good player
    for _ in range(80):
        game.record_detection(
            "Bob",
            detected=True,
            attacker="Script Kiddie",
            skill=0.25,
            data_collected=45.2,
            response_time=45.7
        )
    
    # Charlie - Beginner
    for _ in range(30):
        game.record_detection(
            "Charlie",
            detected=True,
            attacker="Curious User",
            skill=0.05,
            data_collected=10.1,
            response_time=120.5
        )
    
    # Display leaderboard
    game.display_leaderboard()
    
    # Display Alice's profile
    game.display_player_profile("Alice")
    
    print("\n✅ Gamification demo complete!")
