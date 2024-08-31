interface ParsedData {
    title: string;
    summary: string;
    keywords: string[];
}

function parseString(input: string): ParsedData {
    const parts = input.split("<SEP>");
    const meow: ParsedData = {
        title: "",
        summary: "",
        keywords: [],
    };

    for (let i = 1; i < parts.length; i++) {
        const part = parts[i].trim();
        if (part.startsWith("Title:")) {
            meow.title = part.slice(7).trim().replace(/^'|'$/g, "");
        } else if (part.startsWith("Summary:")) {
            meow.summary = part.slice(9).trim().replace(/^'|'$/g, "");
        } else if (part.startsWith("Keywords:")) {
            meow.keywords = part
                .slice(10)
                .trim()
                .replace(/^'|'$/g, "")
                .split(", ");
        }
    }

    console.log(meow);
    return meow;
}

export default function Summary({ data }: { data: any }) {
    const parsedData = parseString(data.summary);

    return (
        <div className="border rounded-lg h-full w-full px-4 py-2 bg-white">
            <h1 className="text-sm font-bold">Summary</h1>
            <p className="opacity-75 text-xs mb-4">
                Summary of the entire audio file
            </p>
            <h2 className="text-base font-semibold mt-2">{parsedData.title}</h2>
            <div className="text-sm opacity-90">{parsedData.summary}</div>
            <div className="mt-4">
                <h3 className="text-xs font-semibold">Keywords:</h3>
                <div className="flex flex-wrap gap-2 mt-1">
                    {parsedData.keywords.map((keyword, index) => (
                        <span
                            key={index}
                            className="text-xs bg-gray-100 px-2 py-1 rounded"
                        >
                            {keyword}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}
