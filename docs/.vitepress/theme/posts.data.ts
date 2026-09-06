import { createContentLoader, type ContentData } from 'vitepress'

export interface Post {
  title: string
  date: string | null
  url: string
  excerpt: string
}

declare const data: Post[]
export { data }

function toPlainText(src: string): string {
  return src
    .replace(/^---[\s\S]*?---\s*/, '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]+>/g, ' ')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/^[-*+]\s+/gm, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function excerptOf(src: string, max = 96): string {
  const text = toPlainText(src)
  if (!text) return ''
  return text.length > max ? `${text.slice(0, max)}…` : text
}

export default createContentLoader('posts/**/*.md', {
  includeSrc: true,
  transform(raw: ContentData[]): Post[] {
    return raw
      .filter((p) => !p.url.endsWith('/index.html') && !p.url.endsWith('/'))
      .map((p) => {
        const fm = p.frontmatter || {}
        const seg = (p.url.split('/').filter(Boolean).pop() || '').replace(/\.html$/, '')
        let fallback = seg
        try {
          fallback = decodeURIComponent(seg)
        } catch {
          fallback = seg
        }

        return {
          title: (fm.title as string) || fallback,
          date: (fm.date as string) || null,
          url: p.url,
          excerpt: excerptOf(p.src || ''),
        }
      })
      .sort((a, b) => {
        const ad = a.date ? +new Date(a.date) : 0
        const bd = b.date ? +new Date(b.date) : 0
        return bd - ad
      })
  },
})
