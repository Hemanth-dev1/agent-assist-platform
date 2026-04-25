# 🤖 Agent Assist Platform

Real-time AI co-pilot for live customer support agents — built on Google Cloud CCAI, Speech-to-Text, Firestore, BigQuery, and Looker Studio.

**Live:** `https://agent-assist-api-941405866776.us-central1.run.app`  
**Agent Panel:** `https://agent-assist-api-941405866776.us-central1.run.app/panel`

---

## What It Does

- 🎙️ **Speech-to-Text** — transcribes customer audio in real time (96% accuracy)
- 💡 **Agent Assist** — surfaces knowledge articles and smart replies mid-call
- 📊 **Sentiment Analysis** — live score per utterance, visualised in the UI
- 📝 **Post-Call Summary** — auto-generates resolution, topics, action items
- 📈 **Analytics Dashboard** — Looker Studio with 100+ conversations

---

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Cloud Run |
| Agent Assist | Google CCAI Conversations API |
| Speech | Cloud Speech-to-Text |
| Real-time | WebSocket |
| Storage | Firestore + BigQuery |
| Dashboard | Looker Studio |

---

## Quick Demo

**1. Open the live agent panel**Type a customer message → watch transcript + sentiment update live.

**2. Full API flow**
```bash
BASE_URL="https://agent-assist-api-941405866776.us-central1.run.app"
RESP=$(curl -s -X POST $BASE_URL/conversations/start \
  -H 'Content-Type: application/json' \
  -d '{"agent_id":"agent_001","customer_phone":"+919000000001"}')
CONV_ID=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['conversation_id'])")
GCP_CONV=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['gcp_conversation_name'])")
CUSTOMER_P=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['customer_participant'])")
curl -s -X POST $BASE_URL/conversations/utterance \
  -H 'Content-Type: application/json' \
  -d "{\"conversation_id\":\"$CONV_ID\",\"gcp_conversation_name\":\"$GCP_CONV\",\"participant_name\":\"$CUSTOMER_P\",\"text\":\"I was charged twice this month\",\"role\":\"customer\"}"
curl -s -X POST $BASE_URL/conversations/$CONV_ID/complete \
  -H 'Content-Type: application/json' \
  -d "{\"gcp_conversation_name\":\"$GCP_CONV\"}" | python3 -m json.tool
```

**3. Speech-to-Text**
```bash
curl -X POST $BASE_URL/transcribe/file \
  -F "file=@call.wav" -F "agent_id=agent_001" | python3 -m json.tool
```

---

## Project Structure---

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/agent-assist-platform
cd agent-assist-platform/api
pip install -r requirements.txt
export PROJECT_ID=agent-assist-platform
export CONVERSATION_PROFILE_ID=projects/agent-assist-platform/locations/global/conversationProfiles/ZArnerq-T7W2iUlAb8wnzw
uvicorn main:app --reload --port 8080
```

---

*Built on GCP — Cloud Run · CCAI · Speech-to-Text · Firestore · BigQuery · Looker Studio*
