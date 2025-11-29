
import sys
import os
from collections import Counter

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from ai_agent.deception_agent import DeceptionAgent, DeceptionState, ActionType

def test_agent_choices():
    agent = DeceptionAgent(epsilon=0.2)
    
    # Create a dummy initial state
    state = DeceptionState(
        service="SSH",
        command_count=0,
        data_exfil_attempts=0,
        auth_success=False,
        duration_seconds=0.0,
        last_command="",
        suspicion_score=0.0
    )
    
    actions = []
    for _ in range(1000):
        action = agent.choose_action(state)
        actions.append(action)
        
    counts = Counter(actions)
    print("Action distribution over 1000 trials (Initial State):")
    for action, count in counts.items():
        print(f"{action.value}: {count}")
        
    # Check if PRESENT_LURE is chosen roughly 4% of the time (approx 40 times)
    lures = counts.get(ActionType.PRESENT_LURE, 0)
    print(f"\nTotal Lures Presented: {lures}")
    print(f"Percentage: {lures/1000*100:.2f}%")

if __name__ == "__main__":
    test_agent_choices()
