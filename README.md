# Shadow — Agentic AI Resume & Portfolio 🤖

Shadow is an interactive, RAG-powered (Retrieval-Augmented Generation) AI agent embedded directly into my personal portfolio. Instead of just reading a static resume, visitors can chat with "Shadow" to ask specific questions about my experience, skills, projects, and background. Shadow answers intelligently, grounding its responses strictly in my personal knowledge base and providing citations for its claims.

🌐 **Live Portfolio:** [https://shadowboy-tech.github.io/shadow-resume-ai/](https://shadowboy-tech.github.io/shadow-resume-ai/)

---

## 🏗️ Architecture & Tech Stack

Shadow is built with a modern, lightweight, and cost-effective AI stack:

### 1. Data Ingestion Pipeline (Python)
*   **Parsers:** Custom parsers extract text from Markdown notes, FAQs, and PDF resumes (`pypdf`).
*   **Chunking:** Text is split into semantic chunks for optimal retrieval.
*   **Embeddings:** Offloaded to the **Mistral Embeddings API** (`mistral-embed`) to generate high-quality 1024-dimensional vectors.
*   **Vector Database:** Chunks and embeddings are upserted to a **Pinecone Serverless** index for fast, scalable similarity search.

### 2. Backend API (FastAPI)
*   **Framework:** Built with **FastAPI** for high performance and automatic interactive API documentation.
*   **RAG Engine:** 
    *   *Retrieve:* User queries are embedded via Mistral and used to query Pinecone for the top 3 most relevant context chunks.
    *   *Generate:* The context chunks are passed to the **Mistral AI** (`open-mistral-nemo`) model using a carefully engineered system prompt to generate accurate, grounded, and concise answers, preventing hallucinations.
*   **Rate Limiting:** Secured with `slowapi` to prevent abuse.
*   **Deployment:** Containerized via Docker and deployed on **Render**.

### 3. Frontend & Chat Widget (Vanilla JS/HTML/CSS)
*   **Portfolio:** A responsive, modern single-page portfolio built with HTML, CSS, and Bootstrap.
*   **Widget:** A standalone, dependency-free vanilla JavaScript (`shadow-chat.js`) and CSS (`shadow-chat.css`) widget that injects a floating Action Button (FAB) and chat interface into the DOM.
*   **Integration:** The widget communicates directly with the deployed FastAPI backend via REST.
*   **Deployment:** Hosted statically on **GitHub Pages**.

---

## 🚀 How It Works

1.  **Ask a Question:** A user visits the portfolio and types a question into the Shadow widget (e.g., "What is Muhammad's experience with PyTorch?").
2.  **Vector Search:** The backend receives the question, embeds it into a 1024-dimensional vector, and queries Pinecone to find the most semantically similar text chunks from my resume and notes.
3.  **Prompt Assembly:** The retrieved chunks are combined with the user's question and a strict system prompt instructing the AI to act as my professional representative.
4.  **Answer Generation:** Mistral AI reads the context, synthesizes an answer, and returns it to the frontend, complete with the source files it used (e.g., `["about.md", "Muhammad_CV.pdf"]`).

---

## 💻 Local Development

To run the backend locally:

### Prerequisites
*   Python 3.11+
*   Mistral AI API Key
*   Pinecone API Key & Environment

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shadowboy-tech/shadow-resume-ai.git
   cd shadow-resume-ai
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   MISTRAL_API_KEY="your_mistral_api_key"
   PINECONE_API_KEY="your_pinecone_api_key"
   PINECONE_ENV="your_pinecone_environment"
   PINECONE_INDEX_NAME="shadow-kb"
   EMBEDDING_MODEL_NAME="mistral-embed"
   LLM_MODEL_NAME="open-mistral-nemo"
   ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:5500"
   ```

4. **Populate the Knowledge Base:**
   Add your Markdown, TXT, or PDF files to the `knowledge_base/` directory, then run the ingestion script:
   ```bash
   python -m backend.ingestion.ingest
   ```

5. **Run the API Server:**
   ```bash
   python -m backend.app.main
   ```
   The API will be available at `http://localhost:8000`. You can test endpoints interactively at `http://localhost:8000/docs`.

---

## 👨‍💻 Author

**Muhammad Inuwa Muhammad**
AI/ML Engineer & Robotics Enthusiast
[LinkedIn](https://linkedin.com/in/muhammad-inuwa-muhammad) | [GitHub](https://github.com/shadowboy-tech)
