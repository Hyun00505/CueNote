<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView } from '@codemirror/view'
import { basicSetup } from '@codemirror/basic-setup'
import { markdown } from '@codemirror/lang-markdown'
import { useVaultStore } from './stores/vault'

const vaultStore = useVaultStore()
const apiBase = 'http://127.0.0.1:8787'

const files = ref<string[]>([])
const selectedPath = ref<string | null>(null)
const content = ref('')
const editorEl = ref<HTMLDivElement | null>(null)
const statusMessage = ref('')
const planStatus = ref('')
const todayPlan = ref<{
  tldr: string
  overdue: {
    id: string
    text: string
    checked: boolean
    notePath: string
    lineNo: number
  }[]
  dueSoon: {
    id: string
    text: string
    checked: boolean
    notePath: string
    lineNo: number
  }[]
  nextActions: string[]
  quickWins: string[]
} | null>(null)
let editorView: EditorView | null = null

async function onOpenVault() {
  const selectedPath = await window.cuenote.selectVault()
  if (selectedPath) {
    vaultStore.setVaultPath(selectedPath)
    await openVault(selectedPath)
    await loadFiles()
  }
}

async function openVault(path: string) {
  statusMessage.value = ''
  const response = await fetch(`${apiBase}/vault/open`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path }),
  })
  if (!response.ok) {
    statusMessage.value = 'Failed to open vault.'
  }
}

async function loadFiles() {
  statusMessage.value = ''
  const response = await fetch(`${apiBase}/vault/files`)
  if (!response.ok) {
    statusMessage.value = 'Failed to load files.'
    files.value = []
    return
  }
  const data = await response.json()
  files.value = Array.isArray(data.files) ? data.files : []
}

async function onSelectFile(path: string) {
  selectedPath.value = path
  statusMessage.value = ''
  const response = await fetch(
    `${apiBase}/vault/file?path=${encodeURIComponent(path)}`,
  )
  if (!response.ok) {
    statusMessage.value = 'Failed to load file.'
    return
  }
  const data = await response.json()
  const nextContent = typeof data.content === 'string' ? data.content : ''
  content.value = nextContent
  if (editorView) {
    const docLength = editorView.state.doc.length
    editorView.dispatch({
      changes: { from: 0, to: docLength, insert: nextContent },
    })
  }
}

async function onSaveFile() {
  if (!selectedPath.value) return
  statusMessage.value = ''
  const response = await fetch(`${apiBase}/vault/file`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      path: selectedPath.value,
      content: content.value,
    }),
  })
  if (!response.ok) {
    statusMessage.value = 'Failed to save file.'
    return
  }
  statusMessage.value = 'Saved.'
}

async function onGenerateTodayPlan() {
  planStatus.value = ''
  todayPlan.value = null
  const response = await fetch(`${apiBase}/ai/today-plan`, { method: 'POST' })
  if (!response.ok) {
    planStatus.value = 'Failed to generate plan.'
    return
  }
  const data = await response.json()
  todayPlan.value = data
}

onMounted(() => {
  if (editorEl.value) {
    editorView = new EditorView({
      state: EditorState.create({
        doc: content.value,
        extensions: [
          basicSetup,
          markdown(),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              content.value = update.state.doc.toString()
            }
          }),
        ],
      }),
      parent: editorEl.value,
    })
  }
})

onBeforeUnmount(() => {
  editorView?.destroy()
  editorView = null
})
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <button class="sidebar-button" type="button" @click="onOpenVault">
        Open Vault
      </button>
      <button class="sidebar-button" type="button" @click="loadFiles">
        Refresh Files
      </button>
      <p v-if="vaultStore.vaultPath" class="sidebar-path">
        {{ vaultStore.vaultPath }}
      </p>
      <div class="file-tree">
        <button
          v-for="file in files"
          :key="file"
          class="file-item"
          :class="{ active: file === selectedPath }"
          type="button"
          @click="onSelectFile(file)"
        >
          {{ file }}
        </button>
      </div>
    </aside>
    <main class="content">
      <header class="content-header">
        <div>
          <h1>CueNote Desktop</h1>
          <p class="muted">
            Select a markdown file to edit. Changes are kept in memory until
            saved.
          </p>
        </div>
        <button
          class="primary-button"
          type="button"
          :disabled="!selectedPath"
          @click="onSaveFile"
        >
          Save
        </button>
      </header>
      <p v-if="statusMessage" class="status">{{ statusMessage }}</p>
      <div class="editor" ref="editorEl"></div>
      <section class="dashboard">
        <header class="dashboard-header">
          <h2>Today Plan</h2>
          <button class="primary-button" type="button" @click="onGenerateTodayPlan">
            Generate Today Plan
          </button>
        </header>
        <p v-if="planStatus" class="status">{{ planStatus }}</p>
        <div v-if="todayPlan" class="card-grid">
          <article class="card">
            <h3>TLDR</h3>
            <p>{{ todayPlan.tldr }}</p>
          </article>
          <article class="card">
            <h3>Next Actions</h3>
            <ul>
              <li v-for="item in todayPlan.nextActions" :key="item">
                {{ item }}
              </li>
            </ul>
          </article>
          <article class="card">
            <h3>Quick Wins</h3>
            <ul>
              <li v-for="item in todayPlan.quickWins" :key="item">
                {{ item }}
              </li>
            </ul>
          </article>
          <article class="card">
            <h3>Overdue</h3>
            <ul>
              <li v-for="item in todayPlan.overdue" :key="item.id">
                {{ item.text }}
              </li>
            </ul>
          </article>
          <article class="card">
            <h3>Due Soon</h3>
            <ul>
              <li v-for="item in todayPlan.dueSoon" :key="item.id">
                {{ item.text }}
              </li>
            </ul>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  padding: 20px;
  border-right: 1px solid #2c2c2c;
  background: #141414;
  color: #f5f5f5;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sidebar-button {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #3a3a3a;
  background: #1f1f1f;
  color: inherit;
  cursor: pointer;
}

.sidebar-button:hover {
  background: #2a2a2a;
}

.sidebar-path {
  font-size: 12px;
  color: #bdbdbd;
  word-break: break-all;
}

.file-tree {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow: auto;
}

.file-item {
  text-align: left;
  background: transparent;
  border: none;
  color: inherit;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
}

.file-item:hover {
  background: #202020;
}

.file-item.active {
  background: #2a2a2a;
}

.content {
  flex: 1;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.primary-button {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #2d2d2d;
  background: #e0e0e0;
  color: #111;
  cursor: pointer;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.muted {
  color: #6f6f6f;
  margin: 4px 0 0;
}

.status {
  font-size: 12px;
  color: #6f6f6f;
}

.editor {
  flex: 1;
  min-height: 400px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}

.card h3 {
  margin: 0 0 8px;
}

.card ul {
  margin: 0;
  padding-left: 16px;
}
</style>
