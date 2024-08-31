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
    currentTime: number;
    audioSrc: string; // New prop for audio source
}

const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
    speaker,
    data,
    onTimeUpdate,
    currentTime,
    audioSrc,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const audioRef = useRef<HTMLAudioElement>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isAudioLoaded, setIsAudioLoaded] = useState(false);
    const [isHovering, setIsHovering] = useState(false);
    const [duration, setDuration] = useState(0);
    const [currentSpeaker, setCurrentSpeaker] = useState<string>(speaker);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        audio.src = audioSrc;
        audio.load();

        const setupAudio = () => {
            if (!audioContextRef.current) {
                audioContextRef.current = new (window.AudioContext ||
                    (window as any).webkitAudioContext)();
            }

            if (!analyserRef.current) {
                analyserRef.current = audioContextRef.current.createAnalyser();
            }

            if (!sourceRef.current) {
                sourceRef.current =
                    audioContextRef.current.createMediaElementSource(audio);
                sourceRef.current.connect(analyserRef.current);
                analyserRef.current.connect(
                    audioContextRef.current.destination
                );
            }

            setIsAudioLoaded(true);
        };

        audio.onloadedmetadata = () => {
            setDuration(audio.duration);
            setupAudio();
        };

        audio.onended = () => setIsPlaying(false);

        return () => {
            if (sourceRef.current) {
                sourceRef.current.disconnect();
            }
            if (analyserRef.current) {
                analyserRef.current.disconnect();
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, [audioSrc]);

    useEffect(() => {
        const audio = audioRef.current;
        if (audio) {
            const updateTime = () => {
                onTimeUpdate(audio.currentTime);
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

    useEffect(() => {
        const audio = audioRef.current;
        if (audio) {
            const handleTimeUpdate = () => {
                onTimeUpdate(audio.currentTime);
            };
            audio.addEventListener("timeupdate", handleTimeUpdate);
            return () => {
                audio.removeEventListener("timeupdate", handleTimeUpdate);
            };
        }
    }, [onTimeUpdate]);

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
        <div className="flex flex-col border rounded-lg px-4 py-2 h-fit bg-white">
            <audio ref={audioRef} className="hidden" controls />
            <div
                className="relative w-full max-w-3xl"
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
            >
                <canvas
                    ref={canvasRef}
                    className="w-full h-64 rounded-lg"
                ></canvas>

                <div className="flex justify-between items-center w-full mt-2">
                    <span className="text-sm text-gray-500 font-bold font-mono">
                        {formatTime(currentTime)}
                    </span>
                    <span className="text-sm text-gray-500 font-bold font-mono">
                        {formatTime(duration)}
                    </span>
                </div>

                <div className="flex items-center justify-center mt-4 rounded-lg">
                    <button
                        onClick={skipBackward}
                        className="text-3xl mx-4 text-orange-400 hover:text-orange-600 transition-colors duration-300"
                    >
                        <TbRewindBackward5 />
                    </button>
                    <button
                        onClick={togglePlayPause}
                        className="text-4xl mx-4 text-orange-400 rounded-full hover:text-orange-600 transition-colors duration-300"
                    >
                        {isPlaying ? <FaRegCirclePause /> : <FaRegCirclePlay />}
                    </button>
                    <button
                        onClick={skipForward}
                        className="text-3xl mx-4 text-orange-400 hover:text-orange-600 transition-colors duration-300"
                    >
                        <TbRewindForward5 />
                    </button>
                </div>
            </div>
            <div className="mt-2 text-center">
                <span className="font-outfit text-sm">
                    Current Speaker: {currentSpeaker}
                </span>
            </div>
        </div>
    );
};

export default AudioVisualizer;
