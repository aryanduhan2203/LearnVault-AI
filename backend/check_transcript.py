import json

video_id = "xB1C1xZZW4k"

with open(
    f"data/chunks/{video_id}_chunks.json",
    "r",
    encoding="utf-8"
) as file:
    chunks = json.load(file)

with open(
    f"data/transcripts/{video_id}.json",
    "r",
    encoding="utf-8"
) as file:
    transcript = json.load(file)["transcript"]

found = False

for chunk in chunks:
    text = chunk["text"]

    if "processinside" in text or "systemitself" in text:
        found = True

        print("\nProblem found!")
        print("Chunk:", chunk["chunk_id"])
        print("Exact chunk text:", repr(text))

        print("\nOriginal segments around this chunk:")

        for segment in transcript:
            if (
                chunk["start_time"] - 3
                <= segment["start"]
                <= chunk["end_time"] + 3
            ):
                print(repr(segment["text"]))

if not found:
    print("Neither suspicious phrase was found in the generated chunks.")