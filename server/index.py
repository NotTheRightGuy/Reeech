import os
import time
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from AudioAnalyser import AudioAnalyser
import concurrent.futures
import uuid
import json
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIRECTORY = os.path.join(os.getcwd(), "result_audio")

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


class FileIdResponse(BaseModel):
    file_id: str


class StatusResponse(BaseModel):
    status: str


class FileStatus(BaseModel):
    file_id: str
    status: str


class AllFilesStatusResponse(BaseModel):
    files: list[FileStatus]


async def save_upload_file(file: UploadFile) -> str:
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join(temp_dir, unique_filename)
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    return temp_file_path


def process_audio(file_id: str, temp_file_path: str):
    try:
        start_time = time.time()

        # Save the audio file in the result_audio folder
        result_audio_dir = "result_audio"
        os.makedirs(result_audio_dir, exist_ok=True)
        audio_file_path = os.path.join(
            result_audio_dir, f"{file_id}{os.path.splitext(temp_file_path)[1]}"
        )
        shutil.copy(temp_file_path, audio_file_path)

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

        result = AnalysisResponse(
            segments=segments_with_sentiment,
            full_transcription=full_transcription_text,
            overall_sentiment=overall_sentiment,
            summary=summary,
            time_taken=time.time() - start_time,
        )

        # Save result to JSON file
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        result_file_path = os.path.join(results_dir, f"{file_id}.json")
        with open(result_file_path, "w") as f:
            json.dump(result.dict(), f)

    finally:
        os.remove(temp_file_path)


@app.post("/analyze_audio", response_model=FileIdResponse)
async def analyze_audio(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .wav, .mp3, or .ogg file.",
        )

    file_id = str(uuid.uuid4())
    temp_file_path = await save_upload_file(file)

    background_tasks.add_task(process_audio, file_id, temp_file_path)

    return FileIdResponse(file_id=file_id)


@app.get("/get_analysis_result")
async def get_analysis_result(file_id: str):
    results_dir = "results"
    result_file_path = os.path.join(results_dir, f"{file_id}.json")

    if not os.path.exists(result_file_path):
        raise HTTPException(status_code=404, detail="Analysis result not found")

    with open(result_file_path, "r") as f:
        result = json.load(f)

    return result


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


@app.get("/get_audio_file")
async def get_audio_file(file_id: str):
    file_name = f"{file_id}.mp3"  # Assuming the audio files are in MP3 format
    file_path = os.path.join(AUDIO_DIRECTORY, file_name)

    if os.path.exists(file_path):
        return JSONResponse(content={"audio_path": file_name})
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")


@app.get("/audio/{file_path:path}")
async def get_audio(file_path: str):
    full_path = os.path.join(AUDIO_DIRECTORY, file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(full_path, media_type="audio/mpeg")


@app.get("/get_all_files_status", response_model=AllFilesStatusResponse)
async def get_all_files_status():
    temp_dir = "temp_uploads"
    results_dir = "results"

    all_files = []

    # Check files in temp_uploads (in queue)
    for filename in os.listdir(temp_dir):
        file_id = os.path.splitext(filename)[0]
        all_files.append(FileStatus(file_id=file_id, status="in_queue"))

    # Check files in results (processed)
    for filename in os.listdir(results_dir):
        if filename.endswith(".json"):
            file_id = os.path.splitext(filename)[0]
            all_files.append(FileStatus(file_id=file_id, status="processed"))

    return AllFilesStatusResponse(files=all_files)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
