# Gia (General Intelligence Assistant)

Gia is a highly autonomous AI assistant capable of comprehending, planning, and executing complex tasks across various domains with minimal human intervention. It leverages local AI models, dynamic tool creation, and various data-gathering capabilities.

## Features

- 🧠 **Task Decomposition & Problem-Solving**

  - Automatic task breakdown into manageable steps
  - Dynamic workflow node generation and orchestration
  - Real-time task flow adaptation

- 🔍 **Information Gathering**

  - Web scraping capabilities
  - GitHub repository exploration
  - Real-time API integration

- 💻 **Code Generation & Execution**

  - Multi-language code generation
  - Secure sandboxed execution
  - GitHub integration

- 🤖 **Adaptive Intelligence**
  - Self-correcting workflows
  - Dynamic context adaptation
  - Continuous performance optimization

## Architecture

Gia consists of two main components:

1. **Backend (Python/FastAPI)**

   - Task processing and workflow management
   - Agent-based architecture
   - Local AI model integration (Mistral-7B)
   - Secure code execution

2. **Frontend (React/TypeScript)**
   - Real-time task visualization
   - Workflow monitoring
   - Interactive task submission

## Prerequisites

- Python 3.9+
- Node.js 18+
- Docker
- 16GB+ RAM (for AI model)
- NVIDIA GPU (optional, for faster processing)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/beyond-repair/gia.git
   cd gia
   ```

2. Set up the backend:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

## Configuration

1. Create a `.env` file in the backend directory:

   ```env
   GITHUB_TOKEN=your_github_token  # Optional, for higher API limits
   MODEL_PATH=./models  # Local path to store AI models
   ```

2. Configure Docker for code execution (optional):
   ```bash
   docker pull python:3.9-slim
   ```

## Usage

1. Start the backend server:

   ```bash
   cd backend
   python run.py
   ```

2. Start the frontend development server:

   ```bash
   cd frontend
   npm run dev
   ```

3. Access the web interface at `http://localhost:5173`

## Development

### Project Structure

```
gia/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       └── agents/
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── src/
    │   ├── components/
    │   └── types/
    ├── package.json
    └── vite.config.ts
```

### Adding New Agents

1. Create a new agent class in `backend/app/services/agents/`
2. Inherit from `BaseAgent`
3. Implement the `execute` method
4. Register the agent in `WorkflowEngine`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Mistral AI](https://mistral.ai/) for the language model
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
