# 🎙️ Bright Minds Discussion

An interactive AI-powered debate simulator that brings historical and modern visionaries to life through intelligent conversations. Watch Elon Musk debate Steve Jobs, or see Einstein discuss with Marie Curie - all powered by GMI Cloud AI.

## ✨ Features

- **🎭 Personality-Driven AI**: Each speaker has unique personality traits, communication styles, and expertise areas
- **⏱️ Real-Time Debate**: Natural 5-10 minute conversations with realistic timing and flow
- **🎯 Topic-Focused**: Choose any debate topic and watch the AI adapt responses accordingly
- **👥 Audience Interaction**: Interrupt the debate with questions and get responses from both speakers
- **🎨 Modern UI**: Clean, podcast-style interface with color-coded speakers and timestamps
- **🔧 Configurable**: Easy to add new speakers or modify existing personalities

## 🚀 Quick Start

### Prerequisites
- Qt6 development environment
- Python 3.7+
- GMI Cloud API key

### Setup

1. **Clone and build the project**:
   ```bash
   mkdir build && cd build
   cmake ..
   make
   ```

2. **Install Python dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

3. **Configure your API key**:
   Create a `.env` file in the project root:
   ```
   GMI_API_KEY=your_gmi_api_key_here
   ```

4. **Run the application**:
   ```bash
   ./BrightMindsDiscussion
   ```

## 🎮 How to Use

1. **Select Speakers**: Choose two different speakers from the dropdown menus
2. **Set Topic**: Enter a debate topic (e.g., "The Future of AI in Society")
3. **Start Debate**: Click "🎬 Start Debate" to begin the conversation
4. **Watch & Interact**: The speakers will alternate responses every 4 seconds
5. **Ask Questions**: Type questions in the bottom field to interrupt the debate
6. **Stop Anytime**: Click the stop button to end the debate

## 🎭 Available Speakers

- **Elon Musk**: Tech entrepreneur, visionary, direct communication
- **Steve Jobs**: Design-focused, inspirational, minimalist philosophy
- **Albert Einstein**: Analytical, philosophical, scientific approach
- **Marie Curie**: Methodical, dedicated, pioneering scientist
- **Nikola Tesla**: Visionary, innovative, futuristic thinking
- **Ada Lovelace**: Analytical, poetic, mathematical pioneer

## 🔧 Customization

### Adding New Speakers

Edit `speakers.json` to add new personalities:

```json
{
  "name": "Your Speaker Name",
  "description": "Brief description of the person",
  "style": "Communication style description",
  "traits": ["trait1", "trait2", "trait3"],
  "temperature": 0.7,
  "prompt_template": "Detailed personality prompt for the AI..."
}
```

### Modifying Debate Parameters

In `src/MainWindow.cpp`, you can adjust:
- **Timer interval**: Change `debateTimer->setInterval(4000)` for different response speeds
- **Max rounds**: Modify the `debateRound >= 20` condition for longer/shorter debates
- **Response length**: Adjust `max_tokens` in the Python script

## 🏗️ Architecture

- **Frontend**: Qt6 C++ with modern UI design
- **Backend**: Python script handling GMI API communication
- **Communication**: QProcess for C++ ↔ Python integration
- **Configuration**: JSON-based speaker profiles
- **Real-time**: Timer-based debate orchestration

## 🎯 GMI Hackathon Features

- **Modular Design**: Easy to extend with more speakers or features
- **Prompt Engineering**: Sophisticated personality simulation
- **Real-time Interaction**: Live audience participation
- **Scalable**: Can support more than 2 speakers in future versions
- **API Integration**: Seamless GMI Cloud API usage

## 🐛 Troubleshooting

### Common Issues

1. **"GMI_API_KEY not found"**: Check your `.env` file and API key
2. **"speakers.json not found"**: Ensure the file is in the project root
3. **Python process errors**: Verify Python dependencies are installed
4. **Unicode errors**: The app handles UTF-8 encoding automatically

### Debug Mode

Enable debug output by checking the console for detailed error messages and API responses.

## 📝 License

MIT License - feel free to use and modify for your projects!

## 🤝 Contributing

This project was created for the GMI Hackathon. Contributions and improvements are welcome!

---

**Made with ❤️ for the GMI Hackathon**
