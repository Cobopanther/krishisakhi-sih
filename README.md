# 🌾 Haritha Chat - Kerala Farming Assistant

A comprehensive AI-powered farming assistant designed specifically for Kerala farmers. Haritha Chat provides intelligent guidance on crop planning, irrigation, pest control, market prices, and agricultural best practices tailored to Kerala's unique farming conditions.

## ✨ Features

### 🤖 AI-Powered Chat Assistant
- **Malayalam & English Support**: Bilingual interface with seamless language switching
- **Context-Aware Responses**: Understands Kerala-specific farming conditions
- **Smart Suggestions**: Provides relevant quick actions and insights
- **Voice Input**: Speech-to-text functionality for hands-free interaction
- **Image Analysis**: Upload crop images for disease identification and analysis

### 👤 User Profile Management
- **Personal Information**: Store and edit farmer details including Aadhaar, contact info, and farm size
- **Achievement System**: Earn badges for active participation (Beginner Farmer, Expert Farmer, Chat Master)
- **Statistics Tracking**: Monitor chat sessions, questions asked, and activity
- **Data Export**: Download chat history and profile data

### 💬 Chat Management
- **Chat History**: Persistent chat sessions with automatic saving
- **New Chat**: Start fresh conversations while preserving history
- **Session Management**: Load, delete, and manage multiple chat sessions
- **Auto-save**: Automatic saving of conversations to localStorage

### 🌤️ Weather Integration
- **Real-time Weather**: Current weather conditions for Thrissur, Kerala
- **Farming Advice**: Weather-based agricultural recommendations
- **Alerts**: Important weather warnings and farming tips
- **Location-specific**: Tailored advice for Kerala's climate

### 🎯 Smart Features
- **Quick Actions**: Predefined farming-related suggestions
- **Insights System**: Contextual recommendations after AI responses
- **Disease Identification**: Crop disease analysis and treatment suggestions
- **Market Information**: Price trends and selling recommendations

### 📱 Mobile-Optimized
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Touch-Friendly**: Optimized for mobile interactions
- **Offline Support**: Local storage for chat history and profile data
- **Progressive Web App**: Installable on mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd krishisakhi-sih
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables** (Optional)
   ```bash
   # For development
   export DEBUG=True
   export PORT=5000
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your browser and go to: `http://localhost:5000`
   - For mobile access on the same network: `http://[your-ip]:5000`

## 📋 Requirements

The application requires the following Python packages:

```
Flask==2.3.3
Werkzeug==2.3.7
google-generativeai==0.3.2
Flask-CORS==4.0.0
```

## 🎮 How to Use

### Getting Started
1. **Open the Application**: Navigate to the chat interface
2. **Language Selection**: Toggle between English and Malayalam using the language switch
3. **Start Chatting**: Type your farming questions or use voice input

### Profile Management
1. **View Profile**: Click on the profile section in the sidebar
2. **Edit Information**: Click "✏️ Edit Profile" to modify your details
3. **View Achievements**: Check your progress and earned badges
4. **Export Data**: Download your chat history and profile information

### Chat Features
1. **New Chat**: Click "New Chat" to start a fresh conversation
2. **Chat History**: Access previous conversations from the sidebar
3. **Voice Input**: Click the microphone button to speak your questions
4. **Image Upload**: Use the image button to upload crop photos for analysis

### Weather Information
1. **Weather Widget**: Ask about weather or click weather-related suggestions
2. **Farming Advice**: Get weather-based agricultural recommendations
3. **Alerts**: Receive important weather warnings and tips

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Set to `True` for development mode (default: `True`)
- `PORT`: Port number for the application (default: `5000`)
- `GEMINI_API_KEY`: Your Google Gemini API key (required for AI responses)

### API Keys
1. **Google Gemini API**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Add to Environment**: Set the `GEMINI_API_KEY` environment variable

## 📱 Mobile Access

### Local Network Access
1. **Find Your IP**: Check your computer's IP address
2. **Mobile Connection**: Connect your phone to the same Wi-Fi network
3. **Access URL**: Open `http://[your-ip]:5000` on your mobile browser

### Example
- Computer IP: `192.168.1.100`
- Mobile URL: `http://192.168.1.100:5000`

## 🎯 Use Cases

### For Kerala Farmers
- **Crop Planning**: Get advice on what to plant and when
- **Pest Control**: Identify and treat crop diseases
- **Irrigation**: Optimize water usage based on weather
- **Market Prices**: Stay updated on crop prices and trends
- **Best Practices**: Learn Kerala-specific farming techniques

### For Agricultural Students
- **Learning Tool**: Interactive way to learn about farming
- **Research**: Access to AI-powered agricultural insights
- **Practice**: Test knowledge with real-world scenarios

### For Agricultural Extension Workers
- **Reference Tool**: Quick access to farming information
- **Communication**: Share knowledge with farmers
- **Documentation**: Track interactions and advice given

## 🏆 Achievement System

### Badges Available
- **🥉 Beginner Farmer**: Ask 5+ questions
- **🏆 Expert Farmer**: Ask 10+ questions  
- **🌟 Chat Master**: Start 10+ chat sessions

### Progress Tracking
- **Questions Asked**: Total number of questions
- **Chat Sessions**: Number of conversations started
- **Days Active**: Time since first use

## 🔒 Data Privacy

### Local Storage
- **Chat History**: Stored locally in your browser
- **Profile Data**: Personal information saved locally
- **No Server Storage**: Your data stays on your device

### Data Export
- **JSON Format**: Download your data in structured format
- **Complete History**: Includes all chats and profile information
- **Privacy Control**: You control your data

## 🛠️ Development

### Project Structure
```
krishisakhi-sih/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── chat.html         # Chat interface template
├── static/               # Static files (if any)
└── README.md            # This file
```

### Key Components
- **Flask Backend**: Handles API requests and AI integration
- **Frontend**: HTML, CSS, and JavaScript for the chat interface
- **AI Integration**: Google Gemini for intelligent responses
- **Local Storage**: Browser-based data persistence

### Adding Features
1. **Backend**: Modify `app.py` for new API endpoints
2. **Frontend**: Update `templates/chat.html` for UI changes
3. **Styling**: Add CSS for new components
4. **JavaScript**: Implement client-side functionality

## 🐛 Troubleshooting

### Common Issues

#### Application Won't Start
- **Check Python Version**: Ensure Python 3.7+ is installed
- **Install Dependencies**: Run `pip install -r requirements.txt`
- **Check Port**: Make sure port 5000 is available

#### AI Responses Not Working
- **API Key**: Verify `GEMINI_API_KEY` is set correctly
- **Internet Connection**: Ensure stable internet connection
- **API Limits**: Check if you've exceeded API usage limits

#### Mobile Access Issues
- **Network**: Ensure devices are on the same network
- **Firewall**: Check if firewall is blocking connections
- **IP Address**: Verify the correct IP address is being used

#### Voice Input Not Working
- **Microphone Permission**: Allow microphone access in browser
- **HTTPS**: Some browsers require HTTPS for microphone access
- **Browser Support**: Use Chrome, Firefox, or Safari for best compatibility

### Getting Help
1. **Check Console**: Open browser developer tools for error messages
2. **Check Logs**: Look at the terminal running the Flask app
3. **Test Features**: Try different browsers and devices
4. **Clear Cache**: Clear browser cache and localStorage

## 📞 Support

### For Issues
- **Browser Console**: Check for JavaScript errors
- **Network Tab**: Verify API requests are working
- **Application Logs**: Check the terminal output

### For Feature Requests
- **GitHub Issues**: Create an issue for new features
- **Pull Requests**: Contribute improvements
- **Documentation**: Help improve this README

## 🔄 Updates

### Version History
- **v1.0**: Initial release with basic chat functionality
- **v1.1**: Added profile management and achievements
- **v1.2**: Implemented voice input and image analysis
- **v1.3**: Added weather integration and mobile optimization

### Future Plans
- **Offline Mode**: Work without internet connection
- **More Languages**: Support for additional Indian languages
- **Advanced Analytics**: Detailed farming insights and reports
- **Community Features**: Connect with other farmers
- **IoT Integration**: Connect with farming sensors and devices

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 🙏 Acknowledgments

- **Google Gemini**: For providing the AI capabilities
- **Kerala Farmers**: For their valuable feedback and insights
- **Open Source Community**: For the tools and libraries used

---

**Made with ❤️ for Kerala Farmers**

*Haritha Chat - Your Smart Farming Companion*
