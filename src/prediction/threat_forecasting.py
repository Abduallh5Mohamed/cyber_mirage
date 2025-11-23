"""
🧠 Advanced Threat Prediction using Time-Series Forecasting
Predict future attacks before they happen!
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import pickle


class ThreatPredictor:
    """
    Time-series forecasting for attack prediction
    Uses LSTM-like patterns and statistical analysis
    """
    
    def __init__(self):
        self.attack_history = []
        self.scaler = StandardScaler()
        self.prediction_model = None
    
    def record_attack(
        self,
        timestamp: datetime,
        attacker: str,
        skill: float,
        origin: str,
        detected: bool
    ):
        """Record attack for analysis"""
        self.attack_history.append({
            'timestamp': timestamp,
            'attacker': attacker,
            'skill': skill,
            'origin': origin,
            'detected': detected,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month
        })
    
    def analyze_patterns(self) -> Dict:
        """Analyze attack patterns"""
        if len(self.attack_history) < 10:
            return {'status': 'insufficient_data'}
        
        print("📊 Analyzing Attack Patterns...")
        
        # Time-based patterns
        hourly_attacks = self._analyze_hourly()
        daily_attacks = self._analyze_daily()
        
        # Attacker patterns
        top_attackers = self._analyze_top_attackers()
        
        # Geographic patterns
        origin_patterns = self._analyze_origins()
        
        # Skill distribution
        skill_distribution = self._analyze_skill_levels()
        
        results = {
            'total_attacks': len(self.attack_history),
            'hourly_patterns': hourly_attacks,
            'daily_patterns': daily_attacks,
            'top_attackers': top_attackers,
            'origin_patterns': origin_patterns,
            'skill_distribution': skill_distribution,
            'peak_hour': max(hourly_attacks.items(), key=lambda x: x[1])[0],
            'peak_day': max(daily_attacks.items(), key=lambda x: x[1])[0]
        }
        
        return results
    
    def _analyze_hourly(self) -> Dict[int, int]:
        """Analyze attacks by hour"""
        hourly = {}
        for attack in self.attack_history:
            hour = attack['hour']
            hourly[hour] = hourly.get(hour, 0) + 1
        return hourly
    
    def _analyze_daily(self) -> Dict[int, int]:
        """Analyze attacks by day of week"""
        daily = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                'Friday', 'Saturday', 'Sunday']
        for attack in self.attack_history:
            day = days[attack['day_of_week']]
            daily[day] = daily.get(day, 0) + 1
        return daily
    
    def _analyze_top_attackers(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get top attackers"""
        attackers = {}
        for attack in self.attack_history:
            attacker = attack['attacker']
            attackers[attacker] = attackers.get(attacker, 0) + 1
        
        return sorted(attackers.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def _analyze_origins(self) -> Dict[str, int]:
        """Analyze attacks by origin"""
        origins = {}
        for attack in self.attack_history:
            origin = attack['origin']
            origins[origin] = origins.get(origin, 0) + 1
        return origins
    
    def _analyze_skill_levels(self) -> Dict[str, int]:
        """Analyze skill level distribution"""
        distribution = {
            'beginner': 0,
            'intermediate': 0,
            'advanced': 0,
            'expert': 0
        }
        
        for attack in self.attack_history:
            skill = attack['skill']
            if skill < 0.25:
                distribution['beginner'] += 1
            elif skill < 0.5:
                distribution['intermediate'] += 1
            elif skill < 0.75:
                distribution['advanced'] += 1
            else:
                distribution['expert'] += 1
        
        return distribution
    
    def predict_next_attack(self) -> Dict:
        """
        Predict characteristics of next attack
        Based on historical patterns
        """
        if len(self.attack_history) < 20:
            return {'status': 'insufficient_data'}
        
        print("🔮 Predicting Next Attack...")
        
        # Recent trend analysis (last 50 attacks)
        recent = self.attack_history[-50:]
        
        # Predict time window
        avg_interval = self._calculate_avg_interval()
        last_attack = self.attack_history[-1]['timestamp']
        predicted_time = last_attack + timedelta(seconds=avg_interval)
        
        # Predict skill level
        recent_skills = [a['skill'] for a in recent]
        predicted_skill = np.mean(recent_skills)
        skill_trend = "increasing" if recent_skills[-10:] > recent_skills[-20:-10] else "decreasing"
        
        # Predict origin
        recent_origins = [a['origin'] for a in recent]
        predicted_origin = max(set(recent_origins), key=recent_origins.count)
        
        # Predict attacker type
        recent_attackers = [a['attacker'] for a in recent]
        predicted_attacker = max(set(recent_attackers), key=recent_attackers.count)
        
        # Calculate confidence
        confidence = min(len(self.attack_history) / 1000, 0.95)
        
        prediction = {
            'predicted_time': predicted_time,
            'predicted_time_window': f"{predicted_time.strftime('%H:%M')} ± 30 min",
            'predicted_skill_level': predicted_skill,
            'skill_category': self._skill_category(predicted_skill),
            'skill_trend': skill_trend,
            'predicted_origin': predicted_origin,
            'likely_attacker_type': predicted_attacker,
            'confidence': confidence * 100,
            'recommendation': self._get_recommendation(predicted_skill)
        }
        
        return prediction
    
    def _calculate_avg_interval(self) -> float:
        """Calculate average time between attacks"""
        if len(self.attack_history) < 2:
            return 3600  # Default 1 hour
        
        intervals = []
        for i in range(1, len(self.attack_history)):
            interval = (
                self.attack_history[i]['timestamp'] - 
                self.attack_history[i-1]['timestamp']
            ).total_seconds()
            intervals.append(interval)
        
        return np.mean(intervals)
    
    def _skill_category(self, skill: float) -> str:
        """Categorize skill level"""
        if skill < 0.25:
            return "beginner"
        elif skill < 0.5:
            return "intermediate"
        elif skill < 0.75:
            return "advanced"
        else:
            return "expert"
    
    def _get_recommendation(self, predicted_skill: float) -> str:
        """Get security recommendation"""
        if predicted_skill >= 0.8:
            return "⚠️ HIGH ALERT: Expert-level attack predicted. Activate advanced monitoring."
        elif predicted_skill >= 0.6:
            return "⚠️ ALERT: Advanced attack predicted. Increase defense posture."
        elif predicted_skill >= 0.4:
            return "✓ MODERATE: Intermediate attack predicted. Standard monitoring."
        else:
            return "✓ LOW: Beginner-level attack predicted. Normal operations."
    
    def generate_threat_report(self) -> str:
        """Generate comprehensive threat intelligence report"""
        patterns = self.analyze_patterns()
        prediction = self.predict_next_attack()
        
        report = f"""
{'='*80}
🛡️ THREAT INTELLIGENCE REPORT
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 ATTACK STATISTICS
{'='*80}
Total Attacks Recorded: {patterns['total_attacks']:,}
Detection Rate: {sum(1 for a in self.attack_history if a['detected']) / len(self.attack_history) * 100:.1f}%

⏰ TEMPORAL PATTERNS
{'='*80}
Peak Hour: {patterns['peak_hour']}:00
Peak Day: {patterns['peak_day']}

🎯 TOP 5 ATTACKERS
{'='*80}
"""
        for i, (attacker, count) in enumerate(patterns['top_attackers'][:5], 1):
            report += f"{i}. {attacker}: {count} attacks ({count/patterns['total_attacks']*100:.1f}%)\n"
        
        report += f"""
🌍 GEOGRAPHIC DISTRIBUTION
{'='*80}
"""
        for origin, count in sorted(patterns['origin_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"{origin}: {count} attacks ({count/patterns['total_attacks']*100:.1f}%)\n"
        
        report += f"""
📈 SKILL LEVEL DISTRIBUTION
{'='*80}
Beginner: {patterns['skill_distribution']['beginner']} ({patterns['skill_distribution']['beginner']/patterns['total_attacks']*100:.1f}%)
Intermediate: {patterns['skill_distribution']['intermediate']} ({patterns['skill_distribution']['intermediate']/patterns['total_attacks']*100:.1f}%)
Advanced: {patterns['skill_distribution']['advanced']} ({patterns['skill_distribution']['advanced']/patterns['total_attacks']*100:.1f}%)
Expert: {patterns['skill_distribution']['expert']} ({patterns['skill_distribution']['expert']/patterns['total_attacks']*100:.1f}%)
"""
        
        if prediction.get('status') != 'insufficient_data':
            report += f"""
🔮 NEXT ATTACK PREDICTION
{'='*80}
Predicted Time: {prediction['predicted_time_window']}
Expected Skill Level: {prediction['skill_category'].upper()} ({prediction['predicted_skill_level']:.2f})
Skill Trend: {prediction['skill_trend'].upper()}
Likely Origin: {prediction['predicted_origin']}
Probable Attacker: {prediction['likely_attacker_type']}
Confidence: {prediction['confidence']:.1f}%

{prediction['recommendation']}
"""
        
        report += f"\n{'='*80}\n"
        
        return report


class AnomalyDetector:
    """
    Detect anomalous attack patterns
    """
    
    def __init__(self):
        self.baseline = None
        self.threshold = 2.0  # Standard deviations
    
    def establish_baseline(self, attack_history: List[Dict]):
        """Establish baseline attack patterns"""
        if len(attack_history) < 50:
            print("⚠️ Need at least 50 attacks to establish baseline")
            return
        
        print("📊 Establishing baseline attack patterns...")
        
        skills = [a['skill'] for a in attack_history]
        hours = [a['hour'] for a in attack_history]
        
        self.baseline = {
            'skill_mean': np.mean(skills),
            'skill_std': np.std(skills),
            'hour_distribution': np.histogram(hours, bins=24)[0]
        }
        
        print("✅ Baseline established!")
    
    def detect_anomaly(self, attack: Dict) -> Dict:
        """Detect if attack is anomalous"""
        if not self.baseline:
            return {'status': 'no_baseline'}
        
        anomalies = []
        
        # Check skill level anomaly
        skill_z_score = abs(
            (attack['skill'] - self.baseline['skill_mean']) / 
            self.baseline['skill_std']
        )
        
        if skill_z_score > self.threshold:
            anomalies.append({
                'type': 'skill_level',
                'severity': 'high' if skill_z_score > 3 else 'medium',
                'message': f"Unusual skill level: {attack['skill']:.2f} "
                          f"(z-score: {skill_z_score:.2f})"
            })
        
        # Check time anomaly
        expected_attacks = self.baseline['hour_distribution'][attack['hour']]
        if expected_attacks < np.percentile(self.baseline['hour_distribution'], 10):
            anomalies.append({
                'type': 'unusual_time',
                'severity': 'medium',
                'message': f"Attack at unusual hour: {attack['hour']}:00"
            })
        
        is_anomalous = len(anomalies) > 0
        
        return {
            'is_anomalous': is_anomalous,
            'anomalies': anomalies,
            'risk_score': len(anomalies) * 30
        }


# Example usage
if __name__ == "__main__":
    print("🔮 Threat Prediction System Demo")
    print("="*80)
    
    # Create predictor
    predictor = ThreatPredictor()
    
    # Simulate attack history
    print("\n📝 Simulating attack history...")
    base_time = datetime.now() - timedelta(days=30)
    
    attackers = ['APT28', 'Lazarus', 'Script Kiddie', 'APT29', 'Curious User']
    origins = ['Russia', 'North Korea', 'USA', 'China', 'Unknown']
    
    for i in range(150):
        timestamp = base_time + timedelta(hours=i*2)
        attacker = np.random.choice(attackers)
        
        # Skill increases over time (adaptive attackers)
        base_skill = 0.3 + (i / 150) * 0.5
        skill = base_skill + np.random.normal(0, 0.1)
        skill = max(0.05, min(1.0, skill))
        
        origin = np.random.choice(origins)
        detected = np.random.random() > (skill * 0.3)
        
        predictor.record_attack(timestamp, attacker, skill, origin, detected)
    
    print(f"✅ Recorded {len(predictor.attack_history)} attacks")
    
    # Analyze patterns
    print("\n" + "="*80)
    patterns = predictor.analyze_patterns()
    print(f"📊 Peak attack hour: {patterns['peak_hour']}:00")
    print(f"📊 Peak attack day: {patterns['peak_day']}")
    
    # Predict next attack
    print("\n" + "="*80)
    prediction = predictor.predict_next_attack()
    if prediction.get('status') != 'insufficient_data':
        print(f"🔮 Next attack predicted for: {prediction['predicted_time_window']}")
        print(f"🎯 Expected skill: {prediction['skill_category']} ({prediction['predicted_skill_level']:.2f})")
        print(f"📍 Likely origin: {prediction['predicted_origin']}")
        print(f"💯 Confidence: {prediction['confidence']:.1f}%")
        print(f"\n{prediction['recommendation']}")
    
    # Generate report
    print("\n" + "="*80)
    report = predictor.generate_threat_report()
    print(report)
    
    # Anomaly detection
    print("\n" + "="*80)
    print("🔍 Anomaly Detection Demo")
    detector = AnomalyDetector()
    detector.establish_baseline(predictor.attack_history)
    
    # Test with anomalous attack
    anomalous_attack = {
        'timestamp': datetime.now(),
        'attacker': 'Unknown',
        'skill': 0.99,  # Very high!
        'origin': 'Unknown',
        'detected': False,
        'hour': 3,
        'day_of_week': 2,
        'month': 10
    }
    
    result = detector.detect_anomaly(anomalous_attack)
    if result['is_anomalous']:
        print("⚠️ ANOMALY DETECTED!")
        print(f"Risk Score: {result['risk_score']}/100")
        for anomaly in result['anomalies']:
            print(f"  - {anomaly['message']} (Severity: {anomaly['severity']})")
    
    print("\n✅ Threat prediction demo complete!")
