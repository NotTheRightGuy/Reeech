"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import AudioVisualiser from "@/components/AudioVisualiser";
import SentimentInsight from "@/components/SentimentInsight";
import Transcription from "@/components/Transcription";
import SentimentGraph from "@/components/SentimentGraph";
import Summary from "@/components/Summary";

interface AnalysisData {
    segments: any[];
    full_transcription: string;
    overall_sentiment: any[];
    summary: string;
    time_taken: number;
}

export default function Page() {
    const [currentTime, setCurrentTime] = useState<number>(0);
    const [data, setData] = useState<AnalysisData | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [audioSrc, setAudioSrc] = useState<string | null>(null);
    const { id } = useParams();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const analysisResponse = await fetch(
                    `http://localhost:8000/get_analysis_result?file_id=${id}`
                );
                if (!analysisResponse.ok) {
                    throw new Error("Failed to fetch analysis data");
                }
                const analysisResult = await analysisResponse.json();
                setData(analysisResult);

                // Fetch audio file path
                const audioPathResponse = await fetch(
                    `http://localhost:8000/get_audio_file?file_id=${id}`
                );
                if (!audioPathResponse.ok) {
                    throw new Error("Failed to fetch audio file path");
                }

                const { audio_path } = await audioPathResponse.json();

                // Construct the URL for the audio file
                const audioUrl = `http://localhost:8000/audio/${encodeURIComponent(
                    audio_path
                )}`;
                setAudioSrc(audioUrl);

                setIsLoading(false);
            } catch (err) {
                setError("Error fetching data. Please try again.");
                setIsLoading(false);
            }
        };

        fetchData();

        // No need to revoke object URL as we're not creating one anymore
    }, [id]);

    const handleTimeUpdate = (time: number) => {
        setCurrentTime(time);
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    if (!data || !audioSrc) {
        return <div>No data available</div>;
    }

    return (
        <div className="px-2 py-2 grid grid-cols-3 gap-x-2 font-outfit bg-[#F5F5F5] h-screen overflow-clip">
            <div className="grid grid-rows-2 gap-y-2">
                <AudioVisualiser
                    data={data}
                    speaker="none"
                    onTimeUpdate={handleTimeUpdate}
                    currentTime={currentTime}
                    audioSrc={audioSrc}
                />
                <Summary data={data} />
            </div>

            <div className="grid gap-y-2">
                <SentimentInsight
                    segments={data.segments}
                    currentTime={currentTime}
                />
                <SentimentGraph
                    segments={data.segments}
                    currentTime={currentTime}
                />
            </div>
            <Transcription data={data} currentTime={currentTime} />
        </div>
    );
}
