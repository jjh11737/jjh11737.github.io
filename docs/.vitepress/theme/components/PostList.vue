<script setup lang="ts">
import { data as posts } from '../posts.data'

const props = withDefaults(defineProps<{ limit?: number }>(), { limit: 0 })

const list = props.limit && props.limit > 0 ? posts.slice(0, props.limit) : posts
</script>

<template>
  <div class="post-list">
    <a v-for="post in list" :key="post.url" class="post-card" :href="post.url">
      <div class="post-head">
        <h3 class="post-title">{{ post.title }}</h3>
        <time v-if="post.date" class="post-date">{{ post.date }}</time>
      </div>
      <p v-if="post.excerpt" class="post-excerpt">{{ post.excerpt }}</p>
    </a>
  </div>
</template>

<style scoped>
.post-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.post-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background-color: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  text-decoration: none !important;
  transition:
    border-color 0.25s,
    transform 0.25s,
    box-shadow 0.25s;
}

.post-card:hover {
  border-color: var(--vp-c-brand-2);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.07);
  text-decoration: none !important;
}

.post-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.post-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--vp-c-text-1);
}

.post-date {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--vp-c-text-3);
}

.post-excerpt {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}
</style>
