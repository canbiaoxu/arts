"use strict";

class Multi_tts {
    constructor() {
        this.languages = {
            '英': { lang: 'en-GB', voice: null },
            '美': { lang: 'en-US', voice: null },
            '普': { lang: 'zh-CN', voice: null },
            '日': { lang: 'ja-JP', voice: null },
        }
    }

    async speak(text, lang_mark = '普', rate = 1.0, clear_speech_queue = false) {
        /*
        rate推荐值：
            普通话：1.0
            英文：1.1
            日语：0.9
        */
        let language = this.languages[lang_mark]
        if (!language['voice']) {
            let lang = language['lang']
            console.log(`查找 ${lang} Natural`)
            for (let voice of window.speechSynthesis.getVoices()) {
                if (voice.lang.startsWith(lang) && voice.name.includes('Natural')) {
                    language['voice'] = voice
                    break
                }
            }
        }
        let voice = language['voice']
        let utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = language.lang
        utterance.rate = Math.min(Math.max(rate, 0.5), 2)
        utterance.volume = 1
        if (voice) {
            utterance.voice = voice
        }
        return new Promise((resolve, reject) => {
            utterance.onend = () => resolve({})
            utterance.onerror = (event) => reject(new Error(`朗读失败：${event.error}`))
            if (clear_speech_queue) {
                window.speechSynthesis.cancel()
            }
            window.speechSynthesis.speak(utterance)
        })
    }
}

window.tts = new Multi_tts()
