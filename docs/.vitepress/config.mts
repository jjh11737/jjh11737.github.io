import { defineConfig } from 'vitepress'
import mathjax3 from 'markdown-it-mathjax3'
import { generateSidebar } from './sidebar.mjs'
// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "jjh's blog",
  description: "主要是笔记",

  markdown: {
	config(md){
		md.use(mathjax3)
	}
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' }
    ],
    
    sidebar: generateSidebar(),

    socialLinks: [
      { icon: 'github', link: 'https://github.com/jjh11737' }
    ]
  }
})
