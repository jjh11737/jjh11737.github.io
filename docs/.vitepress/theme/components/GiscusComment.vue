<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useData, useRoute } from 'vitepress'

const route = useRoute()
const { isDark } = useData()

const container = ref<HTMLElement | null>(null)

const config = {
  repo: 'jjh11737/jjh11737.github.io',
  repoId: 'R_kgDOSIoI4g',
  category: 'Announcements',
  categoryId: 'DIC_kwDOSIoI4s4DE_29',
  mapping: 'pathname',
  strict: '0',
  reactionsEnabled: '1',
  emitMetadata: '0',
  inputPosition: 'bottom',
  lang: 'zh-CN',
  loading: 'lazy',
}

function currentTheme(): string {
  return isDark.value ? 'noborder_dark' : 'noborder_light'
}

function loadGiscus(): void {
  const el = container.value
  if (!el) return

  el.innerHTML = ''

  const script = document.createElement('script')
  script.src = 'https://giscus.app/client.js'
  script.async = true
  script.crossOrigin = 'anonymous'
  script.setAttribute('data-repo', config.repo)
  script.setAttribute('data-repo-id', config.repoId)
  script.setAttribute('data-category', config.category)
  script.setAttribute('data-category-id', config.categoryId)
  script.setAttribute('data-mapping', config.mapping)
  script.setAttribute('data-strict', config.strict)
  script.setAttribute('data-reactions-enabled', config.reactionsEnabled)
  script.setAttribute('data-emit-metadata', config.emitMetadata)
  script.setAttribute('data-input-position', config.inputPosition)
  script.setAttribute('data-lang', config.lang)
  script.setAttribute('data-loading', config.loading)
  script.setAttribute('data-theme', currentTheme())
  el.appendChild(script)
}

function sendTheme(): void {
  const iframe = container.value?.querySelector<HTMLIFrameElement>('iframe.giscus-frame')
  if (!iframe) return
  iframe.contentWindow?.postMessage(
    { giscus: { setConfig: { theme: currentTheme() } } },
    'https://giscus.app'
  )
}

onMounted(loadGiscus)

watch(
  () => route.path,
  () => loadGiscus()
)

watch(isDark, () => {
  if (container.value?.querySelector('iframe.giscus-frame')) {
    sendTheme()
  } else {
    loadGiscus()
  }
})

onBeforeUnmount(() => {
  if (container.value) container.value.innerHTML = ''
})
</script>

<template>
  <div ref="container" class="giscus-comment" />
</template>

<style scoped>
.giscus-comment {
  margin-top: 32px;
}
</style>
