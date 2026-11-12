import json
import os

vocab_list = [
    # HSK 1 Core Basics & School (Trilingual: Chinese, English, Malay)
    {
        "zh": "你好", "py": "nǐ hǎo", "en": "hello; hi", "ms": "helo; hai; salam",
        "pos": "interjection", "hsk": 1, "note": "Standard polite greeting",
        "ex_zh": "你好！很高兴认识你。", "ex_en": "Hello! Nice to meet you.", "ex_ms": "Helo! Gembira dapat berkenalan dengan anda."
    },
    {
        "zh": "谢谢", "py": "xiè xie", "en": "thank you; thanks", "ms": "terima kasih",
        "pos": "verb", "hsk": 1, "note": "Universal expression of gratitude",
        "ex_zh": "谢谢你的帮助！", "ex_en": "Thank you for your help!", "ex_ms": "Terima kasih atas bantuan anda!"
    },
    {
        "zh": "不客气", "py": "bú kè qi", "en": "you are welcome", "ms": "sama-sama",
        "pos": "phrase", "hsk": 1, "note": "Polite response to '谢谢' / 'Terima kasih'",
        "ex_zh": "不客气，这是我应该做的。", "ex_en": "You're welcome, it's my pleasure.", "ex_ms": "Sama-sama, ini tanggungjawab saya."
    },
    {
        "zh": "再见", "py": "zài jiàn", "en": "goodbye; see you again", "ms": "selamat tinggal; jumpa lagi",
        "pos": "verb", "hsk": 1, "note": "Literally: again see / jumpa lagi",
        "ex_zh": "明天见，再见！", "ex_en": "See you tomorrow, goodbye!", "ex_ms": "Jumpa esok, selamat tinggal!"
    },
    {
        "zh": "老师", "py": "lǎo shī", "en": "teacher", "ms": "cikgu; guru",
        "pos": "noun", "hsk": 1, "note": "Measure word: 位 (wèi) / seorang guru",
        "ex_zh": "王老师是我们的英语老师。", "ex_en": "Teacher Wang is our English teacher.", "ex_ms": "Cikgu Wang ialah guru bahasa Inggeris kami."
    },
    {
        "zh": "学生", "py": "xué sheng", "en": "student; pupil", "ms": "murid; pelajar",
        "pos": "noun", "hsk": 1, "note": "Measure word: 个 (gè) / seorang murid",
        "ex_zh": "他们都是大学一年级的学生。", "ex_en": "They are all first-year university students.", "ex_ms": "Mereka semua ialah pelajar tahun satu universiti."
    },
    {
        "zh": "朋友", "py": "péng you", "en": "friend", "ms": "kawan; sahabat",
        "pos": "noun", "hsk": 1, "note": "好朋友 = best friend / kawan baik",
        "ex_zh": "他是我的好朋友。", "ex_en": "He is my good friend.", "ex_ms": "Dia ialah kawan baik saya."
    },
    {
        "zh": "同学", "py": "tóng xué", "en": "classmate; schoolmate", "ms": "rakan sekelas",
        "pos": "noun", "hsk": 1, "note": "同 = same, 学 = study",
        "ex_zh": "我们在同一所学校，是老同学。", "ex_en": "We are at the same school; we are old classmates.", "ex_ms": "Kami di sekolah yang sama, kami rakan sekelas lama."
    },
    {
        "zh": "学校", "py": "xué xiào", "en": "school", "ms": "sekolah",
        "pos": "noun", "hsk": 1, "note": "Measure word: 所 (suǒ) / sebuah sekolah",
        "ex_zh": "我们学校很大，环境也很美。", "ex_en": "Our school is very large and the environment is beautiful.", "ex_ms": "Sekolah kami sangat besar dan persekitarannya cantik."
    },
    {
        "zh": "教室", "py": "jiào shì", "en": "classroom", "ms": "bilik darjah; kelas",
        "pos": "noun", "hsk": 2, "note": "Measure word: 间 (jiān) / sebuah bilik",
        "ex_zh": "同学们正在教室里认真听讲。", "ex_en": "The classmates are listening attentively in the classroom.", "ex_ms": "Murid-murid sedang mendengar dengan teliti di dalam bilik darjah."
    },
    {
        "zh": "图书馆", "py": "tú shū guǎn", "en": "library", "ms": "perpustakaan",
        "pos": "noun", "hsk": 2, "note": "Measure word: 座 (zuò) / sebuah perpustakaan",
        "ex_zh": "周末我喜欢在图书馆看书。", "ex_en": "On weekends I like reading books in the library.", "ex_ms": "Pada hujung minggu saya suka membaca buku di perpustakaan."
    },
    {
        "zh": "中文", "py": "zhōng wén", "en": "Chinese language", "ms": "bahasa Cina",
        "pos": "noun", "hsk": 1, "note": "Written and spoken Chinese",
        "ex_zh": "我每天学习一个小时中文。", "ex_en": "I study Chinese for one hour every day.", "ex_ms": "Saya belajar bahasa Cina selama satu jam setiap hari."
    },
    {
        "zh": "英语", "py": "yīng yǔ", "en": "English language", "ms": "bahasa Inggeris",
        "pos": "noun", "hsk": 1, "note": "English language subject",
        "ex_zh": "他的英语发音非常纯正。", "ex_en": "His English pronunciation is very authentic.", "ex_ms": "Sebutan bahasa Inggerisnya sangat fasih."
    },
    {
        "zh": "马来语", "py": "mǎ lái yǔ", "en": "Malay language", "ms": "bahasa Melayu",
        "pos": "noun", "hsk": 2, "note": "National language of Malaysia",
        "ex_zh": "马来语是马来西亚的官方语言。", "ex_en": "Malay is the official language of Malaysia.", "ex_ms": "Bahasa Melayu ialah bahasa kebangsaan Malaysia."
    },
    {
        "zh": "学习", "py": "xué xí", "en": "to study; to learn", "ms": "belajar; menuntut ilmu",
        "pos": "verb/noun", "hsk": 1, "note": "Root word in Malay: ajar -> belajar",
        "ex_zh": "学习新语言很有趣。", "ex_en": "Learning a new language is very interesting.", "ex_ms": "Belajar bahasa baharu sangat menyeronokkan."
    },
    {
        "zh": "翻译", "py": "fān yì", "en": "to translate; translation", "ms": "terjemah; menterjemah",
        "pos": "verb/noun", "hsk": 4, "note": "Root word in Malay: terjemah",
        "ex_zh": "请把这句话翻译成英文或马来文。", "ex_en": "Please translate this sentence into English or Malay.", "ex_ms": "Sila terjemahkan ayat ini ke bahasa Inggeris atau bahasa Melayu."
    },
    {
        "zh": "词汇", "py": "cí huì", "en": "vocabulary; words", "ms": "kosa kata; perbendaharaan kata",
        "pos": "noun", "hsk": 4, "note": "Important for language acquisition",
        "ex_zh": "多阅读可以扩大你的词汇量。", "ex_en": "Reading more can expand your vocabulary.", "ex_ms": "Banyak membaca dapat meluaskan kosa kata anda."
    },
    {
        "zh": "语法", "py": "yǔ fǎ", "en": "grammar", "ms": "tatabahasa",
        "pos": "noun", "hsk": 3, "note": "Rules of sentence structure",
        "ex_zh": "掌握语法规则对写好作文很有帮助。", "ex_en": "Mastering grammar rules is very helpful for writing good essays.", "ex_ms": "Menguasai hukum tatabahasa sangat membantu dalam penulisan karangan."
    },
    {
        "zh": "书", "py": "shū", "en": "book", "ms": "buku",
        "pos": "noun", "hsk": 1, "note": "Measure word: 本 (běn) / sebuah buku",
        "ex_zh": "桌子上有一本新书。", "ex_en": "There is a new book on the desk.", "ex_ms": "Terdapat sebuah buku baharu di atas meja."
    },
    {
        "zh": "笔", "py": "bǐ", "en": "pen; writing utensil", "ms": "pen; pena",
        "pos": "noun", "hsk": 2, "note": "Measure word: 支 (zhī) / sebatang pen",
        "ex_zh": "我可以借用一下你的笔吗？", "ex_en": "May I borrow your pen for a moment?", "ex_ms": "Bolehkah saya pinjam pen awak sebentar?"
    },
    {
        "zh": "本子", "py": "běn zi", "en": "notebook", "ms": "buku latihan; buku nota",
        "pos": "noun", "hsk": 2, "note": "Measure word: 本 (běn) / sebuah buku nota",
        "ex_zh": "他在本子上认真做笔记。", "ex_en": "He took notes conscientiously in the notebook.", "ex_ms": "Dia mencatat nota dengan teliti di dalam buku latihan."
    },
    {
        "zh": "作业", "py": "zuò yè", "en": "homework; assignment", "ms": "kerja rumah; tugasan",
        "pos": "noun", "hsk": 2, "note": "做作业 = buat kerja rumah",
        "ex_zh": "你今天的作业完成了吗？", "ex_en": "Have you finished today's homework?", "ex_ms": "Adakah anda sudah menyiapkan kerja rumah hari ini?"
    },
    {
        "zh": "考试", "py": "kǎo shì", "en": "exam; test", "ms": "peperiksaan; ujian",
        "pos": "noun/verb", "hsk": 2, "note": "参加考试 = menduduki peperiksaan",
        "ex_zh": "下周一有一场重要的英语考试。", "ex_en": "There is an important English exam next Monday.", "ex_ms": "Ada peperiksaan bahasa Inggeris yang penting pada hari Isnin depan."
    },
    {
        "zh": "问题", "py": "wèn tí", "en": "question; problem", "ms": "soalan; masalah",
        "pos": "noun", "hsk": 2, "note": "回答问题 = menjawab soalan",
        "ex_zh": "如果你有任何问题，可以随时问老师。", "ex_en": "If you have any questions, you can ask the teacher anytime.", "ex_ms": "Jika anda ada sebarang soalan, boleh bertanya cikgu bila-bila masa."
    },
    {
        "zh": "回答", "py": "huí dá", "en": "to answer; reply", "ms": "jawab; menjawab",
        "pos": "verb/noun", "hsk": 2, "note": "Root word: jawab",
        "ex_zh": "他的回答非常清晰准确。", "ex_en": "His answer was very clear and accurate.", "ex_ms": "Jawapannya sangat jelas dan tepat."
    },
    {
        "zh": "练习", "py": "liàn xí", "en": "practice; exercise", "ms": "latihan; berlatih",
        "pos": "noun/verb", "hsk": 3, "note": "Latihan pengukuhan",
        "ex_zh": "坚持每天练习口语很重要。", "ex_en": "Practicing spoken language daily is crucial.", "ex_ms": "Berlatih bertutur setiap hari sangat penting."
    },
    {
        "zh": "句子", "py": "jù zi", "en": "sentence", "ms": "ayat",
        "pos": "noun", "hsk": 2, "note": "Bina ayat = 造句",
        "ex_zh": "造句可以帮助记忆新单词。", "ex_en": "Making sentences helps memorize new words.", "ex_ms": "Membina ayat dapat membantu mengingati perkataan baharu."
    },
    {
        "zh": "读", "py": "dú", "en": "to read aloud; study", "ms": "baca; membaca",
        "pos": "verb", "hsk": 1, "note": "Membaca buku = 读书",
        "ex_zh": "请跟我一起大声读这个词。", "ex_en": "Please read this word out loud with me.", "ex_ms": "Sila baca perkataan ini dengan kuat bersama saya."
    },
    {
        "zh": "写", "py": "xiě", "en": "to write", "ms": "tulis; menulis",
        "pos": "verb", "hsk": 1, "note": "Menulis karangan = 写作文",
        "ex_zh": "写汉字要注意笔顺。", "ex_en": "Pay attention to stroke order when writing Chinese characters.", "ex_ms": "Perhatikan urutan goresan semasa menulis tulisan Cina."
    },
    {
        "zh": "听", "py": "tīng", "en": "to listen; hear", "ms": "dengar; mendengar",
        "pos": "verb", "hsk": 1, "note": "Mendengar teliti = 仔细听",
        "ex_zh": "你仔细听录音里的发音。", "ex_en": "Listen carefully to the pronunciation in the recording.", "ex_ms": "Dengar sebutan dalam rakaman itu dengan teliti."
    },
    {
        "zh": "说", "py": "shuō", "en": "to speak; say", "ms": "cakap; bercakap; bertutur",
        "pos": "verb", "hsk": 1, "note": "Bercakap bahasa Cina = 说中文",
        "ex_zh": "不要害怕说错，大胆开口。", "ex_en": "Don't be afraid of making mistakes, speak up boldly.", "ex_ms": "Jangan takut buat salah, bertuturlah dengan yakin."
    },
    {
        "zh": "懂", "py": "dǒng", "en": "to understand", "ms": "faham; mengerti",
        "pos": "verb", "hsk": 2, "note": "Faham tak? = 懂不懂？",
        "ex_zh": "老师，我听懂这一段了。", "ex_en": "Teacher, I understood this section.", "ex_ms": "Cikgu, saya sudah faham bahagian ini."
    },
    {
        "zh": "明白", "py": "míng bai", "en": "clear; understand", "ms": "faham; jelas",
        "pos": "verb/adjective", "hsk": 2, "note": "Saya faham = 我明白了",
        "ex_zh": "现在你明白这道题的做法了吗？", "ex_en": "Do you understand how to solve this problem now?", "ex_ms": "Adakah sekarang anda faham cara menyelesaikan soalan ini?"
    },
    {
        "zh": "难", "py": "nán", "en": "difficult; hard", "ms": "susah; sukar",
        "pos": "adjective", "hsk": 2, "note": "Opposite: 容易 / mudah",
        "ex_zh": "刚开始学有点难，但坚持就有收获。", "ex_en": "It is a bit difficult at first, but persistence pays off.", "ex_ms": "Pada mulanya agak sukar, tetapi usaha gigih pasti membuahkan hasil."
    },
    {
        "zh": "容易", "py": "róng yì", "en": "easy; likely", "ms": "senang; mudah",
        "pos": "adjective", "hsk": 2, "note": "Opposite: 难 / sukar",
        "ex_zh": "掌握了规律，背单词就会更容易。", "ex_en": "Once you grasp the patterns, memorizing words becomes easier.", "ex_ms": "Setelah memahami polanya, mengingati perkataan akan menjadi lebih mudah."
    },
    {
        "zh": "重要", "py": "zhòng yào", "en": "important", "ms": "penting",
        "pos": "adjective", "hsk": 3, "note": "Perkara penting = 重要的事情",
        "ex_zh": "每天复习对巩固记忆非常重要。", "ex_en": "Daily review is very important for consolidating memory.", "ex_ms": "Ulang kaji harian sangat penting untuk mengukuhkan ingatan."
    },
    {
        "zh": "复习", "py": "fù xí", "en": "to review; revise", "ms": "ulang kaji; mengulang kaji",
        "pos": "verb/noun", "hsk": 3, "note": "Mengulang kaji pelajaran = 复习功课",
        "ex_zh": "考前一定要留出时间好好复习。", "ex_en": "Make sure to set aside time to review well before tests.", "ex_ms": "Pastikan peruntukkan masa untuk mengulang kaji sebelum peperiksaan."
    },
    {
        "zh": "努力", "py": "nǔ lì", "en": "hardworking; effort", "ms": "rajin; berusaha gigih",
        "pos": "adjective/verb", "hsk": 2, "note": "Berusaha gigih = 努力奋斗",
        "ex_zh": "只要坚持努力，就一定会取得成功。", "ex_en": "As long as you persevere and work hard, you will succeed.", "ex_ms": "Asalkan berusaha dengan gigih, anda pasti akan berjaya."
    },
    {
        "zh": "进步", "py": "jìn bù", "en": "progress; improvement", "ms": "kemajuan; peningkatan",
        "pos": "noun/verb", "hsk": 3, "note": "Ada kemajuan = 有进步",
        "ex_zh": "这个月他的听力有了很大的进步。", "ex_en": "This month his listening comprehension made great progress.", "ex_ms": "Kemahiran mendengarnya menunjukkan kemajuan besar bulan ini."
    },
    {
        "zh": "成绩", "py": "chéng jì", "en": "grade; score; result", "ms": "keputusan; markah; pencapaian",
        "pos": "noun", "hsk": 3, "note": "Keputusan cemerlang = 优异成绩",
        "ex_zh": "这次期末考试大家都取得了理想的成绩。", "ex_en": "Everyone achieved ideal results in this final exam.", "ex_ms": "Semua orang memperoleh keputusan yang memuaskan dalam peperiksaan akhir ini."
    },
    # Common Malay Idioms / Simpulan Bahasa
    {
        "zh": "书呆子", "py": "shū dāi zi", "en": "bookworm (studious)", "ms": "ulat buku",
        "pos": "idiom/noun", "hsk": 4, "note": "Malay idiom: ulat buku (gemar membaca buku)",
        "ex_zh": "他整天泡在图书馆里，是个名副其实的书呆子。", "ex_en": "He spends all day in the library, truly a bookworm.", "ex_ms": "Dia meluangkan masa sepanjang hari di perpustakaan, memang seorang ulat buku."
    },
    {
        "zh": "勤快", "py": "qín kuài", "en": "diligent; hardworking", "ms": "ringan tulang",
        "pos": "idiom/adjective", "hsk": 3, "note": "Malay idiom: ringan tulang (rajin bekerja)",
        "ex_zh": "他做事勤快，深得老师和同学们的喜欢。", "ex_en": "He is hardworking and very popular among teachers and classmates.", "ex_ms": "Dia seorang yang ringan tulang, sangat disukai oleh guru dan rakan-rakan."
    },
    {
        "zh": "熟能生巧", "py": "shú néng shēng qiǎo", "en": "practice makes perfect", "ms": "alah bisa tegal biasa",
        "pos": "idiom", "hsk": 5, "note": "Proverb: Practice makes perfect",
        "ex_zh": "学语言是熟能生巧的过程。", "ex_en": "Learning a language is a process where practice makes perfect.", "ex_ms": "Belajar bahasa ialah proses alah bisa tegal biasa."
    },
    {
        "zh": "温故知新", "py": "wēn gù zhī xīn", "en": "review the old to learn the new", "ms": "mengulang kaji untuk mendapat kefahaman baharu",
        "pos": "idiom", "hsk": 5, "note": "Analects proverb on reviewing lessons",
        "ex_zh": "学习要懂得温故知新。", "ex_en": "In studying, one must review the old to gain new insights.", "ex_ms": "Dalam pembelajaran, kita perlu mengulang kaji perkara lama untuk pemahaman baharu."
    }
]

# Grammar rules guide (Chinese + Malay Tatabahasa)
grammar_rules = [
    {
        "id": "hukum_dm",
        "lang": "ms",
        "title": "Hukum D-M (Diterangkan - Menerangkan)",
        "title_zh": "马来文核心语序：修饰词置于名词后 (Hukum D-M)",
        "explanation": "In Bahasa Melayu, the descriptive adjective comes AFTER the noun (Diterangkan + Menerangkan). E.g. 'kereta merah' (car red), NOT 'merah kereta'. In English & Chinese, adjectives come before nouns ('red car', '红色的车'). This is one of the most common student mistakes!",
        "example_zh": "红色的书 (Chinese: Adjective + Noun) ➔ Sebuah buku merah (Malay: Noun + Adjective)。",
        "example_en": "Red book (English) ➔ Buku (Noun) + Merah (Adjective) in Malay."
    },
    {
        "id": "imbuhan_awalan",
        "lang": "ms",
        "title": "Imbuhan Awalan (Prefixes: meN-, ber-, peN-, ter-)",
        "title_zh": "马来文字首缀词 (Imbuhan Awalan)",
        "explanation": "Malay verbs and nouns are formed by adding prefixes to the root word (kata dasar):\n• meN-: Active transitive verb (ajar ➔ mengajar = to teach; baca ➔ membaca = to read)\n• ber-: Intransitive/habitual action (ajar ➔ belajar = to study; main ➔ bermain = to play)\n• peN-: Person/agent of action (ajar ➔ pengajar = educator; tulis ➔ penulis = writer)\n• ter-: Accidental or superlative (paling) action (baca ➔ terbaca = accidentally read; pandai ➔ terpandai = cleverest).",
        "example_zh": "Root: ajar (教) ➔ Belajar (学习 - murid), Mengajar (教学 - cikgu), Pengajar (导师)。",
        "example_en": "Root: ajar ➔ Belajar (to learn), Mengajar (to teach), Pengajar (teacher/instructor)."
    },
    {
        "id": "kata_sendi_nama",
        "lang": "ms",
        "title": "Kata Sendi Nama: 'Dari' vs 'Daripada'",
        "title_zh": "介词辨析：“Dari” 与 “Daripada” 的区别",
        "explanation": "A critical SPM/KSSR grammar pitfall:\n• DARI is used strictly for ATM: Arah (direction), Tempat (place), Masa (time). E.g., 'dari sekolah' (from school), 'dari pukul 8' (from 8 AM).\n• DARIPADA is used for everything else: People, Comparisons, Origin/Material, and Sources. E.g., 'hadiah daripada ibu' (gift from mother), 'lebih tinggi daripada' (taller than).",
        "example_zh": "从学校出来 (Tempat) ➔ Dari sekolah; 老师给的信 (Orang) ➔ Daripada cikgu。",
        "example_en": "From school (Place) ➔ Dari sekolah; From the teacher (Person) ➔ Daripada cikgu."
    },
    {
        "id": "penjodoh_bilangan",
        "lang": "ms",
        "title": "Penjodoh Bilangan (Malay Classifiers / 量词)",
        "title_zh": "马来文量词 (Penjodoh Bilangan)",
        "explanation": "Just like Chinese measure words (量词), Malay requires Penjodoh Bilangan with numbers:\n• buah: large items, books, buildings, vehicles (sebuah buku, sebuah kereta)\n• orang: human beings (seorang guru, dua orang murid)\n• batang: long, rigid objects like pens, roads, trees (sebatang pen)\n• ekor: animals (seekor kucing)\n• helai: thin, flat items like paper, clothes (sehelai kertas).",
        "example_zh": "三本书 (三 + 本 + 书) ➔ Tiga buah buku (Tiga + buah + buku)。",
        "example_en": "Three books ➔ Tiga (three) + buah (classifier) + buku (book)."
    },
    {
        "id": "svo",
        "lang": "zh",
        "title": "Basic Word Order: S + V + O",
        "title_zh": "中文基本语序：主语 + 谓语 + 宾语",
        "explanation": "Chinese, English, and Malay all fundamentally follow Subject + Verb + Object order in simple declarative statements.",
        "example_zh": "我 (Subject) + 学习 (Verb) + 汉语 (Object)。",
        "example_en": "I study Chinese. / Saya belajar bahasa Cina."
    },
    {
        "id": "time_manner_place",
        "lang": "zh",
        "title": "Time and Place Before the Verb in Chinese",
        "title_zh": "时间与地点位于动词前",
        "explanation": "In English and Malay, time and place often appear at the end of a sentence ('Saya membaca buku di perpustakaan pada waktu pagi'). In Chinese, time and location usually go BEFORE the main verb: Subject + Time + Place + Verb + Object.",
        "example_zh": "我 (Subject) + 今天上午 (Time) + 在图书馆 (Place) + 看书 (Verb + Object)。",
        "example_en": "Saya membaca buku di perpustakaan pagi ini. / I read books in the library this morning."
    },
    {
        "id": "de_particles",
        "lang": "zh",
        "title": "The Three 'De's in Chinese: 的, 得, 地",
        "title_zh": "“的、得、地”的区别",
        "explanation": "• 的 (de): Noun modifier / possession ('我的书' = buku saya).\n• 地 (de): Adverb marker before a verb ('认真地学习' = belajar dengan tekun).\n• 得 (de): Complement marker after a verb describing manner/degree ('他说得很好' = dia bercakap dengan baik).",
        "example_zh": "他认真地 (地) 读完了这本有趣的 (的) 书，并且学得 (得) 很快乐。",
        "example_en": "Dia membaca buku yang menarik (的) dengan tekun (地) dan belajar dengan gembira (得)."
    }
]

os.makedirs("data", exist_ok=True)

with open("data/dictionary.json", "w", encoding="utf-8") as f:
    json.dump(vocab_list, f, ensure_ascii=False, indent=2)

with open("data/grammar_notes.json", "w", encoding="utf-8") as f:
    json.dump(grammar_rules, f, ensure_ascii=False, indent=2)

print(f"Generated {len(vocab_list)} trilingual vocabulary items and {len(grammar_rules)} grammar points.")
