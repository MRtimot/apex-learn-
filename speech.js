// Speech Synthesis helper for Mandarin Chinese, English, and Bahasa Melayu
const SpeechManager = {
    synth: window.speechSynthesis,
    currentSpeed: 1.0,
    voices: [],

    init() {
        if (!('speechSynthesis' in window)) {
            console.warn('Speech synthesis not supported in this browser.');
            return;
        }
        this.loadVoices();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = () => this.loadVoices();
        }
    },

    loadVoices() {
        if (!this.synth) return;
        this.voices = this.synth.getVoices();
    },

    getVoiceForLanguage(langCode) {
        if (!this.voices || this.voices.length === 0) {
            this.loadVoices();
        }
        
        // Priority for Chinese
        if (langCode.startsWith('zh')) {
            const zhVoice = this.voices.find(v => v.lang === 'zh-CN') ||
                            this.voices.find(v => v.lang.startsWith('zh')) ||
                            this.voices.find(v => v.name.includes('Chinese') || v.name.includes('Mandarin') || v.name.includes('Tingting') || v.name.includes('Meijia') || v.name.includes('Sin-ji'));
            return zhVoice;
        }

        // Priority for Bahasa Melayu (fallback to id-ID Indonesian if ms-MY not installed on user's OS)
        if (langCode.startsWith('ms') || langCode.startsWith('id')) {
            const msVoice = this.voices.find(v => v.lang === 'ms-MY') ||
                            this.voices.find(v => v.lang.startsWith('ms')) ||
                            this.voices.find(v => v.lang === 'id-ID') ||
                            this.voices.find(v => v.lang.startsWith('id')) ||
                            this.voices.find(v => v.name.toLowerCase().includes('malay') || v.name.toLowerCase().includes('indonesian') || v.name.toLowerCase().includes('damayanti'));
            return msVoice;
        }

        // Priority for English
        if (langCode.startsWith('en')) {
            const enVoice = this.voices.find(v => v.lang === 'en-US') ||
                            this.voices.find(v => v.lang.startsWith('en')) ||
                            this.voices.find(v => v.name.includes('Samantha') || v.name.includes('Google US English') || v.name.includes('Daniel'));
            return enVoice;
        }

        return null;
    },

    speak(text, lang = null, onStart = null, onEnd = null) {
        if (!this.synth) {
            alert('Audio speech playback is not supported by your browser.');
            return;
        }

        this.synth.cancel();

        if (!text || !text.trim()) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.currentSpeed;
        utterance.pitch = 1.0;

        let targetLang = lang;
        if (!targetLang) {
            const hasChinese = /[\u4e00-\u9fa5]/.test(text);
            targetLang = hasChinese ? 'zh-CN' : 'en-US';
        }
        utterance.lang = targetLang;

        const voice = this.getVoiceForLanguage(targetLang);
        if (voice) {
            utterance.voice = voice;
        }

        if (onStart) utterance.onstart = onStart;
        if (onEnd) {
            utterance.onend = onEnd;
            utterance.onerror = onEnd;
        }

        this.synth.speak(utterance);
    },

    stop() {
        if (this.synth) {
            this.synth.cancel();
        }
    },

    setSpeed(speed) {
        this.currentSpeed = parseFloat(speed) || 1.0;
    }
};

window.addEventListener('DOMContentLoaded', () => {
    SpeechManager.init();
});
