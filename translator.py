import json
import os
import re
import urllib.parse
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Load dictionary & pinyin
try:
    with open(os.path.join(DATA_DIR, "dictionary.json"), "r", encoding="utf-8") as f:
        VOCAB_LIST = json.load(f)
except Exception:
    VOCAB_LIST = []

try:
    with open(os.path.join(DATA_DIR, "pinyin_dict.json"), "r", encoding="utf-8") as f:
        PINYIN_MAP = json.load(f)
except Exception:
    PINYIN_MAP = {}

try:
    with open(os.path.join(DATA_DIR, "grammar_notes.json"), "r", encoding="utf-8") as f:
        GRAMMAR_RULES = json.load(f)
except Exception:
    GRAMMAR_RULES = []

# Quick lookups
ZH_TO_ENTRY = {item["zh"]: item for item in VOCAB_LIST}
EN_TO_ENTRY = {}
MS_TO_ENTRY = {}

for item in VOCAB_LIST:
    # index english keywords
    en_words = re.findall(r"[a-zA-Z]+", item.get("en", "").lower())
    for w in en_words:
        if len(w) > 2 and w not in EN_TO_ENTRY:
            EN_TO_ENTRY[w] = item
            
    # index malay keywords
    ms_words = re.findall(r"[a-zA-Z]+", item.get("ms", "").lower())
    for w in ms_words:
        if len(w) > 2 and w not in MS_TO_ENTRY:
            MS_TO_ENTRY[w] = item

# Common Malay indicator words
MALAY_KEYWORDS = {
    "yang", "di", "dan", "ini", "itu", "untuk", "tidak", "saya", "kamu", "dia",
    "mereka", "kami", "dengan", "ada", "ke", "dari", "daripada", "pada", "oleh",
    "seorang", "sebuah", "murid", "pelajar", "guru", "cikgu", "sekolah", "buku",
    "belajar", "terima", "kasih", "sama", "selamat", "pagi", "petang", "malam",
    "soalan", "peperiksaan", "latihan", "tatabahasa", "bahasa", "melayu", "membaca",
    "menulis", "gembira", "anda", "ialah", "adalah", "awak", "bagaimana", "mengapa",
    "kenapa", "siapa", "bila", "apa", "berapa", "rajin", "pandai", "karangan"
}

def is_chinese(text):
    return any("\u4e00" <= char <= "\u9fff" for char in text)

def is_malay(text):
    if is_chinese(text):
        return False
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if not words:
        return False
    match_count = sum(1 for w in words if w in MALAY_KEYWORDS)
    return match_count >= 1 and (match_count / max(len(words), 1)) >= 0.2

def get_char_pinyin(char):
    if char in PINYIN_MAP:
        return PINYIN_MAP[char]["py"], PINYIN_MAP[char]["tone"]
    return "", 5

def text_to_pinyin(zh_text):
    """Converts Chinese text to pinyin string and word tokens."""
    i = 0
    pinyin_tokens = []
    sorted_words = sorted(ZH_TO_ENTRY.keys(), key=len, reverse=True)
    
    while i < len(zh_text):
        matched = False
        for word in sorted_words:
            if zh_text[i:].startswith(word):
                entry = ZH_TO_ENTRY[word]
                pinyin_tokens.append({
                    "char": word,
                    "pinyin": entry["py"],
                    "tone": 1,
                    "english": entry.get("en", ""),
                    "malay": entry.get("ms", ""),
                    "pos": entry.get("pos", ""),
                    "hsk": entry.get("hsk", 1),
                    "note": entry.get("note", ""),
                    "example_zh": entry.get("ex_zh", ""),
                    "example_en": entry.get("ex_en", ""),
                    "example_ms": entry.get("ex_ms", "")
                })
                i += len(word)
                matched = True
                break
        
        if not matched:
            char = zh_text[i]
            if "\u4e00" <= char <= "\u9fff":
                py, tone = get_char_pinyin(char)
                pinyin_tokens.append({
                    "char": char,
                    "pinyin": py if py else "",
                    "tone": tone,
                    "english": "",
                    "malay": "",
                    "pos": "character",
                    "hsk": 1,
                    "note": ""
                })
            else:
                pinyin_tokens.append({
                    "char": char,
                    "pinyin": "",
                    "tone": 5,
                    "english": "",
                    "malay": "",
                    "pos": "punct",
                    "hsk": 0
                })
            i += 1
            
    pinyin_str = " ".join([t["pinyin"] for t in pinyin_tokens if t["pinyin"]])
    return pinyin_str, pinyin_tokens

def detect_grammar_tips(zh_text="", en_text="", ms_text=""):
    """Detect applicable grammar tips for students based on Chinese and Malay keywords."""
    tips = []
    combined = f"{zh_text} {en_text} {ms_text}".lower()
    
    # Chinese Grammar Tips
    if "了" in zh_text:
        tips.append({
            "point": "Aspect Marker '了' (le)",
            "explanation": "'了' indicates completion of an action or a change in state, rather than a past tense.",
            "rule": "Subject + Verb + 了 + Object"
        })
    if "把" in zh_text:
        tips.append({
            "point": "把 Construction (Disposal Form)",
            "explanation": "Used when an action affects a specific object and produces a result.",
            "rule": "Subject + 把 + Object + Verb + Other Element"
        })
    if any(k in zh_text for k in ["的", "得", "地"]):
        tips.append({
            "point": "The Three 'De's: 的, 得, 地",
            "explanation": "• 的 (de) + Noun (possessive/description: 我的书)\n• Verb + 得 (de) + Degree/Manner (跑得很快)\n• Adverb + 地 (de) + Verb (认真地学习)",
            "rule": "我的书 (Noun) | 跑得很快 (Manner) | 认真地学习 (Action)"
        })
    time_words = ["今天", "明天", "昨天", "上午", "下午", "晚上", "现在", "周末", "下周"]
    if any(tw in zh_text for tw in time_words):
        tips.append({
            "point": "Time Before Verb Rule (Chinese)",
            "explanation": "In Chinese, time expressions appear BEFORE the verb. In English and Malay, time can be placed at the end ('I study at 8 AM' / 'Saya belajar pada pukul 8').",
            "rule": "Subject + [Time] + [Place] + Verb + Object"
        })
        
    # Malay Grammar Tips (Tatabahasa & Imbuhan)
    if "dari" in combined or "daripada" in combined:
        tips.append({
            "point": "Tatabahasa: 'Dari' vs 'Daripada'",
            "explanation": "• DARI is used strictly for ATM: Arah (direction), Tempat (place), Masa (time).\n• DARIPADA is used for People, Comparisons, Origin/Material, and Sources.",
            "rule": "Dari sekolah (Tempat) | Dari pukul 8 (Masa) | Daripada cikgu (Orang)"
        })
    if any(k in combined for k in ["sebuah", "seorang", "sebatang", "seekor", "sehelai"]):
        tips.append({
            "point": "Penjodoh Bilangan (Malay Classifiers / 量词)",
            "explanation": "Like Chinese measure words (量词), Malay requires Penjodoh Bilangan before nouns: sebuah buku (一本), seorang guru (一位老师), sebatang pen (一支笔).",
            "rule": "Bilangan + [Penjodoh Bilangan] + Kata Nama"
        })
    if any(k in combined for k in ["ulat buku", "ringan tulang", "berat mulut"]):
        tips.append({
            "point": "Simpulan Bahasa (Malay Idioms)",
            "explanation": "• ulat buku = bookworm (gemar membaca buku)\n• ringan tulang = hardworking / diligent (rajin bekerja)\n• berat mulut = quiet / shy (pendiam)",
            "rule": "Simpulan Bahasa mencerminkan nilai murni dalam bahasa Melayu."
        })
    if any(w.startswith("me") or w.startswith("ber") or w.startswith("pe") for w in re.findall(r"[a-zA-Z]+", ms_text.lower())):
        tips.append({
            "point": "Hukum D-M (Diterangkan - Menerangkan)",
            "explanation": "In Malay, adjectives follow nouns (D-M rule): 'kereta merah' (red car), 'murid rajin' (diligent student). In English & Chinese, adjectives come before nouns!",
            "rule": "Kata Nama (D) + Penerang/Kata Adjektif (M)"
        })
        
    return tips

# Phrase dictionaries for student fallback
STUDENT_PHRASES = {
    # English -> (Chinese, Malay)
    "how are you today": ("你今天好吗", "apa khabar anda hari ini"),
    "how are you": ("你好吗", "apa khabar"),
    "good morning": ("早上好", "selamat pagi"),
    "good afternoon": ("下午好", "selamat petang"),
    "good evening": ("晚上好", "selamat malam"),
    "nice to meet you": ("很高兴认识你", "gembira dapat berkenalan dengan anda"),
    "thank you very much": ("非常感谢你", "terima kasih banyak-banyak"),
    "thank you": ("谢谢你", "terima kasih"),
    "you are welcome": ("不客气", "sama-sama"),
    "see you tomorrow": ("明天见", "jumpa lagi esok"),
    "see you later": ("待会儿见", "jumpa lagi nanti"),
    "goodbye": ("再见", "selamat tinggal"),
    "what is your name": ("你叫什么名字", "siapakah nama anda"),
    "where is the library": ("图书馆在哪里", "di manakah perpustakaan"),
    "excuse me": ("请问", "tumpang tanya; maaf"),
    "i am sorry": ("对不起", "minta maaf; saya minta maaf"),
    "it doesn't matter": ("没关系", "tidak mengapa; tak apa"),
    "i want to learn chinese": ("我想学习中文", "saya ingin belajar bahasa Cina"),
    "i want to study": ("我想学习", "saya mahu belajar"),
    "take an exam": ("参加考试", "menduduki peperiksaan"),
    "have an exam": ("有一场考试", "ada peperiksaan"),
    "do homework": ("做作业", "buat kerja rumah"),
    "in the classroom": ("在教室里", "di dalam bilik darjah"),
    "in the library": ("在图书馆里", "di dalam perpustakaan")
}

def translate_mymemory(text, source_lang, target_lang):
    """Query free MyMemory Translation API with timeout."""
    try:
        s = "zh-CN" if source_lang == "zh" else source_lang
        t = "zh-CN" if target_lang == "zh" else target_lang
        lang_pair = f"{s}|{t}"
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair={lang_pair}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StudentTrilingualLearningApp/2.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data and "responseData" in data and "translatedText" in data["responseData"]:
                res = data["responseData"]["translatedText"]
                if res and not res.startswith("MYMEMORY WARNING"):
                    return res
    except Exception:
        pass
    return None

def translate_offline_fallback(text, source_lang, target_lang):
    """Intelligent trilingual fallback across English, Chinese, and Malay."""
    clean_text = text.strip()
    clean_lower = clean_text.lower()
    
    # 1. Direct dictionary match
    if source_lang == "zh":
        if clean_text in ZH_TO_ENTRY:
            entry = ZH_TO_ENTRY[clean_text]
            return entry.get("ms", "") if target_lang == "ms" else entry.get("en", "")
    elif source_lang == "en":
        for item in VOCAB_LIST:
            en_val = item.get("en", "").lower()
            if clean_lower == en_val or clean_lower in [x.strip() for x in en_val.split(";")]:
                return item.get("ms", "") if target_lang == "ms" else item["zh"]
    elif source_lang == "ms":
        for item in VOCAB_LIST:
            ms_val = item.get("ms", "").lower()
            if clean_lower == ms_val or clean_lower in [x.strip() for x in ms_val.split(";")]:
                return item.get("en", "") if target_lang == "en" else item["zh"]

    # 2. Phrase matching
    for phrase_en, (zh_trans, ms_trans) in STUDENT_PHRASES.items():
        if source_lang == "en" and phrase_en in clean_lower:
            return ms_trans if target_lang == "ms" else zh_trans
        if source_lang == "zh" and zh_trans in clean_text:
            return ms_trans if target_lang == "ms" else phrase_en
        if source_lang == "ms" and ms_trans in clean_lower:
            return zh_trans if target_lang == "zh" else phrase_en

    # 3. Word token replacement
    if source_lang == "zh":
        tokens = []
        i = 0
        sorted_words = sorted(ZH_TO_ENTRY.keys(), key=len, reverse=True)
        while i < len(clean_text):
            matched = False
            for w in sorted_words:
                if clean_text[i:].startswith(w):
                    entry = ZH_TO_ENTRY[w]
                    meaning = entry.get("ms", "").split(";")[0].strip() if target_lang == "ms" else entry.get("en", "").split(";")[0].strip()
                    tokens.append(meaning if meaning else w)
                    i += len(w)
                    matched = True
                    break
            if not matched:
                c = clean_text[i]
                if c in ZH_TO_ENTRY:
                    entry = ZH_TO_ENTRY[c]
                    m = entry.get("ms", "").split(";")[0].strip() if target_lang == "ms" else entry.get("en", "").split(";")[0].strip()
                    tokens.append(m)
                elif re.match(r"[a-zA-Z0-9\s.,!?'\"]", c):
                    tokens.append(c)
                i += 1
        return " ".join([t for t in tokens if t])

    elif source_lang in ["en", "ms"]:
        words = re.findall(r"[a-zA-Z0-9']+|[^\w\s]", clean_text)
        translated_tokens = []
        for w in words:
            w_lower = w.lower()
            if target_lang == "zh":
                if w_lower in EN_TO_ENTRY:
                    translated_tokens.append(EN_TO_ENTRY[w_lower]["zh"])
                elif w_lower in MS_TO_ENTRY:
                    translated_tokens.append(MS_TO_ENTRY[w_lower]["zh"])
                else:
                    # Common student words
                    common_map_zh = {
                        "hello": "你好", "helo": "你好", "hai": "嗨", "hi": "嗨",
                        "terima": "谢谢", "kasih": "", "thank": "谢谢", "thanks": "谢谢",
                        "cikgu": "老师", "guru": "老师", "teacher": "老师",
                        "murid": "学生", "pelajar": "学生", "student": "学生", "students": "学生们",
                        "sekolah": "学校", "school": "学校", "kelas": "教室", "classroom": "教室",
                        "perpustakaan": "图书馆", "library": "图书馆", "buku": "书", "book": "书",
                        "belajar": "学习", "study": "学习", "peperiksaan": "考试", "exam": "考试",
                        "ujian": "考试", "kerja": "作业", "rumah": "", "homework": "作业",
                        "selamat": "好", "pagi": "早上", "petang": "下午", "malam": "晚上",
                        "saya": "我", "i": "我", "awak": "你", "anda": "你", "you": "你",
                        "dia": "他", "he": "他", "she": "她", "mereka": "他们", "they": "他们",
                        "kami": "我们", "we": "我们", "kawan": "朋友", "friend": "朋友",
                        "kosa": "词汇", "kata": "词汇", "tatabahasa": "语法", "grammar": "语法"
                    }
                    translated_tokens.append(common_map_zh.get(w_lower, w))
            elif target_lang == "ms":
                common_map_ms = {
                    "hello": "helo", "hi": "hai", "thank": "terima", "thanks": "terima kasih",
                    "teacher": "cikgu", "student": "murid", "students": "murid-murid",
                    "school": "sekolah", "classroom": "bilik darjah", "library": "perpustakaan",
                    "book": "buku", "books": "buku-buku", "homework": "kerja rumah", "exam": "peperiksaan",
                    "study": "belajar", "learn": "belajar", "chinese": "bahasa Cina", "english": "bahasa Inggeris",
                    "good": "baik", "morning": "pagi", "today": "hari ini", "tomorrow": "esok",
                    "yesterday": "semalam", "like": "suka", "i": "saya", "you": "anda",
                    "we": "kami", "they": "mereka", "he": "dia", "she": "dia", "friend": "kawan"
                }
                translated_tokens.append(common_map_ms.get(w_lower, w) + " ")
            else: # target_lang == 'en'
                common_map_en = {
                    "helo": "hello", "hai": "hi", "cikgu": "teacher", "guru": "teacher",
                    "murid": "student", "pelajar": "student", "sekolah": "school",
                    "buku": "book", "belajar": "study", "peperiksaan": "exam", "ujian": "test",
                    "perpustakaan": "library", "saya": "I", "anda": "you", "awak": "you",
                    "mereka": "they", "kami": "we", "kawan": "friend", "terima": "thank",
                    "kasih": "you", "pagi": "morning", "hari": "day", "esok": "tomorrow"
                }
                translated_tokens.append(common_map_en.get(w_lower, w) + " ")
                
        return "".join(translated_tokens).strip()

    return clean_text

def translate(text, source_lang="auto", target_lang="auto"):
    """Main translation orchestrator supporting English, Chinese, and Malay."""
    text = text.strip()
    if not text:
        return {"translatedText": "", "pinyin": "", "breakdown": [], "grammarTips": []}

    # Auto detect source if auto
    if source_lang == "auto":
        if is_chinese(text):
            source_lang = "zh"
        elif is_malay(text):
            source_lang = "ms"
        else:
            source_lang = "en"

    # Default target based on source
    if target_lang == "auto":
        if source_lang == "zh":
            target_lang = "en"
        elif source_lang == "ms":
            target_lang = "zh"
        else:
            target_lang = "zh"

    # Perform translation (online API first, fallback to offline)
    translated = translate_mymemory(text, source_lang, target_lang)
    if not translated:
        translated = translate_offline_fallback(text, source_lang, target_lang)

    # Determine Chinese portion for pinyin ruby tags
    zh_text = ""
    if source_lang == "zh":
        zh_text = text
    elif target_lang == "zh":
        zh_text = translated
    elif is_chinese(translated):
        zh_text = translated

    en_text = text if source_lang == "en" else (translated if target_lang == "en" else "")
    ms_text = text if source_lang == "ms" else (translated if target_lang == "ms" else "")

    pinyin_str, breakdown = text_to_pinyin(zh_text) if zh_text else ("", [])
    grammar_tips = detect_grammar_tips(zh_text, en_text, ms_text)

    return {
        "sourceLang": source_lang,
        "targetLang": target_lang,
        "originalText": text,
        "translatedText": translated,
        "pinyin": pinyin_str,
        "breakdown": breakdown,
        "grammarTips": grammar_tips
    }

if __name__ == "__main__":
    print("Testing Trilingual Translation:")
    t1 = translate("Selamat pagi cikgu! Saya ingin belajar bahasa Cina.", "ms", "zh")
    print("MS -> ZH:", json.dumps(t1, ensure_ascii=False, indent=2))

    t2 = translate("Tomorrow we will go to the library to read books.", "en", "ms")
    print("EN -> MS:", json.dumps(t2, ensure_ascii=False, indent=2))
