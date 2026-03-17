# 🍽️ First-Gen AI Zomato Restaurant Recommender

An intelligent, context-aware AI application that provides highly personalized restaurant recommendations using the Zomato Bangalore Dataset. Built with a robust data pipeline, SQLite indexing, FastAPI backend, and an interactive Streamlit frontend. The AI engine is powered by **Llama 3** via the **Groq API**.

## 🚀 Features

- **Automated Data Ingestion:** Automatically downloads the Zomato Bangalore dataset directly from Hugging Face.
- **Data Cleaning & Filtering:** Drops unwanted features, cleans cost and rating strings, and removes duplicates.
- **Local Embedded Database:** Uses SQLite to store the cleaned dataset and creates indexes on frequent queries (e.g., location, cuisines, rating).
- **LLM Integration:** Constructs prompts dynamically injected with SQL results and queries Llama 3 (via Groq) to curate personalized, human-like recommendations.
- **RESTful API Endpoint:** Exposes the recommendation engine via a FastAPI POST endpoint (`/api/v1/recommend`).
- **Interactive UI:** A vibrant, user-friendly Streamlit web application.
- **Dynamic Chained Filters:** Select your desired neighborhood and watch the available cuisines dynamically update.
- **Zomato Magic:** Renders the official Zomato logo and embeds real, clickable Zomato restaurant URLs right in the AI's response so you can instantly view menus and photos!
- **Optional Filters:** Toggle budget and minimum rating constraints on or off based on your exact cravings.

## 🛠️ Architecture / Phases

1.  **Phase 1: Data Ingestion** (`phase1_data_ingestion/`)
2.  **Phase 2: Data Cleaning** (`phase2_data_cleaning/`)
3.  **Phase 3: Indexing & Storage** (`phase3_indexing_storage/`)
4.  **Phase 4: LLM Integration** (`phase4_llm_integration/`)
5.  **Phase 5: API Layer** (`phase5_api_layer/`)
6.  **Phase 6: User Interface** (`phase6_ui_layer/` and `streamlit_app.py`)

*See [architecture.md](architecture.md) for deeper technical layout instructions.*

## ⚙️ Installation & Usage

### 1. Requirements

Ensure you have Python 3.9+ installed on your system.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup API Keys

You must have a [Groq API Key](https://console.groq.com/). Create a `.env` file at the root of the project and add your key:

```env
GROQ_API_KEY=gsk_your_api_key_here
```

### 4. Build the Database (Run Once)

Before running the application, you need to ingest the dataset and safely build the SQLite database locally:

```bash
python phase3_indexing_storage/database_manager.py
```

### 5. Run the Application

#### Streamlit UI (Frontend)
Run the user-friendly web application:

```bash
streamlit run streamlit_app.py
```
*The app will automatically open in your browser at `http://localhost:8501`*

#### FastAPI Server (Backend)
If you want to use the application strictly as an API:

```bash
python phase5_api_layer/main.py
```
*Interactive API Swagger docs will be available at `http://localhost:8000/docs`*

## 🧪 Testing

The codebase includes `pytest` integration and unit tests for every distinct phase, including programmatic simulation of the Streamlit application clicking through the frontend. Run the full test suite securely with:

```bash
python -m pytest .
```
