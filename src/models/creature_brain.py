"""
Neural network brain for creature decision-making with reinforcement learning.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import time


@dataclass
class NeuralBrain:
    """
    Lightweight neural network for creature decision-making with social learning.
    
    Architecture: 8 inputs → 3 hidden neurons → 6 outputs
    
    Inputs:
        0: Hunger level (0-1)
        1: Nearest threat distance (0-1, closer = higher)
        2: Nearest food distance (0-1, closer = higher)
        3: HP ratio (0-1)
        4: Ally count nearby (0-1)
        5: Familiarity with nearest creature (0-1, based on interaction count)
        6: Trust level with nearest creature (0-1, cooperation ratio)
        7: Threat level from nearest creature (0-1, damage received ratio)
    
    Outputs:
        0: EAT score
        1: FLEE score
        2: FIGHT score
        3: EXPLORE score
        4: COOPERATE score (help/ally with nearest creature)
        5: AVOID score (stay away from nearest creature)
    """
    # Network weights
    input_weights: np.ndarray  # Shape: (8, 3) - input to hidden
    output_weights: np.ndarray  # Shape: (3, 6) - hidden to output
    
    # Learning parameters
    learning_rate: float = 0.2  # Higher initial learning rate for faster adaptation
    recent_actions: List[Tuple] = field(default_factory=list)  # (inputs, action, timestamp)
    
    # Memory inheritance (strongest parent memories)
    inherited_memories: List[Tuple] = field(default_factory=list)  # (situation, action, success)
    
    @staticmethod
    def create_random():
        """Create brain with random weights."""
        return NeuralBrain(
            input_weights=np.random.randn(8, 3) * 0.5,
            output_weights=np.random.randn(3, 6) * 0.5,
            learning_rate=0.2,
            recent_actions=[],
            inherited_memories=[]
        )
    
    @staticmethod
    def create_default():
        """
        Create brain with reasonable default weights.
        
        Pre-trained weights encode basic survival instincts:
        - High hunger → seek food
        - High threat → flee
        - Low HP → defensive
        """
        input_weights = np.array([
            [0.8, -0.3, 0.2],   # Hunger → eat bias
            [-0.5, 0.9, -0.2],  # Threat → flee bias
            [0.6, -0.2, 0.7],   # Food nearby → approach
            [-0.3, 0.4, 0.1],   # HP low → defensive
            [0.2, 0.1, 0.5],    # Allies nearby → confident
            [0.3, 0.2, 0.4],    # Familiarity → social engagement
            [0.5, -0.4, 0.3],   # Trust → cooperation bias
            [-0.6, 0.7, -0.3],  # Threat from creature → avoidance
        ])
        output_weights = np.array([
            [0.7, -0.6, 0.3, 0.1, 0.2, -0.4],   # Neuron 1: eat/approach/cooperate bias
            [-0.8, 0.9, 0.2, -0.3, -0.5, 0.8],  # Neuron 2: flee/avoid bias
            [0.4, -0.2, 0.6, 0.5, 0.3, -0.2],   # Neuron 3: fight/explore/social bias
        ])
        return NeuralBrain(
            input_weights=input_weights,
            output_weights=output_weights,
            learning_rate=0.2,
            recent_actions=[],
            inherited_memories=[]
        )
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """
        Forward pass through network.
        
        Args:
            inputs: [hunger, threat_distance, food_distance, hp_ratio, ally_count, familiarity, trust, threat_level]
            
        Returns:
            outputs: [eat_score, flee_score, fight_score, explore_score, cooperate_score, avoid_score]
        """
        # Hidden layer with tanh activation
        hidden = np.tanh(inputs @ self.input_weights)
        
        # Output layer with tanh activation
        outputs = np.tanh(hidden @ self.output_weights)
        
        return outputs
    
    def decide_action(self, inputs: np.ndarray) -> str:
        """
        Make decision based on neural network output.
        
        Returns:
            action: 'EAT', 'FLEE', 'FIGHT', 'EXPLORE', 'COOPERATE', or 'AVOID'
        """
        outputs = self.forward(inputs)
        action_idx = np.argmax(outputs)
        actions = ['EAT', 'FLEE', 'FIGHT', 'EXPLORE', 'COOPERATE', 'AVOID']
        
        # Record this decision for learning
        self.recent_actions.append((inputs.copy(), action_idx, time.time()))
        
        # Keep only last 10 decisions
        if len(self.recent_actions) > 10:
            self.recent_actions.pop(0)
        
        return actions[action_idx]
    
    def decide_social_action(self, inputs: np.ndarray) -> Optional[str]:
        """
        Decide on social action specifically (COOPERATE or AVOID).
        
        Returns social action if score is high enough, None otherwise.
        
        Returns:
            'COOPERATE', 'AVOID', or None
        """
        outputs = self.forward(inputs)
        
        cooperate_score = outputs[4]
        avoid_score = outputs[5]
        
        # Threshold for social actions (must be confident)
        SOCIAL_THRESHOLD = 0.3
        
        # Return strongest social action if above threshold
        if cooperate_score > SOCIAL_THRESHOLD and cooperate_score > avoid_score:
            return 'COOPERATE'
        elif avoid_score > SOCIAL_THRESHOLD and avoid_score > cooperate_score:
            return 'AVOID'
        
        return None
    
    def apply_reward(self, reward: float):
        """
        Apply reinforcement learning update to recent decisions.
        
        Uses gradient ascent to strengthen weights for rewarded actions
        and weaken weights for penalized actions.
        
        Args:
            reward: Positive for good outcomes, negative for bad
        """
        # Update weights for last 5 decisions (credit assignment)
        for inputs, action_idx, timestamp in self.recent_actions[-5:]:
            # Time decay: more recent decisions get more credit
            time_weight = 1.0 - (time.time() - timestamp) / 10.0
            time_weight = max(0.1, time_weight)
            
            effective_reward = reward * time_weight
            
            # Forward pass to get current outputs
            hidden = np.tanh(inputs @ self.input_weights)
            outputs = np.tanh(hidden @ self.output_weights)
            
            # Gradient for output layer
            output_grad = np.zeros(6)
            output_grad[action_idx] = effective_reward
            
            # Backprop (simplified)
            output_delta = output_grad * (1 - outputs**2)  # tanh derivative
            hidden_delta = (output_delta @ self.output_weights.T) * (1 - hidden**2)
            
            # Update weights
            self.output_weights += np.outer(hidden, output_delta) * self.learning_rate
            self.input_weights += np.outer(inputs, hidden_delta) * self.learning_rate
            
            # Clip weights to prevent explosion
            self.input_weights = np.clip(self.input_weights, -5.0, 5.0)
            self.output_weights = np.clip(self.output_weights, -5.0, 5.0)
    
    def copy_from(self, other: 'NeuralBrain', blend_factor: float = 0.1):
        """
        Copy weights from another brain (observational learning).
        
        Args:
            other: Brain to copy from
            blend_factor: How much to blend (0.0 = no change, 1.0 = full copy)
        """
        self.input_weights = (1 - blend_factor) * self.input_weights + blend_factor * other.input_weights
        self.output_weights = (1 - blend_factor) * self.output_weights + blend_factor * other.output_weights
    
    def mutate(self, mutation_rate: float = 0.1):
        """
        Apply random mutations to weights (for evolution).
        
        Args:
            mutation_rate: Strength of mutations
        """
        self.input_weights += np.random.randn(8, 3) * mutation_rate
        self.output_weights += np.random.randn(3, 6) * mutation_rate
        
        # Clip after mutation
        self.input_weights = np.clip(self.input_weights, -5.0, 5.0)
        self.output_weights = np.clip(self.output_weights, -5.0, 5.0)
    
    def inherit_from_parents(self, parent1: 'NeuralBrain', parent2: 'NeuralBrain'):
        """
        Inherit brain from parents with memory preservation.
        
        Blends parent weights and keeps strongest memories.
        
        Args:
            parent1: First parent brain
            parent2: Second parent brain
        """
        # Blend parent weights
        self.input_weights = (parent1.input_weights + parent2.input_weights) / 2
        self.output_weights = (parent1.output_weights + parent2.output_weights) / 2
        
        # Inherit strongest memories from both parents
        # This gives offspring a head start on learning
        all_memories = parent1.inherited_memories + parent2.inherited_memories
        
        # Keep top 5 most successful memories
        all_memories.sort(key=lambda m: m[2], reverse=True)  # Sort by success
        self.inherited_memories = all_memories[:5]
        
        # Apply small mutation
        self.mutate(mutation_rate=0.1)
        
        # Start with higher learning rate (decays over time)
        self.learning_rate = 0.3  # Faster learning for young creatures
    
    def decay_learning_rate(self, age: float):
        """
        Reduce learning rate as creature ages.
        
        Young creatures learn fast, old creatures are set in their ways.
        
        Args:
            age: Creature age in seconds
        """
        # Decay from 0.3 to 0.1 over 60 seconds
        target_rate = 0.1
        initial_rate = 0.3
        decay_time = 60.0
        
        progress = min(age / decay_time, 1.0)
        self.learning_rate = initial_rate + (target_rate - initial_rate) * progress
    
    def to_dict(self) -> dict:
        """Serialize for saving."""
        return {
            'input_weights': self.input_weights.tolist(),
            'output_weights': self.output_weights.tolist(),
            'learning_rate': self.learning_rate,
            'inherited_memories': self.inherited_memories
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'NeuralBrain':
        """Deserialize from saved data."""
        return NeuralBrain(
            input_weights=np.array(data['input_weights']),
            output_weights=np.array(data['output_weights']),
            learning_rate=data.get('learning_rate', 0.2),
            recent_actions=[],
            inherited_memories=data.get('inherited_memories', [])
        )
