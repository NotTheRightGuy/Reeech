"use client";

import React, { useState } from "react";
import AudioVisualiser from "@/components/AudioVisualiser";
import data from "@/dummy/1.json";

export default function Page() {
    const [currentTime, setCurrentTime] = useState(0);

    const handleTimeUpdate = (time: number) => {
        setCurrentTime(time);
    };

    return (
        <div>
            <AudioVisualiser
                data={data}
                speaker="none"
                onTimeUpdate={handleTimeUpdate}
            />
            {/* You can now pass currentTime to other components */}
            {/* <OtherComponent currentTime={currentTime} /> */}
        </div>
    );
}
