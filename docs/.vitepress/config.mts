import { defineConfig } from 'vitepress'
import mathjax3 from 'markdown-it-mathjax3'
import { generateSidebar } from './sidebar.mjs'
export default defineConfig({
  title: "jjh's blog",
  description: "主要是笔记",

  markdown: {
	config(md){
		md.use(mathjax3)
	}
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' }
    ],
    
    sidebar: generateSidebar(),

    socialLinks: [
      { icon: 'github', link: 'https://github.com/jjh11737' }
    ]
  }
})
