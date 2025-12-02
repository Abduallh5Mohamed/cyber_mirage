"""
🚀 PPO Agent Dashboard Component
Advanced visualization for PPO (Proximal Policy Optimization) agent performance.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def display_ppo_metrics():
    """Display PPO agent metrics and performance."""
    st.header("🚀 PPO Agent Performance")
    
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        from src.ai_agent import USE_PPO
        
        if not USE_PPO:
            st.warning("⚠️ PPO agent not enabled. Using Q-learning fallback.")
            return
        
        collector = get_metrics_collector()
        metrics = collector.get_metrics_summary()
        
        # Header stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Training Step",
                f"{metrics['training']['training_step']:,}",
                delta=f"v{metrics['training']['policy_version']}"
            )
        
        with col2:
            st.metric(
                "Total Episodes",
                f"{metrics['performance']['total_episodes']:,}",
                delta=f"{metrics['performance']['recent_decisions']} decisions"
            )
        
        with col3:
            st.metric(
                "Avg Reward",
                f"{metrics['performance']['avg_reward']:.3f}",
                delta=f"{metrics['recent']['avg_reward']:.3f} recent"
            )
        
        with col4:
            st.metric(
                "Entropy",
                f"{metrics['training']['entropy']:.4f}",
                delta="exploration" if metrics['training']['entropy'] > 0.5 else "exploitation"
            )
        
        # Training progress
        st.subheader("📈 Training Progress")
        col1, col2 = st.columns(2)
        
        with col1:
            # Loss metrics
            fig_loss = go.Figure()
            fig_loss.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics['training']['actor_loss'],
                title={'text': "Actor Loss"},
                gauge={'axis': {'range': [None, 5]},
                       'bar': {'color': "darkblue"},
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 1.0
                       }}
            ))
            fig_loss.update_layout(height=300)
            st.plotly_chart(fig_loss, use_container_width=True)
        
        with col2:
            fig_critic = go.Figure()
            fig_critic.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics['training']['critic_loss'],
                title={'text': "Critic Loss"},
                gauge={'axis': {'range': [None, 5]},
                       'bar': {'color': "darkgreen"},
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 1.0
                       }}
            ))
            fig_critic.update_layout(height=300)
            st.plotly_chart(fig_critic, use_container_width=True)
        
        # Action distribution
        st.subheader("🎯 Action Distribution")
        
        action_dist = metrics['actions']['distribution']
        action_counts = metrics['actions']['counts']
        
        # Create dataframe for plotting
        df_actions = pd.DataFrame([
            {
                'Action': k.replace('_', ' ').title(),
                'Percentage': v * 100,
                'Count': action_counts.get(k, 0)
            }
            for k, v in action_dist.items()
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                df_actions,
                values='Percentage',
                names='Action',
                title='Action Selection Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                df_actions,
                x='Action',
                y='Count',
                title='Total Action Counts',
                color='Action',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Recent performance
        st.subheader("⚡ Recent Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Reward", f"{metrics['recent']['avg_reward']:.3f}")
        
        with col2:
            st.metric("Max Reward", f"{metrics['recent']['max_reward']:.3f}")
        
        with col3:
            st.metric("Min Reward", f"{metrics['recent']['min_reward']:.3f}")
        
        with col4:
            st.metric("Std Dev", f"{metrics['recent']['reward_std']:.3f}")
        
        # Model info
        with st.expander("🔧 Model Information"):
            st.write(f"**Device:** {metrics['model']['device']}")
            st.write(f"**Model Path:** {metrics['model']['model_path'] or 'Not saved yet'}")
            st.write(f"**Last Update:** {metrics['model']['last_update']}")
            st.write(f"**Policy Version:** v{metrics['training']['policy_version']}")
            
            # Action descriptions
            st.markdown("### Available Actions:")
            st.markdown("""
            - **Maintain Session**: Keep interacting normally
            - **Inject Delay**: Add delay to responses (detect patience)
            - **Swap Service Banner**: Change service identification
            - **Present Lure**: Show fake valuable data
            - **Drop Session**: Terminate connection
            """)
        
        # Comparison with Q-learning (if data available)
        st.subheader("📊 PPO vs Q-Learning")
        st.info("""
        **PPO Advantages:**
        - ✅ Deep Neural Network (256 hidden units)
        - ✅ Generalizes across states
        - ✅ Sophisticated reward shaping
        - ✅ Experience replay buffer
        - ✅ Multi-epoch training
        - ✅ GPU acceleration support
        
        **Q-Learning (Old):**
        - ❌ Simple Q-table (dictionary)
        - ❌ No generalization
        - ❌ Basic rewards
        - ❌ Single-step updates
        """)
        
    except ImportError:
        st.error("❌ PPO agent not available. Install PyTorch to enable.")
        st.code("pip install torch>=2.0.0", language="bash")
    
    except Exception as e:
        st.error(f"❌ Error loading PPO metrics: {e}")
        st.exception(e)


def display_ppo_training_recommendations():
    """Display training recommendations based on current metrics."""
    st.subheader("💡 Training Recommendations")
    
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        metrics = collector.get_metrics_summary()
        
        recommendations = []
        
        # Check actor loss
        if metrics['training']['actor_loss'] > 2.0:
            recommendations.append({
                'level': 'warning',
                'title': 'High Actor Loss',
                'message': 'Policy is changing rapidly. Consider reducing learning rate or increasing training stability.',
                'action': 'Monitor next few training steps'
            })
        
        # Check entropy
        if metrics['training']['entropy'] < 0.1:
            recommendations.append({
                'level': 'info',
                'title': 'Low Entropy',
                'message': 'Policy is becoming deterministic. This is normal as training progresses.',
                'action': 'Exploitation mode - good for deployment'
            })
        elif metrics['training']['entropy'] > 1.0:
            recommendations.append({
                'level': 'warning',
                'title': 'High Entropy',
                'message': 'Policy is too random. Increase training or check reward function.',
                'action': 'More training needed'
            })
        
        # Check action distribution
        action_dist = metrics['actions']['distribution']
        max_action_pct = max(action_dist.values())
        if max_action_pct > 0.8:
            recommendations.append({
                'level': 'warning',
                'title': 'Action Imbalance',
                'message': 'Agent heavily favors one action. Review reward function.',
                'action': 'Check if this is desired behavior'
            })
        
        # Check recent performance
        if metrics['recent']['avg_reward'] < 0:
            recommendations.append({
                'level': 'error',
                'title': 'Negative Rewards',
                'message': 'Agent is performing poorly. Review reward function and training.',
                'action': 'Urgent: Check reward computation'
            })
        
        # Display recommendations
        if not recommendations:
            st.success("✅ All metrics look healthy!")
        else:
            for rec in recommendations:
                if rec['level'] == 'error':
                    st.error(f"**{rec['title']}**: {rec['message']}\n\n*Action: {rec['action']}*")
                elif rec['level'] == 'warning':
                    st.warning(f"**{rec['title']}**: {rec['message']}\n\n*Action: {rec['action']}*")
                else:
                    st.info(f"**{rec['title']}**: {rec['message']}\n\n*Action: {rec['action']}*")
    
    except Exception as e:
        st.error(f"Could not generate recommendations: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="PPO Agent Dashboard", page_icon="🚀", layout="wide")
    display_ppo_metrics()
    display_ppo_training_recommendations()
