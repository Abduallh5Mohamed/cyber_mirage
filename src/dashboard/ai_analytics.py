"""
🧠 AI Analytics Dashboard - Q-Learning Performance Metrics
Advanced visualization for AI deception agent decisions and learning progress.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import psycopg2
import os
import json
from typing import Dict, List
import sys

# Add parent directory for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'cyber_mirage'),
    'user': os.getenv('POSTGRES_USER', 'cybermirage'),
    'password': os.getenv('POSTGRES_PASSWORD', 'ChangeThisToSecurePassword123!')
}

def get_db():
    """Get database connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except:
        return None

def get_ai_performance_metrics() -> Dict:
    """Get comprehensive AI agent performance metrics."""
    conn = get_db()
    if not conn:
        return {}
    
    try:
        cur = conn.cursor()
        
        # Total decisions made
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        total_decisions = cur.fetchone()[0] or 0
        
        # Decisions by action type
        cur.execute("""
            SELECT action, COUNT(*) as count, AVG(reward) as avg_reward
            FROM agent_decisions
            GROUP BY action
            ORDER BY count DESC
        """)
        action_breakdown = {}
        for row in cur.fetchall():
            action_breakdown[row[0]] = {
                'count': row[1],
                'avg_reward': float(row[2]) if row[2] else 0.0
            }
        
        # Overall average reward
        cur.execute("SELECT AVG(reward) FROM agent_decisions WHERE reward IS NOT NULL")
        avg_reward = float(cur.fetchone()[0] or 0.0)
        
        # Reward trend over time (last 100 decisions)
        cur.execute("""
            SELECT created_at, reward, action
            FROM agent_decisions
            WHERE reward IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 100
        """)
        reward_history = []
        for row in cur.fetchall():
            reward_history.append({
                'timestamp': row[0],
                'reward': float(row[1]),
                'action': row[2]
            })
        
        # Exploration vs Exploitation (estimated from action diversity)
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(DISTINCT action) as unique_actions,
                COUNT(*) as total_actions
            FROM agent_decisions
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour DESC
        """)
        exploration_data = []
        for row in cur.fetchall():
            exploration_rate = (row[1] / 5.0) * 100  # 5 possible actions
            exploration_data.append({
                'hour': row[0],
                'exploration_rate': exploration_rate,
                'total_actions': row[2]
            })
        
        # Deception effectiveness (lure success rate) - count positive rewards
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE action = 'present_lure') as lures_presented,
                COUNT(*) FILTER (WHERE action = 'present_lure' AND reward > 0) as successful_lures,
                AVG(reward) FILTER (WHERE action = 'present_lure') as avg_lure_reward
            FROM agent_decisions
        """)
        lure_row = cur.fetchone()
        lures_presented = lure_row[0] or 0
        successful_lures = lure_row[1] or 0
        avg_lure_reward = float(lure_row[2]) if lure_row[2] else 0
        lure_success_rate = (successful_lures / lures_presented * 100) if lures_presented > 0 else 0
        
        # Learning progress (reward improvement over time)
        cur.execute("""
            WITH bucketed AS (
                SELECT 
                    NTILE(10) OVER (ORDER BY created_at) as bucket,
                    reward
                FROM agent_decisions
                WHERE reward IS NOT NULL
            )
            SELECT bucket, AVG(reward) as avg_reward
            FROM bucketed
            GROUP BY bucket
            ORDER BY bucket
        """)
        learning_curve = []
        for row in cur.fetchall():
            learning_curve.append({
                'phase': f"Phase {row[0]}",
                'avg_reward': float(row[1])
            })
        
        cur.close()
        return {
            'total_decisions': total_decisions,
            'action_breakdown': action_breakdown,
            'avg_reward': avg_reward,
            'reward_history': reward_history,
            'exploration_data': exploration_data,
            'lure_success_rate': lure_success_rate,
            'learning_curve': learning_curve
        }
    except Exception as e:
        st.error(f"Error fetching AI metrics: {e}")
        return {}
    finally:
        if conn:
            conn.close()


def render_ai_analytics():
    """Render AI Analytics Dashboard."""
    st.title("AI Analytics Dashboard")
    st.markdown("**Q-Learning Agent Performance & Decision Analysis**")
    
    # Fetch metrics
    metrics = get_ai_performance_metrics()
    
    if not metrics:
        st.warning("No AI decision data available yet. Start attacking the honeypots to see AI in action!")
        return
    
    # === KPIs ===
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Decisions",
            value=f"{metrics['total_decisions']:,}",
            delta="Active" if metrics['total_decisions'] > 0 else "Idle"
        )
    
    with col2:
        # Format reward properly - show more decimals for small values
        avg_r = metrics['avg_reward']
        if avg_r >= 1:
            reward_str = f"{avg_r:.2f}"
        elif avg_r >= 0.01:
            reward_str = f"{avg_r:.3f}"
        else:
            reward_str = f"{avg_r:.4f}"
        st.metric(
            label="Average Reward",
            value=reward_str,
            delta="Learning" if avg_r > 0 else "Starting"
        )
    
    with col3:
        lure_rate = metrics.get('lure_success_rate', 0)
        st.metric(
            label="Lure Success Rate",
            value=f"{lure_rate:.1f}%",
            delta="Improving" if lure_rate > 0 else "Learning"
        )
    
    with col4:
        action_count = len(metrics['action_breakdown'])
        st.metric(
            label="Action Diversity",
            value=f"{action_count}/5 Actions",
            delta="Exploring" if action_count >= 4 else "Exploiting"
        )
    
    st.markdown("---")
    
    # === Action Breakdown ===
    st.markdown("### Action Distribution")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if metrics['action_breakdown']:
            # Pie chart
            df_actions = pd.DataFrame([
                {'Action': k.replace('_', ' ').title(), 'Count': v['count']}
                for k, v in metrics['action_breakdown'].items()
            ])
            fig = px.pie(
                df_actions,
                values='Count',
                names='Action',
                title='AI Action Selection Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Action Details:**")
        for action, data in sorted(metrics['action_breakdown'].items(), key=lambda x: x[1]['count'], reverse=True):
            action_display = action.replace('_', ' ').title()
            avg_r = data['avg_reward']
            # Format reward properly for small values
            if avg_r >= 0.01:
                reward_str = f"{avg_r:.3f}"
            else:
                reward_str = f"{avg_r:.5f}"
            st.markdown(f"""
            **{action_display}**  
            Count: {data['count']}  
            Avg Reward: {reward_str}
            """)
    
    st.markdown("---")
    
    # === Learning Curve ===
    st.markdown("### Learning Progress Over Time")
    if metrics['learning_curve']:
        df_learning = pd.DataFrame(metrics['learning_curve'])
        fig = px.line(
            df_learning,
            x='phase',
            y='avg_reward',
            title='Q-Learning Agent: Reward Improvement Curve',
            markers=True,
            labels={'avg_reward': 'Average Reward', 'phase': 'Learning Phase'}
        )
        fig.update_traces(mode='lines+markers', line_color='#1f77b4', line_width=3, marker_size=10)
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral Reward")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Insight: A rising curve indicates the agent is learning to maximize rewards through better deception strategies!")
    
    st.markdown("---")
    
    # === Reward History ===
    st.markdown("### Recent Reward Timeline (Last 100 Decisions)")
    if metrics['reward_history']:
        df_rewards = pd.DataFrame(metrics['reward_history'])
        df_rewards = df_rewards.sort_values('timestamp')
        
        fig = go.Figure()
        
        # Group by action for color coding
        for action in df_rewards['action'].unique():
            df_action = df_rewards[df_rewards['action'] == action]
            fig.add_trace(go.Scatter(
                x=df_action['timestamp'],
                y=df_action['reward'],
                mode='markers',
                name=action.replace('_', ' ').title(),
                marker=dict(size=8, opacity=0.7)
            ))
        
        fig.update_layout(
            title='Reward Distribution by Action Type',
            xaxis_title='Timestamp',
            yaxis_title='Reward Value',
            hovermode='closest',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # === Exploration vs Exploitation ===
    st.markdown("### Exploration vs Exploitation (Last 24h)")
    if metrics['exploration_data']:
        df_explore = pd.DataFrame(metrics['exploration_data'])
        df_explore = df_explore.sort_values('hour')
        
        fig = px.bar(
            df_explore,
            x='hour',
            y='exploration_rate',
            title='Exploration Rate Over Time',
            labels={'exploration_rate': 'Exploration %', 'hour': 'Hour'},
            color='exploration_rate',
            color_continuous_scale='Viridis'
        )
        fig.add_hline(y=20, line_dash="dash", line_color="red", annotation_text="Min Exploration Target (20%)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("ε-greedy Strategy: High exploration (>40%) means the agent tries new actions. Low (<20%) means it exploits known good actions.")
    
    st.markdown("---")
    
    # === Q-Table Insights ===
    st.markdown("### Q-Table Analysis")
    st.markdown("""
    **Q-Learning Formula:**  
    `Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]`
    
    Where:
    - **α (alpha)**: Learning rate = `0.4`
    - **γ (gamma)**: Discount factor = `0.95`
    - **ε (epsilon)**: Exploration rate = `0.35 → 0.1` (decaying)
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**State Features:**")
        st.code("""
DeceptionState:
  - service (SSH, FTP, HTTP, ...)
  - command_count
  - data_exfil_attempts
  - auth_success
  - duration_seconds
  - last_command
  - suspicion_score
        """, language="yaml")
    
    with col2:
        st.markdown("**Available Actions:**")
        actions_desc = """
1. MAINTAIN: Continue normal operation
2. INJECT_DELAY: Slow down attacker
3. SWAP_BANNER: Change service fingerprint
4. PRESENT_LURE: Offer fake valuable files
5. DROP_SESSION: Terminate connection
        """
        st.code(actions_desc, language="markdown")
    
    st.success("Q-Learning agent is ACTIVE and learning from every attack!")


if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Analytics - Cyber Mirage",
        page_icon="favicon.ico",
        layout="wide"
    )
    render_ai_analytics()
