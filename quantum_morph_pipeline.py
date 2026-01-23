# quantum_morph_pipeline.py

from material_representation import MaterialInterpreter
from transformation_space import TransformationSpace
from quantum_walk_engine import QuantumWalkEngine
from hyperbolic_evaluator import HyperbolicEvaluator
from result_formatter import ResultFormatter

DEFAULT_TRIALS = {
    "student": 15,
    "researcher": 60,
    "industrial": 30
}

class QuantumMorphEngine:
    def __init__(self):
        self.material_interpreter = MaterialInterpreter()
        self.space_generator = TransformationSpace()
        self.walk_engine = QuantumWalkEngine()
        self.evaluator = HyperbolicEvaluator()
        self.formatter = ResultFormatter()

    def run(self, user_input: dict) -> dict:
        # 1. Understand material
        material = self.material_interpreter.interpret(user_input)

        # 2. Generate transformation space
        space = self.space_generator.generate(material)

        # ✅ SET NUMBER OF TRIALS HERE
        self.walk_engine.num_trials = user_input.get("num_trials", 20)

        # 3. Quantum walk search
        paths = self.walk_engine.walk(material, space)
        self.evaluator.num_trials = self.walk_engine.num_trials

        if not paths:
            return {"status": "no_paths_found"}

        # 4. Evaluate paths
        evaluations = self.evaluator.evaluate(paths, material,user_input["optimization_goal"])

        # 5. Select best result
        best_index = max(
            range(len(evaluations)),
            key=lambda i: evaluations[i].adsorption_score * evaluations[i].confidence
        )

        best_path = paths[best_index]
        best_eval = evaluations[best_index]

        # 6. Format final output
        return self.formatter.format(best_path, best_eval, material,user_input)


# =========================
# CLI INTERFACE (Interactive)
# =========================

def ask_choice(title, options):
    print("\n" + title)
    for i, opt in enumerate(options, 1):
        print(f"[{i}] {opt}")
    while True:
        try:
            choice = int(input("Select option: ").strip())
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except ValueError:
            pass
        print("Invalid choice, try again.")

def ask_yes_no(question):
    while True:
        ans = input(f"{question} (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer y or n.")

def ask_float(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            return float(val)
        except ValueError:
            print("Enter a valid number.")

def ask_int(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print("Enter a valid integer.")

def show_progress():
    import time
    print("\nOptimizing material transformation...")
    print("Running quantum-guided simulations: ", end="", flush=True)
    for _ in range(20):
        print("█", end="", flush=True)
        time.sleep(0.04)
    print(" 100%\n")

def print_result_cli(result):
    material = result["material"]
    plan = result["process_plan"]
    perf = result["predicted_performance"]

    print(">>> OPTIMIZATION COMPLETE <<<\n")

    print("Material Information:")
    print("----------------------------------")
    print(f"• Material          : {material['name']}")
    print(f"• Category          : {material['category']}")
    print(f"• Input Mass        : {material.get('input_mass_g', 'N/A')} g")
    print(f"• Moisture          : {round(material['moisture']*100)} %\n")

    print("Process Plan:")
    print("----------------------------------")

    pyro = plan["pyrolysis"]
    print(f"[Pyrolysis]")
    print(f"  - Temperature     : {pyro['temperature_celsius']} °C")
    print(f"  - Duration        : {pyro['duration_hours']} hours")
    print(f"  - Atmosphere      : {pyro['atmosphere']}\n")

    if plan["activation"]["enabled"]:
        act = plan["activation"]
        print("[Activation]")
        print(f"  - Type            : {act['type']}")
        print(f"  - Agent           : {act['agent']}")
        print(f"  - Concentration   : {act['concentration_percent_wv']} % (w/v)")
        print(f"  - Solution Volume : {act['solution_volume_ml']} mL")
        print(f"  - Acid Mass       : {act['acid_mass_g']} g")
        print(f"  - Soaking Time    : {act['soaking_time_hours']} hours\n")

    dry = plan["drying"]
    print("[Drying]")
    print(f"  - Temperature     : {dry['temperature_celsius']} °C")
    print(f"  - Duration        : {dry['duration_hours']} hours\n")

    if plan["composite_formation"]["enabled"]:
        comp = plan["composite_formation"]

        print("[Composite Formation]")
        print(f"  - Biochar Fraction      : {round(comp['fractions']['biochar']*100)} %")
        print(f"  - Binder Fraction       : {round(comp['fractions']['binder']*100)} %")
        print(f"  - Plasticizer Fraction  : {round(comp['fractions']['plasticizer']*100)} %\n")

        print("  Component Masses:")
        print(f"  - Biochar               : {comp['masses_g']['biochar']} g")
        print(f"  - Binder                : {comp['masses_g']['binder']} g")
        print(f"  - Plasticizer           : {comp['masses_g']['plasticizer']} g\n")


        print("Predicted Performance:")
        print("----------------------------------")
        print(f"• CO₂ Adsorption Score : {perf['co2_adsorption_score']}")
        print(f"• Structural Regime    : {perf['structural_regime']}")
        print(f"• Confidence Level     : {round(perf['confidence']*100)} %\n")

        print("✔ Result saved to: best_recipe.json\n")

# =========================
# USER FLOWS
# =========================

def student_flow():
    category = ask_choice(
        "Choose material category:",
        ["agricultural", "plastic"]
    )

    material = ask_choice(
        "Select example material:",
        ["Rice Straw", "Corn Stalks", "Date Palm Waste"]
    )

    mass = ask_float("Enter sample mass (grams) [10–50]: ")

    goal = ask_choice(
        "What do you want to produce?",
        ["raw_biochar", "activated_carbon", "composite_filter"]
    )
    
    opt_goal = ask_choice(
        "Optimization objective:",
        ["max_co2", "balanced", "max_stability"]
    )


    depth = ask_choice(
        "Simulation depth:",
        ["Fast (10)", "Standard (20)", "Deep (30)"]
    )

    default_trials = DEFAULT_TRIALS["student"]

    num_trials = ask_int(
        f"Number of virtual experiments? (default = {default_trials}): ",
        default=default_trials
    )


    activation = None
    composite = None

    if goal in ("activated_carbon", "composite_filter"):
        activation = {
            "type": "chemical",
            "agent": "HCl",
            "concentration": "5% (AI recommended)"
        }

    if goal == "composite_filter":
        composite = {"strategy": "auto"}

    return {
        "user_type": "student",
        "category": category,
        "material_name": material,
        "mass": mass,
        "processing_goal": goal,
        "optimization_goal": opt_goal,
        "activation": activation,
        "composite": composite,
        "moisture": 0.25,
        "num_trials": num_trials
    }


def researcher_flow():
    knows_moisture = ask_yes_no("Do you know the moisture content?")
    moisture = ask_float("Enter moisture (e.g. 0.25): ") if knows_moisture else 0.3

    category = ask_choice(
        "Select material category:",
        ["agricultural", "biomass", "plastic", "mixed"]
    )

    material = ask_choice(
        "Select material:",
        ["Rice Straw", "Date Palm Seeds", "Other"]
    )

    if material == "Other":
        material = input("Enter new material name: ").strip()

    mass = ask_float("Enter sample mass (grams): ")

    goal = ask_choice(
        "Select processing target:",
        ["raw_biochar", "activated_carbon", "composite_filter"]
    )
    opt_goal = ask_choice(
        "Optimization objective:",
        ["max_co2", "balanced", "max_stability"]
    )


    activation = None
    composite = None

    if goal in ("activated_carbon", "composite_filter"):
        act_type = ask_choice(
            "Select activation method:",
            ["chemical", "physical"]
        )

        if act_type == "chemical":
            agent = ask_choice(
                "Select chemical:",
                ["HCl", "KOH", "H3PO4"]
            )
            knows_conc = ask_yes_no("Do you know the concentration?")
            concentration = (
                ask_float("Enter concentration (e.g. 0.05): ")
                if knows_conc else "auto"
            )
            activation = {
                "type": "chemical",
                "agent": agent,
                "concentration": concentration
            }
        else:
            activation = {"type": "physical"}

    if goal == "composite_filter":
        composite = {
            "strategy": ask_choice(
                "Select composite strategy:",
                ["manual", "auto"]
            )
        }

    default_trials = DEFAULT_TRIALS["researcher"]

    num_trials = ask_int(
        f"Number of virtual experiments? (default = {default_trials}): ",
        default=default_trials
    )


    return {
        "user_type": "researcher",
        "category": category,
        "material_name": material,
        "mass": mass,
        "processing_goal": goal,
        "optimization_goal": opt_goal,
        "activation": activation,
        "composite": composite,
        "moisture": moisture,
        "num_trials": num_trials
    }

def industrial_flow():
    category = ask_choice(
        "Select waste type:",
        ["agricultural", "plastic", "mixed"]
    )

    material = ask_choice(
        "Select waste material:",
        ["Rice Straw", "Date Palm Waste", "Other"]
    )

    if material == "Other":
        material = input("Enter material name: ").strip()

    goal = ask_choice(
        "What do you want to produce?",
        ["raw_biochar", "activated_carbon", "composite_filter"]
    )
    opt_goal = ask_choice(
        "Optimization objective:",
        ["max_co2", "balanced", "max_stability"]
    )


    mass = ask_float("Batch mass (kg): ")
    max_temp = ask_float("Maximum furnace temperature (°C): ")

    activation = None
    composite = None

    if goal in ("activated_carbon", "composite_filter"):
        activation = {
            "type": "chemical",
            "agent": "HCl",
            "concentration": "auto"
        }

    if goal == "composite_filter":
        composite = {"strategy": "auto"}


    default_trials = DEFAULT_TRIALS["industrial"]

    num_trials = ask_int(
        f"Number of virtual experiments? (default = {default_trials}): ",
        default=default_trials
    )

    return {
        "user_type": "industrial",
        "category": category,
        "material_name": material,
        "mass": mass,
        "processing_goal": goal,
        "optimization_goal": opt_goal,
        "activation": activation,
        "composite": composite,
        "moisture": 0.25,
        "num_trials": num_trials
}



# =========================
# MAIN CLI ENTRY
# =========================

if __name__ == "__main__":
    import json
    from quantum_morph_pipeline import QuantumMorphEngine

    print("\n========================================")
    print("   QUANTUM-MORPH | MATERIAL AI LAB")
    print("========================================\n")

    user_type = ask_choice(
        "Who are you?",
        ["Researcher / Scientist", "Industrial User (Factory)", "Student / Learning Mode"]
    )

    if user_type.startswith("Researcher"):
        user_input = researcher_flow()
    elif user_type.startswith("Industrial"):
        user_input = industrial_flow()
    else:
        user_input = student_flow()

    show_progress()

    engine = QuantumMorphEngine()
    result = engine.run(user_input)

    print_result_cli(result)

    with open("best_recipe.json", "w") as f:
        json.dump(result, f, indent=2)

    print("Result saved to: best_recipe.json\n")
