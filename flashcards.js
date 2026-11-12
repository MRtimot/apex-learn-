// Flashcards & Interactive Practice Quiz System (Trilingual Support)
const FlashcardManager = {
    cards: [],
    currentIndex: 0,
    isFlipped: false,
    showPinyin: true,

    // Quiz state
    quizQuestions: [],
    quizIndex: 0,
    quizScore: 0,
    quizStreak: 0,
    quizMode: 'all',
    userAnswers: [],

    init(vocabList) {
        this.cards = vocabList || [];
        this.currentIndex = 0;
        this.isFlipped = false;
        this.renderCard();
        this.updateStats();
    },

    setCards(cards) {
        this.cards = cards;
        this.currentIndex = 0;
        this.isFlipped = false;
        this.renderCard();
        this.updateStats();
    },

    flip() {
        this.isFlipped = !this.isFlipped;
        const inner = document.getElementById('flashcardInner');
        if (inner) {
            if (this.isFlipped) {
                inner.classList.add('is-flipped');
            } else {
                inner.classList.remove('is-flipped');
            }
        }
    },

    togglePinyinVisibility() {
        this.showPinyin = !this.showPinyin;
        const pyEl = document.getElementById('cardPinyinFront');
        const toggleBtn = document.getElementById('pinyinToggleBtn');
        if (pyEl) {
            pyEl.style.display = this.showPinyin ? 'block' : 'none';
        }
        if (toggleBtn) {
            toggleBtn.textContent = this.showPinyin ? 'Hide Pinyin' : 'Show Pinyin';
        }
    },

    nextCard() {
        if (this.cards.length === 0) return;
        this.currentIndex = (this.currentIndex + 1) % this.cards.length;
        this.resetFlip();
        this.renderCard();
    },

    prevCard() {
        if (this.cards.length === 0) return;
        this.currentIndex = (this.currentIndex - 1 + this.cards.length) % this.cards.length;
        this.resetFlip();
        this.renderCard();
    },

    shuffle() {
        for (let i = this.cards.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.cards[i], this.cards[j]] = [this.cards[j], this.cards[i]];
        }
        this.currentIndex = 0;
        this.resetFlip();
        this.renderCard();
        App.showToast('Flashcards shuffled! 🔀');
    },

    resetFlip() {
        this.isFlipped = false;
        const inner = document.getElementById('flashcardInner');
        if (inner) inner.classList.remove('is-flipped');
    },

    renderCard() {
        const frontZh = document.getElementById('cardChineseFront');
        const frontPy = document.getElementById('cardPinyinFront');
        const backEn = document.getElementById('cardEnglishBack');
        const backMs = document.getElementById('cardMalayBack');
        const backZh = document.getElementById('cardChineseBack');
        const backPy = document.getElementById('cardPinyinBack');
        const backPos = document.getElementById('cardPosBack');
        const backHsk = document.getElementById('cardHskBack');
        const backExZh = document.getElementById('cardExZhBack');
        const backExEn = document.getElementById('cardExEnBack');
        const backExMs = document.getElementById('cardExMsBack');
        const cardCounter = document.getElementById('cardCounter');

        if (!this.cards || this.cards.length === 0) {
            if (frontZh) frontZh.textContent = "No cards yet";
            if (frontPy) frontPy.textContent = "Save words from the translator to build your deck!";
            if (backEn) backEn.textContent = "Save words to start studying!";
            if (cardCounter) cardCounter.textContent = "0 / 0";
            return;
        }

        const card = this.cards[this.currentIndex];
        const chinese = card.chinese || card.zh || '';
        const pinyin = card.pinyin || card.py || '';
        const english = card.english || card.en || '';
        const malay = card.malay || card.ms || '';
        const pos = card.pos || '';
        const hsk = card.hsk || 1;
        const exZh = card.example_zh || card.ex_zh || '';
        const exEn = card.example_en || card.ex_en || '';
        const exMs = card.example_ms || card.ex_ms || '';

        if (frontZh) frontZh.textContent = chinese;
        if (frontPy) frontPy.textContent = pinyin;
        if (cardCounter) cardCounter.textContent = `${this.currentIndex + 1} / ${this.cards.length}`;

        if (backZh) backZh.textContent = chinese;
        if (backPy) backPy.textContent = pinyin;
        if (backEn) backEn.textContent = english;
        if (backMs) backMs.textContent = malay ? `BM: ${malay}` : '';
        if (backPos) backPos.textContent = pos;
        if (backHsk) backHsk.textContent = `HSK ${hsk}`;
        if (backExZh) backExZh.textContent = exZh;
        if (backExEn) backExEn.textContent = exEn ? `EN: ${exEn}` : '';
        if (backExMs) backExMs.textContent = exMs ? `BM: ${exMs}` : '';

        // Front Audio button (Chinese)
        const audioBtn = document.getElementById('cardAudioFront');
        if (audioBtn) {
            audioBtn.onclick = (e) => {
                e.stopPropagation();
                SpeechManager.speak(chinese, 'zh-CN');
            };
        }
        
        // Back Audio button (speaks English or Malay)
        const audioBtnBack = document.getElementById('cardAudioBack');
        if (audioBtnBack) {
            audioBtnBack.onclick = (e) => {
                e.stopPropagation();
                SpeechManager.speak(english, 'en-US');
            };
        }

        // Back Malay Audio button
        const audioBtnBackMs = document.getElementById('cardAudioBackMs');
        if (audioBtnBackMs) {
            if (malay) {
                audioBtnBackMs.classList.remove('hidden');
                audioBtnBackMs.onclick = (e) => {
                    e.stopPropagation();
                    SpeechManager.speak(malay, 'ms-MY');
                };
            } else {
                audioBtnBackMs.classList.add('hidden');
            }
        }
    },

    updateStats() {
        const mastered = this.cards.filter(c => c.mastered === 1).length;
        const total = this.cards.length;
        const percent = total > 0 ? Math.round((mastered / total) * 100) : 0;

        const statTotal = document.getElementById('statTotalCards');
        const statMastered = document.getElementById('statMasteredCards');
        const statPercent = document.getElementById('statPercentProgress');
        const progressBar = document.getElementById('deckProgressBar');

        if (statTotal) statTotal.textContent = total;
        if (statMastered) statMastered.textContent = mastered;
        if (statPercent) statPercent.textContent = `${percent}%`;
        if (progressBar) progressBar.style.width = `${percent}%`;
    },

    async markCardMastered(isMastered) {
        if (!this.cards || this.cards.length === 0) return;
        const card = this.cards[this.currentIndex];
        if (card && card.id) {
            await fetch('/api/vocab/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: card.id })
            });
            card.mastered = isMastered ? 1 : 0;
            this.updateStats();
            App.loadVocabulary();
        }
        this.nextCard();
    },

    // ================= QUIZ MODE =================
    async startQuiz(count = 5, mode = 'all') {
        this.quizMode = mode;
        const quizContainer = document.getElementById('quizActiveArea');
        const quizSummary = document.getElementById('quizSummaryArea');
        const quizLoading = document.getElementById('quizLoading');

        if (quizSummary) quizSummary.classList.add('hidden');
        if (quizContainer) quizContainer.classList.add('hidden');
        if (quizLoading) quizLoading.classList.remove('hidden');

        try {
            const res = await fetch(`/api/quiz?count=${count}&mode=${mode}`);
            const data = await res.json();
            if (data.status === 'success' && data.questions.length > 0) {
                this.quizQuestions = data.questions;
                this.quizIndex = 0;
                this.quizScore = 0;
                this.quizStreak = 0;
                this.userAnswers = [];
                
                if (quizLoading) quizLoading.classList.add('hidden');
                if (quizContainer) quizContainer.classList.remove('hidden');
                this.renderQuizQuestion();
            } else {
                alert('Could not generate quiz. Please save more words or try again.');
                if (quizLoading) quizLoading.classList.add('hidden');
            }
        } catch (err) {
            console.error('Quiz start error:', err);
            if (quizLoading) quizLoading.classList.add('hidden');
        }
    },

    renderQuizQuestion() {
        const q = this.quizQuestions[this.quizIndex];
        if (!q) {
            this.finishQuiz();
            return;
        }

        const qProgress = document.getElementById('quizProgress');
        const qScore = document.getElementById('quizScoreText');
        const qTitle = document.getElementById('quizQuestionTypeTitle');
        const qPrompt = document.getElementById('quizPrompt');
        const qSubprompt = document.getElementById('quizSubprompt');
        const qPinyin = document.getElementById('quizPinyin');
        const qOptions = document.getElementById('quizOptionsContainer');
        const qAudio = document.getElementById('quizAudioBtn');
        const qFeedback = document.getElementById('quizFeedback');
        const qNextBtn = document.getElementById('quizNextBtn');

        if (qProgress) qProgress.textContent = `Question ${this.quizIndex + 1} of ${this.quizQuestions.length}`;
        if (qScore) qScore.textContent = `Score: ${this.quizScore} | Streak: ${this.quizStreak} 🔥`;
        if (qTitle) qTitle.textContent = q.title || 'Language Quiz';
        if (qPrompt) qPrompt.textContent = q.prompt;
        if (qSubprompt) qSubprompt.textContent = q.subprompt || '';
        if (qPinyin) qPinyin.textContent = q.pinyin || '';
        
        if (qFeedback) {
            qFeedback.classList.add('hidden');
            qFeedback.innerHTML = '';
        }
        if (qNextBtn) qNextBtn.classList.add('hidden');

        // Pronounce prompt in correct voice
        if (qAudio) {
            qAudio.classList.remove('hidden');
            qAudio.onclick = () => {
                if (/[\u4e00-\u9fa5]/.test(q.prompt)) {
                    SpeechManager.speak(q.prompt, 'zh-CN');
                } else if (q.type && q.type.startsWith('ms')) {
                    SpeechManager.speak(q.prompt, 'ms-MY');
                } else {
                    SpeechManager.speak(q.prompt, 'en-US');
                }
            };
        }

        // Render options
        if (qOptions) {
            qOptions.innerHTML = '';
            q.options.forEach((opt) => {
                const btn = document.createElement('button');
                btn.className = "w-full text-left p-4 rounded-xl border-2 border-slate-200 hover:border-indigo-500 hover:bg-indigo-50/50 transition font-medium text-slate-800 text-lg flex items-center justify-between group";
                btn.innerHTML = `
                    <span>${opt}</span>
                    <span class="w-6 h-6 rounded-full border border-slate-300 group-hover:border-indigo-500 flex items-center justify-center text-xs text-transparent group-hover:text-indigo-600">●</span>
                `;
                btn.onclick = () => this.handleAnswer(opt, btn);
                qOptions.appendChild(btn);
            });
        }
    },

    handleAnswer(selectedOption, clickedBtn) {
        const q = this.quizQuestions[this.quizIndex];
        const isCorrect = selectedOption === q.answer;
        const qOptions = document.getElementById('quizOptionsContainer');
        const qFeedback = document.getElementById('quizFeedback');
        const qNextBtn = document.getElementById('quizNextBtn');
        const qScore = document.getElementById('quizScoreText');

        // Disable all option buttons
        const allButtons = qOptions.querySelectorAll('button');
        allButtons.forEach(btn => {
            btn.disabled = true;
            const text = btn.querySelector('span').textContent;
            if (text === q.answer) {
                btn.className = "w-full text-left p-4 rounded-xl border-2 border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold text-lg flex items-center justify-between";
                btn.innerHTML = `<span>${text}</span> <span class="text-emerald-600 font-bold">✓ Betul / Correct</span>`;
            } else if (btn === clickedBtn) {
                btn.className = "w-full text-left p-4 rounded-xl border-2 border-rose-500 bg-rose-50 text-rose-900 font-semibold text-lg flex items-center justify-between";
                btn.innerHTML = `<span>${text}</span> <span class="text-rose-600 font-bold">✗ Salah / Incorrect</span>`;
            } else {
                btn.className = "w-full text-left p-4 rounded-xl border-2 border-slate-200 bg-slate-50 text-slate-400 font-medium text-lg flex items-center justify-between";
            }
        });

        if (isCorrect) {
            this.quizScore += 10;
            this.quizStreak += 1;
            if (qScore) qScore.textContent = `Score: ${this.quizScore} | Streak: ${this.quizStreak} 🔥`;
            if (qFeedback) {
                qFeedback.className = "p-4 rounded-xl bg-emerald-100 text-emerald-800 text-sm font-medium mt-4";
                qFeedback.innerHTML = `🎉 Syabas / Correct! ${q.explanation}`;
                qFeedback.classList.remove('hidden');
            }
        } else {
            this.quizStreak = 0;
            if (qScore) qScore.textContent = `Score: ${this.quizScore} | Streak: 0`;
            if (qFeedback) {
                qFeedback.className = "p-4 rounded-xl bg-rose-100 text-rose-800 text-sm font-medium mt-4";
                qFeedback.innerHTML = `💡 Penerangan / Explanation: ${q.explanation}`;
                qFeedback.classList.remove('hidden');
            }
        }

        if (qNextBtn) {
            qNextBtn.classList.remove('hidden');
            qNextBtn.onclick = () => {
                this.quizIndex++;
                this.renderQuizQuestion();
            };
        }
    },

    finishQuiz() {
        const quizActive = document.getElementById('quizActiveArea');
        const quizSummary = document.getElementById('quizSummaryArea');
        const finalScore = document.getElementById('quizFinalScore');
        const finalMsg = document.getElementById('quizFinalMessage');

        if (quizActive) quizActive.classList.add('hidden');
        if (quizSummary) quizSummary.classList.remove('hidden');

        const totalQ = this.quizQuestions.length;
        const maxScore = totalQ * 10;
        const percentage = Math.round((this.quizScore / maxScore) * 100);

        if (finalScore) finalScore.textContent = `${this.quizScore} / ${maxScore} (${percentage}%)`;

        let msg = "Great effort! Practice trilingual words daily to master tones and vocabulary!";
        if (percentage >= 90) msg = "🌟 Tahniah & Outstanding! Your Trilingual English-Chinese-Malay mastery is top tier!";
        else if (percentage >= 70) msg = "👏 Syabas / Well done! You are building great multilingual skills!";
        else if (percentage >= 50) msg = "💪 Good practice! Review the flashcards to strengthen weak spots.";

        if (finalMsg) finalMsg.textContent = msg;
    }
};
