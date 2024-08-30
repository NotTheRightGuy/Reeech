import os
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from AudioAnalyser import AudioAnalyser
import concurrent.futures

app = FastAPI()

# Initialize AudioAnalyser with your Hugging Face token
# HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
audio_analyser = AudioAnalyser("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")


class AnalysisResponse(BaseModel):
    diarization: dict
    transcription: dict
    sentiment: list
    summary: str
    time_taken: float


class DiarizationResponse(BaseModel):
    diarization: dict
    time_taken: float


class TranscriptionResponse(BaseModel):
    transcription: dict
    time_taken: float


class SentimentResponse(BaseModel):
    sentiment: list
    time_taken: float


class SummaryResponse(BaseModel):
    summary: str
    time_taken: float


async def save_upload_file(file: UploadFile) -> str:
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    return temp_file_path


@app.post("/analyze_audio", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    temp_file_path = await save_upload_file(file)

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            diarization_future = executor.submit(
                audio_analyser.get_diarization, temp_file_path
            )
            transcription_future = executor.submit(
                audio_analyser.get_transcription, temp_file_path
            )

            transcription = transcription_future.result()

            sentiment_future = executor.submit(
                audio_analyser.get_sentiment, transcription["text"]
            )
            summary_future = executor.submit(
                audio_analyser.get_summary, transcription["text"]
            )

            diarization = diarization_future.result()
            sentiment = sentiment_future.result()
            summary = summary_future.result()

        time_taken = time.time() - start_time

        return AnalysisResponse(
            diarization=diarization,
            transcription=transcription,
            sentiment=sentiment,
            summary=summary,
            time_taken=time_taken,
        )

    finally:
        os.remove(temp_file_path)


@app.post("/diarization", response_model=dict)
async def get_diarization(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    temp_file_path = await save_upload_file(file)

    try:
        diarization = audio_analyser.get_diarization(temp_file_path)
        time_taken = time.time() - start_time

        return {"diarization": diarization, "time_taken": time_taken}

    finally:
        os.remove(temp_file_path)


@app.post("/transcription", response_model=TranscriptionResponse)
async def get_transcription(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    temp_file_path = await save_upload_file(file)

    try:
        transcription = audio_analyser.get_transcription(temp_file_path)
        time_taken = time.time() - start_time

        return TranscriptionResponse(transcription=transcription, time_taken=time_taken)

    finally:
        os.remove(temp_file_path)


@app.post("/sentiment", response_model=SentimentResponse)
async def get_sentiment(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    temp_file_path = await save_upload_file(file)

    try:
        transcription = audio_analyser.get_transcription(temp_file_path)
        sentiment = audio_analyser.get_sentiment(transcription["text"])
        time_taken = time.time() - start_time

        return SentimentResponse(sentiment=sentiment, time_taken=time_taken)

    finally:
        os.remove(temp_file_path)


@app.post("/summary", response_model=SummaryResponse)
async def get_summary(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    temp_file_path = await save_upload_file(file)

    try:
        transcription = audio_analyser.get_transcription(temp_file_path)
        summary = audio_analyser.get_summary(transcription["text"])
        time_taken = time.time() - start_time

        return SummaryResponse(summary=summary, time_taken=time_taken)

    finally:
        os.remove(temp_file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
