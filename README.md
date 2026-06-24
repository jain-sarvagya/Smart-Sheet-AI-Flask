# 📘 Smart-Sheet AI (Flask + React Edition)

Smart-Sheet AI is a production-grade, AI-powered learning assistant that converts uploaded PDF documents into structured learning assets: narrative summaries, 3D flip flashcards, customizable quizzes, concept definitions, and context-grounded AI chat. 

The application utilizes a **Retrieval-Augmented Generation (RAG)** pipeline powered by Google Gemini to ensure all generated answers are strictly grounded within the text context of the uploaded documents.

---

## 🏗️ System Architecture & Workflow

### 1. High-Level Architecture Diagram
```mermaid
graph TD
    %% Clients
    React[React Web Client] <-->|REST APIs / JWT| Flask[Flask API Server]

    %% Main Backend Core
    subgraph Flask Server [Flask Application Container]
        Flask
        PDF[PDF Processor Thread]
        RAG[RAG Retrieval Engine]
    end

    %% Storage & DB
    Flask -->|SQLAlchemy| DB[(PostgreSQL / SQLite fallback)]
    Flask -->|Upload File| Cloud[ImageKit.io / Local Disk fallback]
    PDF -->|Extract Text| Chunk[Chunker Service]

    %% AI Integrations
    Chunk -->|Save Text & Vectors| DB
    RAG -->|Similarity Search| DB
    RAG -->|Generate Text & MCQ| Gemini[Google Gemini API]
```

### 2. Authentication Flow
```
[User Signup/Login] ──► [Flask API validation] ──► [Generates JWT Access Token]
         ▲                                                   │
         │                                                   ▼
[Protected Request] ◄── [Attaches token in Bearer header] ◄── [Stored in localStorage]
```

### 3. Document Processing Pipeline
```
[Upload PDF] ──► [ImageKit Cloud / Local Storage] ──► [Initiate BG Thread]
                                                             │
                                                             ▼
[Update DB ready] ◄── [Vector Embeddings & Save] ◄── [Text Chunking]
```

### 4. Grounded RAG Chatbot Workflow
```
[User Query] ──► [Compute Query Vector] ──► [Cosine Similarity Search] ──► [Fetch Top-K Chunks]
                                                                                  │
                                                                                  ▼
[User Response] ◄── [Run grounded query] ◄── [System instructions & constraints] ◄──┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Key Libraries / Frameworks |
| :--- | :--- | :--- |
| **Frontend** | React (Vite) | Redux Toolkit, React Router, Axios, Lucide Icons, PostCSS |
| **Styling** | Vanilla CSS + Tailwind | Tailwind CSS v4, Glassmorphism, 3D CSS Perspectives |
| **Backend** | Python Flask | Flask-JWT-Extended, Flask-SQLAlchemy, Flask-CORS, Marshmallow |
| **Database** | PostgreSQL / SQLite | pg8000 (Pure Python Driver), SQLAlchemy ORM, Flask-Migrate |
| **AI Layer** | Google Gemini API | `google-generativeai` (embeddings-004, gemini-2.5-flash) |
| **PDF Parser** | PyPDF2 & pdfplumber | Pure-Python PDF text extraction |
| **Containers**| Docker | Docker Compose, Multi-stage Nginx serving |

---

## 📂 Project Folder Structure

```text
smart_sheet_flask/
├── backend/
│   ├── app/
│   │   ├── controllers/      # Route request/response handlers (Auth, Docs, Quizzes...)
│   │   ├── models/           # SQLAlchemy Database Entities (User, Document, Chunk...)
│   │   ├── routes/           # Flask Blueprint route maps
│   │   ├── schemas/          # Marshmallow data serializer definitions
│   │   ├── services/         # Core logic layer (Gemini, PDF Chunker, RAG Engine, Storage)
│   │   ├── __init__.py       # Flask App Factory and startup connection checks
│   │   ├── config.py         # Configuration settings & fallback declarations
│   │   └── extensions.py     # Base extensions initializations (SQLAlchemy, JWT, Migrate)
│   ├── tests/                # Pytest integration and unit testing suite
│   ├── run.py                # Backend entrypoint (db.create_all() execution)
│   ├── Dockerfile            # Container config for Flask API
│   ├── requirements.txt      # Backend Python dependencies list
│   └── .env                  # Backend credentials configuration file (ignored in git)
│
├── frontend/
│   ├── src/
│   │   ├── pages/            # View Pages (LandingPage, DashboardPage, StudioPage, AuthPage)
│   │   ├── redux/
│   │   │   ├── slices/       # Redux State slices (authSlice, docSlice)
│   │   │   └── store.js      # Central Redux store configuration
│   │   ├── App.jsx           # Main router layout
│   │   ├── main.jsx          # DOM entry node mounting
│   │   └── index.css         # Styling styles & Tailwind v4 directives
│   ├── postcss.config.js     # PostCSS plugins config (Tailwind v4 PostCSS driver)
│   ├── vite.config.js        # Vite compilation configuration
│   ├── package.json          # Node package descriptors
│   └── Dockerfile            # Multi-stage production Nginx static container config
│
├── docker-compose.yml        # Orchestration configuration mapping frontend, backend, & Postgres
└── setup.bat                 # Automation build script for Windows environments
```

---

## ⚙️ Environment Variables

### Backend Environment (`backend/.env`)
Create a `.env` file in the `backend/` directory based on [backend/.env.example](file:///c:/Users/sarva/OneDrive/Desktop/smart_sheet_flask/backend/.env.example):

```env
# Flask
FLASK_APP=run.py
FLASK_DEBUG=True
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_key_here

# Database
# Default PostgreSQL URL (will fallback to SQLite smart_sheet.db if connection fails)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_sheet

# AI Settings
# Get from Google AI Studio: https://aistudio.google.com/
GEMINI_API_KEY=AIzaSy...

# Cloud Storage (Optional - falls back to local uploads/ directory if empty)
IMAGEKIT_PUBLIC_KEY=
IMAGEKIT_PRIVATE_KEY=
IMAGEKIT_URL_ENDPOINT=

# File Limits
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=uploads
```

### Frontend Environment (`frontend/.env`)
By default, the Vite dev server points to `http://localhost:5000/api`. If your backend runs on a custom address, create a `.env` file inside `frontend/`:
```env
VITE_API_URL=http://your-custom-backend-address/api
```

---

## 🚀 Installation & Local Development Setup

### Automated Windows Script (Recommended)
1. Double-click the **`setup.bat`** file in the root directory.
2. Enter your **Google Gemini API Key** when prompted.
3. Choose **Option 2 (Local Development)** to automatically create the virtual environment, install node packages, configure environment files, and launch mock database engines.

---

### Manual Setup Steps

#### 1. Backend Setup
1. Navigate to the backend directory and create a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   ```
2. Activate the virtual environment:
   * **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
   * **Windows (CMD)**: `.venv\Scripts\activate.bat`
   * **Linux/macOS**: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python run.py
   ```
   *Note: If no local PostgreSQL is active on port 5432, the system automatically prints a terminal warning and initializes an SQLite instance (`smart_sheet.db`) so the server boots smoothly.*

#### 2. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Access the web client at the address displayed (usually `http://localhost:5173`).

---

## 🐳 Docker Deployment Setup

You can build and start the entire stack (PostgreSQL database, Flask API, and React client) using Docker Compose:

1. Open your terminal at the root directory of the project.
2. Build and launch all containers:
   ```bash
   docker-compose up --build
   ```
3. Access points:
   * **React Client**: [http://localhost:3000](http://localhost:3000) (Served via Nginx)
   * **Flask Backend API**: [http://localhost:5000](http://localhost:5000)
   * **PostgreSQL Engine**: `localhost:5432`

---

## 📡 API Reference Map

All endpoints expect JSON payloads (unless uploading files) and are prefixed with `/api`. Protected routes require a valid JWT token sent in the headers as: `Authorization: Bearer <TOKEN>`.

### 🔐 Authentication Flow (`/api/auth`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Create a new account & retrieve access token | No |
| `POST` | `/auth/login` | Authenticate existing credentials & retrieve token | No |
| `GET` | `/auth/profile` | Fetch profile details of the logged-in user | Yes |

### 📂 Document Operations (`/api/documents`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/documents/upload` | Upload PDF file (Form-Data) and start chunking | Yes |
| `GET` | `/documents` | List metadata of all user documents | Yes |
| `GET` | `/documents/<id>` | Fetch detailed metadata & processing status of a file | Yes |
| `DELETE` | `/documents/<id>` | Delete document metadata, file, & related DB assets | Yes |

### 🎯 Practice Quiz Arena (`/api/quizzes`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/quizzes/generate/<doc_id>` | Generate custom count MCQ set (JSON payload: `{"count": 5}`) | Yes |
| `GET` | `/quizzes/<doc_id>` | Retrieve existing generated practice quizzes | Yes |

### 🧠 Study Flashcards (`/api/flashcards`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/flashcards/generate/<doc_id>` | Generate active-recall study flashcards | Yes |
| `GET` | `/flashcards/<doc_id>` | Retrieve generated flashcard deck | Yes |

### 📝 Summaries (`/api/summaries`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/summaries/generate/<doc_id>` | Generate narrative summary and core takeaways | Yes |
| `GET` | `/summaries/<doc_id>` | Retrieve the document summaries | Yes |

### 💬 Grounded RAG Chat (`/api/chat`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/chat/<doc_id>` | Send query message (JSON payload: `{"message": "string"}`) | Yes |
| `GET` | `/chat/<doc_id>` | Fetch conversation history for a document | Yes |

### 🔎 Concept Solver (`/api/explanations`)
| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :--- |
| `POST` | `/explanations/explain/<doc_id>`| Explain concept term from document context (`{"concept_name": "str"}`) | Yes |
| `GET` | `/explanations/<doc_id>` | Fetch previously solved concepts list | Yes |

---

## 🛠️ Troubleshooting Guide

### 1. Database UnboundExecutionError / Connection Refused Warnings
* **Symptom**: The terminal outputs `[DATABASE WARNING] Connection to configured database failed` on backend startup.
* **Explanation**: This is a friendly warning indicating that a local PostgreSQL server was not found running on port 5432 using the credentials specified in `.env`.
* **Solution**: You don't need to do anything! The backend automatically falls back to a local SQLite database (`backend/smart_sheet.db`) so you can keep testing in your local environment.

### 2. Invalid API Key / AI Services Fail
* **Symptom**: Summaries or Flashcards show error text containing `400 API key not valid. Please pass a valid API key`.
* **Explanation**: The Gemini API key you provided in `.env` is invalid or contains placeholder values.
* **Solution**:
  1. Generate a key from [Google AI Studio](https://aistudio.google.com/).
  2. Open `backend/.env` and verify the `GEMINI_API_KEY` is pasted correctly.
  3. Close and **restart** your Flask backend server process to load the new key.
  4. The application handles errors gracefully; it won't cache failed generations in the database, allowing you to click generate again to retry.

### 3. Vite PostCSS Warning
* **Symptom**: Vite compiler outputs `It looks like you're trying to use tailwindcss directly as a PostCSS plugin...`
* **Explanation**: The frontend dev environment utilizes Tailwind CSS v4, which uses the `@tailwindcss/postcss` plugin instead of `tailwindcss` inside the PostCSS pipeline.
* **Solution**: The setup script installs `@tailwindcss/postcss` and configures `postcss.config.js` and `index.css` using `@import "tailwindcss"` automatically. Ensure you run standard local dev setups using `npm run dev`.

---

## 🎨 Screenshots & Interface Walkthrough

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ SMART-SHEET AI   [My Documents]    [MySQL_Handbook.pdf]   (● active)        │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │ [Summary] [Flashcards] [Quiz] [Chat] │
│                                      ├──────────────────────────────────────┤
│                                      │                                      │
│                                      │  Practice Quiz                       │
│  [=============================]     │  Answer the questions below.         │
│  [                             ]     │                                      │
│  [                             ]     │  1. What is a primary key?           │
│  [       PDF DOCUMENT          ]     │     (A) A unique identifier          │
│  [          READER             ]     │     (B) A index pointer              │
│  [                             ]     │     (C) A table joining link         │
│  [                             ]     │     (D) A sequence number            │
│  [                             ]     │                                      │
│  [=============================]     │  [Submit Quiz]                       │
│                                      │                                      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 🔮 Future Roadmap

* 📄 **Multi-Document Connections**: Cross-reference facts across multiple uploaded PDFs in the same RAG chat session.
* 📷 **OCR Text Extraction**: Extract texts from scanned documents, diagrams, and image-based PDFs.
* 📊 **Student Performance Logs**: Save quiz grades historically to render student progression charts on the dashboard.
* 🔄 **Alternative Vector DB Integrations**: Add support for vector-database engines like pgvector or Qdrant for managing highly massive document collections.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
