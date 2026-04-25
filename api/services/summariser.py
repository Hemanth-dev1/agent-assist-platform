import logging

def generate_call_summary(transcript: list) -> dict:
    if not transcript:
        return {'reason': 'No transcript', 'resolution': 'UNKNOWN', 'action_items': '', 'topics': []}

    all_text = ' '.join([t['text'].lower() for t in transcript])

    # Detect topics
    topics = []
    if any(w in all_text for w in ['charge', 'bill', 'refund', 'payment', 'charged']):
        topics.append('billing')
    if any(w in all_text for w in ['refund', 'money back', 'credit']):
        topics.append('refund')
    if any(w in all_text for w in ['plan', 'upgrade', 'downgrade', 'cancel']):
        topics.append('plan_change')
    if any(w in all_text for w in ['roaming', 'international', 'travel']):
        topics.append('roaming')
    if any(w in all_text for w in ['network', 'signal', 'outage', 'slow']):
        topics.append('network')
    if not topics:
        topics.append('general')

    # Detect resolution
    if any(w in all_text for w in ['thank', 'resolved', 'fixed', 'great', 'perfect', 'done']):
        resolution = 'RESOLVED'
    elif any(w in all_text for w in ['escalat', 'supervisor', 'manager', 'legal', 'complaint']):
        resolution = 'ESCALATED'
    else:
        resolution = 'UNRESOLVED'

    # Build reason
    customer_texts = [t['text'] for t in transcript if t['role'] == 'customer']
    reason = customer_texts[0] if customer_texts else 'Customer inquiry'

    # Action items
    actions = []
    if 'billing' in topics or 'refund' in topics:
        actions.append('Check billing history for duplicate charges')
    if 'plan_change' in topics:
        actions.append('Process plan change request')
    if resolution == 'UNRESOLVED':
        actions.append('Follow up with customer within 24 hours')
    if resolution == 'ESCALATED':
        actions.append('Escalate to Tier 2 team immediately')

    return {
        'reason': reason[:200],
        'resolution': resolution,
        'action_items': ' | '.join(actions) if actions else 'No action required',
        'topics': topics[:3]
    }
