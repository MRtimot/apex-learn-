import http.server
import json
import os
import random
import socketserver
import urllib.parse
from db import init_db, get_all_vocab, add_vocab, delete_vocab, toggle_mastered, increment_review
from translator import translate, VOCAB_LIST, GRAMMAR_RULES

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

class StudentTranslationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # API Endpoints
        if path == "/api/vocab":
            vocab_items = get_all_vocab()
            self._send_json({"status": "success", "data": vocab_items})
            return

        elif path == "/api/dictionary":
            search_query = query.get("q", [""])[0].lower().strip()
            hsk_filter = query.get("hsk", [""])[0]

            filtered = VOCAB_LIST
            if hsk_filter and hsk_filter.isdigit():
                hsk_num = int(hsk_filter)
                filtered = [v for v in filtered if v.get("hsk") == hsk_num]

            if search_query:
                filtered = [
                    v for v in filtered 
                    if search_query in v.get("zh", "").lower() 
                    or search_query in v.get("en", "").lower() 
                    or search_query in v.get("ms", "").lower() 
                    or search_query in v.get("py", "").lower()
                ]

            self._send_json({"status": "success", "count": len(filtered), "data": filtered})
            return

        elif path == "/api/grammar":
            lang_filter = query.get("lang", [""])[0]
            rules = GRAMMAR_RULES
            if lang_filter:
                rules = [r for r in rules if r.get("lang") == lang_filter]
            self._send_json({"status": "success", "data": rules})
            return

        elif path == "/api/quiz":
            count = int(query.get("count", ["5"])[0])
            mode = query.get("mode", ["all"])[0] # all, zh_en, zh_ms, en_ms
            
            vocab_pool = get_all_vocab()
            
            # Harmonize fields
            formatted_pool = []
            for item in vocab_pool:
                formatted_pool.append({
                    "chinese": item["chinese"],
                    "pinyin": item["pinyin"],
                    "english": item["english"],
                    "malay": item.get("malay", "") or item.get("english", ""),
                    "hsk": item.get("hsk", 1)
                })
                
            # If user has few saved words, combine with built-in trilingual dictionary
            if len(formatted_pool) < 4:
                for item in VOCAB_LIST:
                    if not any(f["chinese"] == item["zh"] for f in formatted_pool):
                        formatted_pool.append({
                            "chinese": item["zh"],
                            "pinyin": item["py"],
                            "english": item["en"],
                            "malay": item.get("ms", item["en"]),
                            "hsk": item.get("hsk", 1)
                        })

            if len(formatted_pool) < 4:
                self._send_json({"status": "error", "message": "Not enough words to generate quiz."}, 400)
                return

            sample_size = min(count, len(formatted_pool))
            selected_words = random.sample(formatted_pool, sample_size)
            questions = []

            for word in selected_words:
                available_types = []
                if mode == "zh_en":
                    available_types = ["zh_to_en", "en_to_zh", "pinyin_match"]
                elif mode == "zh_ms":
                    available_types = ["zh_to_ms", "ms_to_zh", "pinyin_match"]
                elif mode == "en_ms":
                    available_types = ["en_to_ms", "ms_to_en"]
                else: # all trilingual mix
                    available_types = ["zh_to_en", "zh_to_ms", "en_to_zh", "ms_to_zh", "en_to_ms", "pinyin_match"]

                q_type = random.choice(available_types)
                distractors = [w for w in formatted_pool if w["chinese"] != word["chinese"]]
                
                # Ensure at least 3 distinct distractors
                if len(distractors) < 3:
                    for v in VOCAB_LIST:
                        if v["zh"] != word["chinese"] and not any(d["chinese"] == v["zh"] for d in distractors):
                            distractors.append({
                                "chinese": v["zh"],
                                "pinyin": v["py"],
                                "english": v["en"],
                                "malay": v.get("ms", v["en"])
                            })
                        if len(distractors) >= 5:
                            break
                            
                distractor_samples = random.sample(distractors, min(3, len(distractors)))

                if q_type == "zh_to_en":
                    options = [word["english"]] + [d["english"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "zh_to_en",
                        "title": "Chinese ➔ English",
                        "prompt": word["chinese"],
                        "pinyin": word["pinyin"],
                        "options": options,
                        "answer": word["english"],
                        "explanation": f"{word['chinese']} ({word['pinyin']}) means '{word['english']}' in English."
                    })
                elif q_type == "zh_to_ms":
                    options = [word["malay"]] + [d["malay"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "zh_to_ms",
                        "title": "Bahasa Cina ➔ Bahasa Melayu",
                        "prompt": word["chinese"],
                        "pinyin": word["pinyin"],
                        "options": options,
                        "answer": word["malay"],
                        "explanation": f"{word['chinese']} ({word['pinyin']}) bermaksud '{word['malay']}' dalam Bahasa Melayu."
                    })
                elif q_type == "ms_to_zh":
                    options = [word["chinese"]] + [d["chinese"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "ms_to_zh",
                        "title": "Bahasa Melayu ➔ Bahasa Cina",
                        "prompt": word["malay"],
                        "pinyin": "",
                        "options": options,
                        "answer": word["chinese"],
                        "explanation": f"Perkataan '{word['malay']}' dalam Bahasa Cina ialah {word['chinese']} ({word['pinyin']})."
                    })
                elif q_type == "en_to_zh":
                    options = [word["chinese"]] + [d["chinese"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "en_to_zh",
                        "title": "English ➔ Chinese",
                        "prompt": word["english"],
                        "pinyin": "",
                        "options": options,
                        "answer": word["chinese"],
                        "explanation": f"'{word['english']}' in Chinese is {word['chinese']} ({word['pinyin']})."
                    })
                elif q_type == "en_to_ms":
                    options = [word["malay"]] + [d["malay"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "en_to_ms",
                        "title": "English ➔ Bahasa Melayu",
                        "prompt": word["english"],
                        "pinyin": "",
                        "options": options,
                        "answer": word["malay"],
                        "explanation": f"'{word['english']}' in Bahasa Melayu is '{word['malay']}'."
                    })
                elif q_type == "ms_to_en":
                    options = [word["english"]] + [d["english"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "ms_to_en",
                        "title": "Bahasa Melayu ➔ English",
                        "prompt": word["malay"],
                        "pinyin": "",
                        "options": options,
                        "answer": word["english"],
                        "explanation": f"'{word['malay']}' in English is '{word['english']}'."
                    })
                else: # pinyin_match
                    options = [word["pinyin"]] + [d["pinyin"] for d in distractor_samples]
                    random.shuffle(options)
                    questions.append({
                        "type": "pinyin_match",
                        "title": "Match Correct Pinyin (拼音配对)",
                        "prompt": word["chinese"],
                        "subprompt": f"EN: {word['english']} | BM: {word['malay']}",
                        "options": options,
                        "answer": word["pinyin"],
                        "explanation": f"The correct pinyin for {word['chinese']} is '{word['pinyin']}'."
                    })

            self._send_json({"status": "success", "questions": questions})
            return

        # Serve static files
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/translate":
            text = payload.get("text", "")
            source_lang = payload.get("sourceLang", "auto")
            target_lang = payload.get("targetLang", "auto")

            result = translate(text, source_lang, target_lang)
            self._send_json({"status": "success", "data": result})
            return

        elif path == "/api/vocab":
            chinese = payload.get("chinese", "").strip()
            pinyin = payload.get("pinyin", "").strip()
            english = payload.get("english", "").strip()
            malay = payload.get("malay", "").strip()
            pos = payload.get("pos", "").strip()
            example_zh = payload.get("example_zh", "").strip()
            example_en = payload.get("example_en", "").strip()
            example_ms = payload.get("example_ms", "").strip()
            hsk = int(payload.get("hsk", 1))
            note = payload.get("note", "").strip()

            if not (chinese or english or malay):
                self._send_json({"status": "error", "message": "At least one language text is required."}, 400)
                return

            word_id = add_vocab(chinese, pinyin, english, malay, pos, example_zh, example_en, example_ms, hsk, note)
            self._send_json({"status": "success", "id": word_id, "message": "Vocabulary saved successfully!"})
            return

        elif path == "/api/vocab/toggle":
            vocab_id = payload.get("id")
            if not vocab_id:
                self._send_json({"status": "error", "message": "Missing vocab id."}, 400)
                return
            new_status = toggle_mastered(vocab_id)
            self._send_json({"status": "success", "mastered": new_status})
            return

        elif path == "/api/vocab/review":
            vocab_id = payload.get("id")
            if vocab_id:
                increment_review(vocab_id)
            self._send_json({"status": "success"})
            return

        self._send_json({"status": "error", "message": "Endpoint not found."}, 404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/vocab":
            vocab_id = query.get("id", [None])[0]
            if not vocab_id:
                self._send_json({"status": "error", "message": "Missing id parameter."}, 400)
                return
            try:
                delete_vocab(int(vocab_id))
                self._send_json({"status": "success", "message": "Deleted successfully."})
            except (ValueError, TypeError):
                self._send_json({"status": "error", "message": "Invalid id parameter."}, 400)
            return

        self._send_json({"status": "error", "message": "Endpoint not found."}, 404)

def run_server():
    init_db()
    socketserver.TCPServer.allow_reuse_address = True
    env_port = int(os.environ.get("PORT", 0))
    ports_to_try = [env_port] if env_port else [8000, 8080, 8888, 3000, 5000]
    for attempt_port in ports_to_try:
        try:
            with socketserver.TCPServer(("", attempt_port), StudentTranslationHandler) as httpd:
                print(f"🚀 Apex Learn Trilingual Hub server running at http://localhost:{attempt_port}")
                httpd.serve_forever()
                break
        except OSError:
            print(f"Port {attempt_port} occupied, trying next port...")

if __name__ == "__main__":
    run_server()
