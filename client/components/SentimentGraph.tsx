import React, { useMemo } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
} from "recharts";

interface SentimentGraphProps {
    segments: Array<{
        start: number;
        end: number;
        text: string;
        sentiment: {
            compound: number;
        };
    }>;
    currentTime: number;
}

const SentimentGraph: React.FC<SentimentGraphProps> = ({
    segments,
    currentTime,
}) => {
    const data = useMemo(() => {
        let accumulatedSentiment = 0;
        const rawData = segments.map((segment) => {
            accumulatedSentiment += segment.sentiment.compound;
            return {
                time: segment.start,
                sentiment: accumulatedSentiment,
                text: segment.text,
            };
        });

        // Find the maximum absolute sentiment value
        const maxAbsSentiment = Math.max(
            ...rawData.map((d) => Math.abs(d.sentiment))
        );

        // Normalize the sentiment values
        return rawData.map((point) => ({
            ...point,
            sentiment:
                maxAbsSentiment !== 0 ? point.sentiment / maxAbsSentiment : 0,
        }));
    }, [segments]);

    const currentIndex = useMemo(() => {
        return data.findIndex((point) => point.time > currentTime) - 1;
    }, [data, currentTime]);

    const maxSentiment = Math.max(...data.map((d) => Math.abs(d.sentiment)));

    return (
        <div className="w-full h-full bg-white rounded-lg shadow-md overflow-hidden flex flex-col">
            <div className="p-4 ">
                <h1 className="text-sm font-bold">Sentiment Analysis</h1>
                <p className="text-xs opacity-75">
                    Accumulated sentiment over time
                </p>
            </div>
            <div className="flex-grow p-4">
                <ResponsiveContainer width="100%" height="70%">
                    <LineChart
                        data={data.slice(0, currentIndex + 1)}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                        <XAxis
                            dataKey="time"
                            stroke="#6b7280"
                            label={{
                                value: "Time (seconds)",
                                position: "insideBottom",
                                offset: -10,
                                fill: "#4b5563",
                            }}
                        />
                        <YAxis
                            domain={[-1, 1]}
                            stroke="#6b7280"
                            label={{
                                value: "Normalized Sentiment",
                                angle: -90,
                                position: "insideLeft",
                                fill: "#4b5563",
                            }}
                        />
                        <Tooltip
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    return (
                                        <div className="bg-white p-3 border border-gray-200 rounded-md shadow-lg">
                                            <p className="font-semibold">{`Time: ${payload[0].payload.time.toFixed(
                                                2
                                            )}s`}</p>
                                            <p className="text-sm text-gray-600">{`Sentiment: ${
                                                typeof payload[0]?.value ===
                                                "number"
                                                    ? payload[0].value.toFixed(
                                                          2
                                                      )
                                                    : payload[0]?.value ?? "N/A"
                                            }`}</p>
                                            <p className="text-sm mt-1 text-gray-700">{`"${payload[0].payload.text}"`}</p>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <ReferenceLine
                            y={0}
                            stroke="#9CA3AF"
                            strokeDasharray="3 3"
                        />
                        <Line
                            type="monotone"
                            dataKey="sentiment"
                            stroke="#8B5CF6"
                            strokeWidth={3}
                            dot={false}
                            activeDot={{
                                r: 8,
                                fill: "#6D28D9",
                                stroke: "#ffffff",
                                strokeWidth: 2,
                            }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default SentimentGraph;
