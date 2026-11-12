// Pinyin and Ruby Annotation Utility
const PinyinUtil = {
    // Determine tone number from pinyin syllable with tone mark
    getToneFromPinyin(syllable) {
        if (!syllable) return 5;
        const s = syllable.toLowerCase();
        if (/[āēīōūǖ]/.test(s)) return 1;
        if (/[áéíóúǘ]/.test(s)) return 2;
        if (/[ǎěǐǒǔǚ]/.test(s)) return 3;
        if (/[àèìòùǜ]/.test(s)) return 4;
        return 5;
    },

    // Convert Chinese text + breakdown tokens into styled ruby markup
    renderRubyHtml(breakdownTokens, useColors = true) {
        if (!breakdownTokens || breakdownTokens.length === 0) return '';

        return breakdownTokens.map(token => {
            const char = token.char;
            const pinyin = token.pinyin;
            
            // If punctuation or non-Chinese, just return plain text
            if (!pinyin || !/[\u4e00-\u9fa5]/.test(char)) {
                return `<span class="text-slate-600">${char}</span>`;
            }

            // Word with multiple characters or single character
            const pinyinWords = pinyin.split(' ');
            
            // If word is multi-character (like "学生" with "xué sheng")
            if (char.length > 1 && pinyinWords.length === char.length) {
                return char.split('').map((c, idx) => {
                    const py = pinyinWords[idx] || '';
                    const tone = this.getToneFromPinyin(py);
                    const colorClass = useColors ? `tone-${tone}` : 'text-slate-800';
                    return `<ruby class="${colorClass} hover:opacity-80 transition cursor-pointer select-text" onclick="App.openWordDetail('${char}')">
                        <span class="text-2xl md:text-3xl font-medium">${c}</span>
                        <rt class="text-xs ${useColors ? `tone-${tone}` : 'text-slate-500'} font-semibold">${py}</rt>
                    </ruby>`;
                }).join('');
            }

            const tone = token.tone || this.getToneFromPinyin(pinyin);
            const colorClass = useColors ? `tone-${tone}` : 'text-slate-800';

            return `<ruby class="${colorClass} hover:opacity-80 transition cursor-pointer select-text" onclick="App.openWordDetail('${char}')">
                <span class="text-2xl md:text-3xl font-medium">${char}</span>
                <rt class="text-xs ${useColors ? `tone-${tone}` : 'text-slate-500'} font-semibold">${pinyin}</rt>
            </ruby>`;
        }).join(' ');
    },

    // Tone guide pill badge
    getToneBadge(tone) {
        const toneNames = {
            1: "1st Tone (High Flat: ā)",
            2: "2nd Tone (Rising: á)",
            3: "3rd Tone (Falling-Rising: ǎ)",
            4: "4th Tone (Falling: à)",
            5: "Neutral Tone (Light: a)"
        };
        return `<span class="px-2 py-0.5 rounded text-xs font-semibold tone-badge-${tone}">${toneNames[tone] || 'Neutral'}</span>`;
    }
};
