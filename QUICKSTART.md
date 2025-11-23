# 🚀 Cyber Mirage - Quick Start Guide

## ⚡ Quick Installation (2 minutes)

```powershell
# Clone and setup
git clone <your-repo>
cd cyber_mirage

# Create environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install stable-baselines3[extra] gymnasium numpy tensorboard tqdm rich
```

## 🎯 Train Your AI (10-15 minutes)

```powershell
python src/training/train.py
```

**What happens:**
- ✅ Trains for 200,000 timesteps
- ✅ Saves model to `data/models/ppo_honeynet_advanced.zip`
- ✅ Logs training data to `data/logs/`

**Expected Results:**
- Average reward increases from ~20 to ~130+
- Explained variance reaches ~0.70+
- Training time: ~10-15 minutes on CPU

## 📊 Monitor Training (Real-time)

**Open a new terminal while training:**

```powershell
tensorboard --logdir=data/logs
```

Then open: http://localhost:6006

**You'll see:**
- 📈 Reward progression over time
- 📊 Episode length trends
- 🧠 Loss curves
- 🎯 Policy performance metrics

## 🧪 Test Your Model (2 minutes)

```powershell
python src/training/test.py
```

**Output:**
- 20 test episodes against varying attacker skills
- Success rate (aim for 75%+)
- Average reward, data collected
- Performance grade

**Good performance:**
- ✅ Success rate: 70-85%
- ✅ Average reward: 12,000+
- ✅ Data collected: 40+ per episode

## 🎨 Visualize Results (Advanced)

```powershell
# Install matplotlib first
pip install matplotlib pandas seaborn

# Run visualization
python src/training/visualize.py
```

**Generates:**
- 📊 6 comprehensive charts
- 📈 Performance analysis
- 🎯 Action frequency distribution
- 📦 Data collection efficiency

## 🎮 Test Environment Only

```powershell
python src/environment/base_env.py
```

**Quick test to verify:**
- Environment is working
- Actions are executing
- Rewards are calculating
- No need for training

## 📋 Common Commands

### Check if model exists:
```powershell
dir data\models\
```

### Clean logs and restart:
```powershell
rmdir /s data\logs
python src/training/train.py
```

### Install missing packages:
```powershell
pip install -r requirements.txt
```

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
# Training duration
TRAINING_CONFIG['total_timesteps'] = 200000  # Increase for better results

# Neural network size
PPO_CONFIG['policy_kwargs']['net_arch'] = [256, 256, 128]  # Deeper = smarter

# Reward tuning
REWARD_CONFIG['fake_vuln'] = 7.0  # Adjust action rewards
```

## 📊 Understanding Output

### Training Output:
```
ep_rew_mean: 130  ← Average reward (should increase)
explained_variance: 0.7  ← How well model predicts (0.6-0.9 is good)
fps: 920  ← Training speed (steps per second)
```

### Testing Output:
```
✅ SUCCESS! Deceived attacker!  ← Good! Attacker didn't detect
❌ CAUGHT! Attacker detected!   ← Bad! Need more training
```

## 🎯 Performance Targets

| Metric | Beginner | Good | Excellent |
|--------|----------|------|-----------|
| **Average Reward** | 8,000+ | 12,000+ | 15,000+ |
| **Success Rate** | 60%+ | 75%+ | 85%+ |
| **Data/Episode** | 30+ | 50+ | 70+ |
| **Training Time** | 50K steps | 100K steps | 200K+ steps |

## 🐛 Troubleshooting

### Model not found?
```powershell
# Check if training completed
dir data\models\*.zip

# If empty, train again
python src/training/train.py
```

### TensorBoard not working?
```powershell
# Install tensorboard
pip install tensorboard

# Check if logs exist
dir data\logs\

# Start tensorboard
tensorboard --logdir=data/logs --port=6007
```

### Training too slow?
- **Solution 1:** Reduce timesteps in `train.py`
  ```python
  model.learn(total_timesteps=100000)  # Instead of 200000
  ```

- **Solution 2:** Use smaller network
  ```python
  policy_kwargs=dict(net_arch=[128, 128])  # Instead of [256, 256, 128]
  ```

### Out of memory?
```python
# Reduce batch size in train.py
batch_size=64  # Instead of 128
n_steps=2048   # Instead of 4096
```

## 📈 Interpreting Results

### Reward Growth:
- **0-50K steps:** Rapid learning, reward 20→80
- **50K-100K steps:** Stabilizing, reward 80→110
- **100K-150K steps:** Refinement, reward 110→130
- **150K-200K steps:** Fine-tuning, reward 130→140+

### Success Rate:
- **Novice attackers (skill<0.4):** 90%+ success
- **Intermediate (0.4-0.6):** 75%+ success
- **Advanced (0.6-0.8):** 65%+ success  
- **Expert (0.8-0.95):** 50%+ success (challenging!)

## 🎓 Next Steps

1. **Experiment** with different hyperparameters
2. **Analyze** TensorBoard graphs
3. **Compare** different training runs
4. **Extend** the environment with new features
5. **Deploy** to real network (advanced)

## 📚 Key Files

```
cyber_mirage/
├── src/
│   ├── environment/
│   │   └── base_env.py          ← AI environment
│   ├── training/
│   │   ├── train.py             ← Training script
│   │   ├── test.py              ← Testing script
│   │   └── visualize.py         ← Visualization
│   └── config.py                ← Configuration
├── data/
│   ├── logs/                    ← TensorBoard data
│   └── models/                  ← Trained models
├── README.md                    ← Full documentation
├── IMPROVEMENTS.md              ← What changed
└── requirements.txt             ← Dependencies
```

## 💡 Pro Tips

1. **Monitor training** with TensorBoard from the start
2. **Save checkpoints** every 50K steps
3. **Test frequently** to catch issues early
4. **Compare models** by saving with different names
5. **Document results** in a notebook

## 🆘 Get Help

- Check `README.md` for detailed documentation
- Read `IMPROVEMENTS.md` for technical details
- Review `src/config.py` for all settings
- Test environment first: `python src/environment/base_env.py`

---

<div align="center">

**🎯 Ready to train a world-class honeypot? Start now! 🚀**

</div>
