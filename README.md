# Content Planner AI Agent

## Overview
An advanced AI-powered content planning and strategy tool built with Streamlit and Google's Generative AI. This application helps content creators, marketers, and businesses develop comprehensive content strategies, generate ideas, and plan content calendars.

## Features
- **AI-Powered Content Generation**: Uses Google's Gemini AI for intelligent content suggestions
- **Interactive Dashboard**: Streamlit-based web interface for easy interaction
- **Content Strategy Planning**: Comprehensive planning tools for content marketing
- **Multi-format Support**: Support for various content types and formats
- **Real-time Processing**: Instant content generation and analysis

## Technology Stack
- **Frontend**: Streamlit
- **AI Model**: Google Generative AI (Gemini)
- **Data Processing**: Pandas
- **Configuration**: Environment variables and JSON
- **Logging**: Python logging framework

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install streamlit google-generativeai pandas python-dotenv
   ```
3. Set up Google AI API key:
   - Create a `.env` file
   - Add your Google AI API key: `GOOGLE_API_KEY=your_api_key_here`

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run main.py
   ```
2. Open your browser to `http://localhost:8501`
3. Configure your content planning parameters
4. Generate content ideas and strategies
5. Export or save your content plans

## Features in Detail
- **Content Ideation**: AI-generated content ideas based on your niche
- **Content Calendar**: Plan and schedule content across time periods
- **Audience Analysis**: Understand your target audience better
- **Trend Integration**: Incorporate current trends into content strategy
- **Performance Optimization**: Suggestions for content optimization

## Configuration
The application supports various configuration options:
- API key management
- Content preferences
- Output formats
- Planning timeframes

## File Structure
- `main.py` - Main Streamlit application (352 lines)
- `test_main.py` - Test suite for the application
- `.env` - Environment variables (API keys)
- `__pycache__/` - Python cache files

## Environment Setup
Create a `.env` file with:
```
GOOGLE_API_KEY=your_google_ai_api_key
```

## Testing
Run tests using:
```bash
python test_main.py
```

## Logging
The application includes comprehensive logging for:
- API interactions
- User actions
- Error tracking
- Performance monitoring

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## API Requirements
- Google AI API key
- Internet connection for AI model access

## Security
- Keep API keys secure
- Use environment variables
- Don't commit sensitive data

## License
MIT License
