<!-- Add logo at the top -->
<p align="center">
  <img src="literature-app/assets/logo.png" alt="ScholarPilot: AI Literature Review & Knowledge Pipeline Logo" width="280"/>
</p>

**Project Title**

Personal Knowledge Base & Learning Assistant

---

## Table of Contents

1. [Project Purpose](#project-purpose)
2. [Key Features](#key-features)
3. [Project Structure](#project-structure)
4. [Project Progress](#project-progress)
5. [Wish List](#wish-list)
6. [Installation](#installation)
7. [Usage](#usage)
8. [Contributing](#contributing)
9. [License](#license)

---

## Project Purpose

This application is designed as a **personal knowledge base** and **learning assistant**, helping self-driven learners to:

* Ingest and organize various document types (PDFs, articles, notes).
* Ask questions and retrieve accurate information from the knowledge base.
* Generate Anki-style flashcards for efficient review and retention.
* Track learning progress and milestones.

---

## Key Features

* **Document Ingestion:** Import PDFs and text documents via multiple loaders (e.g., PyMuPDF, pdfplumber).
* **Flexible Chunking:** Support sentence-, paragraph-, page-, or fixed-length chunking for vectorization.
* **Retrieval QA:** RAG-powered question-answer interface with citation support.
* **Flashcard Generation:** Automatic creation of Q\&A and cloze Anki cards with detailed notes.
* **Dashboard:** Interactive UI showing project stats, recent activities, and learning metrics.
* **Customization:** User-defined prompts, templates, and chunking strategies.

---

## Project Structure

```
rag-anki-kit/  # renamed to match repository

├── app.py               # Streamlit application entry point
├── retrieve/           
│   ├── __init__.py      # Retriever module
│   ├── initialize_chroma.py
│   └── search.py        # QA search logic
├── loaders/            
│   ├── __init__.py      # Document loaders package
│   ├── pymupdf_loader.py
│   └── pdfplumber_loader.py
├── anki/               
│   ├── __init__.py      # Flashcard generation package
│   └── exporter.py      # Anki export utilities
├── dashboard/          
│   ├── __init__.py      # Dashboard UI components
│   └── metrics.py       # Learning metrics calculations
├── data/               
│   ├── raw/             # Raw document storage
│   └── processed/       # Chunked and vectorized data
├── requirements.txt     # Python dependencies
├── README.md            # Project overview and instructions
└── LICENSE              # License information
```

---

## Project Progress

| Milestone                   | Status         | Notes                            |
| --------------------------- | -------------- | -------------------------------- |
| Initial Project Setup       | ✅ Completed    | Streamlit skeleton created       |
| PDF Ingestion & Chunking    | ✅ Completed    | Supports multiple chunk methods  |
| Vector Database Integration | ✅ Completed    | Chroma DB integration            |
| Retrieval QA Module         | 🔄 In Progress | Streaming Chat UX refinement     |
| Anki Card Export            | 🔄 In Progress | Q\&A and cloze formats supported |
| Dashboard & Metrics         | 🔲 Pending     | Design visualization components  |
| Wish List Integration       | 🔲 Pending     | Add wishlist management UI       |

---

## Wish List

* **Mobile App Frontend:** Flutter or React Native integration for iOS/Android.
* **Advanced Analytics:** Learning curve visualization and spaced repetition tracking.
* **Multilingual Support:** Interface and flashcards in English, Chinese, and Japanese.
* **Citation Management:** Export bibliographies in common formats (BibTeX, RIS).
* **Cloud Sync:** Sync knowledge base and cards across devices via cloud storage.
* **Plugin System:** Allow third-party extensions for new document types and workflows.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mag233/rag-anki-kit.git
   cd knowledge-assistant
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:

   ```bash
   export OPENAI_API_KEY="your_api_key"
   ```

---

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

* Navigate to the *Ingestion* tab to load documents.
* Use the *QA* tab for interactive queries.
* Export flashcards from the *Anki* tab.
* Check *Dashboard* for progress overview.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/xyz`).
3. Commit your changes (`git commit -m "Add feature xyz"`).
4. Push to the branch (`git push origin feature/xyz`).
5. Open a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE).
