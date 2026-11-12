// Core Application Controller for Student Trilingual Translation Hub
const App = {
    currentTab: 'translator',
    sourceLang: 'auto',
    targetLang: 'zh',
    currentTranslationResult: null,
    savedVocabulary: [],
    geminiApiKey: localStorage.getItem('gemini_api_key') || '',
    useToneColors: true,
    autoTranslateEnabled: localStorage.getItem('auto_translate') !== 'false',
    autoTranslateTimer: null,

    init() {
        this.bindEvents();
        this.loadVocabulary();
        this.loadGrammarRules();
        this.setupPresetButtons();
    },

    bindEvents() {
        // Tab switching
        document.querySelectorAll('.nav-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Speed selector
        const speedSelect = document.getElementById('audioSpeedSelect');
        if (speedSelect) {
            speedSelect.addEventListener('change', (e) => {
                SpeechManager.setSpeed(e.target.value);
            });
        }

        // Tone color toggle
        const toneToggle = document.getElementById('toneColorToggle');
        if (toneToggle) {
            toneToggle.addEventListener('change', (e) => {
                this.useToneColors = e.target.checked;
                if (this.currentTranslationResult) {
                    this.renderTranslationResult(this.currentTranslationResult);
                }
            });
        }

        // Auto-translate toggle
        const autoToggle = document.getElementById('autoTranslateToggle');
        if (autoToggle) {
            autoToggle.checked = this.autoTranslateEnabled;
            autoToggle.addEventListener('change', (e) => {
                this.autoTranslateEnabled = e.target.checked;
                localStorage.setItem('auto_translate', this.autoTranslateEnabled ? 'true' : 'false');
                this.showToast(this.autoTranslateEnabled ? '⚡ Auto-translate enabled' : 'Auto-translate paused');
            });
        }

        // Input textarea count & auto-translate debounce
        const inputEl = document.getElementById('sourceTextInput');
        if (inputEl) {
            inputEl.addEventListener('input', () => {
                const text = inputEl.value;
                const charEl = document.getElementById('inputCharCount');
                if (charEl) charEl.textContent = `${text.length} chars`;

                // Update auto-detect indicator dynamically
                if (this.sourceLang === 'auto') {
                    this.updateAutoDetectLabel(text);
                }

                if (this.autoTranslateEnabled) {
                    clearTimeout(this.autoTranslateTimer);
                    if (!text.trim()) {
                        this.clearOutput();
                        return;
                    }
                    this.updateAutoTranslateBadge('typing');
                    this.autoTranslateTimer = setTimeout(() => {
                        this.executeTranslation(true);
                    }, 450);
                }
            });

            // Instant auto-translate on paste
            inputEl.addEventListener('paste', () => {
                if (this.autoTranslateEnabled) {
                    clearTimeout(this.autoTranslateTimer);
                    setTimeout(() => {
                        this.executeTranslation(true);
                    }, 150);
                }
            });
        }
    },

    updateAutoDetectLabel(text) {
        const labelEl = document.getElementById('langDirectionLabel');
        if (!labelEl) return;
        if (!text.trim()) {
            labelEl.textContent = 'Auto Detect ➔ Target';
            return;
        }
        if (/[\u4e00-\u9fa5]/.test(text)) {
            labelEl.textContent = '中文 ➔ Target (Auto)';
        } else {
            const malayKeywords = ["saya", "anda", "awak", "cikgu", "guru", "murid", "pelajar", "sekolah", "buku", "belajar", "terima", "kasih", "selamat", "pagi", "petang", "malam", "soalan", "peperiksaan", "dan", "yang", "di", "ini", "itu"];
            const words = text.toLowerCase().split(/\s+/);
            const isMs = words.some(w => malayKeywords.includes(w));
            labelEl.textContent = isMs ? 'Melayu ➔ Target (Auto)' : 'English ➔ Target (Auto)';
        }
    },

    updateAutoTranslateBadge(state) {
        const badge = document.getElementById('autoTranslateBadge');
        if (!badge) return;
        if (state === 'typing') {
            badge.textContent = "⚡ Translating...";
            badge.className = "text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200 animate-pulse";
            badge.classList.remove('hidden');
        } else if (state === 'done') {
            badge.textContent = "✓ Auto-translated";
            badge.className = "text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200";
            badge.classList.remove('hidden');
            setTimeout(() => {
                if (badge.textContent === "✓ Auto-translated") {
                    badge.classList.add('hidden');
                }
            }, 3000);
        } else {
            badge.classList.add('hidden');
        }
    },

    clearOutput() {
        this.currentTranslationResult = null;
        const pinyinRubyArea = document.getElementById('pinyinRubyDisplay');
        const outputTextEl = document.getElementById('translatedResultText');
        const pinyinRawText = document.getElementById('pinyinRawText');
        const wordSection = document.getElementById('wordBreakdownSection');
        const grammarSection = document.getElementById('grammarTipsSection');
        const badge = document.getElementById('autoTranslateBadge');
        const speakChineseOnlyBtn = document.getElementById('speakChineseOnlyBtn');
        const speakMalayOnlyBtn = document.getElementById('speakMalayOnlyBtn');

        if (pinyinRubyArea) pinyinRubyArea.innerHTML = '<span class="text-slate-400 text-sm italic">Translation and pronunciation will appear here...</span>';
        if (outputTextEl) outputTextEl.textContent = '';
        if (pinyinRawText) pinyinRawText.textContent = '';
        if (wordSection) wordSection.classList.add('hidden');
        if (grammarSection) grammarSection.classList.add('hidden');
        if (badge) badge.classList.add('hidden');
        if (speakChineseOnlyBtn) speakChineseOnlyBtn.classList.add('hidden');
        if (speakMalayOnlyBtn) speakMalayOnlyBtn.classList.add('hidden');
    },

    switchTab(tabName) {
        this.currentTab = tabName;
        document.querySelectorAll('.nav-tab-btn').forEach(btn => {
            const isCurrent = btn.getAttribute('data-tab') === tabName;
            if (isCurrent) {
                btn.classList.add('bg-indigo-600', 'text-white', 'shadow-sm');
                btn.classList.remove('text-slate-600', 'hover:bg-slate-100');
            } else {
                btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-sm');
                btn.classList.add('text-slate-600', 'hover:bg-slate-100');
            }
        });

        document.querySelectorAll('.tab-view-content').forEach(view => {
            view.classList.add('hidden');
        });
        const targetView = document.getElementById(`view-${tabName}`);
        if (targetView) targetView.classList.remove('hidden');

        if (tabName === 'flashcards') {
            FlashcardManager.init(this.savedVocabulary);
        } else if (tabName === 'quiz') {
            FlashcardManager.startQuiz(5, 'all');
        } else if (tabName === 'vocab') {
            this.renderVocabList();
        }
    },

    onLangSelectChange() {
        const srcSelect = document.getElementById('sourceLangSelect');
        const tgtSelect = document.getElementById('targetLangSelect');
        if (srcSelect && tgtSelect) {
            this.setLanguageDirection(srcSelect.value, tgtSelect.value);
        }
    },

    setLanguageDirection(source, target) {
        this.sourceLang = source;
        this.targetLang = target;

        const srcSelect = document.getElementById('sourceLangSelect');
        const tgtSelect = document.getElementById('targetLangSelect');
        if (srcSelect) srcSelect.value = source;
        if (tgtSelect) tgtSelect.value = target;

        const langNames = {
            'auto': 'Auto Detect',
            'en': 'English',
            'zh': '简体中文',
            'ms': 'Bahasa Melayu'
        };

        const labelEl = document.getElementById('langDirectionLabel');
        if (labelEl) {
            labelEl.textContent = `${langNames[source] || source} ➔ ${langNames[target] || target}`;
        }

        const inputEl = document.getElementById('sourceTextInput');
        if (inputEl && inputEl.value.trim()) {
            this.executeTranslation(false);
        }
    },

    swapLanguageDirection() {
        const oldSrc = this.sourceLang === 'auto' ? 'en' : this.sourceLang;
        const oldTgt = this.targetLang;
        this.setLanguageDirection(oldTgt, oldSrc);

        const swapBtn = document.getElementById('langSwapBtn');
        if (swapBtn) {
            swapBtn.classList.add('rotate-180');
            setTimeout(() => swapBtn.classList.remove('rotate-180'), 300);
        }
    },

    setupPresetButtons() {
        const presets = [
            { label: "👋 Salam / Greetings", text: "Selamat pagi cikgu! Saya ingin belajar bahasa Cina." },
            { label: "🏫 Sekolah / School", text: "Tomorrow morning we have an important English exam in the classroom." },
            { label: "📖 Belajar / Study", text: "Saya belajar kosa kata bahasa Cina dan bahasa Inggeris setiap hari." },
            { label: "💡 Tanya Soalan", text: "老师，请问这个生词用拼音怎么读？" },
            { label: "📜 Simpulan Bahasa", text: "Dia seorang ulat buku yang sangat rajin membaca di perpustakaan." }
        ];

        const container = document.getElementById('presetPromptsContainer');
        if (!container) return;
        container.innerHTML = '';

        presets.forEach(p => {
            const btn = document.createElement('button');
            btn.className = "px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 rounded-full text-xs font-medium text-slate-700 transition border border-slate-200 shrink-0";
            btn.textContent = p.label;
            btn.onclick = () => {
                const inputEl = document.getElementById('sourceTextInput');
                if (inputEl) {
                    inputEl.value = p.text;
                    const charEl = document.getElementById('inputCharCount');
                    if (charEl) charEl.textContent = `${p.text.length} chars`;
                    this.executeTranslation(false);
                }
            };
            container.appendChild(btn);
        });
    },

    clearInput() {
        const inputEl = document.getElementById('sourceTextInput');
        if (inputEl) {
            inputEl.value = '';
            inputEl.focus();
            const charEl = document.getElementById('inputCharCount');
            if (charEl) charEl.textContent = '0 chars';
            this.clearOutput();
        }
    },

    copyText(elementId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        const text = el.innerText || el.value;
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copied to clipboard! 📋');
        });
    },

    // Speech trigger for source input
    speakInput() {
        const text = document.getElementById('sourceTextInput').value.trim();
        if (!text) return;
        let lang = 'en-US';
        if (/[\u4e00-\u9fa5]/.test(text)) {
            lang = 'zh-CN';
        } else if (this.sourceLang === 'ms' || /selamat|pagi|cikgu|murid|saya|anda|buku/i.test(text)) {
            lang = 'ms-MY';
        }
        SpeechManager.speak(text, lang);
    },

    // Speech trigger for translated output
    speakOutput() {
        if (!this.currentTranslationResult || !this.currentTranslationResult.translatedText) return;
        const res = this.currentTranslationResult;
        let lang = 'en-US';
        if (res.targetLang === 'zh' || /[\u4e00-\u9fa5]/.test(res.translatedText)) {
            lang = 'zh-CN';
        } else if (res.targetLang === 'ms') {
            lang = 'ms-MY';
        }
        SpeechManager.speak(res.translatedText, lang);
    },

    // Specific Chinese pronunciation
    speakChineseText() {
        if (!this.currentTranslationResult) return;
        const res = this.currentTranslationResult;
        const zhText = res.targetLang === 'zh' ? res.translatedText : (res.sourceLang === 'zh' ? res.originalText : '');
        if (zhText) SpeechManager.speak(zhText, 'zh-CN');
    },

    // Specific Malay pronunciation
    speakMalayText() {
        if (!this.currentTranslationResult) return;
        const res = this.currentTranslationResult;
        const msText = res.targetLang === 'ms' ? res.translatedText : (res.sourceLang === 'ms' ? res.originalText : '');
        if (msText) SpeechManager.speak(msText, 'ms-MY');
    },

    // Main translation function
    async executeTranslation(isAuto = false) {
        const inputEl = document.getElementById('sourceTextInput');
        const text = inputEl ? inputEl.value.trim() : '';
        if (!text) {
            if (!isAuto) this.showToast('Please type or paste text to translate!');
            return;
        }

        const translateBtn = document.getElementById('translateActionBtn');
        const loader = document.getElementById('translationLoader');
        if (!isAuto && translateBtn) translateBtn.disabled = true;
        if (!isAuto && loader) loader.classList.remove('hidden');

        try {
            // First check if user provided Gemini API Key
            if (this.geminiApiKey) {
                const aiResult = await this.translateWithGemini(text);
                if (aiResult) {
                    this.currentTranslationResult = aiResult;
                    this.renderTranslationResult(aiResult);
                    if (isAuto) this.updateAutoTranslateBadge('done');
                    return;
                }
            }

            // Determine effective source & target languages
            let src = this.sourceLang;
            if (src === 'auto') {
                if (/[\u4e00-\u9fa5]/.test(text)) {
                    src = 'zh';
                } else if (/selamat|pagi|cikgu|murid|saya|anda|buku|belajar|tatabahasa/i.test(text)) {
                    src = 'ms';
                } else {
                    src = 'en';
                }
            }

            let tgt = this.targetLang;
            if (tgt === 'auto' || tgt === src) {
                tgt = src === 'zh' ? 'en' : 'zh';
            }

            // Client side query to MyMemory for fastest live natural translation
            let clientTranslated = null;
            const pair = `${src === 'zh' ? 'zh-CN' : src}|${tgt === 'zh' ? 'zh-CN' : tgt}`;

            try {
                const clientRes = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${pair}`);
                const clientData = await clientRes.json();
                if (clientData && clientData.responseData && clientData.responseData.translatedText) {
                    const resText = clientData.responseData.translatedText;
                    if (!resText.startsWith('MYMEMORY WARNING')) {
                        clientTranslated = resText;
                    }
                }
            } catch (netErr) {
                console.log('Client-side API fallback to server:', netErr);
            }

            // Call Python server API for full pinyin, token breakdown & grammar rules
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    sourceLang: src,
                    targetLang: tgt
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                const res = data.data;
                if (clientTranslated && clientTranslated.length > 0) {
                    res.translatedText = clientTranslated;
                }
                this.currentTranslationResult = res;
                this.renderTranslationResult(res);
                if (isAuto) this.updateAutoTranslateBadge('done');
            } else {
                if (!isAuto) this.showToast('Translation error occurred.');
            }
        } catch (err) {
            console.error('Translation error:', err);
            if (!isAuto) this.showToast('Could not complete translation. Please check connection.');
        } finally {
            if (translateBtn) translateBtn.disabled = false;
            if (loader) loader.classList.add('hidden');
        }
    },

    // AI translation with Gemini API if key is entered
    async translateWithGemini(text) {
        try {
            const prompt = `You are a trilingual Chinese-English-Malay language tutor for students.
Translate the following text: "${text}".
Provide your output strictly in JSON format with these exact keys:
{
  "sourceLang": "en, zh, or ms",
  "targetLang": "zh, en, or ms",
  "originalText": "${text}",
  "translatedText": "natural translation",
  "pinyin": "pinyin with tone marks for Chinese portions",
  "breakdown": [
    {"char": "word", "pinyin": "py", "english": "meaning", "malay": "maksud dalam BM", "pos": "part of speech", "hsk": 1, "note": "grammatical note"}
  ],
  "grammarTips": [
    {"point": "Key grammar or tatabahasa rule", "explanation": "Why this grammar is used and tips for students", "rule": "Pattern"}
  ]
}`;
            const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${this.geminiApiKey}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: prompt }] }],
                    generationConfig: { responseMimeType: "application/json" }
                })
            });
            const data = await res.json();
            if (data.candidates && data.candidates[0].content.parts[0].text) {
                return JSON.parse(data.candidates[0].content.parts[0].text);
            }
        } catch (e) {
            console.warn('Gemini API call failed, falling back to local server:', e);
        }
        return null;
    },

    renderTranslationResult(res) {
        const outputContainer = document.getElementById('translationOutputCard');
        if (!outputContainer) return;
        outputContainer.classList.remove('hidden');

        // Translated text
        const outputTextEl = document.getElementById('translatedResultText');
        if (outputTextEl) outputTextEl.textContent = res.translatedText;

        // Output Card Heading
        const headingEl = document.getElementById('outputCardHeading');
        const langNames = { 'en': 'English', 'zh': '简体中文', 'ms': 'Bahasa Melayu' };
        if (headingEl) {
            headingEl.textContent = `${langNames[res.targetLang] || 'Target'} Translation & Pronunciation`;
        }

        // Dynamic speak buttons
        const speakChineseOnlyBtn = document.getElementById('speakChineseOnlyBtn');
        const speakMalayOnlyBtn = document.getElementById('speakMalayOnlyBtn');
        const speakOutputLabel = document.getElementById('speakOutputLabel');
        
        if (speakOutputLabel) {
            speakOutputLabel.textContent = `Listen to ${langNames[res.targetLang] || 'Translation'}`;
        }

        const hasChinese = res.targetLang === 'zh' || res.sourceLang === 'zh' || /[\u4e00-\u9fa5]/.test(res.translatedText) || /[\u4e00-\u9fa5]/.test(res.originalText);
        const hasMalay = res.targetLang === 'ms' || res.sourceLang === 'ms';

        if (speakChineseOnlyBtn) {
            if (hasChinese && res.targetLang !== 'zh') {
                speakChineseOnlyBtn.classList.remove('hidden');
            } else {
                speakChineseOnlyBtn.classList.add('hidden');
            }
        }

        if (speakMalayOnlyBtn) {
            if (hasMalay && res.targetLang !== 'ms') {
                speakMalayOnlyBtn.classList.remove('hidden');
            } else {
                speakMalayOnlyBtn.classList.add('hidden');
            }
        }

        // Pinyin Ruby Annotation
        const pinyinRubyArea = document.getElementById('pinyinRubyDisplay');
        const pinyinRawText = document.getElementById('pinyinRawText');
        
        if (hasChinese) {
            pinyinRubyArea.classList.remove('hidden');
            if (res.breakdown && res.breakdown.length > 0) {
                pinyinRubyArea.innerHTML = PinyinUtil.renderRubyHtml(res.breakdown, this.useToneColors);
            } else {
                pinyinRubyArea.innerHTML = `<span class="text-2xl">${res.translatedText}</span>`;
            }
            if (pinyinRawText) {
                pinyinRawText.textContent = res.pinyin ? `Pinyin: ${res.pinyin}` : '';
            }
        } else {
            pinyinRubyArea.classList.add('hidden');
            if (pinyinRawText) pinyinRawText.textContent = '';
        }

        // Render Word-by-word Breakdown
        this.renderWordBreakdown(res.breakdown);

        // Render Grammar Tips
        this.renderGrammarTips(res.grammarTips);

        if (window.innerWidth < 768) {
            outputContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    },

    renderWordBreakdown(tokens) {
        const container = document.getElementById('breakdownChipsContainer');
        const section = document.getElementById('wordBreakdownSection');
        if (!container || !section) return;

        const validTokens = (tokens || []).filter(t => t.pinyin && /[\u4e00-\u9fa5]/.test(t.char));

        if (validTokens.length === 0) {
            section.classList.add('hidden');
            return;
        }

        section.classList.remove('hidden');
        container.innerHTML = '';

        validTokens.forEach(token => {
            const chip = document.createElement('div');
            const tone = token.tone || PinyinUtil.getToneFromPinyin(token.pinyin);
            chip.className = "word-chip p-3.5 bg-white rounded-xl border border-slate-200 shadow-sm hover:border-indigo-400 hover:shadow-md transition cursor-pointer flex flex-col justify-between";
            chip.innerHTML = `
                <div>
                    <div class="flex items-center justify-between gap-2 mb-1">
                        <span class="text-2xl font-bold ${this.useToneColors ? `tone-${tone}` : 'text-slate-800'}">${token.char}</span>
                        ${token.hsk ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700">HSK ${token.hsk}</span>` : ''}
                    </div>
                    <div class="text-xs font-semibold ${this.useToneColors ? `tone-${tone}` : 'text-slate-600'}">${token.pinyin}</div>
                    <div class="text-xs text-slate-800 font-semibold mt-1.5">${token.english || ''}</div>
                    ${token.malay ? `<div class="text-xs text-emerald-700 font-medium mt-0.5">🇲🇾 ${token.malay}</div>` : ''}
                </div>
                <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                    <button class="text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1" onclick="event.stopPropagation(); SpeechManager.speak('${token.char}', 'zh-CN')">
                        🔊 Sebut
                    </button>
                    <button class="text-emerald-600 hover:text-emerald-800 font-medium flex items-center gap-1" onclick="event.stopPropagation(); App.saveSingleWord('${token.char}', '${token.pinyin}', '${token.english || token.char}', '${token.malay || ''}', '${token.pos || ''}', '${token.example_zh || ''}', '${token.example_en || ''}', '${token.example_ms || ''}', ${token.hsk || 1})">
                        + Save
                    </button>
                </div>
            `;
            chip.onclick = () => this.openWordModal(token);
            container.appendChild(chip);
        });
    },

    renderGrammarTips(tips) {
        const container = document.getElementById('grammarTipsContainer');
        const section = document.getElementById('grammarTipsSection');
        if (!container || !section) return;

        if (!tips || tips.length === 0) {
            section.classList.add('hidden');
            return;
        }

        section.classList.remove('hidden');
        container.innerHTML = '';

        tips.forEach(t => {
            const card = document.createElement('div');
            card.className = "p-4 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 text-slate-800";
            card.innerHTML = `
                <div class="flex items-center gap-2 font-bold text-amber-900 mb-1">
                    <span>💡 ${t.point}</span>
                </div>
                <p class="text-xs text-amber-950 mb-2 leading-relaxed whitespace-pre-line">${t.explanation}</p>
                ${t.rule ? `<div class="p-2 bg-white/70 rounded-lg text-xs font-mono font-semibold text-amber-900 border border-amber-200/60">${t.rule}</div>` : ''}
            `;
            container.appendChild(card);
        });
    },

    async openWordDetail(char) {
        let item = this.savedVocabulary.find(v => (v.chinese === char || v.zh === char)) ||
                   (this.currentTranslationResult && this.currentTranslationResult.breakdown && this.currentTranslationResult.breakdown.find(t => t.char === char));
        if (item) {
            this.openWordModal({
                char: item.chinese || item.zh || item.char || char,
                pinyin: item.pinyin || item.py || '',
                english: item.english || item.en || '',
                malay: item.malay || item.ms || '',
                pos: item.pos || 'general',
                hsk: item.hsk || 1,
                note: item.note || '',
                example_zh: item.example_zh || item.ex_zh || '',
                example_en: item.example_en || item.ex_en || '',
                example_ms: item.example_ms || item.ex_ms || ''
            });
            return;
        }

        // Fetch from dictionary
        try {
            const res = await fetch(`/api/dictionary?q=${encodeURIComponent(char)}`);
            const data = await res.json();
            if (data.status === 'success' && data.data && data.data.length > 0) {
                const dictEntry = data.data[0];
                this.openWordModal({
                    char: dictEntry.zh,
                    pinyin: dictEntry.py,
                    english: dictEntry.en,
                    malay: dictEntry.ms || '',
                    pos: dictEntry.pos,
                    hsk: dictEntry.hsk || 1,
                    note: dictEntry.note || '',
                    example_zh: dictEntry.ex_zh || '',
                    example_en: dictEntry.ex_en || '',
                    example_ms: dictEntry.ex_ms || ''
                });
                return;
            }
        } catch (e) {
            console.error('Word lookup failed:', e);
        }

        // Fallback token modal
        this.openWordModal({
            char: char,
            pinyin: '',
            english: 'Chinese Character',
            malay: 'Tulisan Cina',
            pos: 'character',
            hsk: 1,
            note: '',
            example_zh: '',
            example_en: '',
            example_ms: ''
        });
    },

    openWordModal(token) {
        const modal = document.getElementById('wordDetailModal');
        if (!modal) return;

        document.getElementById('modalWordChinese').textContent = token.char;
        document.getElementById('modalWordPinyin').textContent = token.pinyin;
        document.getElementById('modalWordEnglish').textContent = token.english || 'Vocabulary Word';
        document.getElementById('modalWordMalay').textContent = token.malay || 'Tiada terjemahan Melayu';
        document.getElementById('modalWordPos').textContent = token.pos || 'General';
        document.getElementById('modalWordHsk').textContent = `HSK ${token.hsk || 1}`;
        document.getElementById('modalWordExZh').textContent = token.example_zh || 'No example sentence recorded.';
        document.getElementById('modalWordExEn').textContent = token.example_en ? `EN: ${token.example_en}` : '';
        document.getElementById('modalWordExMs').textContent = token.example_ms ? `BM: ${token.example_ms}` : '';
        document.getElementById('modalWordNote').textContent = token.note ? `Note: ${token.note}` : '';

        // Tone badge
        const tone = token.tone || PinyinUtil.getToneFromPinyin(token.pinyin);
        const toneBadgeEl = document.getElementById('modalWordToneBadge');
        if (toneBadgeEl) toneBadgeEl.innerHTML = PinyinUtil.getToneBadge(tone);

        // Audio buttons
        const audioBtn = document.getElementById('modalWordAudioBtn');
        if (audioBtn) {
            audioBtn.onclick = () => SpeechManager.speak(token.char, 'zh-CN');
        }

        const audioMsBtn = document.getElementById('modalWordAudioMsBtn');
        if (audioMsBtn) {
            if (token.malay) {
                audioMsBtn.classList.remove('hidden');
                audioMsBtn.onclick = () => SpeechManager.speak(token.malay, 'ms-MY');
            } else {
                audioMsBtn.classList.add('hidden');
            }
        }

        // Save button
        const saveBtn = document.getElementById('modalWordSaveBtn');
        if (saveBtn) {
            saveBtn.onclick = () => {
                this.saveSingleWord(token.char, token.pinyin, token.english, token.malay, token.pos, token.example_zh, token.example_en, token.example_ms, token.hsk);
                this.closeWordModal();
            };
        }

        modal.classList.remove('hidden');
    },

    closeWordModal() {
        const modal = document.getElementById('wordDetailModal');
        if (modal) modal.classList.add('hidden');
    },

    openAddWordModal() {
        const modal = document.getElementById('addWordModal');
        if (modal) modal.classList.remove('hidden');
    },

    closeAddWordModal() {
        const modal = document.getElementById('addWordModal');
        if (modal) modal.classList.add('hidden');
    },

    async submitNewWord() {
        const zh = document.getElementById('addWordZh').value.trim();
        const py = document.getElementById('addWordPy').value.trim();
        const en = document.getElementById('addWordEn').value.trim();
        const ms = document.getElementById('addWordMs').value.trim();
        const pos = document.getElementById('addWordPos').value.trim();

        if (!zh && !en && !ms) {
            alert('Sila masukkan sekurang-kurangnya satu perkataan (Chinese, English, or Malay).');
            return;
        }

        await this.saveSingleWord(zh, py, en, ms, pos, '', '', '', 1);
        this.closeAddWordModal();

        // Clear inputs
        document.getElementById('addWordZh').value = '';
        document.getElementById('addWordPy').value = '';
        document.getElementById('addWordEn').value = '';
        document.getElementById('addWordMs').value = '';
        document.getElementById('addWordPos').value = '';
    },

    // Save word directly to Vocabulary Database
    async saveSingleWord(chinese, pinyin, english, malay, pos, ex_zh, ex_en, ex_ms, hsk) {
        try {
            const res = await fetch('/api/vocab', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chinese: chinese,
                    pinyin: pinyin,
                    english: english,
                    malay: malay || '',
                    pos: pos || 'general',
                    example_zh: ex_zh || '',
                    example_en: ex_en || '',
                    example_ms: ex_ms || '',
                    hsk: hsk || 1
                })
            });
            const data = await res.json();
            if (data.status === 'success') {
                this.showToast(`Saved "${chinese || english || malay}" to Word Bank! ⭐`);
                this.loadVocabulary();
            }
        } catch (err) {
            this.showToast('Failed to save word.');
        }
    },

    // Save current sentence as flashcard
    async saveCurrentSentence() {
        if (!this.currentTranslationResult) return;
        const res = this.currentTranslationResult;
        let zh = '', en = '', ms = '';
        
        if (res.sourceLang === 'zh') zh = res.originalText;
        else if (res.targetLang === 'zh') zh = res.translatedText;

        if (res.sourceLang === 'en') en = res.originalText;
        else if (res.targetLang === 'en') en = res.translatedText;

        if (res.sourceLang === 'ms') ms = res.originalText;
        else if (res.targetLang === 'ms') ms = res.translatedText;

        const py = res.pinyin || '';
        await this.saveSingleWord(zh || res.originalText, py, en || res.translatedText, ms, 'sentence', zh, en, ms, 2);
    },

    // Vocabulary bank operations
    async loadVocabulary() {
        try {
            const res = await fetch('/api/vocab');
            const data = await res.json();
            if (data.status === 'success') {
                this.savedVocabulary = data.data;
                this.renderVocabList();
                FlashcardManager.setCards(this.savedVocabulary);
            }
        } catch (err) {
            console.error('Error loading vocabulary:', err);
        }
    },

    renderVocabList() {
        const listContainer = document.getElementById('vocabListContainer');
        const emptyState = document.getElementById('vocabEmptyState');
        const searchInput = document.getElementById('vocabSearchInput');
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

        if (!listContainer) return;

        let filtered = this.savedVocabulary;
        if (query) {
            filtered = filtered.filter(v => 
                (v.chinese && v.chinese.toLowerCase().includes(query)) || 
                (v.pinyin && v.pinyin.toLowerCase().includes(query)) || 
                (v.english && v.english.toLowerCase().includes(query)) ||
                (v.malay && v.malay.toLowerCase().includes(query))
            );
        }

        if (filtered.length === 0) {
            listContainer.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');
        listContainer.innerHTML = '';

        filtered.forEach(v => {
            const row = document.createElement('div');
            row.className = "p-4 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col md:flex-row md:items-center justify-between gap-4";
            
            const isMastered = v.mastered === 1;
            const badgeClass = isMastered ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800";
            const badgeText = isMastered ? "✓ Mastered" : "Needs Review";

            row.innerHTML = `
                <div class="flex items-start gap-4">
                    <button class="text-2xl hover:scale-110 transition mt-1" onclick="SpeechManager.speak('${v.chinese || v.malay || v.english}', '${v.chinese ? 'zh-CN' : (v.malay ? 'ms-MY' : 'en-US')}')">
                        🔊
                    </button>
                    <div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="text-2xl font-bold text-slate-800">${v.chinese || ''}</span>
                            <span class="text-sm font-semibold text-indigo-600">${v.pinyin || ''}</span>
                            <span class="px-2 py-0.5 rounded text-xs font-semibold ${badgeClass}">${badgeText}</span>
                            ${v.hsk ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600">HSK ${v.hsk}</span>` : ''}
                        </div>
                        <div class="flex items-center gap-3 mt-1 text-sm flex-wrap">
                            <span class="text-slate-800 font-semibold">EN: ${v.english || '-'}</span>
                            <span class="text-slate-300">|</span>
                            <span class="text-emerald-700 font-bold">BM: ${v.malay || '-'}</span>
                        </div>
                        ${v.example_zh || v.example_ms ? `<p class="text-xs text-slate-500 mt-1 italic">${v.example_zh} ${v.example_ms ? `(BM: ${v.example_ms})` : ''}</p>` : ''}
                    </div>
                </div>
                <div class="flex items-center gap-2 self-end md:self-center">
                    <button class="px-3 py-1.5 rounded-lg text-xs font-semibold border ${isMastered ? 'border-amber-400 text-amber-700 hover:bg-amber-50' : 'border-emerald-500 text-emerald-700 hover:bg-emerald-50'} transition" onclick="App.toggleVocabStatus(${v.id})">
                        ${isMastered ? 'Mark Review' : 'Mark Mastered'}
                    </button>
                    <button class="p-1.5 text-slate-400 hover:text-rose-600 transition" onclick="App.deleteVocabWord(${v.id})">
                        🗑️
                    </button>
                </div>
            `;
            listContainer.appendChild(row);
        });
    },

    async toggleVocabStatus(id) {
        await fetch('/api/vocab/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        });
        this.loadVocabulary();
    },

    async deleteVocabWord(id) {
        if (!confirm('Are you sure you want to delete this word from your vocabulary bank?')) return;
        await fetch(`/api/vocab?id=${id}`, { method: 'DELETE' });
        this.showToast('Word removed from vocabulary bank.');
        this.loadVocabulary();
    },

    // Load grammar & tatabahasa guide
    async loadGrammarRules(langFilter = '') {
        try {
            const url = langFilter ? `/api/grammar?lang=${langFilter}` : '/api/grammar';
            const res = await fetch(url);
            const data = await res.json();
            if (data.status === 'success') {
                const container = document.getElementById('grammarGuideList');
                if (!container) return;
                container.innerHTML = '';
                data.data.forEach(rule => {
                    const card = document.createElement('div');
                    const isMalay = rule.lang === 'ms';
                    card.className = `p-5 bg-white rounded-2xl border ${isMalay ? 'border-emerald-200' : 'border-indigo-100'} shadow-sm hover:shadow-md transition`;
                    card.innerHTML = `
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="font-bold text-slate-900 text-base md:text-lg">${rule.title}</h3>
                            <span class="text-xs font-semibold px-2 py-1 rounded ${isMalay ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-50 text-indigo-700'}">${rule.title_zh}</span>
                        </div>
                        <p class="text-slate-600 text-sm leading-relaxed whitespace-pre-line mb-3">${rule.explanation}</p>
                        <div class="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
                            <div>
                                <div class="text-sm font-bold text-slate-800">${rule.example_zh}</div>
                                <div class="text-xs text-slate-500">${rule.example_en}</div>
                            </div>
                            <button class="text-slate-500 hover:text-indigo-600" onclick="SpeechManager.speak('${rule.example_zh.replace(/\(.*?\)/g, '')}', '${isMalay ? 'ms-MY' : 'zh-CN'}')">
                                🔊
                            </button>
                        </div>
                    `;
                    container.appendChild(card);
                });
            }
        } catch (err) {
            console.error('Error loading grammar:', err);
        }
    },

    filterGrammarRules(lang) {
        this.loadGrammarRules(lang);
    },

    // Save Gemini API key
    saveApiKey() {
        const input = document.getElementById('geminiApiKeyInput');
        if (input) {
            const key = input.value.trim();
            this.geminiApiKey = key;
            localStorage.setItem('gemini_api_key', key);
            this.showToast(key ? 'Gemini AI API key saved! 🤖' : 'API key cleared.');
            this.toggleSettingsModal(false);
        }
    },

    toggleSettingsModal(show) {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            if (show) {
                const input = document.getElementById('geminiApiKeyInput');
                if (input) input.value = this.geminiApiKey;
                modal.classList.remove('hidden');
            } else {
                modal.classList.add('hidden');
            }
        }
    },

    showToast(message) {
        let toast = document.getElementById('appToastNotification');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'appToastNotification';
            toast.className = "fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl bg-slate-900 text-white text-sm font-medium shadow-xl transition transform duration-300 opacity-0 pointer-events-none";
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.classList.remove('opacity-0', 'pointer-events-none');
        setTimeout(() => {
            toast.classList.add('opacity-0', 'pointer-events-none');
        }, 3000);
    }
};

window.addEventListener('DOMContentLoaded', () => {
    App.init();
});
