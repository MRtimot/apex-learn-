# Apex Learn (三语学堂) 🎓
### Trilingual English ⇄ 简体中文 ⇄ Bahasa Melayu Student Learning Hub

A modern, student-focused educational web application designed for students learning in multilingual environments (such as Malaysia, Singapore, and Southeast Asia). It provides seamless multi-directional translation, **Pinyin with tone marks and tone colors**, **native Text-to-Speech audio pronunciation for English, Chinese, and Malay**, **trilingual word-by-word breakdowns**, an interactive **Trilingual Word Bank**, **3D flashcards**, a **practice quiz mode**, and a **Grammar & Tatabahasa guide**.

---

## ✨ Features

1. **Multi-Directional Trilingual Translation**
   - Translate freely between **English (🇺🇸)**, **简体中文 (🇨🇳)**, and **Bahasa Melayu (🇲🇾)**.
   - Quick 1-click pairing shortcuts:
     - `EN ➔ 中文` & `中文 ➔ EN`
     - `EN ➔ Melayu` & `Melayu ➔ EN`
     - `中文 ➔ Melayu` & `Melayu ➔ 中文`
   - Real-time debounced **⚡ Auto-Translation** (translates automatically as you type or paste).
   - Dynamic language auto-detection for all three languages.

2. **Pinyin with Tone Marks & Tone Colors**
   - Renders Pinyin ruby annotations above Chinese characters.
   - Tone color coding:
     - 🔵 **1st Tone (High Flat: ā)** - Blue
     - 🟢 **2nd Tone (Rising: á)** - Green
     - 🟠 **3rd Tone (Falling-Rising: ǎ)** - Amber/Orange
     - 🔴 **4th Tone (Falling: à)** - Red
     - ⚪ **Neutral Tone (Light: a)** - Slate
   - Tone color toggle to suit learner preference.

3. **Native Text-to-Speech (Pronunciation Audio)**
   - Pronunciation support for **Mandarin Chinese (`zh-CN`)**, **English (`en-US`)**, and **Bahasa Melayu (`ms-MY` / `id-ID`)**.
   - Dual audio buttons: listen to translations and original text independently.
   - Learning speed controls: **1.0x (Normal)**, **0.75x (Learning pace)**, and **0.5x (Slow practice)**.

4. **Trilingual Word-by-Word Breakdown**
   - Breaks translated sentences into vocabulary cards displaying:
     - Chinese Character
     - Pinyin with tone marks
     - English definition
     - Bahasa Melayu definition (🇲🇾)
     - Part of speech & HSK level
   - Click any card for the detailed word modal and one-click save.

5. **Trilingual Word Bank (生词本 - Persistent SQLite Storage)**
   - Stored in `data/vocab.db` with support for Chinese, Pinyin, English, and Bahasa Melayu.
   - Search across all three languages.
   - Add your own custom words with the **➕ Add Word (Tambah Perkataan)** modal.
   - Mark words as **Mastered (✓)** or **Needs Review (⏳)**.

6. **3D Trilingual Flashcards**
   - Front: Chinese character + audio + optional Pinyin hide/show toggle.
   - Back: English definition, Bahasa Melayu definition, example sentences in all three languages, and individual audio buttons for Chinese, English, and Malay.
   - Shuffle deck and track mastery progress (% mastered).

7. **Interactive Practice Quiz Mode**
   - Customizable quiz modes:
     - 🌐 **Trilingual Mix**
     - 🇨🇳 ⇄ 🇲🇾 **Cina - Melayu**
     - 🇨🇳 ⇄ 🇺🇸 **Chinese - English**
     - 🇺🇸 ⇄ 🇲🇾 **English - Melayu**
   - Tests meaning match, pinyin recognition, and reverse translations.
   - Instant explanations in both languages, streak counter (🔥), and score cards.

8. **Bilingual Grammar & Tatabahasa Guide**
   - **Chinese Grammar**: SVO word order, Time-Before-Verb rule, Measure Words (量词), the three "De"s (的/得/地), aspect marker 了, and 把-sentences.
   - **Tatabahasa Melayu**:
     - *Hukum D-M (Diterangkan - Menerangkan)*: Nouns come before adjectives (*kereta merah*, not *merah kereta*).
     - *Imbuhan Awalan*: Prefixes *meN-*, *ber-*, *peN-*, *ter-* modifying root words (*kata dasar*).
     - *Kata Sendi Nama*: *Dari* (ATM: Arah, Tempat, Masa) vs *Daripada* (Orang, Perbandingan, Asal).
     - *Penjodoh Bilangan*: Classifiers (*sebuah*, *seorang*, *sebatang*, *sehelai*, *seekor*).
     - *Simpulan Bahasa*: Student idioms (*ulat buku*, *ringan tulang*, *berat mulut*).

9. **Optional Gemini AI Integration**
   - Add a Google Gemini API key via the ⚙️ settings modal for high-grade contextual translations and detailed grammatical breakdowns.

---

## 🚀 Quick Start

### 1. Launch the Server
```bash
python3 server.py
```

### 2. Open in Your Browser
Navigate to:
```
http://localhost:8000
```

---

## 📁 Project Architecture

```
├── server.py              # Lightweight Python HTTP server & REST API
├── translator.py          # Trilingual translation engine, Pinyin generator & Tatabahasa analyzer
├── db.py                  # SQLite database manager with trilingual schema
├── data/
│   ├── vocab.db           # Persistent SQLite database with Chinese, English & Malay columns
│   ├── dictionary.json    # Curated trilingual student dictionary with examples & HSK levels
│   ├── pinyin_dict.json   # Character-to-pinyin lookup table with tones
│   └── grammar_notes.json # Chinese grammar & Malay Tatabahasa rules
├── static/
│   ├── index.html         # Main trilingual study interface
│   ├── css/style.css      # Custom styling, tone colors, ruby layout, 3D flip card
│   └── js/
│       ├── app.js         # Core application logic, event listeners, view tabs
│       ├── pinyin.js      # Tone mark generator & colorizer
│       ├── speech.js      # Web Speech API wrapper with Malay, Chinese & English voices
│       └── flashcards.js  # 3D Flashcard deck controller & interactive quiz engine
└── README.md              # Documentation and guide
```

---

## 🛠️ Requirements
- Python 3.8+ (Zero external pip packages needed! Runs entirely on Python's built-in standard library).
- Any modern web browser (Chrome, Edge, Safari, Firefox).
