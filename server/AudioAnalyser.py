import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import librosa
from pyannote.audio import Pipeline
import soundfile as sf


class AudioAnalyser:
    def __init__(self, hugging_face_token):
        self.hugging_face_token = hugging_face_token
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.transcribe_model_id = "distil-whisper/distil-small.en"
        self.diarization_model_id = "pyannote/speaker-diarization-3.1"

    def get_transcription(self, audio_path, model_id="distil-whisper/distil-small.en"):
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        processor = AutoProcessor.from_pretrained(model_id)
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        result = pipe(audio_path)
        return result

    def get_diarization(self, audio_path):

        diarization_pipeline = Pipeline.from_pretrained(
            self.diarization_model_id, use_auth_token=self.hugging_face_token
        )
        diarization_pipeline.to(torch.device(self.device))
        diarization = diarization_pipeline(audio_path)

        # Prepare the result
        speakers = list(diarization.labels())
        segments = []

        # Process each segment
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            start = segment.start
            end = segment.end

            segments.append(
                {
                    "start": float(start),
                    "end": float(end),
                    "speaker": f"Speaker_{speakers.index(speaker) + 1}",
                }
            )

        return {
            "speakers": [f"Speaker_{i+1}" for i in range(len(speakers))],
            "segments": segments,
        }

    def transcribe_segment(self, audio_array, start, end, sr):
        segment = audio_array[int(start * sr) : int(end * sr)]
        sf.write(f"temp/segment_{start}_{end}.wav", segment, sr)
        temp_file_path = f"temp/segment_{start}_{end}.wav"
        transcription = self.get_transcription(temp_file_path)
        return transcription["text"].strip()

    def get_diarization_with_transcription(self, audio_path):
        audio_array, sr = librosa.load(audio_path, sr=None)

        diarization_pipeline = Pipeline.from_pretrained(
            self.diarization_model_id, use_auth_token=self.hugging_face_token
        )
        diarization_pipeline.to(torch.device(self.device))
        diarization = diarization_pipeline(audio_path)

        speakers = list(diarization.labels())
        segments = []

        for segment, track, speaker in diarization.itertracks(yield_label=True):
            start = segment.start
            end = segment.end

            text = self.transcribe_segment(audio_array, start, end, sr)

            segments.append(
                {
                    "start": float(start),
                    "end": float(end),
                    "speaker": f"Speaker_{speakers.index(speaker) + 1}",
                    "text": text,
                }
            )

        return {
            "speakers": [f"Speaker_{i+1}" for i in range(len(speakers))],
            "segments": segments,
        }

    def get_sentiment(self, text):
        from nltk.tokenize import sent_tokenize
        from nltk.sentiment.vader import SentimentIntensityAnalyzer

        def analyze_sentiment(text):
            sentences = sent_tokenize(text)
            analyser = SentimentIntensityAnalyzer()
            results = []
            for sentence in sentences:
                sentiment = analyser.polarity_scores(sentence)
                results.append({"sentence": sentence, "sentiment": sentiment})
            return results

        return analyze_sentiment(text)

    def get_summary(self, transcript, model="llama3.1"):
        from langchain_ollama.llms import OllamaLLM
        from langchain_core.prompts import PromptTemplate

        template = """
            You are an expert in the field of audio transcription. Your task is to summarize the audio transcription
            and provide a well structured summary of the audio transcription. The conversation will be usually among 
            2 or more speakers. Along with the summary, you are also tasked with extracting any important keywords 
            from the transcription. Also generate a single line description which will be used as the title of the transcript.
            Do not hallucinate or provide any false information. Do not provide any other information or
            notes. Follow this structure only:
            <SEP>Title: 'title:string'
            <SEP>Summary: 'summary:string'
            <SEP>Keywords: 'keywords:comma_separated_list'
            
            This is the audio transcription:
            {transcription}
        """
        llm = OllamaLLM(model=model)
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        result = chain.invoke(input={"transcription": transcript})
        return result
