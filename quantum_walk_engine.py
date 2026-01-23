# quantum_walk_engine.py

import random
from typing import List
from dataclasses import dataclass
from material_representation import MaterialState
from transformation_space import TransformationState


@dataclass
class WalkResult:
    path: List[TransformationState]
    score: float


class QuantumWalkEngine:
    def __init__(self, steps: int = 5, num_trials: int = 20):
        self.steps = steps
        self.num_trials = num_trials

    def transition_probability(
        self,
        current: TransformationState,
        next_state: TransformationState,
        material: MaterialState
    ) -> float:
        """
        Physics-inspired transition probability with composition awareness.
        """

        # ---- Smoothness penalties (avoid large jumps) ----
        temp_jump = abs(next_state.temperature - current.temperature) / 1000.0
        time_jump = abs(next_state.time - current.time) / 5.0
        act_jump = abs(next_state.activation_level - current.activation_level)

        comp_jump = (
            abs(next_state.biochar_fraction - current.biochar_fraction) +
            abs(next_state.binder_fraction - current.binder_fraction) +
            abs(next_state.plasticizer_fraction - current.plasticizer_fraction)
        )

        smooth_penalty = temp_jump + time_jump + act_jump + comp_jump

        # ---- Composition validity penalties ----
        penalty = 0.0

        # Too little binder → fragile composite
        if next_state.binder_fraction < 0.18:
            penalty += 0.4

        # Too much biochar → pore collapse risk
        if next_state.biochar_fraction > 0.75:
            penalty += 0.3

        # Too much plasticizer → pore blockage
        if next_state.plasticizer_fraction > 0.15:
            penalty += 0.3

        # High activation + low binder is dangerous
        if next_state.activation_level > 0.7 and next_state.binder_fraction < 0.25:
            penalty += 0.4

        # ---- Material-dependent tolerance ----
        stability_factor = material.thermal_stability

        # ---- Final probability ----
        raw_score = stability_factor - smooth_penalty - penalty
        probability = max(0.0, raw_score)

        return probability


    def walk(
        self,
        material: MaterialState,
        space: List[TransformationState],
    ) -> List[WalkResult]:

        results = []

        for _ in range(self.num_trials):
            path = []
            current = random.choice(space)
            score = 0.0

            for _ in range(self.steps):
                candidates = random.sample(space, k=min(5, len(space)))

                probs = [
                    self.transition_probability(current, nxt, material)
                    for nxt in candidates
                ]

                if sum(probs) == 0:
                    break

                next_state = random.choices(candidates, weights=probs)[0]
                chosen_prob = probs[candidates.index(next_state)]
                score += chosen_prob * (1-material.uncertainty)
                path.append(next_state)
                current = next_state

            results.append(WalkResult(path=path, score=score))

        results.sort(key=lambda x: x.score, reverse=True)
        return results
