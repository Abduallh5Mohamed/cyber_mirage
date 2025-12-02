"""API endpoints for PPO agent metrics and monitoring."""
from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

# Create blueprint
ppo_api = Blueprint('ppo_api', __name__, url_prefix='/api/ppo')


@ppo_api.route('/metrics', methods=['GET'])
def get_ppo_metrics():
    """Get current PPO agent metrics."""
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        metrics = collector.get_metrics_summary()
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting PPO metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'PPO metrics not available'
        }), 500


@ppo_api.route('/performance', methods=['GET'])
def get_ppo_performance():
    """Get PPO performance statistics."""
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        performance = collector.get_recent_performance()
        
        return jsonify({
            'success': True,
            'performance': performance,
            'total_episodes': collector.metrics.total_episodes,
            'total_decisions': collector.metrics.recent_decisions,
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting PPO performance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ppo_api.route('/actions', methods=['GET'])
def get_action_distribution():
    """Get action distribution statistics."""
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        distribution = collector.get_action_distribution()
        counts = collector.metrics.action_counts
        
        return jsonify({
            'success': True,
            'distribution': distribution,
            'counts': counts,
            'total_actions': sum(counts.values())
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting action distribution: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ppo_api.route('/training', methods=['GET'])
def get_training_status():
    """Get PPO training status."""
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        
        return jsonify({
            'success': True,
            'training_step': collector.metrics.training_step,
            'policy_version': collector.metrics.policy_version,
            'actor_loss': collector.metrics.actor_loss,
            'critic_loss': collector.metrics.critic_loss,
            'entropy': collector.metrics.entropy,
            'last_update': collector.metrics.last_update,
            'device': collector.metrics.device,
            'model_path': collector.metrics.model_path
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ppo_api.route('/health', methods=['GET'])
def ppo_health():
    """Check if PPO agent is available and healthy."""
    try:
        from src.ai_agent.ppo_metrics import get_metrics_collector
        from src.ai_agent import USE_PPO
        
        if not USE_PPO:
            return jsonify({
                'success': False,
                'healthy': False,
                'message': 'PPO agent not enabled',
                'fallback': 'Q-learning'
            }), 200
        
        collector = get_metrics_collector()
        
        return jsonify({
            'success': True,
            'healthy': True,
            'agent_type': 'PPO',
            'training_step': collector.metrics.training_step,
            'policy_version': collector.metrics.policy_version,
            'device': collector.metrics.device
        }), 200
        
    except Exception as e:
        logger.error(f"PPO health check failed: {e}")
        return jsonify({
            'success': False,
            'healthy': False,
            'error': str(e)
        }), 500
