from google.cloud import bigquery
import os, logging
from datetime import datetime

bq = bigquery.Client()
TABLE = f"{os.environ.get('PROJECT_ID', 'agent-assist-platform')}.agent_assist_analytics.conversations"

def write_conversation(conv: dict, summary: dict):
    turns = conv.get('turns', [])
    sentiments = conv.get('sentiment_scores', [])
    avg_sentiment = round(sum(sentiments) / len(sentiments), 2) if sentiments else 0.0

    row = {
        'conversation_id':    conv.get('conversation_id', ''),
        'agent_id':           conv.get('agent_id', ''),
        'customer_phone':     conv.get('customer_phone', ''),
        'started_at':         conv.get('started_at'),
        'ended_at':           conv.get('ended_at', datetime.utcnow().isoformat()),
        'turn_count':         len(turns),
        'avg_sentiment':      avg_sentiment,
        'resolution':         summary.get('resolution', 'UNKNOWN'),
        'topics':             summary.get('topics', []),
        'summary_reason':     summary.get('reason', ''),
        'summary_resolution': summary.get('action_items', ''),
        'summary_actions':    summary.get('action_items', '')
    }

    errors = bq.insert_rows_json(TABLE, [row])
    if errors:
        logging.error(f'bigquery_error: {errors}')
    else:
        logging.info(f'bigquery_written: {conv["conversation_id"]}')
    return errors
