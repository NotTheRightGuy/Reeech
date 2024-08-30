from pyannote.audio import Pipeline
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from nltk.tokenize import sent_tokenize
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate


class AudioAnalyser:
    def __init__(self, hugging_face_token):
        self.hugging_face_token = hugging_face_token
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    def prettify_diarization(self, diarization):
        speakers = list(diarization.labels())
        segments = []

        for segment, track, speaker in diarization.itertracks(yield_label=True):
            segments.append(
                {
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "speaker": f"Speaker_{speakers.index(speaker) + 1}",
                }
            )

        return {
            "speakers": [f"Speaker_{i+1}" for i in range(len(speakers))],
            "segments": segments,
        }

    def get_diarization(self, audio_path):
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1", use_auth_token=self.hugging_face_token
        )

        pipeline.to(torch.device(self.device))
        diarization = pipeline(audio_path)
        return self.prettify_diarization(diarization)

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

    def get_sentiment(
        self, text, model_id="distilbert-base-uncased-finetuned-sst-2-english"
    ):
        sentiment_analyzer = pipeline(
            "sentiment-analysis", model=model_id, device=self.device
        )

        def analyze_sentiment(text):
            sentences = sent_tokenize(text)
            results = []
            for sentence in sentences:
                sentiment = sentiment_analyzer(sentence)[0]
                results.append(
                    {
                        "sentence": sentence,
                        "sentiment": sentiment["label"],
                        "score": sentiment["score"],
                    }
                )
            return results

        return analyze_sentiment(text)

    def get_summary(self, transcript, model="llama3.1"):
        template = """
            You are an expert in the field of audio transcription. Your task is to summarize the audio transcription
            and provide a well structured summary of the audio transcription. The conversation will be usually among 
            2 or more speakers. Along with the summary, you are also tasked with extracting any important keywords 
            from the transcription. Do not hallucinate or provide any false information. Do not provide any other information or
            notes. Only provide the summary and the keywords in markdown format.
            
            This is the audio transcription:
            {transcription}
        """
        llm = OllamaLLM(model=model)
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        result = chain.invoke(input={"transcription": transcript})
        return result
