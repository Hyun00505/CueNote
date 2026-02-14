<p align="center">
  <img src="assets/logo.png" alt="CueNote Logo" width="300" />
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

<p align="center">
  <a href="README_ko.md">🇰🇷 한국어</a> | <strong>🇺🇸 English</strong>
</p>

---

## 🌟 What is CueNote?

**CueNote** is an open-source, privacy-first desktop Markdown note-taking app with built-in AI capabilities. Built with Electron + Vue 3 frontend and a FastAPI backend, it supports a wide range of AI providers — from local LLMs (Ollama) to cloud AI (Gemini, OpenAI, Anthropic Claude).

Unlike cloud-based note apps, CueNote stores all your data in local SQLite databases and Markdown files. You can optionally sync to the cloud via GitHub integration.

<p align="center">
  <img src="docs/assets/images/README_img/AIEdit.gif" alt="CueNote Demo" width="800" />
  <br />
  <em>AI-powered note editing in CueNote</em>
</p>

---

## ✨ Features

### 📝 Rich Markdown Editor
- **WYSIWYG editing** — Tiptap-based rich text editor
- Full Markdown support: tables, checklists, code blocks, image resizing, and more
- File-based Vault system for organizing notes
- Real-time preview and editing

### 🤖 AI Writing Assistant
Select text and right-click or press shortcuts (`Alt+A`, `/`) to open the AI context menu:

| Feature | Description |
|---------|-------------|
| **Summarize** | Condense long notes into key points |
| **Translate** | Translate to 7+ languages (preserving Markdown formatting) |
| **Polish** | Improve sentences in professional, casual, or academic tones |
| **Expand** | Elaborate content with more detail |
| **Condense** | Shorten while preserving core meaning |
| **Proofread** | Fix spelling, grammar, and punctuation (Korean & English) |
| **Custom Prompt** | Freely request any AI editing or writing task |

- **Real-time Streaming** — AI responses appear as they are generated
- **Inline Diff** — Compare AI edits in diff format, accept or reject changes
- **Proofread Panel** — Review errors one by one with individual apply/skip

<p align="center">
  <img src="docs/assets/images/README_img/Autofix.gif" alt="AI Writing Assistance Demo" width="700" />
  <br />
  <em>Real-time AI text analysis and proofreading</em>
</p>

### 💬 AI Chatbot (Tool Calling)
A conversational AI assistant that automatically executes app functions:

- **17+ built-in tools** — Create/read/save/delete notes, search, manage schedules, query TODOs, and more
- **Smart Search** — AI understands meaning to find relevant notes
- **Auto-organize Notes** — AI analyzes content and suggests folder structure
- **Web Search** — Real-time web search via DuckDuckGo
- **Current Note Awareness** — Understands the currently open note and performs related tasks
- **Multi-step Execution** — Handles complex requests through multiple tool calls automatically

<p align="center">
  <img src="docs/assets/images/README_img/chatbot_screenshot.png" alt="AI Chatbot Demo" width="700" />
  <br />
  <em>AI Chatbot with tool calling — listing all notes</em>
</p>

### 🔗 GitHub Integration
Sync your notes directly with GitHub repositories:

- **Clone & Pull** — Fetch GitHub repositories locally
- **Git Status** — View changed files, stage and unstage
- **Commit & Push** — Commit selected files and push
- **AI Commit Messages** — AI analyzes changes and auto-generates commit messages
- **Create Repositories** — Create new GitHub repos from within the app
- **Trash Management** — Restore or permanently delete files

### 🌐 Multi-Environment
Easily switch between multiple workspaces:

- **Local Environment** — Use local folders as vaults
- **GitHub Environment** — Use GitHub repositories as vaults
- **One-click Switching** — Instantly switch between environments
- Independent file management per environment

### 🕸️ Knowledge Graph
AI analyzes relationships between notes and visualizes them:

- **AI Clustering** — Automatically group notes by content
- **Related Note Discovery** — Find notes related to the current one
- **Graph Explorer** — Interactive D3.js-based graph visualization
- **Graph Search** — Search for notes within the graph
- **Cluster Filtering** — View specific clusters only
- **Similarity Control** — Adjust connection sensitivity via slider

<p align="center">
  <img src="docs/assets/images/README_img/graph_screenshot.png" alt="Knowledge Graph Demo" width="700" />
  <br />
  <em>AI-powered knowledge graph with automatic clustering</em>
</p>

### 📅 Smart Calendar
Automatically extract schedules from notes and manage them:

- **AI Schedule Extraction** — Auto-detect dates, times, and events from notes
- **Relative Date Parsing** — Understand expressions like "tomorrow", "next Monday"
- **Calendar Views** — Day / Week / Month / Year views
- **Today Focus Card** — See today's schedule at a glance
- **Quick Add** — Add schedules inline
- **Popover Details** — Click schedules for quick detail view

<p align="center">
  <img src="docs/assets/images/README_img/calendar_screenshot.png" alt="Smart Calendar Demo" width="700" />
  <br />
  <em>Calendar dashboard with today focus and schedule overview</em>
</p>

### 📄 Document & Image Processing
- **PDF Text Extraction** — Convert PDF content to Markdown
- **OCR** — Extract text from images using EasyOCR or Gemini Vision
- **Handwriting Recognition** — Recognize handwriting with TrOCR
- **URL Scraping** — Automatically convert web pages to Markdown notes
- **AI Auto-formatting** — Clean up extracted text into well-structured Markdown

<p align="center">
  <img src="docs/assets/images/README_img/GetWord.gif" alt="Document Processing Demo" width="700" />
  <br />
  <em>Extracting text from images and converting to Markdown</em>
</p>

### 🔌 MCP (Model Context Protocol) Support
Connect external tools to extend AI capabilities:

- **MCP Server Management** — Register, start, and stop external MCP servers
- **Auto-discovery** — Automatically detect tools from connected servers
- **Tool Calling** — Execute MCP tools via natural language in the AI chatbot
- **Built-in Filesystem Server** — Filesystem access MCP server included

### 🎨 Customization

#### AI Model Settings
Freely switch between 4 AI providers:

| Provider | Example Models | Features |
|----------|---------------|----------|
| **Ollama** | Llama 3, Qwen 2.5, etc. | Fully offline, free |
| **Google Gemini** | Gemini 2.0 Flash, Gemini 3 Flash, etc. | Fast and powerful, free tier |
| **OpenAI** | GPT-4o, GPT-4.1, o3, etc. | Best general-purpose |
| **Anthropic** | Claude Sonnet 4.5, Claude Haiku, etc. | Strong at long context |

#### Appearance & Fonts
- **Dark / Light theme** toggle
- **Custom fonts** — 30+ built-in fonts + add your own font files
- **Category fonts** — Set Sans, Serif, and Mono fonts separately
- **UI Scale** — Adjust from 50% to 200%

#### Shortcuts
- **Custom shortcuts** — Freely assign shortcuts for key features like AI menu
- **Multiple shortcuts** — Register multiple shortcuts per function

#### Internationalization
- 🇰🇷 Korean / 🇺🇸 English fully supported

### 🔒 Privacy-First Design
- **100% Local Storage** — All notes stored in local SQLite database
- **Local LLM Support** — Use Ollama for completely offline AI
- **Optional Cloud AI** — Cloud AI only connects when you choose
- **No Telemetry** — Zero usage data collected

---

## 🚀 Installation

### Prerequisites

- **Node.js** 18+ and [pnpm](https://pnpm.io/)
- **Python** 3.11+
- **Ollama** (optional, for local LLM)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hyun00505/CueNote.git
   cd CueNote
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

### Optional: Setup Cloud AI

| Provider | Get API Key |
|----------|-------------|
| **Google Gemini** | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **OpenAI** | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **Anthropic** | [Anthropic Console](https://console.anthropic.com/) |

Enter your API key in CueNote Settings.

---

## 📖 Usage

### Writing Notes
- Create a new note with the **+** button in the sidebar
- Notes are saved as `.md` files in your vault folder
- Use Markdown syntax or the rich text toolbar

### AI Writing Tools
- **Select text** → right-click or press `Alt+A` / `/` to open AI context menu
- Choose from summarize, translate, polish, expand, condense, or proofread
- Results appear as inline diffs — accept or reject

### AI Chatbot
- Click the chatbot icon at the bottom of the sidebar
- Use natural language: "Create a new note", "Add a meeting tomorrow at 3pm", "Find project-related notes"
- AI automatically picks the right tools and shows results

### GitHub Sync
- Connect your GitHub token in Settings
- Select or create a repository
- Use the Git panel to view changes, stage, commit, and push

### Schedule Management
- Write schedules naturally in notes (e.g. "Team meeting on Friday at 3pm")
- Click **AI Schedule Extract** to auto-detect
- View and manage in the calendar

### Importing Documents
- Drag & drop PDF files or images into the editor
- Enter a URL to import web page content
- Enable handwriting mode for handwriting recognition

---

## 🏗️ Architecture

```
CueNote/
├── apps/
│   ├── core/                    # FastAPI Backend
│   │   ├── app/
│   │   │   ├── routers/         # API Endpoints
│   │   │   │   ├── ai.py        # AI features (summarize, translate, polish, etc.)
│   │   │   │   ├── chatbot.py   # AI Chatbot (17+ tool calls)
│   │   │   │   ├── github.py    # GitHub integration
│   │   │   │   ├── graph.py     # Knowledge Graph
│   │   │   │   ├── mcp.py       # MCP server management
│   │   │   │   ├── schedules.py # Schedule management
│   │   │   │   ├── environment.py # Multi-environment
│   │   │   │   ├── vault.py     # File/Note management
│   │   │   │   ├── llm.py       # LLM provider management
│   │   │   │   └── todos.py     # TODO management
│   │   │   ├── ollama_client.py   # Ollama API client
│   │   │   ├── gemini_client.py   # Gemini API client
│   │   │   ├── openai_client.py   # OpenAI API client
│   │   │   ├── anthropic_client.py # Anthropic API client
│   │   │   ├── mcp_client.py      # MCP client manager
│   │   │   ├── web_extractor.py   # Web content extractor
│   │   │   ├── ocr_client.py      # OCR engine (EasyOCR/TrOCR/Gemini Vision)
│   │   │   └── db.py              # SQLite database
│   │   └── data/                  # SQLite database files
│   │
│   └── desktop/                   # Electron + Vue Frontend
│       ├── main.js                # Electron main process
│       └── renderer/
│           └── src/
│               ├── components/
│               │   ├── AIChatbot.vue        # AI Chatbot UI
│               │   ├── AIContextMenu.vue    # AI Context Menu
│               │   ├── AIInlineDiff.vue     # AI Inline Diff
│               │   ├── AIProofreadPanel.vue # Proofreading Panel
│               │   ├── EditorView.vue       # Main Editor
│               │   ├── GraphView.vue        # Graph View
│               │   ├── DashboardView.vue    # Dashboard (Calendar)
│               │   ├── SettingsView.vue     # Settings
│               │   ├── sidebar/             # Sidebar (Files, Git, Environment)
│               │   ├── graph/               # Graph components
│               │   ├── dashboard/           # Calendar components
│               │   ├── toolbar/             # Editor toolbar
│               │   ├── settings/            # Settings tabs (AI, Appearance, OCR, MCP, Fonts, Shortcuts)
│               │   └── editor/              # Editor helper components
│               └── composables/             # Vue Composables
│                   ├── useGitHub.ts          # GitHub integration
│                   ├── useGraph.ts           # Graph management
│                   ├── useChatbot.ts         # Chatbot management
│                   ├── useEnvironment.ts     # Environment management
│                   ├── useSchedule.ts        # Schedule management
│                   ├── useSettings.ts        # Settings management
│                   ├── useFonts.ts           # Font management
│                   ├── useShortcuts.ts       # Shortcut management
│                   ├── useI18n.ts            # Internationalization (KO/EN)
│                   └── useTiptapEditor.ts    # Tiptap editor
│
├── packages/
│   ├── contracts/               # Shared TypeScript types & schemas
│   └── shared/                  # Shared utilities
│
└── data/                        # Default vault location
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Desktop Shell | Electron 28 |
| Frontend | Vue 3, Vite, Tiptap, D3.js |
| Backend | FastAPI, SQLite |
| AI/LLM | Ollama, Google Gemini, OpenAI, Anthropic Claude |
| OCR | EasyOCR, TrOCR (Transformers), Gemini Vision |
| Tool Protocol | MCP (Model Context Protocol) |
| Version Control | GitHub API, Git CLI |

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
- 🐛 **Report bugs** — Open an issue with detailed reproduction steps
- 💡 **Suggest features** — Share your ideas in discussions  
- 📝 **Improve docs** — Help us make documentation clearer
- 🔧 **Submit PRs** — Fix bugs or implement new features

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

- [x] Multi AI provider support (Ollama, Gemini, OpenAI, Anthropic)
- [x] AI Chatbot (Tool Calling)
- [x] GitHub integration & Git sync
- [x] Knowledge Graph & AI Clustering
- [x] MCP (Model Context Protocol) support
- [x] Multi-environment system
- [x] Custom fonts & UI scale
- [x] Internationalization (KO/EN)
- [x] Custom shortcuts
- [ ] Plugin system
- [ ] Mobile companion app
- [ ] Real-time collaboration
- [ ] Export to various formats

---

## 📄 License

CueNote is open-source software licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [Tiptap](https://tiptap.dev/) — Headless rich text editor
- [Ollama](https://ollama.ai/) — Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — Ready-to-use OCR
- [Electron](https://www.electronjs.org/) — Cross-platform desktop apps
- [D3.js](https://d3js.org/) — Data-driven visualizations

---

<p align="center">
  Made with ❤️
</p>

<p align="center">
  <a href="https://github.com/Hyun00505/CueNote/stargazers">⭐ Star us on GitHub</a>
</p>
