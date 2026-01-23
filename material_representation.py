# material_representation.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class MaterialState:
    carbon_richness: float
    oxygen_content: float
    thermal_stability: float
    decomposition_rate: float
    moisture_level: float
    uncertainty: float


class MaterialInterpreter:
    def __init__(self):
        pass

    def interpret(self, user_input: Dict) -> MaterialState:
        """
        Convert vague waste information into a unified material state.
        """

        category = user_input.get("category", "unknown")
        moisture = user_input.get("moisture", 0.3)

        # Default assumptions (universal baseline)
        carbon_richness = 0.5
        oxygen_content = 0.5
        thermal_stability = 0.5
        decomposition_rate = 0.5
        uncertainty = 0.4

        if category == "agricultural":
            carbon_richness = 0.6
            oxygen_content = 0.7
            thermal_stability = 0.4
            decomposition_rate = 0.7
            uncertainty = 0.2

        elif category == "plastic":
            carbon_richness = 0.8
            oxygen_content = 0.2
            thermal_stability = 0.8
            decomposition_rate = 0.3
            uncertainty = 0.25

        elif category == "biomass":
            carbon_richness = 0.65
            oxygen_content = 0.6
            thermal_stability = 0.45
            decomposition_rate = 0.6
            uncertainty = 0.3

        return MaterialState(
            carbon_richness=carbon_richness,
            oxygen_content=oxygen_content,
            thermal_stability=thermal_stability,
            decomposition_rate=decomposition_rate,
            moisture_level=moisture,
            uncertainty=uncertainty
        )
