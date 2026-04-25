from fastapi import FastAPI
from routes.conversations import router as conv_router
import os

app = FastAPI(
    title='Agent Assist Platform',
    version='1.0.0'
)

app.include_router(conv_router)

@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'agent-assist-platform',
        'version': '1.0.0'
    }
