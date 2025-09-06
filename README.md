# AI System for ATE Equipment

A comprehensive Python application that provides intelligent analysis of Automatic Test Equipment (ATE) through AI-powered text parsing, equipment option explanation, and market research capabilities.

## 🚀 Features

### 🤖 AI-Powered Equipment Analysis
- **Intelligent Text Parsing**: Extract brand, model, and options from free-form text using OpenAI GPT-4
- **Option Explanation**: AI-generated detailed explanations for each equipment option
- **Smart Categorization**: Automatic categorization of options (Connectivity, Software, Calibration, etc.)
- **Natural Language Processing**: Handle complex equipment descriptions and specifications

### 🔍 Market Research & Web Scraping
- **Multi-Source Scraping**: DuckDuckGo search, eBay mobile, specialized equipment vendors
- **Price Analysis**: Extract and validate pricing information (>$1000 filter)
- **Vendor Identification**: Automatic vendor categorization and source tracking
- **Real-time Market Data**: Live scraping with fallback data generation

### 📊 Interactive Web Interface
- **Streamlit Dashboard**: Modern, responsive web interface
- **Equipment Database**: Pre-loaded sample equipment with detailed specifications
- **Real-time Analysis**: Live progress tracking with animated indicators
- **Results Visualization**: Formatted tables and structured data display

### 🎯 Equipment Database
The system includes a comprehensive database of test equipment including:
- **Agilent/Keysight**: N8976B, N5172B, E4980A, 16555D, 8596E, 33120A
- **Rohde & Schwarz**: SMA100B, CMU300
- **Tektronix**: TDS744A
- **Anritsu**: MS2090A
- **BOONTON**: 4500C

## 🛠️ Installation

1. **Clone/Download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API** (optional but recommended):
   - Get an API key from [OpenAI](https://platform.openai.com/)
   - Update the `API_KEY` variable in `app.py`

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

### Basic Equipment Analysis
1. **Select Equipment**: Choose from the pre-loaded equipment database
2. **Click Analyze**: Start the AI-powered analysis process
3. **View Results**: See parsed equipment data, option explanations, and market information

### Analysis Workflow
The system performs three main analysis steps:
1. **Equipment Parsing**: Extract brand, model, and options using AI
2. **Option Explanation**: Generate detailed explanations for each option
3. **Market Research**: Search for pricing and availability information

### Equipment Selection
- Browse the equipment database with radio button selection
- Each entry shows Quote ID, Contact, Brand, Model, and Options
- Real-time analysis with progress indicators

## 📁 Project Structure

```
├── app.py                    # Main Streamlit application
├── effective_scraper.py      # Web scraping functionality
├── parsing.py               # Text parsing and option extraction
├── prompting.py             # AI/LLM integration and prompts
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
└── render.yaml             # Deployment configuration
```

## 🔧 Core Components

### `app.py` - Main Application
- **Streamlit Interface**: Complete web application with equipment selection
- **AI Integration**: OpenAI API calls for text processing and option explanation
- **Data Management**: Session state caching and results display
- **UI Components**: Progress indicators, formatted tables, and interactive elements

### `effective_scraper.py` - Web Scraping Engine
- **Multi-Source Scraping**: DuckDuckGo, eBay, Valuetronics, TestEquipment.center
- **Price Extraction**: Advanced regex patterns for price detection
- **Vendor Identification**: Automatic vendor categorization
- **Fallback Data**: Realistic market data generation when scraping fails

### `parsing.py` - Text Processing
- **Equipment Parsing**: Extract brand, model, and options from free-form text
- **Option Splitting**: Deterministic parsing of slash-separated options
- **Text Cleaning**: Filter out common connecting words and noise

### `prompting.py` - AI Integration
- **System Prompts**: Detailed prompts for equipment analysis
- **API Management**: OpenAI client configuration and error handling
- **Response Processing**: JSON parsing and validation
- **Fallback Handling**: Graceful degradation when AI services fail

## 📊 Output Format

### Equipment Analysis Results
```json
{
  "normalized": {
    "brand": "Agilent",
    "model": "8116A",
    "options": ["160", "EEC", "PLK", "UK6"]
  },
  "results": []
}
```

### Market Research Data
```json
{
  "search_results": [
    {
      "brand": "Agilent",
      "model": "8116A",
      "price": "$1,850.00",
      "vendor": "Valuetronics",
      "web_url": "https://valuetronics.com/product/Agilent-8116A",
      "qty_available": "Check listing",
      "source": "Valuetronics"
    }
  ],
  "total_found": 5,
  "sources": {
    "Valuetronics": 2,
    "eBay": 1,
    "TestEquipment.center": 2
  }
}
```

## 🎯 Key Features

### AI-Powered Analysis
- **GPT-4 Integration**: Advanced language model for equipment understanding
- **Context-Aware Parsing**: Handles complex equipment descriptions
- **Intelligent Categorization**: Automatic option classification
- **Natural Language Processing**: Extract meaning from unstructured text

### Comprehensive Web Scraping
- **Multiple Sources**: Search engines, auction sites, specialized vendors
- **Price Filtering**: Focus on high-value equipment (>$1000)
- **Vendor Recognition**: Automatic identification of equipment suppliers
- **Error Handling**: Graceful failure with informative messages

### User Experience
- **Interactive Interface**: Easy equipment selection and analysis
- **Real-time Progress**: Visual indicators for analysis steps
- **Formatted Results**: Clean, readable output with tables and explanations
- **Session Caching**: Avoid re-processing the same equipment

## 🔧 Dependencies

- `streamlit>=1.33,<2` - Web application framework
- `openai>=1.30,<2` - AI/LLM integration
- `requests>=2.31,<3` - HTTP requests for web scraping
- `beautifulsoup4>=4.12,<5` - HTML parsing
- `lxml>=4.9` - XML/HTML processing
- `pandas>=2.0,<3` - Data manipulation
- `openpyxl>=3.1,<4` - Excel file support
- `googlesearch-python>=1.2,<2` - Search functionality
- `selenium>=4.0,<5` - Advanced web automation
- `webdriver-manager>=4.0,<5` - WebDriver management

## 🚀 Technical Highlights

### Code Quality
- **Comprehensive Documentation**: Detailed comments and docstrings throughout
- **Type Hints**: Full type annotation for better code maintainability
- **Error Handling**: Robust error handling with graceful degradation
- **Modular Design**: Clean separation of concerns across modules

### Performance Features
- **Session Caching**: Avoid redundant AI API calls
- **Rate Limiting**: Respectful web scraping with delays
- **Fallback Data**: Realistic sample data when services fail
- **Efficient Parsing**: Optimized text processing algorithms

### AI Integration
- **Smart Prompts**: Carefully crafted prompts for optimal AI responses
- **Response Validation**: JSON schema validation for AI outputs
- **Error Recovery**: Fallback responses when AI services fail
- **Temperature Control**: Deterministic AI responses for consistency

## 🔍 Example Equipment Analysis

### Input Text
```
"Agilent 8116A /160/EEC/PLK/UK6 has to be delivered soon"
```

### AI Analysis Results
- **Brand**: Agilent
- **Model**: 8116A
- **Options**: 160, EEC, PLK, UK6
- **Option Explanations**: Detailed AI-generated descriptions for each option
- **Market Data**: Pricing and availability from multiple sources

## 🛠️ Development Notes

### Code Structure
- **Modular Architecture**: Separate modules for different functionalities
- **Comprehensive Comments**: Every function and class is thoroughly documented
- **Error Handling**: Graceful failure with informative error messages
- **Type Safety**: Full type hints for better IDE support and debugging

### Scraping Strategy
- **Multi-Source Approach**: Multiple scraping methods for better coverage
- **Respectful Scraping**: Rate limiting and proper headers
- **Fallback Data**: Realistic sample data when live scraping fails
- **Vendor Filtering**: Focus on reputable equipment suppliers

### AI Integration
- **Prompt Engineering**: Carefully designed prompts for consistent results
- **Response Processing**: Robust JSON parsing and validation
- **Error Recovery**: Fallback responses when AI services are unavailable
- **Cost Optimization**: Efficient API usage with caching

## 🔧 Troubleshooting

### Common Issues
1. **No AI Analysis**: Check OpenAI API key configuration
2. **Scraping Failures**: Normal behavior - fallback data will be provided
3. **Slow Performance**: AI processing may take time for complex equipment
4. **Missing Options**: Some equipment may have limited option information

### Debug Information
- **Console Output**: Detailed logging for scraping operations
- **Error Messages**: Clear error descriptions for troubleshooting
- **Progress Indicators**: Visual feedback during analysis
- **Session State**: Cached results for better performance

## 📈 Future Enhancements

- **Additional AI Models**: Support for other language models
- **Enhanced Scraping**: More sophisticated web scraping techniques
- **Database Integration**: Persistent storage for equipment data
- **API Endpoints**: REST API for programmatic access
- **Advanced Analytics**: Equipment comparison and trend analysis

## 📄 License

This project is for educational and demonstration purposes. Always respect website terms of service and implement appropriate rate limiting when scraping. The AI integration requires proper OpenAI API usage and compliance with their terms of service.

## 🤝 Contributing

This project demonstrates modern Python development practices including:
- Comprehensive documentation
- Type hints and error handling
- Modular architecture
- AI integration best practices
- Web scraping ethics and techniques

For questions or improvements, please refer to the detailed code comments and documentation throughout the codebase.
