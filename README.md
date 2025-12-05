# PrivateGPT

A private, local-first document AI assistant. Upload your documents, chat with them, and keep your data secure on your own machine.

## Features
- Upload and process PDF, TXT, DOCX, and MD files
- Chat with your documents using local AI (Ollama)
- Semantic search and chunking
- Modern Streamlit UI
- All Python, fully local

## Project Structure
```
privategpt/
  main.py            # Main orchestrator (PrivateGPT class)
  core/              # Backend logic (AI, embeddings, storage, etc.)
  ui/                # Streamlit UI components and app
    streamlit_app.py # Main Streamlit entry point
    components/      # Modular UI components
    utils/           # UI utilities
    assets/          # Static assets
  tests/             # (For future unit/integration tests)
requirements.txt     # Python dependencies
README.md            # This file
.env                 # (Optional) Environment variables
```

## Setup
1. **Clone the repo and navigate to the project root.**
2. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **(Optional) Create a `.env` file for configuration.**
5. **Start the app:**
   ```
   streamlit run ui/streamlit_app.py
   ```

## Configuration
- Use a `.env` file for environment variables (see `.env.example`).
- Ollama must be running locally for AI chat (see [Ollama docs](https://ollama.ai)).

## Development
- All backend logic is in `core/`.
- All UI logic is in `ui/`.
- Add tests in `tests/`.

## License
MIT 