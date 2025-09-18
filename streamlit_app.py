#!/usr/bin/env python3
"""
Gurmukhi Learning App for Kids
Fun and interactive way to learn 35 Gurmukhi Akhari (letters)
With LLM+RAG for latest Punjabi stories and bilingual content
"""

import streamlit as st
import random
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
import sqlite3
import os

# Configure page
st.set_page_config(
    page_title="ਗੁਰਮੁਖੀ ਸਿੱਖਿਆ - Gurmukhi Learning",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 35 Gurmukhi Akhari (letters) with pronunciation and meanings
GURMUKHI_AKHARI = {
    "ੳ": {"roman": "Oora", "sound": "a", "example": "ਅੰਗੂਰ (Angoor - Grapes)", "emoji": "🍇"},
    "ਅ": {"roman": "Aira", "sound": "aa", "example": "ਆਮ (Aam - Mango)", "emoji": "🥭"},
    "ੲ": {"roman": "Iri", "sound": "i", "example": "ਇਕ (Ik - One)", "emoji": "1️⃣"},
    "ਸ": {"roman": "Sassa", "sound": "s", "example": "ਸੇਬ (Seb - Apple)", "emoji": "🍎"},
    "ਹ": {"roman": "Haha", "sound": "h", "example": "ਹਾਥੀ (Haathi - Elephant)", "emoji": "🐘"},
    "ਕ": {"roman": "Kakka", "sound": "k", "example": "ਕਮਲ (Kamal - Lotus)", "emoji": "🪷"},
    "ਖ": {"roman": "Khakha", "sound": "kh", "example": "ਖਰਗੋਸ਼ (Khargosh - Rabbit)", "emoji": "🐰"},
    "ਗ": {"roman": "Gagga", "sound": "g", "example": "ਗਾਂ (Gaan - Cow)", "emoji": "🐄"},
    "ਘ": {"roman": "Ghagha", "sound": "gh", "example": "ਘੋੜਾ (Ghora - Horse)", "emoji": "🐎"},
    "ਙ": {"roman": "Nganga", "sound": "ng", "example": "ਅੰਗ (Ang - Body part)", "emoji": "👤"},
    "ਚ": {"roman": "Chacha", "sound": "ch", "example": "ਚੰਦ (Chand - Moon)", "emoji": "🌙"},
    "ਛ": {"roman": "Chhachha", "sound": "chh", "example": "ਛਤਰੀ (Chhatri - Umbrella)", "emoji": "☂️"},
    "ਜ": {"roman": "Jajja", "sound": "j", "example": "ਜਹਾਜ਼ (Jahaaz - Ship)", "emoji": "🚢"},
    "ਝ": {"roman": "Jhajha", "sound": "jh", "example": "ਝੰਡਾ (Jhanda - Flag)", "emoji": "🏳️"},
    "ਞ": {"roman": "Nyanya", "sound": "ny", "example": "ਞਾਣ (Gyaan - Knowledge)", "emoji": "🧠"},
    "ਟ": {"roman": "Tanka", "sound": "t", "example": "ਟੋਪੀ (Topi - Hat)", "emoji": "🎩"},
    "ਠ": {"roman": "Thatha", "sound": "th", "example": "ਠੰਡ (Thand - Cold)", "emoji": "🥶"},
    "ਡ": {"roman": "Dadda", "sound": "d", "example": "ਡਰਾਮਾ (Drama)", "emoji": "🎭"},
    "ਢ": {"roman": "Dhadha", "sound": "dh", "example": "ਢੋਲ (Dhol - Drum)", "emoji": "🥁"},
    "ਣ": {"roman": "Nana", "sound": "n", "example": "ਗੁਣ (Gun - Quality)", "emoji": "⭐"},
    "ਤ": {"roman": "Tatta", "sound": "t", "example": "ਤਾਰਾ (Tara - Star)", "emoji": "⭐"},
    "ਥ": {"roman": "Thatha", "sound": "th", "example": "ਥਾਲੀ (Thaali - Plate)", "emoji": "🍽️"},
    "ਦ": {"roman": "Dadda", "sound": "d", "example": "ਦਰਵਾਜ਼ਾ (Darwaza - Door)", "emoji": "🚪"},
    "ਧ": {"roman": "Dhadha", "sound": "dh", "example": "ਧੁੱਪ (Dhoop - Sunlight)", "emoji": "☀️"},
    "ਨ": {"roman": "Nanna", "sound": "n", "example": "ਨਦੀ (Nadi - River)", "emoji": "🏞️"},
    "ਪ": {"roman": "Pappa", "sound": "p", "example": "ਪੰਛੀ (Panchhi - Bird)", "emoji": "🐦"},
    "ਫ": {"roman": "Phappha", "sound": "ph", "example": "ਫੁੱਲ (Phul - Flower)", "emoji": "🌸"},
    "ਬ": {"roman": "Babba", "sound": "b", "example": "ਬਿੱਲਾ (Billa - Cat)", "emoji": "🐱"},
    "ਭ": {"roman": "Bhabha", "sound": "bh", "example": "ਭਾਲੂ (Bhaloo - Bear)", "emoji": "🐻"},
    "ਮ": {"roman": "Mamma", "sound": "m", "example": "ਮੱਛੀ (Machhi - Fish)", "emoji": "🐟"},
    "ਯ": {"roman": "Yayya", "sound": "y", "example": "ਯੋਗ (Yog - Yoga)", "emoji": "🧘"},
    "ਰ": {"roman": "Rara", "sound": "r", "example": "ਰੋਟੀ (Roti - Bread)", "emoji": "🫓"},
    "ਲ": {"roman": "Lalla", "sound": "l", "example": "ਲੱਡੂ (Laddu - Sweet)", "emoji": "🍬"},
    "ਵ": {"roman": "Vava", "sound": "v", "example": "ਵਿਆਹ (Viah - Wedding)", "emoji": "💒"},
    "ੜ": {"roman": "Rara", "sound": "r", "example": "ਪੜ੍ਹਨਾ (Parhna - To read)", "emoji": "📖"}
}

class GurmukhiLearningApp:
    def __init__(self):
        self.init_database()
        self.init_session_state()
    
    def init_database(self):
        """Initialize SQLite database for progress tracking"""
        self.db_path = "gurmukhi_progress.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id TEXT PRIMARY KEY,
                letters_learned TEXT DEFAULT '[]',
                total_score INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_activity TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_punjabi TEXT,
                title_english TEXT,
                content_punjabi TEXT,
                content_english TEXT,
                difficulty_level INTEGER,
                created_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'user_name' not in st.session_state:
            st.session_state.user_name = ""
        if 'current_letter' not in st.session_state:
            st.session_state.current_letter = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'learned_letters' not in st.session_state:
            st.session_state.learned_letters = []
        if 'game_mode' not in st.session_state:
            st.session_state.game_mode = "learn"

def main():
    app = GurmukhiLearningApp()
    
    # Custom CSS for Gurmukhi fonts and styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gurmukhi:wght@400;700&display=swap');
    
    .gurmukhi-text {
        font-family: 'Noto Sans Gurmukhi', sans-serif;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B35;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .letter-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .letter-card:hover {
        transform: translateY(-10px);
    }
    
    .app-header {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        height: 100%;
        transition: width 0.5s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App Header
    st.markdown("""
    <div class="app-header">
        <h1 style="color: white; margin: 0; font-size: 3rem;">📚 ਗੁਰਮੁਖੀ ਸਿੱਖਿਆ</h1>
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">Gurmukhi Learning Adventure</h2>
        <p style="color: white; margin: 10px 0;">Learn the 35 Gurmukhi letters through fun games and stories!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User name input
    if not st.session_state.user_name:
        st.markdown("### 👋 Welcome! What's your name?")
        name = st.text_input("Enter your name:", placeholder="Your name here...")
        if st.button("Start Learning! 🚀") and name:
            st.session_state.user_name = name
            st.rerun()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {st.session_state.user_name}!")
        
        # Progress display
        progress = len(st.session_state.learned_letters) / len(GURMUKHI_AKHARI) * 100
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>
        <p style="text-align: center; margin-top: 10px;">
            Progress: {len(st.session_state.learned_letters)}/35 letters ({progress:.1f}%)
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎮 Choose Activity")
        mode = st.selectbox("Select learning mode:", 
                           ["📖 Learn Letters", "🎯 Practice Game", "📚 Read Stories", "🏆 Quiz Challenge"])
        
        if mode == "📖 Learn Letters":
            st.session_state.game_mode = "learn"
        elif mode == "🎯 Practice Game":
            st.session_state.game_mode = "practice"
        elif mode == "📚 Read Stories":
            st.session_state.game_mode = "stories"
        else:
            st.session_state.game_mode = "quiz"
    
    # Main content based on selected mode
    if st.session_state.game_mode == "learn":
        display_learn_mode()
    elif st.session_state.game_mode == "practice":
        display_practice_mode()
    elif st.session_state.game_mode == "stories":
        display_stories_mode()
    else:
        display_quiz_mode()

def display_learn_mode():
    """Display letter learning interface"""
    st.markdown("## 📖 Learn Gurmukhi Letters")
    
    letters = list(GURMUKHI_AKHARI.keys())
    
    # Letter navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous") and st.session_state.current_letter > 0:
            st.session_state.current_letter -= 1
            st.rerun()
    
    with col3:
        if st.button("Next ➡️") and st.session_state.current_letter < len(letters) - 1:
            st.session_state.current_letter += 1
            st.rerun()
    
    with col2:
        st.markdown(f"Letter {st.session_state.current_letter + 1} of {len(letters)}")
    
    # Current letter display
    current_letter = letters[st.session_state.current_letter]
    letter_info = GURMUKHI_AKHARI[current_letter]
    
    # Letter card
    st.markdown(f"""
    <div class="letter-card">
        <div class="gurmukhi-text">{current_letter}</div>
        <h2 style="color: white; margin: 1rem 0;">{letter_info['roman']}</h2>
        <h3 style="color: white; margin: 1rem 0;">Sound: "{letter_info['sound']}"</h3>
        <div style="font-size: 4rem; margin: 1rem 0;">{letter_info['emoji']}</div>
        <p style="color: white; font-size: 1.2rem; margin: 1rem 0;">{letter_info['example']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio pronunciation using browser's speech synthesis
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔊 Play Sound", use_container_width=True):
            # Use HTML5 audio with JavaScript for text-to-speech
            audio_text = letter_info['sound']
            st.components.v1.html(f"""
            <script>
                function playSound() {{
                    if ('speechSynthesis' in window) {{
                        const utterance = new SpeechSynthesisUtterance('{audio_text}');
                        utterance.lang = 'pa-IN'; // Punjabi language
                        utterance.rate = 0.7;
                        utterance.pitch = 1.2;
                        speechSynthesis.speak(utterance);
                    }} else {{
                        alert('Speech synthesis not supported in this browser');
                    }}
                }}
                playSound();
            </script>
            """, height=0)
            st.success(f"🔊 Playing: {letter_info['roman']} ({letter_info['sound']})")
    
    # Mark as learned
    if current_letter not in st.session_state.learned_letters:
        if st.button("✅ Mark as Learned", use_container_width=True):
            st.session_state.learned_letters.append(current_letter)
            st.session_state.score += 10
            st.balloons()
            st.success("Great job! Letter learned! 🎉")

def display_practice_mode():
    """Display practice games"""
    st.markdown("## 🎯 Practice Games")
    
    game_type = st.selectbox("Choose a game:", 
                            ["🎯 Letter Recognition", "🔤 Sound Matching", "🧩 Letter Puzzle"])
    
    if game_type == "🎯 Letter Recognition":
        display_recognition_game()
    elif game_type == "🔤 Sound Matching":
        display_sound_matching_game()
    else:
        display_puzzle_game()

def display_recognition_game():
    """Letter recognition game"""
    st.markdown("### 🎯 Letter Recognition Game")
    st.markdown("Look at the letter and choose the correct name!")
    
    if 'game_letter' not in st.session_state:
        st.session_state.game_letter = random.choice(list(GURMUKHI_AKHARI.keys()))
    
    letter = st.session_state.game_letter
    letter_info = GURMUKHI_AKHARI[letter]
    
    # Display letter
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: #f0f0f0; border-radius: 15px; margin: 2rem 0;">
        <div class="gurmukhi-text">{letter}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Multiple choice options
    correct_answer = letter_info['roman']
    all_romans = [info['roman'] for info in GURMUKHI_AKHARI.values()]
    options = random.sample([r for r in all_romans if r != correct_answer], 3)
    options.append(correct_answer)
    random.shuffle(options)
    
    selected = st.radio("What is this letter called?", options)
    
    if st.button("Check Answer"):
        if selected == correct_answer:
            st.success("🎉 Correct! Well done!")
            st.session_state.score += 5
            st.balloons()
        else:
            st.error(f"❌ Not quite! This is {correct_answer}")
        
        # New letter for next round
        st.session_state.game_letter = random.choice(list(GURMUKHI_AKHARI.keys()))
        if st.button("Next Letter"):
            st.rerun()

def display_sound_matching_game():
    """Sound matching game"""
    st.markdown("### 🔤 Sound Matching Game")
    st.info("Match the letter with its sound!")
    
    # Simple matching interface
    letters = random.sample(list(GURMUKHI_AKHARI.keys()), 4)
    
    for i, letter in enumerate(letters):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #e3f2fd; border-radius: 10px;">
                <div class="gurmukhi-text" style="font-size: 2rem;">{letter}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            sound_options = [GURMUKHI_AKHARI[l]['sound'] for l in letters]
            selected_sound = st.selectbox(f"Sound for {letter}:", sound_options, key=f"sound_{i}")
            
            if st.button(f"Check {letter}", key=f"check_{i}"):
                if selected_sound == GURMUKHI_AKHARI[letter]['sound']:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Wrong! Correct sound is '{GURMUKHI_AKHARI[letter]['sound']}'")

def display_puzzle_game():
    """Letter puzzle game"""
    st.markdown("### 🧩 Letter Puzzle")
    st.info("Complete the word by choosing the missing letter!")
    
    # Simple word completion game
    sample_words = [
        {"word": "ਸੇਬ", "missing_pos": 0, "meaning": "Apple"},
        {"word": "ਗਾਂ", "missing_pos": 0, "meaning": "Cow"},
        {"word": "ਚੰਦ", "missing_pos": 0, "meaning": "Moon"}
    ]
    
    if 'puzzle_word' not in st.session_state:
        st.session_state.puzzle_word = random.choice(sample_words)
    
    word_data = st.session_state.puzzle_word
    word = word_data['word']
    missing_pos = word_data['missing_pos']
    
    # Display word with missing letter
    display_word = list(word)
    missing_letter = display_word[missing_pos]
    display_word[missing_pos] = "___"
    
    st.markdown(f"### Complete this word: {''.join(display_word)}")
    st.markdown(f"**Meaning:** {word_data['meaning']}")
    
    # Letter options
    options = random.sample(list(GURMUKHI_AKHARI.keys()), 4)
    if missing_letter not in options:
        options[0] = missing_letter
    random.shuffle(options)
    
    selected = st.radio("Choose the missing letter:", options)
    
    if st.button("Complete Word"):
        if selected == missing_letter:
            st.success(f"🎉 Correct! The word is {word}")
            st.session_state.score += 10
        else:
            st.error(f"❌ Wrong! The correct letter is {missing_letter}")
        
        st.session_state.puzzle_word = random.choice(sample_words)

def display_stories_mode():
    """Display Punjabi stories with bilingual support"""
    st.markdown("## 📚 Punjabi Stories")
    
    # Sample stories (in real app, these would come from RAG system)
    sample_stories = [
        {
            "title_punjabi": "ਚੰਗਾ ਬੱਚਾ",
            "title_english": "The Good Child",
            "content_punjabi": "ਇੱਕ ਵਾਰ ਇੱਕ ਚੰਗਾ ਬੱਚਾ ਸੀ। ਉਹ ਰੋਜ਼ ਸਕੂਲ ਜਾਂਦਾ ਸੀ।",
            "content_english": "Once there was a good child. He went to school every day.",
            "difficulty": 1
        },
        {
            "title_punjabi": "ਸੁੰਦਰ ਬਾਗ਼",
            "title_english": "Beautiful Garden",
            "content_punjabi": "ਬਾਗ਼ ਵਿੱਚ ਬਹੁਤ ਸਾਰੇ ਫੁੱਲ ਸਨ। ਤਿਤਲੀਆਂ ਉੱਡ ਰਹੀਆਂ ਸਨ।",
            "content_english": "There were many flowers in the garden. Butterflies were flying.",
            "difficulty": 2
        }
    ]
    
    # Story selection
    story = st.selectbox("Choose a story:", 
                        [f"{s['title_english']} - {s['title_punjabi']}" for s in sample_stories])
    
    story_index = [f"{s['title_english']} - {s['title_punjabi']}" for s in sample_stories].index(story)
    selected_story = sample_stories[story_index]
    
    # Language toggle
    show_punjabi = st.checkbox("Show Punjabi text", value=True)
    show_english = st.checkbox("Show English translation", value=True)
    
    # Story display
    st.markdown("---")
    
    if show_punjabi:
        st.markdown(f"""
        <div style="background: #fff3e0; padding: 2rem; border-radius: 15px; margin: 1rem 0;">
            <h2 style="color: #e65100; font-family: 'Noto Sans Gurmukhi';">{selected_story['title_punjabi']}</h2>
            <p style="font-size: 1.5rem; line-height: 2; font-family: 'Noto Sans Gurmukhi'; color: #333333;">
                {selected_story['content_punjabi']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    if show_english:
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 2rem; border-radius: 15px; margin: 1rem 0;">
            <h2 style="color: #2e7d32;">{selected_story['title_english']}</h2>
            <p style="font-size: 1.2rem; line-height: 1.8; color: #333333;">
                {selected_story['content_english']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Story comprehension questions
    st.markdown("### 🤔 Story Questions")
    st.info("Answer these questions about the story!")
    
    # Simple comprehension questions (would be generated by LLM in real app)
    if story_index == 0:
        question = st.radio("What did the good child do every day?", 
                           ["Played games", "Went to school", "Watched TV"])
        if st.button("Check Answer"):
            if question == "Went to school":
                st.success("🎉 Correct!")
            else:
                st.error("❌ Try again!")

def display_quiz_mode():
    """Display quiz challenge"""
    st.markdown("## 🏆 Quiz Challenge")
    st.info("Test your Gurmukhi knowledge!")
    
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.quiz_score = 0
        st.session_state.quiz_question = 0
    
    if not st.session_state.quiz_started:
        st.markdown("### Ready for the challenge?")
        st.markdown("Answer 10 questions about Gurmukhi letters!")
        
        if st.button("🚀 Start Quiz", use_container_width=True):
            st.session_state.quiz_started = True
            st.session_state.quiz_questions = random.sample(list(GURMUKHI_AKHARI.keys()), 10)
            st.rerun()
    else:
        # Quiz interface
        if st.session_state.quiz_question < 10:
            current_q = st.session_state.quiz_question
            letter = st.session_state.quiz_questions[current_q]
            letter_info = GURMUKHI_AKHARI[letter]
            
            st.markdown(f"### Question {current_q + 1}/10")
            
            # Display letter
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: #f5f5f5; border-radius: 15px;">
                <div class="gurmukhi-text">{letter}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Multiple choice
            correct = letter_info['roman']
            all_options = [info['roman'] for info in GURMUKHI_AKHARI.values()]
            options = random.sample([o for o in all_options if o != correct], 3)
            options.append(correct)
            random.shuffle(options)
            
            # Initialize quiz answer key for this question
            quiz_answer_key = f"quiz_answer_{current_q}"
            if quiz_answer_key not in st.session_state:
                st.session_state[quiz_answer_key] = None
            
            answer = st.radio("What is this letter called?", options, key=f"quiz_radio_{current_q}")
            
            if st.button("Submit Answer", key=f"submit_{current_q}"):
                if answer == correct:
                    st.success("✅ Correct!")
                    st.session_state.quiz_score += 1
                else:
                    st.error(f"❌ Wrong! Correct answer: {correct}")
                
                st.session_state.quiz_question += 1
                
                if st.session_state.quiz_question < 10:
                    st.info("Click below to continue to the next question!")
                    if st.button("Next Question ➡️", key=f"next_{current_q}"):
                        st.rerun()
                else:
                    st.rerun()
        else:
            # Quiz completed
            score = st.session_state.quiz_score
            st.markdown(f"""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #4CAF50, #45a049); border-radius: 20px;">
                <h1 style="color: white; font-size: 3rem;">🎉 Quiz Complete!</h1>
                <h2 style="color: white;">Your Score: {score}/10</h2>
                <p style="color: white; font-size: 1.2rem;">
                    {"Excellent work! 🌟" if score >= 8 else "Good job! Keep practicing! 💪" if score >= 6 else "Keep learning! You're improving! 📚"}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Take Quiz Again"):
                st.session_state.quiz_started = False
                st.session_state.quiz_score = 0
                st.session_state.quiz_question = 0
                st.rerun()

if __name__ == "__main__":
    main()
