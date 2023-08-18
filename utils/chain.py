from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

chat_history = []


def create_conversational_chain(db, openai_api_key, model="gpt-4"):
    # Create a ChatOpenAI model instance
    llm = ChatOpenAI(model=model, temperature=0.3, openai_api_key=openai_api_key)

    # Create a retriever from the FAISS instance
    retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 3, "fetch_k": 9})

    # Create a ConversationalRetrievalChain instance
    chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        return_source_documents=True,
        return_generated_question=False,
    )

    return chain


base_prompt = """Try to be as complete as possible,
answer in the same language of the question,
reason step by step

QUESTION:
"""


def use_conversational_chain(query, chain):
    """Search for a response to the query in the FAISS database."""

    # Query the database
    result = chain({"question": f"{base_prompt} {query}", "chat_history": chat_history})

    # Add the query and result to the chat history
    chat_history.append((query, result["answer"]))

    # Return the result of the query
    return result["answer"]
