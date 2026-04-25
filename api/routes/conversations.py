from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.agent_assist import create_conversation, add_participant, analyze_content, complete_conversation
from services.firestore_client import create_conversation as db_create, add_turn, update_summary, get_conversation
from services.summariser import generate_call_summary
from services.bigquery_writer import write_conversation
import uuid, logging

router = APIRouter()

class StartConvRequest(BaseModel):
    agent_id: str
    customer_phone: str = ''

class UtteranceRequest(BaseModel):
    conversation_id: str
    gcp_conversation_name: str
    participant_name: str
    text: str
    role: str
    language: str = 'en-US'

class CompleteRequest(BaseModel):
    gcp_conversation_name: str = ''

@router.post('/conversations/start')
async def start_conversation(req: StartConvRequest):
    conv_id = str(uuid.uuid4())[:8]
    gcp_conv = create_conversation()
    agent_p = add_participant(gcp_conv, 'HUMAN_AGENT')
    customer_p = add_participant(gcp_conv, 'END_USER')
    db_create(conv_id, req.agent_id, req.customer_phone)
    return {
        'conversation_id': conv_id,
        'gcp_conversation_name': gcp_conv,
        'agent_participant': agent_p,
        'customer_participant': customer_p
    }

@router.post('/conversations/utterance')
async def send_utterance(req: UtteranceRequest):
    suggestions = analyze_content(req.participant_name, req.text, req.language)
    add_turn(req.conversation_id, req.role, req.text, suggestions['sentiment'])
    return {'suggestions': suggestions, 'turn_saved': True}

@router.post('/conversations/{conv_id}/complete')
async def complete(conv_id: str, req: CompleteRequest = CompleteRequest()):
    conv = get_conversation(conv_id)
    if not conv:
        raise HTTPException(404, 'Conversation not found')

    complete_conversation(req.gcp_conversation_name)

    summary = generate_call_summary(conv.get('turns', []))
    update_summary(conv_id, summary)
    write_conversation(conv, summary)

    return {'status': 'completed', 'conversation_id': conv_id, 'summary': summary}

@router.get('/conversations/{conv_id}')
async def get_conv(conv_id: str):
    conv = get_conversation(conv_id)
    if not conv:
        raise HTTPException(404, 'Not found')
    return conv
