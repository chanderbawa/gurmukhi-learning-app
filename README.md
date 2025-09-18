# 📚 ਗੁਰਮੁਖੀ ਸਿੱਖਿਆ - Gurmukhi Learning App

A fun and interactive educational app for kids to learn the 35 Gurmukhi letters (Akhari) through games, stories, and activities.

## 🌟 Features

### 📖 Core Learning
- **35 Gurmukhi Letters**: Complete coverage of all Gurmukhi Akhari
- **Interactive Letter Cards**: Visual learning with emojis and examples
- **Audio Pronunciation**: Sound playback for each letter
- **Progress Tracking**: Monitor learning progress with visual indicators

### 🎮 Fun Games
- **Letter Recognition**: Identify letters by their appearance
- **Sound Matching**: Match letters with their correct sounds
- **Word Puzzles**: Complete words by finding missing letters
- **Quiz Challenges**: Test knowledge with timed quizzes

### 📚 Bilingual Stories
- **Punjabi Stories**: Age-appropriate content in Gurmukhi script
- **English Translations**: Side-by-side bilingual learning
- **Story Comprehension**: Interactive questions and activities
- **RAG Integration**: Latest Punjabi articles and stories

### 🏆 Gamification
- **Score System**: Earn points for correct answers
- **Progress Levels**: Advance through difficulty levels
- **Achievement Badges**: Unlock rewards for milestones
- **Celebration Animations**: Fun feedback for achievements

## 🚀 Quick Start

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd "/Users/vbawa/Documents/Family Immigration/Python Projects/gurmukhi-learning-app"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the app:**
```bash
streamlit run gurmukhi_app.py
```

4. **Open your browser and go to:**
```
http://localhost:8501
```

## 🎯 How to Use

### 1. **Getting Started**
- Enter your name to create a personalized learning experience
- View your progress on the sidebar
- Choose from different learning modes

### 2. **Learning Modes**

#### 📖 Learn Letters
- Navigate through all 35 Gurmukhi letters
- See letter, pronunciation, sound, and example word
- Mark letters as learned to track progress

#### 🎯 Practice Games
- **Letter Recognition**: Look at a letter and choose its name
- **Sound Matching**: Match letters with their sounds
- **Letter Puzzle**: Complete words with missing letters

#### 📚 Read Stories
- Read Punjabi stories in Gurmukhi script
- Toggle between Punjabi and English versions
- Answer comprehension questions

#### 🏆 Quiz Challenge
- Take a 10-question quiz to test your knowledge
- Get immediate feedback on answers
- See your final score and performance

## 🔧 Technical Features

### Database Integration
- **SQLite Database**: Stores user progress and content
- **Progress Tracking**: Monitors letters learned and scores
- **Story Storage**: Manages bilingual content

### RAG System
- **Content Fetching**: Retrieves latest Punjabi articles
- **Text Analysis**: Analyzes Gurmukhi content for difficulty
- **Bilingual Support**: Provides translations and explanations

### Responsive Design
- **Mobile-Friendly**: Works on tablets and phones
- **Custom Fonts**: Proper Gurmukhi font rendering
- **Interactive UI**: Engaging animations and feedback

## 📱 App Structure

```
gurmukhi-learning-app/
├── gurmukhi_app.py          # Main Streamlit application
├── gurmukhi_rag.py          # RAG system for content
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── gurmukhi_progress.db    # User progress database (auto-created)
└── gurmukhi_content.db     # Content database (auto-created)
```

## 🎨 Customization

### Adding New Letters
Modify the `GURMUKHI_AKHARI` dictionary in `gurmukhi_app.py`:
```python
"ਅ": {
    "roman": "Aira", 
    "sound": "aa", 
    "example": "ਆਮ (Aam - Mango)", 
    "emoji": "🥭"
}
```

### Adding Stories
Use the RAG system to add new content:
```python
from gurmukhi_rag import GurmukhiRAG
rag = GurmukhiRAG()
rag.store_article(story_data)
```

## 🌐 Future Enhancements

- **Text-to-Speech**: Real audio pronunciation
- **Voice Recognition**: Speaking practice
- **Multiplayer Games**: Compete with friends
- **Advanced RAG**: Real-time content from Punjabi news
- **Handwriting Practice**: Draw letters on screen
- **Parent Dashboard**: Track child's progress

## 🤝 Contributing

This app is designed to make Gurmukhi learning fun and accessible for children. Contributions for new games, stories, or features are welcome!

## 📞 Support

For questions or issues, please refer to the code comments or create an issue in the project repository.

---

**ਸਿੱਖੋ ਅਤੇ ਮਜ਼ਾ ਕਰੋ! (Learn and Have Fun!)**
