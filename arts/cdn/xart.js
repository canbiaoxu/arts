window.xart = {}

xart.video_template = `<div><video loading="lazy" src='{{src}}' controls onclick="xart.show('{{src}}')"></video></div>`
xart.img_template = `<div><img loading="lazy" src='{{src}}' onclick="xart.show('{{src}}')"></div>`
xart.audio_template = `<audio loading="lazy" controls src="{{src}}"></audio>`

xart.big_video_template = `<video loading="lazy" src='{{src}}' controls onclick="xart.show('{{src}}')"></video>`
xart.big_img_template = `<img loading="lazy" src='{{src}}' onclick="xart.show('{{src}}')">`

xart.art_title = `<h1>{{title}}</h1>`
xart.min_title = `<mintitle>{{title}}</mintitle>`
xart.go_home_box = `<div class='go_home_box'>\n<button class="go_home" onclick="xart.show('/')">我的主页</button> 👈</div>`
xart.portrait_template = `<img class="portrait" loading="lazy" src='{{src}}'>`

xart.show = (src) => {event.preventDefault(); window.open(src, '_blank')}

xart.video_suffixes = ['mp4']
xart.img_suffixes = ['jpg', 'png', 'jpeg']
xart.audio_suffixes = ['flac', 'mp3', 'ogg']

xart.modify_src = (src) => {return src}

xart.media = (srcs) => {
    if (srcs) {
        let content = []
        for (let src of srcs) {
            let suffix = src.match(/\.([^.]+)$/)
            src = xart.modify_src(src)
            if (suffix) {
                suffix = suffix[1]
                if (xart.video_suffixes.includes(suffix))
                    {content.push(xart.video_template.replace(/{{src}}/g, src))}
                else if (xart.img_suffixes.includes(suffix))
                    {content.push(xart.img_template.replace(/{{src}}/g, src))}
                else if (xart.audio_suffixes.includes(suffix)) {
                    {content.push(xart.audio_template.replace(/{{src}}/g, src))}
                }
            }
        }
        let ele = document.createElement('div')
        ele.classList.add('ch_15')
        ele.innerHTML += content.join('\n')
        let currentScript = document.currentScript; currentScript.parentElement.insertBefore(ele, currentScript)
    }
}

xart.big_media = (srcs) => {
    if (srcs) {
        let content = []
        for (let src of srcs) {
            let suffix = src.match(/\.([^.]+)$/)
            src = xart.modify_src(src)
            if (suffix) {
                suffix = suffix[1]
                if (xart.video_suffixes.includes(suffix))
                    {content.push(xart.big_video_template.replace(/{{src}}/g, src))}
                else if (xart.img_suffixes.includes(suffix))
                    {content.push(xart.big_img_template.replace(/{{src}}/g, src))}
                else if (xart.audio_suffixes.includes(suffix)) {
                    {content.push(xart.audio_template.replace(/{{src}}/g, src))}
                }
            }
        }
        let ele = document.createElement('div')
        ele.classList.add('ch_16')
        ele.innerHTML += content.join('\n')
        let currentScript = document.currentScript; currentScript.parentElement.insertBefore(ele, currentScript)
    }
}

xart.avatar = (src) => {
    document.currentScript.parentElement.innerHTML += xart.portrait_template.replace(/{{src}}/g, xart.modify_src(src))
}

xart.clean_text = (text) => text.replace(/\s*\\\s*/g, '').trim()

xart.render = (author=true, title=true, mintitle=false) => {
    if (!document.title) {try { document.title = decodeURIComponent(document.URL).match(/\/([\d\s]*-)?\s*([^/]+)\/[^/]*\.html$/)[2] } catch (e) {}}
    let pre = document.querySelector('body > pre')
    for (let ele of document.querySelectorAll('quote')) {ele.innerHTML = ele.innerHTML.trim()}
    for (let ele of document.querySelectorAll('pre')) {if (ele !== pre) {ele.innerHTML = xart.clean_text(ele.innerHTML)}}
    {
        let innerHTML = xart.clean_text(pre.innerHTML)
        if (window.self === window.top) {
            if (title) {innerHTML = xart.art_title.replace(/{{title}}/g, document.title) + '\n\n' + innerHTML}
            if (author) {innerHTML += xart.go_home_box}
        }
        else {
            if (mintitle) {innerHTML = xart.min_title.replace(/{{title}}/g, document.title) + '\n\n' + innerHTML}
        }
        pre.innerHTML = innerHTML
    }
    // 置底
    for (let ele of document.querySelectorAll('textarea.code')) {ele.innerHTML = ele.innerHTML.trim(); ele.style.height = ele.scrollHeight + 'px'}
    pre.addEventListener('dblclick', () => {window.open(document.URL, '_blank')})
}

{
    const iframe = window.frameElement
    if (iframe) {
        const resizeObserver = new ResizeObserver(entries => {
            iframe.style.height = `${entries[0].contentRect.height}px`
        })
        resizeObserver.observe(document.documentElement)
    }
}