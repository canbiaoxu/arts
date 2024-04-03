show = (src) => {event.preventDefault(); window.open(src, '_blank')}
{
    if (typeof media !== "undefined") {
        let video_template = `<div><video loading="lazy" controls onclick="show('{{src}}')"><source src='{{src}}' type='video/mp4'></video></div>`
        let img_template = `<div><img loading="lazy" src='{{src}}' onclick="show('{{src}}')"></div>`
        let content = []
        let video_suffixes = ['mp4']
        let img_suffixes = ['jpg', 'png']
        for (let src of media) {
            let suffix = src.match(/\.([^.]+)$/)
            if (suffix) {
                if (video_suffixes.includes(suffix[1]))
                    {content.push(video_template.replace(/{{src}}/g, src))}
                else if (img_suffixes.includes(suffix[1]))
                    {content.push(img_template.replace(/{{src}}/g, src))}
            }
        }
        let ch_15 = document.createElement('div')
        ch_15.id = 'ch_15'
        ch_15.innerHTML += content.join('\n')
        document.body.appendChild(ch_15)
    }
}
document.body.getElementsByTagName('pre')[0].addEventListener('dblclick', () => {window.open(document.URL, '_blank')})
document.title = decodeURIComponent(document.URL).match(/\/(\d*\s*-\s*)?([^/\\]+)\/?$/)[2]