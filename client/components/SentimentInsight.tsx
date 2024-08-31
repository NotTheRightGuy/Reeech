import React, { useMemo } from "react";

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
    const currentSegment = useMemo(() => {
        return segments.find(
            (segment) =>
                currentTime >= segment.start && currentTime < segment.end
        );
    }, [segments, currentTime]);

    const getBackgroundColor = (compound: number) => {
        if (compound > 0.05) return "bg-green-100";
        if (compound < -0.05) return "bg-red-100";
        return "bg-gray-100";
    };

    if (!currentSegment) return null;

    return (
        <div
            className={`p-4 rounded-lg ${getBackgroundColor(
                currentSegment.sentiment.compound
            )}`}
        >
            <p className="font-semibold">{currentSegment.speaker}</p>
            <p>{currentSegment.text}</p>
        </div>
    );
};

export default SentimentInsight;
