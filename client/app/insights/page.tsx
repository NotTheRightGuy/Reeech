import AudioVisualiser from "@/components/AudioVisualiser";

export default function Insights() {
    return (
        <main className="flex min-h-screen justify-center items-center">
            <AudioVisualiser
                audioSrc="/1.mp3"
                barCount={64}
                key={1}
                speakerNumber={2}
            />
        </main>
    );
}
