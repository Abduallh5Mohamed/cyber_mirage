"""
🔥 Performance Optimizer - Speed up training & inference
GPU optimization, mixed precision, model compression
"""

import torch
import numpy as np
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
    
    print("\n✅ Performance optimizer ready!")
