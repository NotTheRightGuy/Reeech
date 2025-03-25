"use client";

import React, { useRef, useEffect, useState } from "react";
import { TbRewindForward5, TbRewindBackward5 } from "react-icons/tb";
import { FaRegCirclePlay, FaRegCirclePause } from "react-icons/fa6";

interface AudioVisualizerProps {
    speaker: "speaker1" | "speaker2" | "none";
    data: {
        segments: {
            start: number;
            end: number;
            speaker: string;
            text: string;
        }[];
    };
    onTimeUpdate: (time: number) => void;
}

const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
    speaker,
    data,
    onTimeUpdate,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const audioRef = useRef<HTMLAudioElement>(null);
    const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
    const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isAudioLoaded, setIsAudioLoaded] = useState(false);
    const [isHovering, setIsHovering] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [currentSpeaker, setCurrentSpeaker] = useState<string>(speaker);

    useEffect(() => {
        if (audioContext && analyser && canvasRef.current) {
            const canvas = canvasRef.current;
            const canvasCtx = canvas.getContext("2d");
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);

            const draw = () => {
                requestAnimationFrame(draw);

                analyser.getByteFrequencyData(dataArray);

                if (canvasCtx) {
                    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

                    const gradient = canvasCtx.createLinearGradient(
                        0,
                        0,
                        0,
                        canvas.height
                    );

                    // Change gradient colors based on current speaker
                    if (currentSpeaker === "Speaker_1") {
                        gradient.addColorStop(0, "rgba(0, 0, 255, 0.8)"); // Blue
                        gradient.addColorStop(1, "rgba(0, 0, 128, 0.8)");
                    } else {
                        gradient.addColorStop(0, "rgba(255, 0, 0, 0.8)"); // Red
                        gradient.addColorStop(1, "rgba(128, 0, 0, 0.8)");
                    }

                    const barWidth = (canvas.width / bufferLength) * 4;
                    let x = 0;

                    for (let i = 0; i < bufferLength; i++) {
                        const barHeight = isAudioLoaded
                            ? Math.max(dataArray[i] / 2, 1)
                            : 1;

                        canvasCtx.fillStyle = gradient;
                        canvasCtx.beginPath();
                        canvasCtx.roundRect(
                            x,
                            canvas.height / 2 - barHeight / 2,
                            barWidth,
                            barHeight,
                            5
                        );
                        canvasCtx.fill();

                        x += barWidth + 2.5;
                    }
                }
            };

            draw();

            // Add keyboard shortcuts
            const handleKeyDown = (event: KeyboardEvent) => {
                if (event.key === " ") {
                    togglePlayPause();
                } else if (event.key === "ArrowRight") {
                    skipForward();
                } else if (event.key === "ArrowLeft") {
                    skipBackward();
                } else if (event.key === "r") {
                    restartAudio();
                }
            };

            window.addEventListener("keydown", handleKeyDown);

            return () => {
                window.removeEventListener("keydown", handleKeyDown);
            };
        }
    }, [audioContext, analyser, isAudioLoaded, currentSpeaker]);

    useEffect(() => {
        const audio = audioRef.current;
        if (audio) {
            const updateTime = () => {
                const newTime = audio.currentTime;
                setCurrentTime(newTime);
                onTimeUpdate(newTime);
            };

            audio.addEventListener("timeupdate", updateTime);
            audio.addEventListener("loadedmetadata", () => {
                setDuration(audio.duration);
            });

            const updateSpeaker = () => {
                if (audioRef.current) {
                    const currentTime = audioRef.current.currentTime;
                    const segment = data.segments.find(
                        (seg) =>
                            currentTime >= seg.start && currentTime < seg.end
                    );
                    if (segment) {
                        setCurrentSpeaker(segment.speaker);
                    }
                }
            };

            audio.addEventListener("timeupdate", updateSpeaker);
            return () => {
                audio.removeEventListener("timeupdate", updateTime);
                audio.removeEventListener("timeupdate", updateSpeaker);
            };
        }
    }, [data.segments, onTimeUpdate]);

    const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const audio = audioRef.current;
            if (audio) {
                audio.src = URL.createObjectURL(file);
                audio.load();
                audio.play();

                const audioCtx = new (window.AudioContext ||
                    (window as any).webkitAudioContext)();
                const analyserNode = audioCtx.createAnalyser();
                const source = audioCtx.createMediaElementSource(audio);
                source.connect(analyserNode);
                analyserNode.connect(audioCtx.destination);

                setAudioContext(audioCtx);
                setAnalyser(analyserNode);
                setIsPlaying(true);
                setIsAudioLoaded(true);

                audio.onended = () => {
                    setIsPlaying(false);
                };
            }
        }
    };

    const formatTime = (time: number) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    };

    const togglePlayPause = () => {
        const audio = audioRef.current;
        if (audio) {
            if (isPlaying) {
                audio.pause();
            } else {
                audio.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const skipForward = () => {
        const audio = audioRef.current;
        if (audio) {
            audio.currentTime += 5;
        }
    };

    const skipBackward = () => {
        const audio = audioRef.current;
        if (audio) {
            audio.currentTime -= 5;
        }
    };

    const restartAudio = () => {
        const audio = audioRef.current;
        if (audio) {
            audio.currentTime = 0;
            audio.play();
            setIsPlaying(true);
        }
    };

    return (
        <div className="flex flex-col items-center bg-white rounded-md border p-4">
            <input
                type="file"
                accept="audio/*"
                onChange={handleAudioUpload}
                className="mb-4 p-2 rounded"
            />
            <audio ref={audioRef} className="hidden" controls />
            <div
                className="relative w-full"
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
            >
                <canvas
                    ref={canvasRef}
                    className="w-full h-64 rounded-lg"
                ></canvas>

                <div className="flex justify-between items-center w-full mt-2">
                    <span className="text-sm text-gray-600 font-bold font-mono">
                        {formatTime(currentTime)}
                    </span>
                    <span className="text-sm text-gray-600 font-bold font-mono">
                        {formatTime(duration)}
                    </span>
                </div>

                <div className="flex items-center justify-center mt-4 space-x-6">
                    <button
                        onClick={skipBackward}
                        className="text-3xl text-orange-400 hover:text-orange-600 transition-colors duration-300"
                    >
                        <TbRewindBackward5 />
                    </button>
                    <button
                        onClick={togglePlayPause}
                        className="text-5xl text-orange-400 hover:text-orange-600 transition-colors duration-300"
                    >
                        {isPlaying ? <FaRegCirclePause /> : <FaRegCirclePlay />}
                    </button>
                    <button
                        onClick={skipForward}
                        className="text-3xl text-orange-400 hover:text-orange-600 transition-colors duration-300"
                    >
                        <TbRewindForward5 />
                    </button>
                </div>
            </div>
            <div className="mt-4 text-center">
                <span className="font-outfit text-sm bg-gray-100 px-3 py-1 rounded-full">
                    Current Speaker: {currentSpeaker}
                </span>
            </div>
        </div>
    );
};

export default AudioVisualizer;
