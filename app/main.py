from fastapi import FastAPI

app = FastAPI(title="Booking API")


@app.get("/health")
def health_check():
    return {"status": "ok"}