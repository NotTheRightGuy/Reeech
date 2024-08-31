import os
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from AudioAnalyser import AudioAnalyser
import concurrent.futures
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AudioAnalyser with your Hugging Face token
HUGGING_FACE_TOKEN = os.getenv(
    "HUGGING_FACE_TOKEN", "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"
)
audio_analyser = AudioAnalyser(HUGGING_FACE_TOKEN)


class SegmentWithSentiment(BaseModel):
    start: float
    end: float
    speaker: str
    text: str
    sentiment: dict


class AnalysisResponse(BaseModel):
    segments: list[SegmentWithSentiment]
    full_transcription: str
    overall_sentiment: list
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
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join(temp_dir, unique_filename)
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
            diarization_with_transcription_future = executor.submit(
                audio_analyser.get_diarization_with_transcription, temp_file_path
            )

            diarization_with_transcription = (
                diarization_with_transcription_future.result()
            )

            segments_with_sentiment = []
            full_transcription = []

            for segment in diarization_with_transcription["segments"]:
                sentiment = audio_analyser.get_sentiment(segment["text"])
                segments_with_sentiment.append(
                    SegmentWithSentiment(
                        start=segment["start"],
                        end=segment["end"],
                        speaker=segment["speaker"],
                        text=segment["text"],
                        sentiment=sentiment[0]["sentiment"] if sentiment else {},
                    )
                )
                full_transcription.append(segment["text"])

            full_transcription_text = " ".join(full_transcription)

            overall_sentiment_future = executor.submit(
                audio_analyser.get_sentiment, full_transcription_text
            )
            summary_future = executor.submit(
                audio_analyser.get_summary, full_transcription_text
            )

            overall_sentiment = overall_sentiment_future.result()
            summary = summary_future.result()

        time_taken = time.time() - start_time

        return AnalysisResponse(
            segments=segments_with_sentiment,
            full_transcription=full_transcription_text,
            overall_sentiment=overall_sentiment,
            summary=summary,
            time_taken=time_taken,
        )

    finally:
        os.remove(temp_file_path)


@app.post("/diarization", response_model=DiarizationResponse)
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

        return DiarizationResponse(diarization=diarization, time_taken=time_taken)

    finally:
        os.remove(temp_file_path)


@app.post("/diarization-with-transcription", response_model=dict)
async def get_diarization_with_transcription(file: UploadFile = File(...)):
    start_time = time.time()

    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    temp_file_path = await save_upload_file(file)

    try:
        diarization = audio_analyser.get_diarization_with_transcription(temp_file_path)
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
