import React from "react";

function Sidebar() {
    return <aside className="min-h-screen w-16 bg-white">Meow</aside>;
}

export default function page() {
    return (
        <div className="min-h-screen bg-[#] flex">
            <Sidebar />
            <main></main>
        </div>
    );
}
