import os
import json
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.faiss_store import create_multiple_and_merge, save_store

# from utils.pinecone_store import create_store
import tiktoken
from functools import reduce


folder = "src_recipes"
index_name = "blubasilico-ai"


def tokens_count(text):
    # encoding = tiktoken.encoding_for_model("text-embedding-ada-002") # cl100k_base
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens_integer = encoding.encode(text)
    # print(f"number of tokens: {len(tokens_integer)}")
    return len(tokens_integer)


def create_docs(folder):
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=600)

    for file in tqdm(os.listdir(folder)):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(folder, file)
        with open(file_path, "r") as f:
            content = f.read()
            recipe = json.loads(content)
            title = recipe["title"]
            title = title.encode("utf-8").decode("unicode_escape") if title else title
            category = recipe["category"]
            category = (
                category.encode("utf-8").decode("unicode_escape")
                if category
                else category
            )
            difficulty = recipe["difficulty"]
            difficulty = (
                difficulty.encode("utf-8").decode("unicode_escape")
                if difficulty
                else difficulty
            )
            docs = splitter.create_documents([content])
            for doc in docs:
                doc.metadata = {"title": title, "category": category}
            all_docs.extend(docs)

    return all_docs


MAX_TOKENS = 1000000


def update_docs_batches(res, current_doc):
    # calculate number of tokens for current doc
    current_doc_count = tokens_count(current_doc.page_content)

    # Attempt to get the last element from the result array.
    last = res[-1] if res else None

    # If there's a last element and its count combined with the current document count
    # is less than MAX_TOKENS, append to it. Otherwise, create a new batch.
    if last and last["count"] + current_doc_count < MAX_TOKENS:
        last["docs"].append(current_doc)
        last["count"] += current_doc_count
    else:
        res.append({"count": current_doc_count, "docs": [current_doc]})

    return res


def ingest_faiss(docs_batches):
    if not os.path.exists("faiss_index"):
        db = create_multiple_and_merge(
            docs_batches, openai_api_key=os.environ["OPENAI_API_KEY"]
        )

        # save the db
        save_store("recipes", db, True)


def ingest_pinecone(docs_batches):
    # merge all docs from all batches into docs
    docs = []
    for batch in docs_batches:
        docs.extend(batch["docs"])

    # create db
    # create_store(index_name, docs, openai_api_key=os.environ["OPENAI_API_KEY"])


def main():
    docs = create_docs(folder)
    docs_batches = reduce(update_docs_batches, docs, [])
    # from docs_batches print the number and the count for every batch
    for i, batch in enumerate(docs_batches):
        print(f"batch {i+1}: {len(batch['docs'])} docs, {batch['count']} tokens")

    print(f"docs length: {len(docs)}")

    ingest_faiss(docs_batches)
    # ingest_pinecone(docs_batches)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
