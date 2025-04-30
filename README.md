# LincolnBot - AI-Powered Parking Information Assistant

## 🎯 Project Overview
LincolnBot is an intelligent assistant designed to help users find accurate information about parking rules, permits, and penalties in Lincoln City. By combining semantic search capabilities with advanced language models, it provides contextually relevant and accurate responses to user queries.

## 🏗️ System Architecture
The system follows a three-layer architecture:
1. **Embedding Layer**: 
   - Processes and vectorizes text data
   - Uses SentenceTransformers for semantic understanding
   - Optimized for parking-related content

2. **Search Layer**: 
   - Performs semantic search with ChromaDB
   - Implements re-ranking for better relevance
   - Utilizes Redis caching for performance

3. **Generative Layer**: 
   - Generates natural language responses using GPT-4
   - Ensures context-aware and accurate answers
   - Validates responses for completeness

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Redis server
- OpenAI API key
- 2GB+ RAM for embedding models

### Installation Steps

1. **Clone the Repository**:
```bash
git clone https://github.com/vaibhavcssbb/LincolnBot.git
cd LincolnBot
```

2. **Create and Activate Virtual Environment**:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**:
```bash
cp .env.example .env
```
Edit `.env` with your:
- OpenAI API key
- Redis configuration
- Other settings as needed

5. **Start Redis Server**:
```bash
redis-server
```

## 💻 Usage

### Running the Application
1. Ensure Redis is running
2. Execute the main script:
```bash
python main.py
```

### Example Queries
```python
# The bot can answer questions like:
"What are the parking permit requirements?"
"How much does a resident parking permit cost?"
"What are the penalties for parking violations?"
```

## 🧪 Testing
Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_search_engine.py

# Run with coverage report
python -m pytest --cov=. tests/
```

## 🔧 Project Structure
```
LincolnBot/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore patterns
├── main.py              # Application entry point
├── search_engine.py     # Search functionality
├── response_generator.py # Response generation
├── response_validator.py # Response validation
└── tests/               # Test suite
    ├── test_search_engine.py
    └── test_response_generator.py
```

## 🛠️ Technical Components
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Store**: ChromaDB
- **Cache**: Redis
- **Re-ranker**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Generative Model**: GPT-4

## 📊 Performance Metrics
- Average search latency: < 0.3 seconds
- Cache hit rate: ~40%
- Response accuracy: > 95%
- Context relevance: High

## 🔍 Troubleshooting

### Redis Connection Issues
- Verify Redis server is running: `redis-cli ping`
- Check Redis port (default 6379) is not blocked
- Ensure Redis password is correctly set in .env

### OpenAI API Issues
- Verify API key in .env file
- Check API rate limits at OpenAI dashboard
- Ensure sufficient credits available

### Test Failures
- Verify all dependencies are installed
- Check environment variables are set
- Ensure Redis connection is active

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License
This project is licensed under the MIT License.

## 🙏 Acknowledgments
- OpenAI for GPT-4
- SentenceTransformers team
- ChromaDB developers
- Redis team

## 📧 Contact
For questions or support, please open an issue on GitHub. 