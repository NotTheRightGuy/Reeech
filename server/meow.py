from AudioAnalyser import AudioAnalyser

audio_analyser = AudioAnalyser("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")

transcription = audio_analyser.get_diarization_with_transcription("./audio/1.mp3")
with open("trans.txt", "w") as file:
    # Write the transcription to the file which is a dict
    file.write(str(transcription))
