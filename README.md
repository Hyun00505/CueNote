<p align="center">
  <img src="local_data/logo.svg" alt="CueNote Logo" width="300" />
</p>
<p align="center">
  <strong>AI-Powered Local-First Markdown Note-Taking App</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/electron-28.x-47848F.svg" alt="Electron" />
  <img src="https://img.shields.io/badge/vue-3.x-4FC08D.svg" alt="Vue" />
  <img src="https://img.shields.io/badge/fastapi-0.100+-009688.svg" alt="FastAPI" />
</p>

---

## 🌟 What is CueNote?

**CueNote** is an open-source, privacy-first desktop application for markdown note-taking with powerful AI assistance. Built with Electron and Vue 3 on the frontend and FastAPI on the backend, CueNote keeps all your data local while providing intelligent features powered by both local LLMs (via Ollama) and cloud APIs (Google Gemini).

Unlike cloud-based note apps, CueNote ensures your notes never leave your device unless you explicitly choose to use cloud AI services. Your data stays in a simple SQLite database and markdown files on your local filesystem.

---

## ✨ Features

### 📝 Rich Markdown Editor
- **WYSIWYG editing** with Tiptap-based rich text editor
- Full markdown support including tables, task lists, code blocks, and more
- Real-time preview and editing
- File-based vault system for organizing notes

### 🤖 AI-Powered Writing Assistance
- **Summarize** - Get concise summaries of long notes with key points
- **Translate** - Translate text to 7+ languages while preserving markdown formatting
- **Improve** - Enhance your writing with different styles (professional, casual, academic, etc.)
- **Expand** - Add more detail and explanation to your content
- **Shorten** - Condense text while keeping essential meaning
- **Proofread** - Fix spelling, grammar, and punctuation errors (supports Korean & English)
- **Real-time streaming** - Watch AI responses appear in real-time

### 📅 Smart Schedule Extraction
- **AI-powered schedule detection** - Automatically extract dates, times, and events from your notes
- **Calendar integration** - View and manage extracted schedules in a built-in calendar
- **Relative date parsing** - Understands "tomorrow", "next Monday", "this Friday", etc.

### 📄 Document & Image Processing
- **PDF text extraction** - Extract and convert PDF content to markdown
- **OCR support** - Extract text from images using EasyOCR
- **Handwriting recognition** - Recognize handwritten text using TrOCR
- **Auto-formatting** - AI converts extracted text into clean, structured markdown

### 🔒 Privacy-First Design
- **100% local storage** - All notes stored in local SQLite database
- **Local LLM support** - Use Ollama for completely offline AI features
- **Optional cloud AI** - Connect to Gemini API only when you choose to
- **No telemetry** - We don't collect any usage data

### 🛠️ Developer-Friendly
- **Monorepo architecture** - Clean separation of concerns
- **Type-safe** - Full TypeScript support in frontend
- **RESTful API** - Well-documented FastAPI backend
- **Hot reload** - Fast development with Vite and uvicorn

---

## 🚀 Installation

### Prerequisites

- **Node.js** 18+ and [pnpm](https://pnpm.io/)
- **Python** 3.11+
- **Ollama** (optional, for local LLM support)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/cuenote.git
   cd cuenote
   ```

2. **Install JavaScript dependencies**
   ```bash
   pnpm install
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r apps/core/requirements.txt
   ```

4. **Run the application**
   ```bash
   # Start everything together
   pnpm dev:all
   
   # Or run separately:
   pnpm dev:core     # Start FastAPI backend
   pnpm dev:desktop  # Start Electron app
   ```

5. **Access the app**
   - Desktop app launches automatically
   - API available at `http://127.0.0.1:8787`

### Optional: Setup Ollama for Local AI

1. Install [Ollama](https://ollama.ai/)
2. Pull a model (recommended: `llama3.2` or `qwen2.5`)
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama server
   ```bash
   ollama serve
   ```

### Optional: Setup Gemini API

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Configure the key in CueNote settings

---

## 📖 Usage

### Creating Notes
- Click the **+** button in the sidebar to create a new note
- Notes are stored as `.md` files in your vault folder
- Use markdown syntax or the rich text toolbar

### AI Features
- **Select text** and right-click to access AI context menu
- Choose from: Summarize, Translate, Improve, Expand, Shorten, or Proofread
- Results appear in real-time with streaming support

### Schedule Extraction
- Write your plans naturally in notes (e.g., "Meeting with team on Friday at 3pm")
- Click **Extract Schedules** to let AI find all events
- Review and add extracted schedules to your calendar

### Document Import
- Drag & drop PDF files or images into the editor
- CueNote extracts text and converts it to markdown
- Enable **Handwriting Mode** for handwritten content

---

## 🏗️ Architecture

```
cuenote/
├── apps/
│   ├── core/                 # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/      # API endpoints
│   │   │   │   ├── ai.py     # AI features (summarize, translate, etc.)
│   │   │   │   ├── schedules.py
│   │   │   │   ├── todos.py
│   │   │   │   └── vault.py
│   │   │   ├── ollama_client.py
│   │   │   ├── gemini_client.py
│   │   │   ├── ocr_client.py
│   │   │   └── db.py
│   │   └── data/             # SQLite database
│   │
│   └── desktop/              # Electron + Vue frontend
│       ├── main.js           # Electron main process
│       └── renderer/
│           └── src/
│               ├── components/
│               └── composables/
│
├── packages/
│   ├── contracts/            # Shared TypeScript types & schemas
│   └── shared/               # Shared utilities
│
└── data/                     # Default vault location
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Desktop Shell | Electron 28 |
| Frontend | Vue 3, Vite, Tiptap |
| Backend | FastAPI, SQLite |
| AI/LLM | Ollama, Google Gemini |
| OCR | EasyOCR, TrOCR (Transformers) |

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
- 🐛 **Report bugs** - Open an issue with detailed reproduction steps
- 💡 **Suggest features** - Share your ideas in discussions
- 📝 **Improve docs** - Help us make documentation clearer
- 🔧 **Submit PRs** - Fix bugs or implement new features

### Development Setup

1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests and linting
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push and open a Pull Request

### Code Style
- Frontend: ESLint + Prettier
- Backend: Black + isort
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📋 Roadmap

- [ ] Multi-vault support
- [ ] Note linking and backlinks
- [ ] Full-text search
- [ ] Plugin system
- [ ] Mobile companion app
- [ ] Real-time collaboration
- [ ] More LLM providers (OpenAI, Claude, etc.)
- [ ] Export to various formats

---

## 📄 License

CueNote is open-source software licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [Tiptap](https://tiptap.dev/) - Headless rich text editor
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Ready-to-use OCR
- [Electron](https://www.electronjs.org/) - Cross-platform desktop apps

---

<p align="center">
  Made with my very heart
</p>

<p align="center">
  <a href="https://github.com/your-username/cuenote/stargazers">⭐ Star us on GitHub</a>
</p>
