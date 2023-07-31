## Loading Environment Variables
import os
import argparse
from typing import List, Tuple
from dotenv import load_dotenv
load_dotenv()

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import TextLoader
#from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredFileLoader
from langchain.callbacks import get_openai_callback

def load_docs(root_dir, file_extensions=None):
    """
    Load documents from the specified root directory.
    Ignore dotfiles, dot directories, and files that match .gitignore rules.
    Optionally filter by file extensions.
    """
    docs = []

    # Load .gitignore rules
    gitignore_path = os.path.join(root_dir, ".gitignore")

    if os.path.isfile(gitignore_path):
        with open(gitignore_path, "r") as gitignore_file:
            gitignore = gitignore_file.read()
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, gitignore.splitlines()
        )
    else:
        spec = None

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove dot directories from the list of directory names
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for file in filenames:
            file_path = os.path.join(dirpath, file)

            # Skip dotfiles
            if file.startswith("."):
                continue

            # Skip files that match .gitignore rules
            if spec and spec.match_file(file_path):
                continue

            ext = os.path.splitext(file)[1]

            if file_extensions and ext not in file_extensions:
                continue

            try:
                print(f"processing {file}")
                # loader = UnstructuredFileLoader(
                #     file, mode="elements"
                # )
                if(ext in [".pdf",".PDF"]):
                    loader = PyPDFLoader(file_path)
                    docs.extend(loader.load_and_split())
                else:
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs.extend(loader.load_and_split())

            except Exception:
                pass
    return docs

def similarity_search(db,query):
    # "simple" similarity_search
    docs_with_score = db.similarity_search_with_score(query)
    for doc, score in docs_with_score:
        print("-" * 80)
        print("Score: ", score)
        print(doc.page_content)
        print("-" * 80)


def process_reponse(response):
    print(response["result"])
    print("-" * 80)
    print("\nSources:")
    for source in response["source_documents"]:
        print(f"  - {source.metadata['source']}")

def main(index: bool,query: str):
    embeddings = OpenAIEmbeddings()

    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        
        database=os.environ.get("POSTGRES_DB", "postgres"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )

    COLLECTION_NAME = os.environ.get("PGVECTOR_COLLECTION", "my_collection")

    if index:    
        root_dir = "/repository"
        docs = load_docs(root_dir=root_dir)

        print("Docs loaded")

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(docs)

        # Create the index and store documents in the database
        db = PGVector.from_documents(
            embedding=embeddings,
            documents=texts,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
            #pre_delete_collection=False 
        )

        print("Indexing complete.")
    else:
        
        db = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
            embedding_function=embeddings,
        )



        # build q&a chain
        retriever = db.as_retriever()
        retriever.search_kwargs["distance_metric"] = "cos"
        retriever.search_kwargs["fetch_k"] = 100
        retriever.search_kwargs["maximal_marginal_relevance"] = True
        retriever.search_kwargs["k"] = 10

        # Perform similarity search with the given query
        # similarity_search(db,"What is the required runtime for this application?")

        # RetrievalQA
        # qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(verbose=True),
        #                                        chain_type="stuff",
        #                                        retriever=retriever,
        #                                        return_source_documents=True,
        #                                        verbose=True)
        #response = qa_chain(query)
        #process_reponse(response)

        model = ChatOpenAI(model_name=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"))
        crc = ConversationalRetrievalChain.from_llm(model, retriever=retriever,return_source_documents=True,
                                               verbose=True)
        
        with get_openai_callback() as cb:
            result = crc({"question": query, "chat_history": []})
            print(result["answer"])
            print(f"\n{cb}")






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document Indexing and Similarity Search")
    mutually_exclusive_group = parser.add_mutually_exclusive_group()
    mutually_exclusive_group.add_argument("--index", action="store_true", help="Whether to perform document indexing.")
    mutually_exclusive_group.add_argument("query", nargs="?", type=str, help="The query for similarity search.")

    args = parser.parse_args()
    main(index=args.index, query=args.query)