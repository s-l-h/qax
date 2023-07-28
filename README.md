# 🕵 QAgent - Retrieval Q&A for Code Repositories

QAgent is a small and efficient implementation for Retrieval Question & Answer (Q&A) designed to store embeddings for code repositories or any folder full of text files. With RetriQ, you can create embeddings for folder structures containing text files, such as code repositories, and leverage OpenAI's GPT 3.5 model for performing Q&A on the indexed data.

## Features

- Efficiently stores embeddings for code repositories and other text-based folders.
- Utilizes OpenAI's GPT 3.5 model for question answering on indexed data.
- Supports integration with [pgVector](https://python.langchain.com/docs/integrations/vectorstores/pgvector), a vector extension for PostgreSQL databases.

## Installation and Setup

### Prerequisites
Make sure you have the following installed on your machine:

Docker - for containerization
Git - for cloning the repository

### Clone the Repository

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
PGVECTOR_DATABASE=vectordb
PGVECTOR_USER=victor
PGVECTOR_PASSWORD=vector
PGVECTOR_COLLECTION=git-gpt
```

`db.env`:
```sh
POSTGRES_USER=victor
POSTGRES_PASSWORD=vector
POSTGRES_DB=vectordb
PGDATA=/.vectordb
```

### Start the pgVector Container

#### Linux 🐧
```sh
docker run -d \
--name pgvector \
--env-file=db.env \
-p 5432:5432 \
-v $PWD/.vectordb:/var/lib/postgresql \
ankane/pgvector
```

#### Windows ⌛
```powershell
docker run -d `
--name pgvector `
--env-file=db.env `
-p 54321:5432 `
-v ${PWD}/.vectordb:/var/lib/postgresql `
ankane/pgvector
```

### Enable Extension

```sh
docker cp ./load-ext.sh pgvector:/load-ext.sh && \
docker exec pgvector /load-ext.sh
```

### Parse Files and Create Embeddings

Run the following command to create embeddings for the files in the repository:

```sh
docker run --rm -it --env-file=.env -v ${PWD}:/repository git-gpt --index
```

### Query the Index

To ask questions about the indexed data, use the following command:

```sh
docker run --rm -it --env-file=.env -v ${PWD}:/repository git-gpt "Which libraries are needed to build the app?"
```

## Example Output

Upon querying the index, you will receive an answer based on the indexed data:

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

## License

This project is licensed under the [MIT License](LICENSE).

## Contribution

We welcome contributions from the community! Please follow our [contribution guidelines](link_to_contribution_guidelines) for more details.

## Contact

For any inquiries or support, feel free to reach out to us at [support@logistik.systems](mailto:support@logistik.systems) or join our community on [Discord](https://discord.com/channels/1055055966317588510/1055055966317588513).
