# JARVIS - AI Voice Assistant

A voice-activated AI assistant with wake word detection, command processing, and a graphical user interface. JARVIS can help you with daily tasks, answer questions, control applications, and more.

## Features

- **Wake Word Detection**: Activate JARVIS by saying "Hey JARVIS", "JARVIS", or "Okay JARVIS"
- **Voice Commands**: Control your computer with natural voice commands
- **AI Integration**: Powered by Google's Gemini AI for intelligent conversations
- **GUI Interface**: Visual feedback with conversation logs and status indicators
- **Email Integration**: Send emails via Gmail API
- **Spotify Control**: Play, pause, skip tracks (requires Spotify Premium)
- **Weather Information**: Get current weather updates
- **File Operations**: Search, open, and manage files
- **Application Control**: Launch and manage applications
- **System Commands**: Time, date, calculations, and system controls

## Prerequisites

- Python 3.8 or higher
- Microphone for voice input
- Internet connection
- Spotify Premium account (for Spotify features)
- Google Cloud account (for Gmail features)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd JARVIS
   ```

2. **Install dependencies**
   ```bash
   pip install speech_recognition gtts pygame google-generativeai python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client spotipy requests
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```
   API_KEY=your_gemini_api_key_here
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   WEATHER_API_KEY=your_openweathermap_api_key
   ```

4. **Configure Gmail (Optional)**
   
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials and save as `credentials.json` in the project root
   - Run `test_gmail.py` to authenticate

## Getting API Keys

### Gemini API Key (Required)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `API_KEY`

### Spotify API (Optional)
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Get Client ID and Client Secret
4. Set redirect URI to `http://localhost:8888/callback`
5. Add credentials to `.env`

### Weather API (Optional)
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add to `.env` as `WEATHER_API_KEY`

## Usage

### Running JARVIS

```bash
python testv5.py
```

### Voice Commands

**Wake Up JARVIS:**
- "Hey JARVIS"
- "JARVIS"
- "Okay JARVIS"

**Sleep Mode:**
- "Go to sleep"
- "Sleep mode"

**General Queries:**
- "What's the weather?"
- "What time is it?"
- "What's the date?"
- "Calculate 25 times 4"

**Web Commands:**
- "Open YouTube"
- "Open Google"
- "Open GitHub"

**File Operations:**
- "Search for [filename]"
- "Open folder Desktop"
- "List files"

**Application Control:**
- "Open Chrome"
- "Launch Spotify"
- "Start Calculator"

**Spotify Commands:**
- "Play music"
- "Pause music"
- "Next song"
- "Previous song"
- "What's playing?"

**System Commands:**
- "Lock screen"
- "Shutdown"
- "Restart"

**Exit:**
- "Exit"
- "Quit"
- "Goodbye"

## Project Structure

```
JARVIS/
├── testv5.py                 # Main JARVIS application
├── test_gmail.py             # Gmail API testing
├── test_spotify.py           # Spotify API testing
├── test_weather.py           # Weather API testing
├── .env                      # Environment variables (create this)
├── credentials.json          # Google OAuth credentials (optional)
├── token.json                # Gmail auth token (auto-generated)
├── .spotify_cache            # Spotify auth cache (auto-generated)
├── chat_history.json         # AI conversation history (auto-generated)
└── README.md                 # This file
```

## Testing Individual Features

**Test Gmail:**
```bash
python test_gmail.py
```

**Test Spotify:**
```bash
python test_spotify.py
```

**Test Weather:**
```bash
python test_weather.py
```

## Troubleshooting

### Microphone Issues
- Ensure your microphone is properly connected
- Check system microphone permissions
- Try adjusting the ambient noise threshold

### API Errors
- Verify all API keys are correct in `.env`
- Check internet connection
- Ensure API services are enabled in their respective consoles

### Spotify Not Working
- Requires Spotify Premium account
- Make sure Spotify app is open on a device
- Check if device is set as active in Spotify

### Gmail Authentication
- Delete `token.json` and re-authenticate if issues occur
- Ensure Gmail API is enabled in Google Cloud Console

## Notes

- JARVIS requires an active internet connection for AI and API features
- Some commands may require administrator privileges
- Chat history is saved locally in `chat_history.json`
- Temporary audio files are created and deleted automatically

## Privacy

- All voice commands are processed through Google Speech Recognition
- AI conversations are sent to Google Gemini API
- Gmail and Spotify credentials are stored locally
- No data is collected or sent to third parties beyond necessary API calls

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Google Gemini AI for natural language processing
- Google Speech Recognition for voice-to-text
- gTTS for text-to-speech
- Spotipy for Spotify integration
- All open-source libraries used in this project

---

THIS IS A HOBBY PROJECT, RUN testv5 to actually see how it works live. and again feel free to use some of this code idk if its that good LOL
