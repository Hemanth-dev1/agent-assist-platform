from google.cloud import dialogflow_v2
import os, logging

PROJECT_ID = os.environ.get('PROJECT_ID', 'agent-assist-platform')
LOCATION = 'global'
PROFILE_ID = os.environ.get('CONVERSATION_PROFILE_ID', '')

conv_client = dialogflow_v2.ConversationsClient()
participant_client = dialogflow_v2.ParticipantsClient()

def get_profile_path():
    if PROFILE_ID.startswith('projects/'):
        return PROFILE_ID
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/conversationProfiles/{PROFILE_ID}"

def create_conversation():
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    conversation = conv_client.create_conversation(
        parent=parent,
        conversation=dialogflow_v2.Conversation(
            conversation_profile=get_profile_path()
        )
    )
    return conversation.name

def add_participant(conversation_name, role):
    role_enum = (
        dialogflow_v2.Participant.Role.HUMAN_AGENT
        if role == 'HUMAN_AGENT'
        else dialogflow_v2.Participant.Role.END_USER
    )
    participant = participant_client.create_participant(
        parent=conversation_name,
        participant=dialogflow_v2.Participant(role=role_enum)
    )
    return participant.name

def analyze_content(participant_name, text, language='en-US'):
    response = participant_client.analyze_content(
        participant=participant_name,
        text_input=dialogflow_v2.TextInput(
            text=text,
            language_code=language
        )
    )
    return _parse_suggestions(response)

def _parse_suggestions(response):
    result = {
        'smart_replies': [],
        'knowledge_articles': [],
        'sentiment': 0.0
    }
    # Fix: sentiment is on the message object differently
    try:
        msg = response.message
        if msg:
            sentiment = getattr(msg, 'sentiment_analysis', None)
            if sentiment is None:
                # Try direct attribute
                try:
                    score = msg.sentiment.score
                    result['sentiment'] = round(score, 2)
                except Exception:
                    pass
            else:
                result['sentiment'] = round(sentiment.score, 2)
    except Exception as e:
        logging.warning(f'sentiment_parse_error: {e}')

    for s in response.human_agent_suggestion_results:
        try:
            if s.suggest_smart_replies_response:
                for a in s.suggest_smart_replies_response.smart_reply_answers:
                    result['smart_replies'].append({
                        'reply': a.reply,
                        'confidence': round(a.confidence, 2)
                    })
        except Exception:
            pass
        try:
            if s.suggest_knowledge_assist_response:
                ka = s.suggest_knowledge_assist_response.knowledge_assist_answer
                if ka and ka.suggested_query_answer:
                    result['knowledge_articles'].append({
                        'query': ka.suggested_query,
                        'answer': ka.suggested_query_answer.answer
                    })
        except Exception:
            pass

    return result

def complete_conversation(conversation_name):
    if conversation_name:
        try:
            conv_client.complete_conversation(name=conversation_name)
        except Exception as e:
            logging.warning(f'complete_error: {e}')
