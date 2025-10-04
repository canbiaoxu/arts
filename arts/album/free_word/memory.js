"use strict";

let db
let is_new_db = false

class Memory {
    constructor(notes) {
        this.notes = notes
        this.add_setp_ratio = 1.2;
        this.sub_setp_ratio = 1.2;
    }

    async fetch_next_note() {
        return this.notes[0]
    }

    async handle_remember() {
        const note = this.notes.shift();
        const old_aim_setp = note.aim_setp;
        const real_setp = note.pre_real_setp;

        note.aim_setp = Math.max(
            real_setp * this.add_setp_ratio,
            real_setp + 1,
            old_aim_setp
        );

        note.pre_real_setp = Math.min(Math.floor(note.aim_setp), this.notes.length);
        this.notes.splice(note.pre_real_setp, 0, note);
        await window.save_notes(this.notes)
    }

    async handle_forget() {
        const note = this.notes.shift();
        const old_aim_setp = note.aim_setp;
        const real_setp = note.pre_real_setp;

        note.aim_setp = Math.max(1, Math.min(
            real_setp / this.sub_setp_ratio,
            real_setp - 1,
            old_aim_setp
        ));

        note.pre_real_setp = Math.min(Math.floor(note.aim_setp), this.notes.length);
        this.notes.splice(note.pre_real_setp, 0, note);
        await window.save_notes(this.notes)
    }

    async handle_master() {
        const note = this.notes.shift();
        const old_aim_setp = note.aim_setp;

        note.aim_setp = Math.max(
            this.notes.length,
            old_aim_setp
        );

        note.pre_real_setp = Math.min(Math.floor(note.aim_setp), this.notes.length);
        this.notes.push(note);
        await window.save_notes(this.notes)
    }

    async handle_tobottom() {
        const note = this.notes.shift();
        note.pre_real_setp = this.notes.length;
        this.notes.push(note);
        await window.save_notes(this.notes)
    }

    async handle_delete() {
        this.notes.shift();
        await window.save_notes(this.notes)
    }

    async feedback_and_fetch(previous_state = null) {
        if (previous_state) {
            switch (previous_state) {
                case "tobottom":
                    await this.handle_tobottom();
                    break;
                case "master":
                    await this.handle_master();
                    break;
                case "forget":
                    await this.handle_forget();
                    break;
                case "remember":
                    await this.handle_remember();
                    break;
            }
        }
        return { word: (await this.fetch_next_note()).word };
    }
}

window.save_notes = async (notes) => {
    const tx = db.transaction("words_sort", "readwrite")
    const store = tx.objectStore("words_sort")
    store.put({ key: 'notes', value: notes })
    tx.oncomplete = () => {}
    tx.onerror = e => console.error("保存进度失败:", e.target.error)
}

window.read_notes = async () => {
    return await new Promise((resolve, reject) => {
        const tx = db.transaction("words_sort", "readonly")
        const store = tx.objectStore("words_sort")
        const request = store.get('notes')
        request.onsuccess = () => {
            const result = request.result
            if (result) {
                resolve(result.value)
            } else {
                resolve(null)
            }
        }
        request.onerror = (e) => reject(e.target.error)
    })
}

window.request_ai_answer_then_save = async (word) => {
    // await 并不会中断 “整个主程序”，只会中断当前 async 函数的执行流程；而不加 await 时，未处理的错误确实只会在控制台警告，不影响任何执行流程。

    // 获取实时答案
    let encoded_prompt = encodeURIComponent(`单词\`${word}\`是什么意思？`)
    let api_url = `https://text.pollinations.ai/openai/${encoded_prompt}`
    let answer = await (await fetch(api_url)).text()

    // 存储答案
    const tx = db.transaction("ai_answers", "readwrite")
    const store = tx.objectStore("ai_answers")
    store.put({ key: word, value: answer })
    tx.oncomplete = () => {}
    tx.onerror = e => console.error("保存ai回答失败:", e.target.error)
}

window.read_ai_answer = async (word) => {
    return await new Promise((resolve, reject) => {
        const tx = db.transaction("ai_answers", "readonly")
        const store = tx.objectStore("ai_answers")
        const request = store.get(word)
        request.onsuccess = () => {
            const result = request.result
            if (result) {
                resolve(result.value)
            } else {
                resolve('')  // 主键不存在时返回空字符串
            }
        }
        request.onerror = (e) => reject(e.target.error)
    })
}

const request = indexedDB.open("github.com.canbiaoxu.arts.free_word.v1", 1)
// 库名不能包含斜杠`/`

request.onupgradeneeded = function (event) {
    // onupgradeneeded比onsuccess先执行
    // 触发时机：数据库不存在、数据库版本号增加
    is_new_db = true
    db = event.target.result
    if (!db.objectStoreNames.contains("words_sort")) {
        db.createObjectStore("words_sort", { keyPath: "key" }) // 创建对象存储，并设置key为主键
    }
    if (!db.objectStoreNames.contains("ai_answers")) {
        db.createObjectStore("ai_answers", { keyPath: "key" })
    }
}

request.onsuccess = async function (event) {
    db = event.target.result;
    if (is_new_db) {
        let all_word = await (await fetch('all_word.json')).json()
        let notes = all_word.map((word, i) => ({
            word: word,
            aim_setp: 1,
            pre_real_setp: i
        }))
        await window.save_notes(notes)
        window.english = new Memory(notes)
        console.log("已加载新进度")
    }
    else {
        let notes = await window.read_notes()
        window.english = new Memory(notes)
        console.log("已加载原进度")
    }
    await window.show_first_word()
}

request.onerror = function (event) {
    console.error("打开数据库失败:", event.target.error);
}