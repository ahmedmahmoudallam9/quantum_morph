from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from quantum_morph_pipeline import QuantumMorphEngine
import uuid

app = FastAPI()
engine = QuantumMorphEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

@app.post("/optimize")
def optimize(user_input: dict):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "result": None
    }

    def run_job():
        result = engine.run(user_input)
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = result

    import threading
    threading.Thread(target=run_job).start()

    return {"job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})
