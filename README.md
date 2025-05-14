# Anki-LLM-withQA

## Project Description

Anki-LLM-withQA is a Python-based Streamlit application that integrates Retrieval-Augmented Generation (RAG) with large language models to streamline knowledge ingestion, QA, and Anki card creation workflows. This tool allows users to create and manage projects by subject or category, upload a variety of document types (PDF, MD, DOCX, TXT, images), and automatically index content into a vector database. Users can then perform interactive Q&A, generate concise summaries, and produce customizable Anki flashcards based on their content.

## Key Features

1. **Project Management**

   - Create and organize multiple projects by subject and category.
   - Upload and manage source files: PDF, Markdown, Word, text, and images.
   - Store raw files alongside their vector embeddings for efficient retrieval.

2. **Retrieval-Augmented Generation (RAG)**

   - Ingest and index documents into a vector store (e.g., FAISS, Pinecone, or SQLite + embeddings).
   - Retrieve relevant passages in response to user queries.
   - Summarize and elaborate with a large language model using a default system prompt, designed and optimized for academic QA.

3. **Interactive QA Interface**

   - Query your project knowledge base through a conversational UI.
   - Receive detailed answers, references to source documents, and inline citations.
   - Easily adjust prompts via an advanced prompt-engineering panel.

4. **Anki Flashcard Generation**

   - Automatically convert key concepts and Q&A into Anki cards.
   - Support for basic card types (front/back, cloze deletions).
   - Choose between default templates or customize your own to match your study style.

## Streamlit UI Tabs

The application UI is organized into three main tabs:

1. **RAG**

   - Project and file management.
   - Document ingestion and vector indexing.
   - Embedding settings and index rebuilding.

2. **QA**

   - Enter natural language queries.
   - View model-generated answers with source snippets.
   - Access and fine‑tune the system prompt for tailored responses.

3. **Anki**

   - Generate flashcards from selected Q&A pairs or document sections.
   - Preview cards in-app and export as `.apkg` or Markdown.
   - Manage and edit custom templates.

## Architecture Overview

```
┌────────────────────┐    ┌───────────────────┐    ┌────────────────────┐
│  Streamlit Frontend│ ──▶│  Backend Services │ ──▶│ Vector Store (DB)  │
│  - RAG Tab         │    │  - Ingestion      │    │  (FAISS/Pinecone)  │
│  - QA Tab          │    │  - Embedding      │    └────────────────────┘
│  - Anki Tab        │    │  - Retrieval      │             ▲          
└────────────────────┘    │  - LLM Wrapper    │             │          
                          │  - Anki Export    │             │          
                          └───────────────────┘             │          
                                                            │          
                                                  ┌───────────────────┐
                                                  │   Storage Layer   │
                                                  │  - Raw Files      │
                                                  │  - Metadata       │
                                                  └───────────────────┘
```

## Technology Stack

- **Language**: Python 3.9+
- **UI**: Streamlit
- **Vector Database**: FAISS (local) or Pinecone (cloud)
- **LLM API**: OpenAI GPT-3.5/4 or compatible models
- **File Parsing**: PyMuPDF, python-docx, Markdown, PIL
- **Anki Integration**: genanki or Markdown-to-Anki export

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/mag233/Anki-LLM-withQA.git
   cd Anki-LLM-withQA
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API keys**
   - Set your OpenAI API key:
     ```bash
     export OPENAI_API_KEY="your_key_here"
     ```
4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Future Enhancements

- Support for additional LLM providers and open-source models.
- Multi-user authentication and project sharing.
- Enhanced analytics dashboard for study patterns.
- Mobile-responsive UI and deployment to Streamlit Cloud.

---

Ready to supercharge your study and research workflow with RAG-powered QA and Anki flashcards? Get started now!
