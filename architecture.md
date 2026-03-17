# Architecture: AI-Powered Restaurant Recommendation Service

## System Overview
The AI-Powered Restaurant Recommendation Service is designed to provide users with highly personalized dining options. It accepts user preferences—specifically **price, location/place, rating, and cuisine**—and retrieves relevant restaurants from a curated dataset (sourced from the Hugging Face Zomato Restaurant Recommendation dataset). An advanced Large Language Model (LLM) then processes these retrieved matches to generate clear, conversational, and user-friendly recommendations explaining exactly why they suit the user's needs.

---

## High-Level System Architecture & Components

The system is composed of several decoupled layers ensuring scalability, maintainability, and clear separation of concerns:

1. **Data Layer**: Responsible for acquiring the raw dataset, cleaning, and preprocessing it for fast retrieval.
2. **Storage/Indexing Layer**: Holds the preprocessed data in an optimized format (e.g., Vector Database or structured SQL) for efficient querying based on user preferences.
3. **Core API / Backend Layer**: The orchestrator that takes user input, applies hard filters against the Storage Layer, and marshals the filtered results to the LLM.
4. **LLM Integration Layer**: Handles prompt construction and communication with the fast **Groq API** for high-speed inference.
5. **User Interface (UI) Layer**: The frontend where users input their preferences and view the final personalized recommendations.

---

## Development Phases

### Phase 1: Data Ingestion
* **Responsibility**: Acquire and load the raw data into the working environment.
* **Tasks**:
  * Connect to the Hugging Face Hub API.
  * Download the `ManikaSaini/zomato-restaurant-recommendation` dataset.
  * Load the raw CSV/Parquet data into memory (e.g., using Pandas or Polars) for initial inspection.

### Phase 2: Data Cleaning & Preprocessing
* **Responsibility**: Transform the raw dataset into a clean, normalized, and reliable format suitable for semantic search or structured filtering.
* **Tasks**:
  * **Filtering Relevant Data**: Extract only the necessary columns required for the recommendation logic (e.g., Restaurant Name, Location, Average Cost for two, Aggregate Rating, Cuisines, URL). Drop irrelevant metadata that introduces noise.
  * **Handling Missing or Inconsistent Values**: 
    * Impute or drop rows with missing crucial data (e.g., dropping rows without ratings or valid locations).
    * Normalize text fields (e.g., standardizing cuisine names, fixing casing/formatting inconsistencies).
    * Parse textual cost and rating values into numerical formats (integers/floats) for strict mathematical filtering (`>`, `<`).
  * **Removing Duplicate Records**: Identify and eliminate duplicate restaurant entries based on a combination of Name and Location/Address to ensure varied and accurate recommendations.

### Phase 3: Indexing & Storage
* **Responsibility**: Store the cleaned data in a system optimized for the expected query patterns.
* **Tasks**:
  * Define the target schema for the processed data.
  * Choose a storage mechanism: 
    * *Relational DB (SQLite/PostgreSQL)* for strict, structured filtering on price, rating, and location.
    * *Vector Database (ChromaDB/Pinecone)* if implementing semantic search over cuisines or restaurant reviews.
  * Ingest the cleaned dataset into the chosen database.
  * Create indexes on frequently queried fields (`location`, `cuisine`, `rating`, `cost`) to ensure low latency.

### Phase 4: Core Recommendation & LLM Integration
* **Responsibility**: Build the engine that matches user preferences to data and generates the final natural language output.
* **Tasks**:
  * **Retrieval Logic (RAG Engine)**: Implement the query logic that maps the user's `(price, place, rating, cuisine)` inputs to a database query, retrieving the top `N` highest-rated candidate restaurants.
  * **Prompt Construction**: Design a structured prompt that injects the user's preferences alongside the details of the top `N` retrieved restaurants. Example: *"You are an expert food critic. The user wants [Cuisine] in [Place] under [Price] with at least [Rating] stars. Based on these available restaurants: [Retrieved Data Context], recommend the best options and explain why they fit the criteria in a user-friendly way."*
  * **API Configuration**: Securely load the user-provided **Groq API Key** (e.g., via `.env` environment variables) to authenticate inference requests.
  * **LLM Calls**: Integrate the **Groq API** (either directly via the `groq` Python client or via LangChain) to submit the prompt, stream the response, and receive the generated recommendation rapidly.

### Phase 5: API Layer
* **Responsibility**: Expose the recommendation engine as a reliable, scalable service.
* **Tasks**:
  * Set up a backend web framework (e.g., Python FastAPI or Flask).
  * Design the RESTful endpoint (e.g., `POST /api/v1/recommend`).
  * Define strict input validation schemas (e.g., using Pydantic) to ensure the client provides valid constraints (e.g., positive price, rating between 0 and 5).
  * Handle edge cases gracefully (e.g., returning a helpful fallback response if no restaurants match the strict database criteria before calling the LLM).

### Phase 6: User Interface (UI) Layer
* **Responsibility**: Provide an intuitive and engaging experience for the end user to interact with the service.
* **Tasks**:
  * Build a frontend application (e.g., Streamlit/Gradio for AI prototyping, or React/Next.js for production).
  * Create intuitive input forms:
    * Dropdowns/Autocomplete for `Place` and `Cuisine`.
    * Sliders/Numeric Inputs for maximum `Price` and minimum `Rating`.
  * Manage loading state to set user expectations during the LLM generation delay.
  * Render the LLM's response (Markdown) cleanly, potentially alongside links to the actual Zomato restaurant pages.
