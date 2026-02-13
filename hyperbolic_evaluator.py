import math
from dataclasses import dataclass
from typing import List
from quantum_walk_engine import WalkResult
from material_representation import MaterialState


@dataclass
class EvaluationResult:
    adsorption_score: float
    stability_score: float
    regime: str
    confidence: float
    

class HyperbolicEvaluator:
    def __init__(self):
        pass

    def hyperbolic_distance(self, x: float, y: float) -> float:
        """
        Simplified hyperbolic distance proxy.
        """
        return math.acosh(1 + abs(x - y))

    def evaluate_path(
            self,
            path: WalkResult,
            material: MaterialState,
            goal
    ) -> EvaluationResult:
            """
            Geometry-aware evaluation combining pore hierarchy and composite stability.
            """
    
            if not path.path:
                return EvaluationResult(0.0,0.0, "invalid", 0.0)
        
            pore_scores = []
            stability_scores = []

            if goal == "max_co2":
                target_biochar = 0.75
                target_binder = 0.25
            elif goal == "max_stability":
                target_biochar = 0.55
                target_binder = 0.45
            else:  # balanced
                target_biochar = 0.65
                target_binder = 0.35

        
            for state in path.path:
                pore_index = (
                    0.6 * state.activation_level +
                    0.4 * state.biochar_fraction
                )
        
                pore_index *= (1 - state.plasticizer_fraction)

                composition_alignment = (
                    1
                    - abs(state.biochar_fraction - target_biochar)
                    - abs(state.binder_fraction - target_binder)
                )

                composition_alignment = max(0.0, composition_alignment)
        
                stability_index = (
                    0.45 * state.binder_fraction +
                    0.25 * (1 - abs(state.biochar_fraction - 0.6)) +
                    0.15 * (1 - state.activation_level) +
                    0.1 * (1 - (state.temperature - 300) / 400) +
                    0.05 * (1 - state.time / 5)
                )

                
                if state.activation_level > 0.7 and state.binder_fraction < 0.25:
                    stability_index *= 0.7
        
                pore_scores.append(pore_index)
                stability_scores.append(stability_index)
        
            avg_pore = sum(pore_scores) / len(pore_scores)
            avg_stability = sum(stability_scores) / len(stability_scores)
        
            if avg_pore > 0.65 and avg_stability > 0.5:
                regime = "optimal_composite"
            elif avg_pore > 0.65 and avg_stability <= 0.5:
                regime = "high_adsorption_low_stability"
            elif avg_pore <= 0.65 and avg_stability > 0.5:
                regime = "stable_low_adsorption"
            else:
                regime = "suboptimal"
        
            if goal == "max_co2":
                adsorption_score = avg_pore * 0.8 + avg_stability * 0.2
            elif goal == "max_stability":
                adsorption_score = avg_pore * 0.3 + avg_stability * 0.7
            elif goal == "balanced":  
                adsorption_score = avg_pore * 0.5 + avg_stability * 0.5
            else:
                adsorption_score = avg_pore * 0.5 + avg_stability * 0.5

        
            base_confidence = max(
                0.1,
                min(
                    1.0,
                    (1 - material.uncertainty) * avg_stability
                )
            )
            num_trials = getattr(self, "num_trials", 20)
            trial_factor = min(1.0, (num_trials / 50) ** 0.5)
            final_confidence = min(1.0
                                   ,0.9 * base_confidence + 0.5 * trial_factor)
            confidence = round(final_confidence, 3)


            return EvaluationResult(
                adsorption_score=round(adsorption_score, 3),
                stability_score=round(avg_stability, 3),
                regime=regime,
                confidence=round(confidence, 3)
            )
        
        
    def evaluate(
        self,
        paths: List[WalkResult],
        material: MaterialState,
        goal
    ) -> List[EvaluationResult]:

        results = []
        for p in paths:
            results.append(self.evaluate_path(p, material,goal))
        return results
