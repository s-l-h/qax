# 🕵 QAX - Q&A over indeX

qax is a small proof-of-concept implementation for Retrieval Question & Answer (Q&A) aimed to store embeddings for code repositories or any folder full of text files. This code is a simple adaption of the langchain examples, embedded in docker containers

With qax, you can create embeddings for folder structures containing text files, such as code repositories, leverage OpenAI's [text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings) model and store them in a [pgVector](https://python.langchain.com/docs/integrations/vectorstores/pgvector) container. 
After the index has been built, the app uses [langchain´s RetrievelQA chain](https://python.langchain.com/docs/use_cases/question_answering/how_to/vector_db_qa) with `gpt-3.5-turbo` (or `gpt-4` if available) model for performing Q&A on the indexed data.


![Alt text](doc/qa_flow.jpeg)
(see [langchain QA Docs](https://python.langchain.com/docs/use_cases/question_answering/))

## 1. Installation and Setup

### Prerequisites

- [OpenAI API Key](https://platform.openai.com/account/api-keys)
- [Docker](https://docs.docker.com/get-docker/)


### Build the application container

Build a lokal docker container to run the app:

```sh
docker build -t qax .
```

___

## 2. Prepare the data source

To get started, clone any repository and navigate to its root directory:

```sh
git clone https://github.com/your_username/example.git && cd example
```

### Set up Environment Variables

Create two `.env` files in the root directory of the repository with the following contents:

`.env`:
```sh
OPENAI_API_KEY=your_openai_api_key_here

# Database Connection
PGVECTOR_HOST=IP_OF_HOST
PGVECTOR_PORT=5432
PGVECTOR_COLLECTION=qax
```

`db.env`:
```sh
POSTGRES_USER=victor
POSTGRES_PASSWORD=vector
POSTGRES_DB=vectordb
PGDATA=/.vectordb
```

### Start the pgVector Container

#### 🐧 Linux 
```sh
docker run -d \
--name pgvector \
--env-file=db.env \
-p 5432:5432 \
-v $PWD/.vectordb:/var/lib/postgresql \
ankane/pgvector
```

#### ⌛ Windows 
```powershell
docker run -d `
--name pgvector `
--env-file=db.env `
-p 5432:5432 `
-v ${PWD}/.vectordb:/var/lib/postgresql `
ankane/pgvector
```

#### Enable pgVector Extension

```sh
docker cp ./load-ext.sh pgvector:/load-ext.sh && \
docker exec pgvector /load-ext.sh
```
___

## 3. Parse files and create embeddings

Run the following command to create embeddings for the files in the repository:

```sh
docker run --rm -it \
--env-file=.env \
--env-file=db.env \
-v ${PWD}:/repository \
qax --index
```

This will, by default, create a `.vectordb` folder in your repository to store the index. 
To change the name, adjust `PGDATA` variable in `db.env`

___

## 4. Query the Index 💬

To ask questions about the indexed data, use the command below:

```sh
docker run --rm -it \
--env-file=.env \
--env-file=db.env \
-v ${PWD}:/repository \
qax [QUERY]
```

Example 1:

```sh
docker run --rm -it \
--env-file=.env \
--env-file=db.env \
-v ${PWD}:/repository \
qax "Which libraries are needed to build the app?"
```
```
> Entering new RetrievalQA chain...

> Finished chain.
 The libraries needed to build the app are langchain, openai, tiktoken, pathspec, python-dotenv, psycopg2-binary, and pgvector.
--------------------------------------------------------------------------------

Sources:
  - /repository/requirements.txt
  - /repository/Dockerfile
  - /repository/load-ext.sh
  - /repository/README.md
```

Example 2:

```sh
docker run --rm -it \
--env-file=.env \
--env-file=db.env \
-v ${PWD}:/repository \
qax "Create inline documentation for the main function"
```

```
> Entering new RetrievalQA chain...

> Finished chain.


    """The main function of the document indexing and similarity search program.

    Args:
        index (bool): Whether to perform document indexing.
    """
    embeddings = OpenAIEmbeddings()
--------------------------------------------------------------------------------

Sources:
  - /repository/app.py
  - /repository/requirements.txt
  - /repository/README.md
  - /repository/app.py
```

___

## License

This project is licensed under the [MIT License](LICENSE).

## Contribution

We welcome contributions from the community! Please follow our [contribution guidelines](link_to_contribution_guidelines) for more details.

## Contact

For any inquiries or support, feel free to join our community on [Discord](https://discord.com/channels/1055055966317588510/1055055966317588513).
