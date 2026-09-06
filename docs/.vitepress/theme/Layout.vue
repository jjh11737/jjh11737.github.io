<script setup lang="ts">
import { computed } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { useData, useRoute } from 'vitepress'
import GiscusComment from './components/GiscusComment.vue'

const { Layout } = DefaultTheme
const { frontmatter } = useData()
const route = useRoute()

const isPost = computed(() => {
  const p = route.path
  return p.startsWith('/posts/') && p !== '/posts/' && !p.endsWith('/index.html')
})

const showComments = computed(() => {
  const setting = frontmatter.value.comments
  if (setting !== undefined) return !!setting
  return isPost.value
})
</script>

<template>
  <Layout>
    <template #doc-after>
      <GiscusComment v-if="showComments" />
    </template>
  </Layout>
</template>
