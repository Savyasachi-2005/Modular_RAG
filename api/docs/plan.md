Of course. Here is a complete documentation for the project structure you requested, incorporating the six main modules of Modular RAG and a simple JWT-based authentication system.

### Project Overview

This document outlines the file structure and architecture for a FastAPI backend that implements the **Modular RAG** framework described in the research paper. The system will use Pinecone as the vector database, Google Gemini for generation, and Google's embedding model. It includes a simple, self-contained JWT authentication system for securing endpoints.

The architecture is designed to be clean and maintainable, following the standard separation of concerns:

*   **`routes`**: Defines the API endpoints.
*   **`controller`**: Contains the core business logic.
*   **`service`**: Handles interactions with external services (Pinecone, Gemini) and implements the core RAG modules.
*   **`schema`**: Defines the data models for request and response validation.
*   **`lib`**: Holds utility code, configuration, and database connections.

---

### File Structure

```
api/
├── main.py
├── controller/
│   ├── __init__.py
│   ├── auth_controller.py
│   └── rag_controller.py
├── lib/
│   ├── __init__.py
│   ├── config.py
│   └── utils.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   └── rag.py
├── schema/
│   ├── __init__.py
│   ├── rag_schema.py
│   ├── token_schema.py
│   └── user_schema.py
├── service/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── gemini_service.py
│   ├── pinecone_service.py
│   └── rag_modules_service.py
├── .env
└── requirements.txt
```

---

### Directory and File Breakdown

#### 1. Root Directory

*   **`main.py`**
    *   **Purpose**: The entry point of the FastAPI application.
    *   **Content**:
        *   Initializes the FastAPI app instance.
        *   Includes the routers from the `routes` directory.
        *   Defines any global middleware (e.g., for CORS).

*   **`.env`**
    *   **Purpose**: Stores environment variables and secrets. This file should NOT be committed to version control.
    *   **Content**:
        ```
        PINECONE_API_KEY=your_pinecone_api_key
        GOOGLE_API_KEY=your_google_api_key
        JWT_SECRET_KEY=your_strong_secret_key
        JWT_ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```

*   **`requirements.txt`**
    *   **Purpose**: Lists all project dependencies.
    *   **Content**:
        ```
        fastapi
        uvicorn[standard]
        pydantic
        python-dotenv
        pinecone-client
        google-generativeai
        passlib[bcrypt]
        python-jose[cryptography]
        ```

#### 2. `routes/` - API Endpoints

*   **`routes/auth.py`**
    *   **Purpose**: Defines the API endpoints for user authentication.
    *   **Endpoints**:
        *   `POST /auth/signup`: To register a new user.
        *   `POST /auth/login`: To authenticate a user and receive a JWT access token.

*   **`routes/rag.py`**
    *   **Purpose**: Defines the protected endpoints for the Modular RAG functionalities.
    *   **Endpoints**:
        *   `POST /rag/index-document`: An endpoint to upload, chunk, embed, and index a document. This will be a protected route.
        *   `POST /rag/query`: The main endpoint to ask a question. It will orchestrate the full Pre-retrieval -> Retrieval -> Post-retrieval -> Generation flow. This will be a protected route.

#### 3. `controller/` - Business Logic

*   **`controller/auth_controller.py`**
    *   **Purpose**: Handles the business logic for user registration and login.
    *   **Functions**:
        *   `register_user()`: Manages the user creation process, calling the service layer to hash the password and save the user.
        *   `login_for_access_token()`: Manages the login process, verifying credentials and creating a JWT token by calling the `auth_service`.

*   **`controller/rag_controller.py`**
    *   **Purpose**: Orchestrates the entire Modular RAG workflow. This is where the "flow" is controlled.
    *   **Functions**:
        *   `process_and_index_document()`: Controls the flow for indexing a new document.
        *   `orchestrate_rag_flow()`: This is the core function. It takes a user query and executes the RAG modules in sequence by calling the appropriate services:
            1.  Calls `pre_retrieval_module` from `rag_modules_service`.
            2.  Calls `retrieval_module` from `rag_modules_service`.
            3.  Calls `post_retrieval_module` from `rag_modules_service`.
            4.  Calls `generation_module` from `rag_modules_service`.
            5.  Returns the final generated answer.

#### 4. `service/` - External Services & Module Implementation

*   **`service/auth_service.py`**
    *   **Purpose**: Handles JWT creation and password hashing.
    *   **Functions**:
        *   `create_access_token()`: Generates a JWT.
        *   `verify_password()`: Compares a plain password with a hashed one.
        *   `get_password_hash()`: Hashes a plain password.
        *   `get_current_user()`: A FastAPI dependency function to decode the JWT from the request header and retrieve the user.

*   **`service/pinecone_service.py`**
    *   **Purpose**: Encapsulates all interactions with the Pinecone vector database.
    *   **Functions**:
        *   `initialize_pinecone()`: Connects to Pinecone.
        *   `upsert_vectors()`: Adds document chunk vectors to the index.
        *   `query_vectors()`: Performs a similarity search for a given query vector.

*   **`service/gemini_service.py`**
    *   **Purpose**: Encapsulates all interactions with the Google Gemini and Embedding APIs.
    *   **Functions**:
        *   `get_embedding()`: Generates a vector embedding for a given text.
        *   `generate_answer()`: Generates a text response based on a prompt (query + context).

*   **`service/rag_modules_service.py`**
    *   **Purpose**: Implements the logic for each of the 6 core RAG modules as described in the paper.
    *   **Functions**:
        *   **`indexing_module(document)`**:
            *   Chunks the input document.
            *   For each chunk, calls `gemini_service.get_embedding`.
            *   Calls `pinecone_service.upsert_vectors` to store the embeddings.
        *   **`pre_retrieval_module(query)`**:
            *   Implements query rewriting or expansion using Gemini.
            *   Returns the enhanced query.
        *   **`retrieval_module(query)`**:
            *   Gets the embedding for the query from `gemini_service`.
            *   Calls `pinecone_service.query_vectors` to fetch relevant chunks.
            *   Returns the retrieved chunks.
        *   **`post_retrieval_module(chunks)`**:
            *   Implements reranking or filtering logic on the retrieved chunks.
            *   Returns the optimized list of chunks.
        *   **`generation_module(query, context_chunks)`**:
            *   Constructs a prompt from the original query and the final context chunks.
            *   Calls `gemini_service.generate_answer` to get the final response.
            *   Returns the generated answer.

#### 5. `schema/` - Data Models

*   **`schema/user_schema.py`**
    *   **Purpose**: Pydantic models related to users.
    *   **Models**: `UserCreate` (for signup), `UserLogin`, `UserInDB`.

*   **`schema/token_schema.py`**
    *   **Purpose**: Pydantic models related to JWTs.
    *   **Models**: `Token`, `TokenData`.

*   **`schema/rag_schema.py`**
    *   **Purpose**: Pydantic models for RAG inputs and outputs.
    *   **Models**: `DocumentPayload` (for indexing), `QueryRequest`, `QueryResponse`.

#### 6. `lib/` - Utilities & Configuration

*   **`lib/config.py`**
    *   **Purpose**: Loads and provides access to environment variables.
    *   **Content**: Uses `python-dotenv` to load the `.env` file and exposes settings through a configuration object.

*   **`lib/utils.py`**
    *   **Purpose**: Contains helper functions. For this project, it can contain a simple user "database."
    *   **Content**:
        *   A simple in-memory dictionary or a JSON file to store user data for this simple auth implementation.
        *   Functions like `get_user`, `create_user`.
        *   **Note**: For production, you would replace this with a proper database connection (e.g., using SQLAlchemy).