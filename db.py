import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vocab.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chinese TEXT NOT NULL,
        pinyin TEXT NOT NULL,
        english TEXT NOT NULL,
        malay TEXT DEFAULT '',
        pos TEXT DEFAULT '',
        example_zh TEXT DEFAULT '',
        example_en TEXT DEFAULT '',
        example_ms TEXT DEFAULT '',
        hsk INTEGER DEFAULT 1,
        note TEXT DEFAULT '',
        mastered INTEGER DEFAULT 0,
        review_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # Migration: check and add missing columns for existing databases
    cursor.execute("PRAGMA table_info(vocabulary)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "malay" not in columns:
        try:
            cursor.execute("ALTER TABLE vocabulary ADD COLUMN malay TEXT DEFAULT ''")
            conn.commit()
        except Exception:
            pass
    if "example_ms" not in columns:
        try:
            cursor.execute("ALTER TABLE vocabulary ADD COLUMN example_ms TEXT DEFAULT ''")
            conn.commit()
        except Exception:
            pass

    # Pre-populate sample starter vocabulary if empty
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_cards = [
            ("你好", "nǐ hǎo", "hello; hi", "helo; hai; salam", "interjection", "你好！很高兴认识你。", "Hello! Nice to meet you.", "Helo! Gembira berkenalan dengan anda.", 1, "Polite greeting"),
            ("学习", "xué xí", "to study; to learn", "belajar", "verb", "学习新语言很有趣。", "Learning a new language is very interesting.", "Belajar bahasa baharu sangat menyeronokkan.", 1, "Essential verb"),
            ("学生", "xué sheng", "student; pupil", "murid; pelajar", "noun", "我们都是中文系的学生。", "We are all students in the Chinese department.", "Kami semua ialah pelajar jabatan bahasa Cina.", 1, "Noun: student"),
            ("老师", "lǎo shī", "teacher", "cikgu; guru", "noun", "王老师是我们的英语老师。", "Teacher Wang is our English teacher.", "Cikgu Wang ialah guru bahasa Inggeris kami.", 1, "Respectful title"),
            ("翻译", "fān yì", "to translate; translation", "terjemah; terjemahan", "verb/noun", "请把这句话翻译成英文。", "Please translate this sentence into English.", "Sila terjemahkan ayat ini ke bahasa Inggeris.", 4, "Translate"),
            ("学校", "xué xiào", "school", "sekolah", "noun", "我们学校很大，环境也很美。", "Our school is very large and the environment is beautiful.", "Sekolah kami sangat besar dan persekitarannya indah.", 1, "Noun: school"),
            ("谢谢", "xiè xie", "thank you; thanks", "terima kasih", "verb", "谢谢你的帮助！", "Thank you for your help!", "Terima kasih atas bantuan anda!", 1, "Thanks")
        ]
        cursor.executemany("""
        INSERT INTO vocabulary (chinese, pinyin, english, malay, pos, example_zh, example_en, example_ms, hsk, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_cards)
        conn.commit()

    conn.close()

def get_all_vocab():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vocabulary ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def add_vocab(chinese, pinyin, english, malay="", pos="", example_zh="", example_en="", example_ms="", hsk=1, note=""):
    conn = get_db()
    cursor = conn.cursor()
    # Check if word already exists to avoid duplicates
    cursor.execute("SELECT id FROM vocabulary WHERE chinese = ? OR english = ? OR (malay != '' AND malay = ?)", (chinese, english, malay))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
        UPDATE vocabulary 
        SET pinyin = ?, english = ?, malay = ?, pos = ?, example_zh = ?, example_en = ?, example_ms = ?, hsk = ?, note = ?
        WHERE id = ?
        """, (pinyin, english, malay, pos, example_zh, example_en, example_ms, hsk, note, existing["id"]))
        word_id = existing["id"]
    else:
        cursor.execute("""
        INSERT INTO vocabulary (chinese, pinyin, english, malay, pos, example_zh, example_en, example_ms, hsk, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (chinese, pinyin, english, malay, pos, example_zh, example_en, example_ms, hsk, note))
        word_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return word_id

def delete_vocab(vocab_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vocabulary WHERE id = ?", (vocab_id,))
    conn.commit()
    conn.close()

def toggle_mastered(vocab_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE vocabulary SET mastered = CASE WHEN mastered = 1 THEN 0 ELSE 1 END WHERE id = ?", (vocab_id,))
    conn.commit()
    cursor.execute("SELECT mastered FROM vocabulary WHERE id = ?", (vocab_id,))
    row = cursor.fetchone()
    conn.close()
    return row["mastered"] if row else 0

def increment_review(vocab_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE vocabulary SET review_count = review_count + 1 WHERE id = ?", (vocab_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and migrated with Malay columns successfully.")
