import fs from 'fs'
import path from 'path'

function scanDir(dir, base = '') {
  const entries = fs.readdirSync(dir, { withFileTypes: true })

  const items = []

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)

    if (entry.isDirectory()) {
      const children = scanDir(
        fullPath,
        `${base}/${entry.name}`
      )

      items.push({
        text: entry.name,
        items: children
      })
    }

    else if (
      entry.isFile() &&
      entry.name.endsWith('.md') &&
      entry.name !== 'index.md'
    ) {
      const name = entry.name.replace('.md', '')

      items.push({
        text: name,
        link: `${base}/${name}`
      })
    }
  }

  return items
}

export function generateSidebar() {
  return {
    '/notes/': scanDir(
      path.resolve('docs/notes'),
      '/notes'
    ),

    '/posts/': scanDir(
      path.resolve('docs/posts'),
      '/posts'
    )
  }
}
