from fastapi import FastAPI
from quantum_morph_pipeline import QuantumMorphEngine

app = FastAPI()
engine = QuantumMorphEngine()

@app.post("/optimize")
def optimize(user_input: dict):
    return engine.run(user_input)
