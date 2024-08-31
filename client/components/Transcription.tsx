import React from "react";

interface TranscriptionProps {
    data: {
        segments: Array<{
            start: number;
            end: number;
            text: string;
        }>;
    };
    currentTime: number;
}

export default function Transcription({
    data,
    currentTime,
}: TranscriptionProps) {
    return (
        <main className="border rounded-lg h-full w-full px-4 py-2 bg-white overflow-y-auto">
            <h1 className="text-sm font-bold">Transcription</h1>
            <p className="opacity-75 text-xs mb-4">
                Transcription of the entire audio file
            </p>
            <div className="text-sm opacity-90">
                {data.segments.map((segment, index) => (
                    <span
                        key={index}
                        className={`${
                            currentTime >= segment.start &&
                            currentTime < segment.end
                                ? "bg-yellow-200"
                                : ""
                        }`}
                    >
                        {segment.text}{" "}
                    </span>
                ))}
            </div>
        </main>
    );
}
