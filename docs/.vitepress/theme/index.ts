import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import PostList from './components/PostList.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component('PostList', PostList)
  },
}
