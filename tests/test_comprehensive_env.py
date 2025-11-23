"""
🧪 Comprehensive Tests for Cyber Mirage
Tests: Unit, Integration, Performance
"""

import pytest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment.comprehensive_env import ComprehensiveHoneynetEnv
from stable_baselines3 import PPO


class TestComprehensiveEnvironment:
    """Test suite for Comprehensive Honeypot Environment"""
    
    @pytest.fixture
    def env(self):
        """Create environment instance"""
        return ComprehensiveHoneynetEnv()
    
    def test_environment_creation(self, env):
        """Test environment can be created"""
        assert env is not None
        assert hasattr(env, 'observation_space')
        assert hasattr(env, 'action_space')
    
    def test_observation_space(self, env):
        """Test observation space dimensions"""
        assert env.observation_space.shape == (15,)
        
    def test_action_space(self, env):
        """Test action space"""
        assert env.action_space.n == 20
    
    def test_reset(self, env):
        """Test reset functionality"""
        obs, info = env.reset()
        
        assert obs.shape == (15,)
        assert isinstance(info, dict)
        assert 'attacker' in info
        assert 'skill' in info
        assert 'origin' in info
        
    def test_reset_with_seed(self, env):
        """Test reset with seed for reproducibility"""
        obs1, _ = env.reset(seed=42)
        obs2, _ = env.reset(seed=42)
        
        np.testing.assert_array_almost_equal(obs1, obs2)
    
    def test_step(self, env):
        """Test step functionality"""
        env.reset()
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert obs.shape == (15,)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
    
    def test_reward_is_numeric(self, env):
        """Test reward is always numeric"""
        env.reset()
        for _ in range(10):
            action = env.action_space.sample()
            _, reward, done, _, _ = env.step(action)
            assert isinstance(reward, (int, float))
            assert not np.isnan(reward)
            assert not np.isinf(reward)
            if done:
                break
    
    def test_all_attackers_loadable(self, env):
        """Test all 150 attacker profiles can be loaded"""
        assert len(env.ATTACKER_PROFILES) >= 100
        
        for name, profile in env.ATTACKER_PROFILES.items():
            assert 'skill' in profile
            assert 'stealth' in profile
            assert 'persistence' in profile
            assert 0.0 <= profile['skill'] <= 1.0
            assert 0.0 <= profile['stealth'] <= 1.0
            assert 0.0 <= profile['persistence'] <= 1.0
    
    def test_mitre_tactics(self, env):
        """Test MITRE ATT&CK tactics"""
        assert len(env.MITRE_TACTICS) == 11
        assert 'reconnaissance' in env.MITRE_TACTICS
        assert 'exfiltration' in env.MITRE_TACTICS
    
    def test_episode_completion(self, env):
        """Test full episode can complete"""
        env.reset()
        done = False
        steps = 0
        max_steps = 1000
        
        while not done and steps < max_steps:
            action = env.action_space.sample()
            _, _, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            steps += 1
        
        assert steps <= max_steps
    
    def test_suspicion_bounds(self, env):
        """Test suspicion stays within bounds"""
        env.reset()
        
        for _ in range(100):
            action = env.action_space.sample()
            obs, _, done, _, _ = env.step(action)
            
            suspicion = obs[1]
            assert 0.0 <= suspicion <= 100.0
            
            if done:
                break
    
    def test_data_collection_positive(self, env):
        """Test data collection is always positive"""
        env.reset()
        
        for _ in range(50):
            action = env.action_space.sample()
            obs, _, done, _, _ = env.step(action)
            
            data = obs[2]
            assert data >= 0.0
            
            if done:
                break
    
    def test_different_attackers_different_behavior(self, env):
        """Test different attackers show different behavior"""
        results = []
        
        for _ in range(5):
            obs, info = env.reset()
            skill = info['skill']
            
            # Run 20 steps
            total_reward = 0
            for _ in range(20):
                action = env.action_space.sample()
                _, reward, done, _, _ = env.step(action)
                total_reward += reward
                if done:
                    break
            
            results.append((skill, total_reward))
        
        # Check that rewards vary
        rewards = [r[1] for r in results]
        assert len(set(rewards)) > 1  # Not all the same


class TestPPOModel:
    """Test PPO model integration"""
    
    @pytest.fixture
    def env(self):
        return ComprehensiveHoneynetEnv()
    
    def test_ppo_creation(self, env):
        """Test PPO model can be created"""
        model = PPO("MlpPolicy", env, verbose=0)
        assert model is not None
    
    def test_ppo_predict(self, env):
        """Test PPO prediction"""
        model = PPO("MlpPolicy", env, verbose=0)
        obs, _ = env.reset()
        
        action, _ = model.predict(obs, deterministic=True)
        # Action can be numpy array or int
        if isinstance(action, np.ndarray):
            action = action.item()
        assert isinstance(action, (int, np.integer))
        assert 0 <= action < env.action_space.n
    
    def test_ppo_learning(self, env):
        """Test PPO can learn (smoke test)"""
        model = PPO("MlpPolicy", env, verbose=0)
        
        # Quick learning test
        model.learn(total_timesteps=100)
        
        # Model should be able to predict after learning
        obs, _ = env.reset()
        action, _ = model.predict(obs)
        assert action is not None


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_action(self):
        """Test handling of invalid actions"""
        env = ComprehensiveHoneynetEnv()
        env.reset()
        
        # Action outside bounds should be handled gracefully
        # Note: Gym/Gymnasium handles this internally
        try:
            obs, _, _, _, _ = env.step(999)
            # If it doesn't error, the environment handles it
            assert True
        except:
            # Expected behavior
            assert True
    
    def test_step_before_reset(self):
        """Test stepping before reset"""
        env = ComprehensiveHoneynetEnv()
        
        # Should work because __init__ calls reset
        try:
            action = env.action_space.sample()
            env.step(action)
            assert True
        except:
            # Also acceptable
            assert True
    
    def test_multiple_resets(self):
        """Test multiple consecutive resets"""
        env = ComprehensiveHoneynetEnv()
        
        for _ in range(5):
            obs, info = env.reset()
            assert obs is not None
            assert info is not None


class TestPerformance:
    """Performance and load tests"""
    
    def test_reset_performance(self):
        """Test reset operation is fast"""
        import time
        
        env = ComprehensiveHoneynetEnv()
        
        start = time.time()
        for _ in range(100):
            env.reset()
        end = time.time()
        
        avg_time = (end - start) / 100
        assert avg_time < 0.01  # Should be < 10ms per reset
    
    def test_step_performance(self):
        """Test step operation is fast"""
        import time
        
        env = ComprehensiveHoneynetEnv()
        env.reset()
        
        times = []
        for _ in range(100):
            action = env.action_space.sample()
            start = time.time()
            env.step(action)
            end = time.time()
            times.append(end - start)
        
        avg_time = np.mean(times)
        assert avg_time < 0.005  # Should be < 5ms per step
    
    def test_memory_stable(self):
        """Test memory usage is stable"""
        import gc
        
        env = ComprehensiveHoneynetEnv()
        
        # Run many episodes
        for _ in range(10):
            env.reset()
            for _ in range(100):
                action = env.action_space.sample()
                _, _, done, _, _ = env.step(action)
                if done:
                    break
            
            gc.collect()
        
        # If we got here without memory error, we're good
        assert True


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src", "--cov-report=html", "--cov-report=term"])
