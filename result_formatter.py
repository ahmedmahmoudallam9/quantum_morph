from typing import Dict
from quantum_walk_engine import WalkResult
from hyperbolic_evaluator import EvaluationResult
from material_representation import MaterialState


def quantify_activation(mass_g, concentration_percent):
    solution_volume_ml = mass_g * 20
    acid_mass_g = (solution_volume_ml * concentration_percent / 100) * 3
    return solution_volume_ml, acid_mass_g


def quantify_composite(mass_g, fractions):
    return {
        "biochar": round(mass_g * fractions["biochar"], 2),
        "binder": round(mass_g * fractions["binder"], 2),
        "plasticizer": round(mass_g * fractions["plasticizer"], 2)
    }


class ResultFormatter:
    def format(
        self,
        best_path: WalkResult,
        evaluation: EvaluationResult,
        material: MaterialState,
        user_input: Dict
    ) -> Dict:

        avg_temp = sum(s.temperature for s in best_path.path) / len(best_path.path)
        avg_time = sum(s.time for s in best_path.path) / len(best_path.path)

        goal = user_input.get("processing_goal")
        mass_g = user_input.get("mass", 20)

        pyrolysis = {
            "temperature_celsius": round(avg_temp, 1),
            "duration_hours": round(avg_time, 2),
            "atmosphere": "inert"
        }

        activation = {"enabled": False}

        if goal in ("activated_carbon", "composite_filter"):
            concentration = 5  
            solution_volume, acid_mass = quantify_activation(mass_g, concentration)
        
            activation_input = user_input.get("activation", {})
            agent = activation_input.get("agent", "HCl")

            activation = {
                "enabled": True,
                "type": "chemical",
                "agent": agent,
                "concentration_percent_wv": concentration,
                "solution_volume_ml": round(solution_volume, 1),
                "acid_mass_g": round(acid_mass, 2),
                "soaking_time_hours": 2
            }

        drying = {
            "temperature_celsius": 80,
            "duration_hours": 6
        }

        composite = {"enabled": False}

        if goal == "composite_filter":
            final_state = best_path.path[-1]

            fractions = {
                "biochar": round(final_state.biochar_fraction, 2),
                "binder": round(final_state.binder_fraction, 2),
                "plasticizer": round(final_state.plasticizer_fraction, 2)
            }

            composite = {
                "enabled": True,
                "fractions": fractions,
                "masses_g": quantify_composite(mass_g, fractions)
            }

        return {
            "status": "success",

            "material": {
                "category": user_input.get("category"),
                "name": user_input.get("material_name", "unknown"),
                "input_mass_g": mass_g,
                "moisture": material.moisture_level
            },

            "process_plan": {
                "pyrolysis": pyrolysis,
                "activation": activation,
                "washing": {
                    "enabled": activation["enabled"],
                    "method": "distilled_water_until_neutral_pH"
                },
                "drying": drying,
                "composite_formation": composite
            },

            "predicted_performance": {
                "co2_adsorption_score": evaluation.adsorption_score,
                "stability_score": evaluation.stability_score,
                "structural_regime": evaluation.regime,
                "confidence": round(evaluation.confidence, 2)
            },

            "risk_assessment": {
                "overall_risk": "low",
                "most_sensitive_step": "activation"
            },

            "scientific_explanation": (
                "The AI jointly optimized thermal conditions and composite composition "
                "to balance pore hierarchy and mechanical stability."
            )
        }


