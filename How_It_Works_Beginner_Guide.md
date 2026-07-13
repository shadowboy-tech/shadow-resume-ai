# How We Built Shadow: A Beginner's Guide 🚀

If you are looking at this code and wondering, *"How does all of this actually work?"*, you are in the right place! We are going to break down exactly how we built this AI chatbot from scratch, explaining it as simply as possible.

---

## The Core Concept: What is RAG?

Normally, if you ask an AI model (like ChatGPT or Mistral) a specific question about *you*—like "What did Muhammad build at Togo Mobility?"—it will guess or say it doesn't know. It only knows what it was trained on months or years ago.

To fix this, we used a technique called **RAG (Retrieval-Augmented Generation)**. 
Think of RAG like giving the AI an **open-book test**. 

Instead of asking the AI to answer from memory, we:
1. **Find** the exact paragraphs in your resume that contain the answer.
2. **Hand** those paragraphs to the AI.
3. **Ask** the AI to read them and answer the user's question based *only* on what we just handed it.

Here is exactly how we built the code to do that, step-by-step.

---

## Step 1: Ingestion (Reading the Book)
**Folder:** `backend/ingestion/`

Before the AI can answer questions, we have to prepare your knowledge base (your PDF resume, the `about.md` file, and the `faq.md` file). Computers can't just "read" a whole folder of files instantly, so we have to process them.

1. **Extracting Text (`parser.py`):** First, we wrote code using the `pypdf` library to open your resume and pull out all the raw text. We did the same for your Markdown (`.md`) files.
2. **Chunking (`chunker.py`):** If we give the AI too much text at once, it gets confused (and it costs more money). So, we wrote a "chunker." It takes your entire resume and chops it into small paragraphs (about 500 characters each). 
3. **Embeddings (`embed.py`):** This is the magic part. Computers don't understand English; they understand math. We send every single text chunk to **Mistral's Embedding API**. Mistral reads the chunk and turns its "meaning" into a long list of 1,024 numbers (a vector). For example, the word "Apple" and "Banana" will have numbers that look mathematically similar.
4. **The Database (`ingest.py`):** We take those chunks of text and their 1,024 numbers and save them in a special database called **Pinecone**. Pinecone is a "Vector Database"—it is extremely fast at comparing those lists of numbers to find similar meanings.

---

## Step 2: The Backend (The Librarian)
**Folder:** `backend/app/`

Now that your data is saved in Pinecone, we need a server that acts like a librarian. It listens for questions from users, finds the right data, and talks to the AI. We built this using **FastAPI** (a very fast Python web framework).

Here is what happens when someone asks: *"Where did Muhammad go to school?"*

1. **Receiving the Question (`main.py`):** The FastAPI server receives the question over the internet.
2. **Embedding the Question (`rag/embed.py`):** We immediately send the user's question to Mistral to turn it into a list of 1,024 numbers (just like we did with your resume).
3. **Searching (`rag/retrieve.py`):** We take the question's numbers and ask Pinecone: *"Find the 3 chunks of text in the database that have numbers most similar to this question."* Pinecone instantly returns the exact paragraphs from your resume mentioning your education.
4. **Generating the Answer (`rag/generate.py`):** We take those 3 paragraphs and the user's question and send them *both* to the main **Mistral AI model** (`open-mistral-nemo`). We give it a strict prompt: *"You are Muhammad's AI assistant. Answer the user's question using ONLY the context provided."* Mistral reads the context, generates a smart, human-like answer, and sends it back to our server.

---

## Step 3: The Frontend (The Interface)
**Folder:** `frontend/components/ShadowChat/`

We have a working brain (the backend), but users need a way to talk to it on your website. 

1. **The Widget (`shadow-chat.js` & `shadow-chat.css`):** Instead of using a heavy framework like React, we wrote pure, vanilla JavaScript and CSS. This makes the code tiny and fast. 
2. **How it works:** The JavaScript creates the HTML elements for the chat bubble (💬) and the chat window. 
3. **Talking to the Backend:** When a user types a message and hits "Send", the JavaScript uses the `fetch()` API to send an HTTP request to our FastAPI backend over the internet. While it waits for the backend to do all the vector math and AI prompting, it shows a little typing animation. When the answer comes back, it displays it in the chat window.

---

## Step 4: Deployment (Putting it on the Internet)

If the code only lives on your laptop, nobody can use it. We had to deploy it.

1. **Docker (`Dockerfile`):** We put the backend code into a "Docker container." This is like putting the code in a specialized, portable shipping container that has exactly the right version of Python and all the required libraries pre-installed so it never breaks.
2. **Render (The Backend Host):** We pushed the code to GitHub and linked it to **Render.com**. Render takes our Docker container and runs it on a live server 24/7. This gave us our live API URL (`https://shadow-resume-ai.onrender.com`).
3. **GitHub Pages (The Website Host):** Your portfolio (`index.html` and the chat widget) doesn't need a complex server; it's just static files. We set up a "GitHub Action" (`.github/workflows/pages.yml`) that automatically copies your `frontend/` folder and publishes it to the web for free whenever you push new code to GitHub.

---

## Summary of the Tech Stack

*   **Python:** The language powering the backend logic.
*   **FastAPI:** The web framework for the backend server.
*   **Mistral AI:** The "brain" that turns text into numbers (Embeddings) and generates human-like answers (LLM).
*   **Pinecone:** The vector database that quickly finds the right paragraphs.
*   **Vanilla JS/CSS:** Used to build the lightweight chat widget.
*   **Render & GitHub Pages:** Used to host the backend and frontend on the live internet.
