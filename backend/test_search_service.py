from app.services.search_service import SearchService

search_service = SearchService()

queries = [
    "How does database indexing improve query performance?",
    "Who won the FIFA World Cup in 1998?"
]

try:
    for query in queries:
        print("\nQuery:", query)

        results = search_service.search(query, limit=5)

        if not results:
            print("No sufficiently relevant results found.")
            continue

        for i, result in enumerate(results, 1):
            print(f"\nResult {i}")
            print("Score:", round(result["score"], 4))
            print("Video ID:", result["video_id"])
            print("Text:", result["text"][:300])

finally:
    search_service.close()