from google.cloud import speech
import logging

speech_client = speech.SpeechClient()

def get_streaming_config():
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_automatic_punctuation=True,
    )
    return speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

def transcribe_file(audio_path: str) -> list:
    import os
    if not os.path.exists(audio_path):
        return []

    with open(audio_path, 'rb') as f:
        content = f.read()

    # Use standard recognize (not streaming) for file transcription
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_automatic_punctuation=True,
    )

    try:
        response = client.recognize(config=config, audio=audio)
        results = []
        for result in response.results:
            results.append({
                'transcript': result.alternatives[0].transcript,
                'confidence': round(result.alternatives[0].confidence, 2),
                'is_final': True
            })
        return results
    except Exception as e:
        logging.error(f'stt_error: {e}')
        return []

def transcribe_chunks(audio_chunks: list) -> list:
    streaming_config = get_streaming_config()

    def generator():
        for chunk in audio_chunks:
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    results = []
    try:
        responses = speech_client.streaming_recognize(streaming_config, generator())
        for response in responses:
            for result in response.results:
                results.append({
                    'transcript': result.alternatives[0].transcript,
                    'confidence': round(result.alternatives[0].confidence, 2),
                    'is_final': result.is_final
                })
    except Exception as e:
        logging.error(f'stt_stream_error: {e}')
    return results
