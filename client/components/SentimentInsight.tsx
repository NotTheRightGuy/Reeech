import React, { useState, useEffect } from "react";

interface Segment {
    start: number;
    end: number;
    speaker: string;
    text: string;
    sentiment: {
        compound: number;
    };
}

interface SentimentInsightProps {
    segments: Segment[];
    currentTime: number;
}

const SentimentInsight: React.FC<SentimentInsightProps> = ({
    segments,
    currentTime,
}) => {
    const [currentSegment, setCurrentSegment] = useState<Segment | null>(null);

    useEffect(() => {
        console.log("Segments:", segments);
        console.log("Current Time:", currentTime);
        const segment = segments.find(
            (segment) =>
                currentTime >= segment.start && currentTime < segment.end
        );
        console.log("Found Segment:", segment);
        setCurrentSegment(segment || null);
    }, [segments, currentTime]);

    const getBackgroundColor = (compound: number) => {
        if (compound > 0.05) return "bg-green-100";
        if (compound < -0.05) return "bg-red-100";
        return "bg-gray-100";
    };

    return (
        <main className="border w-full bg-white rounded-lg p-2 overflow-hidden">
            <h1 className="text-sm font-bold">Transcription with sentiments</h1>
            <p className="opacity-75 text-xs">
                Live sentiment analysis of the transcription
            </p>
            <div className="mt-2 h-36 overflow-y-auto">
                {currentSegment ? (
                    <div
                        className={`${getBackgroundColor(
                            currentSegment.sentiment.compound
                        )} p-2 rounded`}
                    >
                        <p className="text-xs">{currentSegment.text}</p>
                        <p className="text-xs mt-1">
                            Sentiment:{" "}
                            {currentSegment.sentiment.compound.toFixed(2)}
                        </p>
                    </div>
                ) : (
                    <div>
                        <p className="text-xs">No current segment</p>
                        <p className="text-xs">Current Time: {currentTime}</p>
                        <p className="text-xs">Segments: {segments.length}</p>
                    </div>
                )}
            </div>
        </main>
    );
};

export default SentimentInsight;
