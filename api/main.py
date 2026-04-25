from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.conversations import router as conv_router
from routes.realtime import router as ws_router
import os

app = FastAPI(title='Agent Assist Platform', version='1.0.0')
app.include_router(conv_router)
app.include_router(ws_router)
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'agent-assist-platform', 'version': '1.0.0'}

@app.get('/panel')
def panel():
    return FileResponse('static/agent_panel.html')
