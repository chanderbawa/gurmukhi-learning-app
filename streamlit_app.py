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
from PIL import Image
import io
import pytesseract
import cv2
import numpy as np
import google.generativeai as genai

# Configure page
st.set_page_config(
    page_title="ਗੁਰਮੁਖੀ ਸਿੱਖਿਆ - Gurmukhi Learning",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 35 Gurmukhi Akhari (letters) with pronunciation and meanings
GURMUKHI_AKHARI = {
    "ੳ": {"roman": "Oora", "sound": "a", "phonetic": "OO-dha", "example": "ਅੰਗੂਰ (Angoor - Grapes)", "emoji": "🍇"},
    "ਅ": {"roman": "Aira", "sound": "aa", "phonetic": "AY-dha", "example": "ਆਮ (Aam - Mango)", "emoji": "🥭"},
    "ੲ": {"roman": "Iri", "sound": "i", "phonetic": "EE-dhee", "example": "ਇਕ (Ik - One)", "emoji": "1️⃣"},
    "ਸ": {"roman": "Sassa", "sound": "s", "phonetic": "SUSS-saa", "example": "ਸੇਬ (Seb - Apple)", "emoji": "🍎"},
    "ਹ": {"roman": "Haha", "sound": "h", "phonetic": "HAH-haa", "example": "ਹਾਥੀ (Haathi - Elephant)", "emoji": "🐘"},
    "ਕ": {"roman": "Kakka", "sound": "k", "phonetic": "KUCK-kaa", "example": "ਕਮਲ (Kamal - Lotus)", "emoji": "🪷"},
    "ਖ": {"roman": "Khakha", "sound": "kh", "phonetic": "KHUCK-khaa", "example": "ਖਰਗੋਸ਼ (Khargosh - Rabbit)", "emoji": "🐰"},
    "ਗ": {"roman": "Gagga", "sound": "g", "phonetic": "GUCK-gaa", "example": "ਗਾਂ (Gaan - Cow)", "emoji": "🐄"},
    "ਘ": {"roman": "Ghagha", "sound": "gh", "phonetic": "GHUCK-ghaa", "example": "ਘੋੜਾ (Ghora - Horse)", "emoji": "🐎"},
    "ਙ": {"roman": "Nganga", "sound": "ng", "phonetic": "NG-ung-gaa", "example": "ਅੰਗ (Ang - Body part)", "emoji": "👤"},
    "ਚ": {"roman": "Chacha", "sound": "ch", "phonetic": "CHUH-chaa", "example": "ਚੰਦ (Chand - Moon)", "emoji": "🌙"},
    "ਛ": {"roman": "Chhachha", "sound": "chh", "phonetic": "CHHUH-chhaa", "example": "ਛਤਰੀ (Chhatri - Umbrella)", "emoji": "☂️"},
    "ਜ": {"roman": "Jajja", "sound": "j", "phonetic": "JUH-jaa", "example": "ਜਹਾਜ਼ (Jahaaz - Ship)", "emoji": "🚢"},
    "ਝ": {"roman": "Jhajha", "sound": "jh", "phonetic": "JHUH-jhaa", "example": "ਝੰਡਾ (Jhanda - Flag)", "emoji": "🏳️"},
    "ਞ": {"roman": "Nyanya", "sound": "ny", "phonetic": "NYUH-nyaa", "example": "ਞਾਣ (Gyaan - Knowledge)", "emoji": "🧠"},
    "ਟ": {"roman": "Tanka", "sound": "t", "phonetic": "TUNK-kaa", "example": "ਟੋਪੀ (Topi - Hat)", "emoji": "🎩"},
    "ਠ": {"roman": "Thatha", "sound": "th", "phonetic": "THUH-thaa", "example": "ਠੰਡ (Thand - Cold)", "emoji": "🥶"},
    "ਡ": {"roman": "Dadda", "sound": "d", "phonetic": "DUH-daa", "example": "ਡਰਾਮਾ (Drama)", "emoji": "🎭"},
    "ਢ": {"roman": "Dhadha", "sound": "dh", "phonetic": "DHUH-dhaa", "example": "ਢੋਲ (Dhol - Drum)", "emoji": "🥁"},
    "ਣ": {"roman": "Nana", "sound": "n", "phonetic": "NUH-naa", "example": "ਗੁਣ (Gun - Quality)", "emoji": "⭐"},
    "ਤ": {"roman": "Tatta", "sound": "t", "phonetic": "TUH-taa", "example": "ਤਾਰਾ (Tara - Star)", "emoji": "⭐"},
    "ਥ": {"roman": "Thatha", "sound": "th", "phonetic": "THUH-thaa", "example": "ਥਾਲੀ (Thaali - Plate)", "emoji": "🍽️"},
    "ਦ": {"roman": "Dadda", "sound": "d", "phonetic": "DUH-daa", "example": "ਦਰਵਾਜ਼ਾ (Darwaza - Door)", "emoji": "🚪"},
    "ਧ": {"roman": "Dhadha", "sound": "dh", "phonetic": "DHUH-dhaa", "example": "ਧੁੱਪ (Dhoop - Sunlight)", "emoji": "☀️"},
    "ਨ": {"roman": "Nanna", "sound": "n", "phonetic": "NUH-naa", "example": "ਨਦੀ (Nadi - River)", "emoji": "🏞️"},
    "ਪ": {"roman": "Pappa", "sound": "p", "phonetic": "PUH-paa", "example": "ਪੰਛੀ (Panchhi - Bird)", "emoji": "🐦"},
    "ਫ": {"roman": "Phappha", "sound": "ph", "phonetic": "PHUH-phaa", "example": "ਫੁੱਲ (Phul - Flower)", "emoji": "🌸"},
    "ਬ": {"roman": "Babba", "sound": "b", "phonetic": "BUH-baa", "example": "ਬਿੱਲਾ (Billa - Cat)", "emoji": "🐱"},
    "ਭ": {"roman": "Bhabha", "sound": "bh", "phonetic": "BHUH-bhaa", "example": "ਭਾਲੂ (Bhaloo - Bear)", "emoji": "🐻"},
    "ਮ": {"roman": "Mamma", "sound": "m", "phonetic": "MUH-maa", "example": "ਮੱਛੀ (Machhi - Fish)", "emoji": "🐟"},
    "ਯ": {"roman": "Yayya", "sound": "y", "phonetic": "YUH-yaa", "example": "ਯੋਗ (Yog - Yoga)", "emoji": "🧘"},
    "ਰ": {"roman": "Rara", "sound": "r", "phonetic": "RUH-raa", "example": "ਰੋਟੀ (Roti - Bread)", "emoji": "🫓"},
    "ਲ": {"roman": "Lalla", "sound": "l", "phonetic": "LUH-laa", "example": "ਲੱਡੂ (Laddu - Sweet)", "emoji": "🍬"},
    "ਵ": {"roman": "Vava", "sound": "v", "phonetic": "VUH-vaa", "example": "ਵਿਆਹ (Viah - Wedding)", "emoji": "💒"},
    "ੜ": {"roman": "Rara", "sound": "r", "phonetic": "RUH-raa", "example": "ਪੜ੍ਹਨਾ (Parhna - To read)", "emoji": "📖"}
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
                           ["📖 Learn Letters", "🎯 Practice Game", "📚 Read Stories", "🏆 Quiz Challenge", "📷 Camera Practice", "🤖 AI Homework Helper"])
        
        if mode == "📖 Learn Letters":
            st.session_state.game_mode = "learn"
        elif mode == "🎯 Practice Game":
            st.session_state.game_mode = "practice"
        elif mode == "📚 Read Stories":
            st.session_state.game_mode = "stories"
        elif mode == "📷 Camera Practice":
            st.session_state.game_mode = "camera"
        elif mode == "🤖 AI Homework Helper":
            st.session_state.game_mode = "ai_helper"
        else:
            st.session_state.game_mode = "quiz"
    
    # Main content based on selected mode
    if st.session_state.game_mode == "learn":
        display_learn_mode()
    elif st.session_state.game_mode == "practice":
        display_practice_mode()
    elif st.session_state.game_mode == "stories":
        display_stories_mode()
    elif st.session_state.game_mode == "camera":
        display_camera_mode()
    elif st.session_state.game_mode == "ai_helper":
        display_ai_helper_mode()
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
    
    # Audio pronunciation with recording capability
    import os
    audio_file_path = f"audio/{current_letter}.wav"
    
    # Check if custom audio exists
    has_custom_audio = os.path.exists(audio_file_path)
    
    if has_custom_audio:
        # Play custom recorded audio
        st.markdown("### 🎵 **Custom Pronunciation Available**")
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 Play Custom Audio", use_container_width=True):
                st.success(f"🎵 Playing custom pronunciation for {letter_info['roman']}")
        with col2:
            if st.button("🗑️ Delete Custom Audio", use_container_width=True):
                os.remove(audio_file_path)
                st.success("Custom audio deleted!")
                st.rerun()
    else:
        # Recording and upload interface
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Upload audio file
            uploaded_file = st.file_uploader(
                "📁 Upload Audio", 
                type=['wav', 'mp3', 'ogg'], 
                key=f"upload_{current_letter}",
                help="Upload your recorded pronunciation"
            )
            
            if uploaded_file is not None:
                # Save uploaded file
                os.makedirs("audio", exist_ok=True)
                with open(audio_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("✅ Audio saved!")
                st.rerun()
        
        with col2:
            # Record using device microphone
            st.markdown("**🎙️ Record Audio**")
            st.components.v1.html(f"""
            <div style="text-align: center; padding: 10px;">
                <button id="recordBtn" onclick="startRecording()" 
                        style="background: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">
                    🎙️ Start Recording
                </button>
                <button id="stopBtn" onclick="stopRecording()" disabled
                        style="background: #666; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">
                    ⏹️ Stop
                </button>
                <div id="status" style="margin: 10px; font-weight: bold;"></div>
                <audio id="audioPlayback" controls style="display:none; margin: 10px;"></audio>
                <div id="downloadSection"></div>
            </div>
            
            <script>
                let mediaRecorder;
                let audioChunks = [];
                
                async function startRecording() {{
                    try {{
                        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        
                        mediaRecorder.ondataavailable = event => {{
                            audioChunks.push(event.data);
                        }};
                        
                        mediaRecorder.onstop = () => {{
                            const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                            const audioUrl = URL.createObjectURL(audioBlob);
                            const audioPlayback = document.getElementById('audioPlayback');
                            audioPlayback.src = audioUrl;
                            audioPlayback.style.display = 'block';
                            
                            // Create download link
                            const downloadSection = document.getElementById('downloadSection');
                            downloadSection.innerHTML = `
                                <a href="${{audioUrl}}" download="{current_letter}_pronunciation.wav" 
                                   style="background: #28a745; color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; display: inline-block; margin: 5px;">
                                    💾 Download Recording
                                </a>
                                <div style="font-size: 12px; color: #666; margin-top: 5px;">
                                    Download and upload above to save permanently
                                </div>
                            `;
                        }};
                        
                        mediaRecorder.start();
                        document.getElementById('recordBtn').disabled = true;
                        document.getElementById('stopBtn').disabled = false;
                        document.getElementById('status').textContent = '🔴 Recording...';
                        
                    }} catch (err) {{
                        document.getElementById('status').textContent = 'Error: ' + err.message;
                    }}
                }}
                
                function stopRecording() {{
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    document.getElementById('recordBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    document.getElementById('status').textContent = '✅ Recording complete!';
                }}
            </script>
            """, height=250)
        
        with col3:
            # TTS fallback
            if st.button("🔊 Play TTS", use_container_width=True, help="Text-to-speech pronunciation"):
                audio_text = letter_info['phonetic']
                st.components.v1.html(f"""
                <script>
                    function playSound() {{
                        if ('speechSynthesis' in window) {{
                            const utterance = new SpeechSynthesisUtterance('{audio_text}');
                            utterance.lang = 'hi-IN';
                            utterance.rate = 0.4;
                            utterance.pitch = 0.9;
                            utterance.volume = 0.9;
                            speechSynthesis.speak(utterance);
                        }}
                    }}
                    playSound();
                </script>
                """, height=0)
                st.success(f"🔊 Playing TTS: {letter_info['roman']}")
    
    st.markdown("---")
    
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

def display_camera_mode():
    """Display camera functionality for taking pictures"""
    st.markdown("## 📷 Camera Practice")
    st.markdown("Take pictures of Gurmukhi letters, handwriting, or anything related to your learning!")
    
    # Create images directory if it doesn't exist
    images_dir = "captured_images"
    os.makedirs(images_dir, exist_ok=True)
    
    # Camera input section
    st.markdown("### 📸 Take a Picture")
    
    # Camera input widget
    camera_photo = st.camera_input("Take a photo with your camera")
    
    if camera_photo is not None:
        # Display the captured image
        st.markdown("### 🖼️ Your Captured Image")
        
        # Convert to PIL Image for processing
        image = Image.open(camera_photo)
        
        # Display the image
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image, caption="Captured Image", use_column_width=True)
        
        with col2:
            st.markdown("**Image Info:**")
            st.write(f"📏 Size: {image.size[0]} x {image.size[1]} pixels")
            st.write(f"🎨 Mode: {image.mode}")
            st.write(f"📊 Format: {image.format if hasattr(image, 'format') else 'Unknown'}")
        
        # Image processing options
        st.markdown("### ⚙️ Image Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Save image option
            if st.button("💾 Save Image", use_container_width=True):
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gurmukhi_photo_{timestamp}.jpg"
                filepath = os.path.join(images_dir, filename)
                
                # Save the image
                image.save(filepath, "JPEG")
                st.success(f"✅ Image saved as {filename}")
                
                # Update session state with saved images
                if 'saved_images' not in st.session_state:
                    st.session_state.saved_images = []
                st.session_state.saved_images.append({
                    'filename': filename,
                    'filepath': filepath,
                    'timestamp': timestamp
                })
        
        with col2:
            # Rotate image
            if st.button("🔄 Rotate 90°", use_container_width=True):
                rotated_image = image.rotate(-90, expand=True)
                st.image(rotated_image, caption="Rotated Image", use_column_width=True)
        
        with col3:
            # Convert to grayscale
            if st.button("⚫ Grayscale", use_container_width=True):
                gray_image = image.convert('L')
                st.image(gray_image, caption="Grayscale Image", use_column_width=True)
    
    # Display saved images gallery
    st.markdown("---")
    st.markdown("### 🖼️ Your Photo Gallery")
    
    # Check for existing saved images
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        
        if image_files:
            st.markdown(f"📁 Found {len(image_files)} saved images")
            
            # Display images in a grid
            cols = st.columns(3)
            for i, img_file in enumerate(image_files):
                with cols[i % 3]:
                    img_path = os.path.join(images_dir, img_file)
                    try:
                        img = Image.open(img_path)
                        st.image(img, caption=img_file, use_column_width=True)
                        
                        # Delete button for each image
                        if st.button(f"🗑️ Delete", key=f"delete_{img_file}"):
                            os.remove(img_path)
                            st.success(f"Deleted {img_file}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error loading {img_file}: {str(e)}")
        else:
            st.info("📷 No images saved yet. Take your first photo above!")
    
    # Additional camera features
    st.markdown("---")
    st.markdown("### 🎯 Learning Activities with Camera")
    
    activity = st.selectbox("Choose a camera activity:", [
        "📝 Photograph handwritten Gurmukhi",
        "📖 Capture Gurmukhi text from books",
        "🎨 Take pictures of letter practice",
        "🌟 Creative Gurmukhi art photos"
    ])
    
    if activity == "📝 Photograph handwritten Gurmukhi":
        st.info("✍️ Practice writing Gurmukhi letters on paper and photograph them to track your progress!")
        
    elif activity == "📖 Capture Gurmukhi text from books":
        st.info("📚 Find Gurmukhi text in books, newspapers, or signs and capture them to practice reading!")
        
    elif activity == "🎨 Take pictures of letter practice":
        st.info("🎨 Create artistic representations of Gurmukhi letters and photograph your creativity!")
        
    else:
        st.info("🌟 Get creative! Take artistic photos that incorporate Gurmukhi letters or Punjabi culture!")
    
    # Tips section
    with st.expander("💡 Photography Tips"):
        st.markdown("""
        **📸 Tips for better photos:**
        - Ensure good lighting for clear text
        - Hold the camera steady
        - Get close enough to see letter details
        - Use a plain background for handwriting
        - Take multiple shots if needed
        
        **🎯 Learning Ideas:**
        - Photograph your daily Gurmukhi practice
        - Capture Gurmukhi signs in your community
        - Document your letter formation progress
        - Create a visual learning journal
        """)

def extract_text_from_image(image):
    """Extract text from image using OCR"""
    try:
        # Convert PIL image to numpy array for OpenCV
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get better text recognition
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(thresh, config='--psm 6')
        
        return extracted_text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def get_ai_response(question, context="", is_followup=False):
    """Get AI response for homework questions"""
    try:
        # Configure Gemini API (you'll need to set your API key)
        # genai.configure(api_key="YOUR_GEMINI_API_KEY")
        
        # For now, we'll use a mock response since API key setup is needed
        if is_followup:
            prompt = f"""
            You are a friendly AI tutor helping a student with their homework. 
            The student has a follow-up question: {question}
            
            Previous context: {context}
            
            Please provide a clear, kid-friendly explanation with examples.
            """
        else:
            prompt = f"""
            You are a friendly AI tutor helping a student with their homework.
            
            Question from image: {question}
            
            Please:
            1. Solve the problem step by step
            2. Explain each step clearly for a student
            3. Provide examples if helpful
            4. Use simple language appropriate for kids
            5. Include visual descriptions when helpful
            
            Format your response in a clear, structured way.
            """
        
        # Mock response for demonstration (replace with actual API call)
        if "rotation" in question.lower() or "coordinate" in question.lower():
            return """
            🎯 **Coordinate Geometry Solution**
            
            I can see this is about transformations! Let me solve this step by step:
            
            **Step 1: Translation**
            - Move each point left 2 and up 1
            - A(3,4) → A'(1,5)
            - B(-1,-2) → B'(-3,-1)
            
            **Step 2: Rotation 90° clockwise about C(1,3)**
            - Use formula: (x,y) → (h+(y-k), k-(x-h))
            - A'(1,5) → A''(3,3)
            - B'(-3,-1) → B''(-3,7)
            
            **Why this works:**
            - Rotation swaps and flips coordinates
            - Think of turning a clock hand 90° clockwise
            
            **Final Answer:** A''(3,3), B''(-3,7)
            
            💡 **Need help understanding any step? Just ask!**
            """
        else:
            return f"""
            📚 **AI Homework Helper**
            
            I can see your question: "{question}"
            
            Let me help you solve this step by step:
            
            1. **Understanding the problem:** [Analysis of what's being asked]
            2. **Solution approach:** [Method to solve]
            3. **Step-by-step solution:** [Detailed steps]
            4. **Final answer:** [Clear result]
            
            💡 **Want me to explain any part differently? Just ask a follow-up question!**
            """
            
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again!"

def display_ai_helper_mode():
    """Display AI-powered homework helper"""
    st.markdown("## 🤖 AI Homework Helper")
    st.markdown("Upload a photo of your homework question and get detailed explanations!")
    
    # Initialize session state for chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_question_context' not in st.session_state:
        st.session_state.current_question_context = ""
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📷 Camera Upload", "📁 File Upload"])
    
    with tab1:
        st.markdown("### 📸 Take a Photo of Your Question")
        camera_photo = st.camera_input("Capture your homework question")
        
        if camera_photo is not None:
            process_homework_image(camera_photo)
    
    with tab2:
        st.markdown("### 📁 Upload Question Image")
        uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Upload a clear photo of your homework question"
        )
        
        if uploaded_file is not None:
            process_homework_image(uploaded_file)
    
    # Chat interface for follow-up questions
    display_chat_interface()
    
    # Tips section
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        **📸 Photo Tips:**
        - Ensure good lighting
        - Keep text clear and readable
        - Avoid shadows on the paper
        - Take photo straight-on (not at an angle)
        
        **📚 Question Types I Can Help With:**
        - Math problems (algebra, geometry, calculus)
        - Science questions (physics, chemistry, biology)
        - English grammar and writing
        - History and social studies
        - And much more!
        
        **🤔 Follow-up Questions:**
        - "Can you explain step 2 differently?"
        - "Why did we use this formula?"
        - "Can you give me another example?"
        - "What if the numbers were different?"
        """)

def process_homework_image(image_file):
    """Process uploaded homework image and extract question"""
    try:
        # Display the uploaded image
        image = Image.open(image_file)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image, caption="Your Question", use_column_width=True)
        
        with col2:
            st.markdown("**Processing...**")
            
            # Extract text from image
            with st.spinner("🔍 Reading your question..."):
                extracted_text = extract_text_from_image(image)
            
            if extracted_text and len(extracted_text.strip()) > 0:
                st.success("✅ Text extracted!")
                
                # Show extracted text
                with st.expander("📝 Extracted Text"):
                    st.text_area("Detected text:", extracted_text, height=100)
                
                # Get AI response
                if st.button("🤖 Get AI Help", use_container_width=True):
                    with st.spinner("🧠 Analyzing your question..."):
                        ai_response = get_ai_response(extracted_text)
                        
                        # Store in session state
                        st.session_state.current_question_context = extracted_text
                        st.session_state.chat_history.append({
                            'type': 'question',
                            'content': extracted_text,
                            'timestamp': datetime.now().strftime("%H:%M")
                        })
                        st.session_state.chat_history.append({
                            'type': 'answer',
                            'content': ai_response,
                            'timestamp': datetime.now().strftime("%H:%M")
                        })
                        
                        st.rerun()
            else:
                st.warning("⚠️ Could not extract text from image. Please ensure the text is clear and try again.")
                
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")

def display_chat_interface():
    """Display chat interface for follow-up questions"""
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 💬 Question & Answer Session")
        
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            if message['type'] == 'question':
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <strong>🙋 Your Question ({message['timestamp']}):</strong><br>
                    {message['content'][:200]}{'...' if len(message['content']) > 200 else ''}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #f1f8e9; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <strong>🤖 AI Tutor ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Follow-up question input
        st.markdown("### 🤔 Have a Follow-up Question?")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            followup_question = st.text_input(
                "Ask anything about the solution above:",
                placeholder="e.g., 'Why did we use this formula?' or 'Can you explain step 2 again?'",
                key="followup_input"
            )
        
        with col2:
            if st.button("Ask 🚀", use_container_width=True):
                if followup_question.strip():
                    # Get AI response for follow-up
                    with st.spinner("🤖 Thinking..."):
                        followup_response = get_ai_response(
                            followup_question, 
                            st.session_state.current_question_context, 
                            is_followup=True
                        )
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            'type': 'question',
                            'content': followup_question,
                            'timestamp': datetime.now().strftime("%H:%M")
                        })
                        st.session_state.chat_history.append({
                            'type': 'answer',
                            'content': followup_response,
                            'timestamp': datetime.now().strftime("%H:%M")
                        })
                        
                        st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.current_question_context = ""
            st.rerun()

if __name__ == "__main__":
    main()
