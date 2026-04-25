from google.cloud import firestore
from datetime import datetime

db = firestore.Client()

def create_conversation(conv_id, agent_id, customer_phone):
    doc = {
        'conversation_id': conv_id,
        'agent_id': agent_id,
        'customer_phone': customer_phone,
        'status': 'active',
        'started_at': datetime.utcnow().isoformat(),
        'turns': [],
        'sentiment_scores': [],
        'summary': None
    }
    db.collection('conversations').document(conv_id).set(doc)
    return doc

def add_turn(conv_id, role, text, sentiment=0.0):
    turn = {'role': role, 'text': text, 'sentiment': sentiment,
            'timestamp': datetime.utcnow().isoformat()}
    db.collection('conversations').document(conv_id).update({
        'turns': firestore.ArrayUnion([turn]),
        'sentiment_scores': firestore.ArrayUnion([sentiment])
    })

def update_summary(conv_id, summary):
    db.collection('conversations').document(conv_id).update({
        'summary': summary, 'status': 'completed',
        'ended_at': datetime.utcnow().isoformat()
    })

def get_conversation(conv_id):
    doc = db.collection('conversations').document(conv_id).get()
    return doc.to_dict() if doc.exists else None
