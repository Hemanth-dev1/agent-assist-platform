from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.agent_assist import create_conversation, add_participant, analyze_content
from services.firestore_client import create_conversation as db_create, add_turn
import uuid, json, logging

router = APIRouter()

@router.websocket('/ws/assist/{agent_id}')
async def assist_websocket(websocket: WebSocket, agent_id: str):
    await websocket.accept()

    conv_id = str(uuid.uuid4())[:8]
    gcp_conv = create_conversation()
    agent_p = add_participant(gcp_conv, 'HUMAN_AGENT')
    customer_p = add_participant(gcp_conv, 'END_USER')
    db_create(conv_id, agent_id, '')

    await websocket.send_json({
        'type': 'session_started',
        'conversation_id': conv_id,
        'gcp_conversation_name': gcp_conv,
        'agent_participant': agent_p,
        'customer_participant': customer_p
    })

    try:
        while True:
            data = await websocket.receive_json()
            text = data.get('text', '').strip()
            role = data.get('role', 'customer')
            if not text:
                continue

            participant = agent_p if role == 'agent' else customer_p
            suggestions = analyze_content(participant, text)
            add_turn(conv_id, role, text, suggestions['sentiment'])

            await websocket.send_json({
                'type': 'suggestions',
                'text': text,
                'role': role,
                'suggestions': suggestions
            })

    except WebSocketDisconnect:
        logging.info(f'ws_disconnected conv={conv_id}')
    except Exception as e:
        logging.error(f'ws_error: {e}')
        await websocket.close()
