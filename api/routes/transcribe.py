from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.speech_client import transcribe_chunks, transcribe_file
from services.agent_assist import create_conversation, add_participant, analyze_content
from services.firestore_client import create_conversation as db_create, add_turn
import uuid, logging, tempfile, os

router = APIRouter()

@router.post('/transcribe/file')
async def transcribe_audio_file(
    file: UploadFile = File(...),
    agent_id: str = 'agent_001'
):
    """
    Upload a WAV file → transcribe → run through Agent Assist → return suggestions
    This simulates a complete call: audio → text → AI suggestions
    """
    if not file.filename.endswith('.wav'):
        raise HTTPException(400, 'Only WAV files supported')

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Step 1: Transcribe audio
        logging.info(f'Transcribing file: {file.filename}')
        transcripts = transcribe_file(tmp_path)

        if not transcripts:
            return JSONResponse({
                'status': 'no_speech_detected',
                'transcripts': [],
                'suggestions': []
            })

        # Step 2: Create Agent Assist conversation
        conv_id = str(uuid.uuid4())[:8]
        gcp_conv = create_conversation()
        agent_p = add_participant(gcp_conv, 'HUMAN_AGENT')
        customer_p = add_participant(gcp_conv, 'END_USER')
        db_create(conv_id, agent_id, '')

        # Step 3: Send each final transcript through Agent Assist
        results = []
        for t in transcripts:
            if t['is_final'] and t['transcript'].strip():
                suggestions = analyze_content(customer_p, t['transcript'])
                add_turn(conv_id, 'customer', t['transcript'], suggestions['sentiment'])
                results.append({
                    'transcript': t['transcript'],
                    'confidence': t['confidence'],
                    'suggestions': suggestions
                })

        return {
            'status': 'success',
            'conversation_id': conv_id,
            'total_transcripts': len(transcripts),
            'final_transcripts': len(results),
            'results': results
        }

    finally:
        os.unlink(tmp_path)


@router.post('/transcribe/stream')
async def transcribe_stream(chunks_b64: list, agent_id: str = 'agent_001'):
    """Accept base64-encoded audio chunks and transcribe them."""
    import base64
    try:
        audio_chunks = [base64.b64decode(chunk) for chunk in chunks_b64]
        transcripts = transcribe_chunks(audio_chunks)
        return {'transcripts': transcripts}
    except Exception as e:
        raise HTTPException(500, str(e))
