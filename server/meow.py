from AudioAnalyser import AudioAnalyser

audio_analyser = AudioAnalyser("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")

diarization = audio_analyser.get_diarization("./audio/1.mp3")
transcription = audio_analyser.get_transcription("./audio/1.mp3")
diarization_with_transcription = audio_analyser.get_diarization_with_transcription(
    "./audio/1.mp3"
)

# print(diarization)
# print("================================")
# print(transcription)
# print("================================")
print(diarization_with_transcription)
