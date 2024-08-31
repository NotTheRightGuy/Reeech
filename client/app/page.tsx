"use client";

import Ripple from "@/components/magicui/ripple";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export default function Page() {
    const router = useRouter();
    return (
        <div className="relative flex h-screen w-full flex-col items-center justify-center overflow-hidden rounded-lg border bg-background md:shadow-xl">
            <p className="z-10 whitespace-pre-wrap text-center text-5xl font-medium tracking-tighter font-outfit text-black">
                Reeech
            </p>
            <p>Turn conversations into insights</p>
            <Button
                className="mt-4 cursor-pointer z-50 "
                onClick={() => {
                    router.push("/dashboard");
                }}
            >
                Let's get Started
            </Button>
            <Ripple />
        </div>
    );
}
