from app.services.rag_service import RAGService

rag = RAGService()

try:
    query = "Who won the FIFA World Cup in 1998?"

    result = rag.generate_answer(query)

    print("\nQUESTION:")
    print(query)

    print("\nGENERATED ANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    print(result["sources"])

finally:
    rag.close()