"""Adaptive learning engine with finite state machine."""

import time
from utils.logger import get_logger

logger = get_logger(__name__)


class AdaptiveLearningEngine:
    """
    Adaptive learning engine with hysteresis.
    
    Adjusts learning content based on sustained brain states.
    """
    
    HYSTERESIS_SECONDS = 10.0
    
    def __init__(self, initial_difficulty=5.0):
        """
        Initialize adaptive engine.
        
        Args:
            initial_difficulty (float): Starting difficulty (1-10 scale)
        """
        self.difficulty = initial_difficulty
        self.current_state = None
        self.state_start_time = None
        self.last_action = None
        
        logger.info(f"Initialized adaptive engine (difficulty={self.difficulty})")
    
    def update(self, state, timestamp=None):
        """
        Update with new brain state.
        
        Args:
            state (str): Brain state ('focused', 'drowsy', 'stressed')
            timestamp (float, optional): Current timestamp
        
        Returns:
            dict: Action to take
        """
        if timestamp is None:
            timestamp = time.time()
        
        # State changed
        if state != self.current_state:
            self.current_state = state
            self.state_start_time = timestamp
            return {'action': 'none', 'difficulty': self.difficulty}
        
        # Check if state sustained long enough
        duration = timestamp - self.state_start_time
        
        if duration >= self.HYSTERESIS_SECONDS:
            action = self.get_action(state)
            return action
        
        return {'action': 'none', 'difficulty': self.difficulty}
    
    def get_action(self, state):
        """
        Get action for sustained state.
        
        Args:
            state (str): Brain state
        
        Returns:
            dict: Action and updated difficulty
        """
        if state == 'focused':
            # Increase difficulty
            self.difficulty = min(10.0, self.difficulty + 0.5)
            action = 'increase_difficulty'
            logger.info(f"Action: {action} -> difficulty={self.difficulty}")
            
        elif state == 'drowsy':
            # Trigger break
            action = 'trigger_break'
            logger.info(f"Action: {action}")
            
        elif state == 'stressed':
            # Simplify content
            self.difficulty = max(1.0, self.difficulty - 0.5)
            action = 'simplify_content'
            logger.info(f"Action: {action} -> difficulty={self.difficulty}")
        
        else:
            action = 'none'
        
        self.last_action = action
        
        return {
            'action': action,
            'difficulty': self.difficulty
        }
    
    def reset(self):
        """Reset engine state."""
        self.current_state = None
        self.state_start_time = None
        self.difficulty = 5.0
        logger.info("Adaptive engine reset")


if __name__ == '__main__':
    # Test adaptive engine
    engine = AdaptiveLearningEngine()
    
    # Simulate focused state for 12 seconds
    t = 0
    for i in range(25):
        result = engine.update('focused', timestamp=t)
        print(f"t={t:2.0f}s: {result}")
        t += 0.5
    
    # Switch to stressed
    for i in range(25):
        result = engine.update('stressed', timestamp=t)
        print(f"t={t:2.0f}s: {result}")
        t += 0.5
