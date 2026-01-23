# transformation_space.py

from dataclasses import dataclass
from typing import List
import numpy as np
from material_representation import MaterialState


@dataclass
class TransformationState:
    temperature: float
    time: float
    activation_level: float

    biochar_fraction: float
    binder_fraction: float
    plasticizer_fraction: float


class TransformationSpace:
    def __init__(self):
        pass

    def generate(self, material: MaterialState) -> List[TransformationState]:
        """
        Generate a feasible transformation space based on material behavior.
        """

        # Base ranges (universal defaults)
        temp_min, temp_max = 300, 900
        time_min, time_max = 0.5, 3.0
        activation_min, activation_max = 0.0, 1.0

        # Adapt ranges based on material stability
        stability = material.thermal_stability

        temp_max = temp_min + stability * (temp_max - temp_min)
        time_max = time_min + material.decomposition_rate * (time_max - time_min)

        temperatures = np.linspace(temp_min, temp_max, 6)
        times = np.linspace(time_min, time_max, 5)
        activations = np.linspace(activation_min, activation_max, 4)
        # ---- COMPOSITION SPACE ----
        if material.thermal_stability < 0.5:
            biochar_range = [0.45, 0.55, 0.65]
            binder_range = [0.25, 0.35]
        else:
            biochar_range = [0.55, 0.65, 0.75]
            binder_range = [0.15, 0.25, 0.35]

        plasticizer_range = [0.0, 0.1, 0.15]

        space = []

        for T in temperatures:
            for t in times:
                for a in activations:
                    for b in biochar_range:
                        for bd in binder_range:
                            for p in plasticizer_range:
                                if abs((b + bd + p) - 1.0) < 0.05:
                                    space.append(
                                        TransformationState(
                                            temperature=float(T),
                                            time=float(t),
                                            activation_level=float(a),

                                            biochar_fraction=b,
                                            binder_fraction=bd,
                                            plasticizer_fraction=p
                                        )
                                    )
        return space
