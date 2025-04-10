# Jarvis Voice Assistant

A voice-controlled personal assistant that can perform various tasks including:
- Playing music on YouTube
- Providing time information
- Searching Wikipedia
- Telling jokes
- Checking weather
- Reading news headlines
- Controlling system volume
- Opening websites
- Answering questions using Ollama LLM
- Displaying text responses in a GUI window alongside voice output

## Project Structure

```
jarvis/
├── config/
│   ├── __init__.py
│   └── settings.py       # Configuration settings
├── core/
│   ├── __init__.py
│   ├── assistant.py      # Main assistant class
│   ├── speech.py         # Speech recognition and synthesis
│   └── command_handler.py # Command processing logic
├── services/
│   ├── __init__.py
│   ├── weather.py        # Weather API integration
│   ├── news.py           # News API integration
│   ├── media.py          # Media playback functions
│   ├── browser.py        # Web browser functions
│   ├── system.py         # System control functions
│   └── llm.py            # Ollama LLM integration
├── utils/
│   ├── __init__.py
│   └── helpers.py        # Utility functions
├── .env                  # Environment variables (API keys)
├── requirements.txt      # Project dependencies
└── main.py              # Entry point
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file:
   ```
   WEATHER_API_KEY=your_api_key
   NEWS_API_KEY=your_api_key
   ```

3. Make sure Ollama is installed and the required model is available:
   ```
   ollama pull gemma:2b
   ```

4. Run the assistant:
   ```
   python main.py
   ```

## Requirements

- Python 3.12+
- Ollama with gemma:2b model
- For volume control on Windows: NirCmd utility#   J a r v i s - 2 . 0 
 
 