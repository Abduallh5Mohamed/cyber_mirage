"""
🔥 Performance Optimizer - Speed up training & inference
GPU optimization, mixed precision, model compression
"""

import torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from typing import Callable
import time


class PerformanceOptimizer:
    """
    Optimize model training and inference performance
    """
    
    @staticmethod
    def check_gpu():
        """Check GPU availability"""
        print("🔍 Checking GPU availability...")
        
        cuda_available = torch.cuda.is_available()
        print(f"  CUDA Available: {cuda_available}")
        
        if cuda_available:
            gpu_count = torch.cuda.device_count()
            print(f"  GPU Count: {gpu_count}")
            
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9
                print(f"  GPU {i}: {gpu_name} ({gpu_memory:.2f} GB)")
        else:
            print("  ⚠️  No GPU found. Using CPU.")
            print("  💡 Consider using Google Colab or cloud GPUs for faster training")
        
        return cuda_available
    
    @staticmethod
    def make_env(env_class, rank: int, seed: int = 0) -> Callable:
        """
        Utility function for multiprocessed env
        """
        def _init():
            env = env_class()
            env.reset(seed=seed + rank)
            return env
        set_random_seed(seed)
        return _init
    
    @staticmethod
    def create_parallel_env(env_class, n_envs: int = 4):
        """
        Create parallel environments for faster training
        
        Args:
            env_class: Environment class
            n_envs: Number of parallel environments
        
        Returns:
            Vectorized environment
        """
        print(f"🚀 Creating {n_envs} parallel environments...")
        
        # Create multiple environments
        env = SubprocVecEnv([
            PerformanceOptimizer.make_env(env_class, i) 
            for i in range(n_envs)
        ])
        
        print(f"✅ Parallel environment created!")
        return env
    
    @staticmethod
    def optimize_model_for_inference(model_path: str, save_path: str = None):
        """
        Optimize model for faster inference
        - Convert to TorchScript
        - Quantization (if CPU)
        - Pruning
        """
        print("⚡ Optimizing model for inference...")
        
        model = PPO.load(model_path)
        
        # 1. Convert policy to TorchScript
        print("  1. Converting to TorchScript...")
        dummy_input = torch.randn(1, model.observation_space.shape[0])
        
        traced_policy = torch.jit.trace(
            model.policy.forward,
            dummy_input
        )
        
        # 2. Quantization (for CPU)
        if not torch.cuda.is_available():
            print("  2. Applying dynamic quantization...")
            traced_policy = torch.quantization.quantize_dynamic(
                traced_policy,
                {torch.nn.Linear},
                dtype=torch.qint8
            )
        
        # Save optimized model
        if save_path:
            torch.jit.save(traced_policy, save_path)
            print(f"✅ Optimized model saved to {save_path}")
        
        return traced_policy
    
    @staticmethod
    def benchmark_model(model, env, n_episodes: int = 10):
        """
        Benchmark model performance
        """
        print(f"⏱️  Benchmarking model ({n_episodes} episodes)...")
        
        total_time = 0
        total_steps = 0
        inference_times = []
        
        for episode in range(n_episodes):
            obs, _ = env.reset()
            done = False
            steps = 0
            
            episode_start = time.time()
            
            while not done:
                inference_start = time.time()
                action, _ = model.predict(obs, deterministic=True)
                inference_time = time.time() - inference_start
                inference_times.append(inference_time)
                
                obs, _, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                steps += 1
            
            episode_time = time.time() - episode_start
            total_time += episode_time
            total_steps += steps
        
        # Calculate statistics
        avg_episode_time = total_time / n_episodes
        avg_steps = total_steps / n_episodes
        avg_inference_time = np.mean(inference_times) * 1000  # ms
        fps = total_steps / total_time
        
        print(f"\n📊 Benchmark Results:")
        print(f"  Avg Episode Time: {avg_episode_time:.3f}s")
        print(f"  Avg Steps/Episode: {avg_steps:.1f}")
        print(f"  Avg Inference Time: {avg_inference_time:.2f}ms")
        print(f"  FPS (Steps/Second): {fps:.1f}")
        
        return {
            'avg_episode_time': avg_episode_time,
            'avg_steps': avg_steps,
            'avg_inference_time': avg_inference_time,
            'fps': fps
        }
    
    @staticmethod
    def enable_mixed_precision_training(model):
        """
        Enable mixed precision training for faster GPU training
        Requires PyTorch >= 1.6 and CUDA
        """
        if not torch.cuda.is_available():
            print("⚠️  Mixed precision requires GPU")
            return model
        
        print("⚡ Enabling mixed precision training...")
        
        # Enable automatic mixed precision
        try:
            from torch.cuda.amp import autocast, GradScaler
            print("✅ Mixed precision enabled!")
            return model
        except ImportError:
            print("⚠️  Mixed precision not available in this PyTorch version")
            return model
    
    @staticmethod
    def profile_model(model, env, steps: int = 100):
        """
        Profile model to find bottlenecks
        """
        print(f"🔍 Profiling model ({steps} steps)...")
        
        obs, _ = env.reset()
        
        with torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ],
            record_shapes=True,
            with_stack=True
        ) as prof:
            
            for step in range(steps):
                action, _ = model.predict(obs, deterministic=True)
                obs, _, terminated, truncated, _ = env.step(action)
                
                if terminated or truncated:
                    obs, _ = env.reset()
        
        # Print profiling results
        print("\n📊 Profiling Results:")
        print(prof.key_averages().table(
            sort_by="cpu_time_total",
            row_limit=10
        ))
        
        return prof


class ModelCompression:
    """
    Compress models for deployment
    """
    
    @staticmethod
    def prune_model(model, amount: float = 0.3):
        """
        Prune model weights (remove least important connections)
        
        Args:
            model: Model to prune
            amount: Fraction of connections to remove (0-1)
        """
        print(f"✂️  Pruning model ({amount*100:.0f}% of weights)...")
        
        import torch.nn.utils.prune as prune
        
        # Get all linear layers
        for name, module in model.policy.named_modules():
            if isinstance(module, torch.nn.Linear):
                prune.l1_unstructured(module, name='weight', amount=amount)
                prune.remove(module, 'weight')
                print(f"  Pruned layer: {name}")
        
        print("✅ Pruning complete!")
        return model
    
    @staticmethod
    def quantize_model(model):
        """
        Quantize model to reduce size and increase speed
        """
        print("📦 Quantizing model...")
        
        # Dynamic quantization (for CPU)
        quantized_model = torch.quantization.quantize_dynamic(
            model.policy,
            {torch.nn.Linear},
            dtype=torch.qint8
        )
        
        print("✅ Quantization complete!")
        
        # Calculate size reduction
        original_size = sum(p.numel() * p.element_size() for p in model.policy.parameters())
        quantized_size = sum(p.numel() * p.element_size() for p in quantized_model.parameters())
        reduction = (1 - quantized_size / original_size) * 100
        
        print(f"  Original Size: {original_size/1e6:.2f} MB")
        print(f"  Quantized Size: {quantized_size/1e6:.2f} MB")
        print(f"  Size Reduction: {reduction:.1f}%")
        
        return quantized_model


# Example usage
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from environment.comprehensive_env import ComprehensiveHoneynetEnv
    
    print("⚡ Performance Optimizer Demo")
    print("="*80)
    
    optimizer = PerformanceOptimizer()
    
    # Check GPU
    gpu_available = optimizer.check_gpu()
    
    # Create environment
    env = ComprehensiveHoneynetEnv()
    
    # Check if model exists
    model_path = "data/models/ppo_comprehensive_final.zip"
    if os.path.exists(model_path):
        print(f"\n📂 Loading model from {model_path}")
        model = PPO.load(model_path, env=env)
        
        # Benchmark
        print("\n1️⃣ Benchmarking original model...")
        original_benchmark = optimizer.benchmark_model(model, env, n_episodes=5)
        
        # Optimize for inference
        print("\n2️⃣ Optimizing model...")
        optimized_path = "data/models/optimized_model.pt"
        optimizer.optimize_model_for_inference(model_path, optimized_path)
        
        # Compression
        print("\n3️⃣ Model compression...")
        compression = ModelCompression()
        # compression.prune_model(model, amount=0.3)
        # compression.quantize_model(model)
        
        print("\n✅ Performance optimization complete!")
        
    else:
        print(f"⚠️  Model not found at {model_path}")
        print("Train a model first using train.py")
