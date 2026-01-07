<template>
  <main class="layout">
    <header>
      <h1>CueNote Desktop</h1>
      <p>Local core service: <strong>{{ coreStatus }}</strong></p>
    </header>

    <section class="panel">
      <h2>Vault</h2>
      <p class="muted">Pick a vault folder to index markdown files.</p>
      <button class="action" @click="openVault">Open Vault</button>
      <p v-if="vaultPath" class="path">Selected: {{ vaultPath }}</p>
      <p v-if="vaultError" class="error">{{ vaultError }}</p>
      <p v-if="todoCount !== null" class="muted">Unchecked TODOs: {{ todoCount }}</p>
      <div v-if="vaultFiles.length > 0" class="workspace">
        <div class="files">
          <h3>Files</h3>
          <ul>
            <li
              v-for="file in vaultFiles"
              :key="file"
              :class="{ active: file === activeFile }"
              @click="openFile(file)"
            >
              {{ file }}
            </li>
          </ul>
        </div>
        <div class="editor">
          <div class="editor-header">
            <div>
              <h3>Editor</h3>
              <p v-if="activeFile" class="path">{{ activeFile }}</p>
            </div>
            <button class="action" :disabled="!activeFile || saving" @click="saveFile">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
          <div ref="editorEl" class="editor-surface">
            <p v-if="!activeFile" class="muted">Select a file to start editing.</p>
          </div>
          <p v-if="editorError" class="error">{{ editorError }}</p>
        </div>
      </div>
    </section>

    <section class="panel">
      <h2>Dashboard</h2>
      <p class="muted">Generate a focused plan from your unchecked TODOs.</p>
      <button class="action" :disabled="planLoading" @click="generatePlan">
        {{ planLoading ? 'Generating...' : 'Generate Today Plan' }}
      </button>
      <p v-if="planError" class="error">{{ planError }}</p>
      <div v-if="todayPlan" class="plan">
        <h3 class="plan-headline">{{ todayPlan.tldr }}</h3>
        <div class="plan-grid">
          <div>
            <h4>Next Actions</h4>
            <ul>
              <li v-for="(item, index) in todayPlan.nextActions" :key="`na-${index}`">
                {{ item }}
              </li>
            </ul>
          </div>
          <div>
            <h4>Quick Wins</h4>
            <ul>
              <li v-for="(item, index) in todayPlan.quickWins" :key="`qw-${index}`">
                {{ item }}
              </li>
            </ul>
          </div>
          <div>
            <h4>Overdue</h4>
            <ul>
              <li v-for="todo in todayPlan.overdue" :key="todo.id">
                {{ todo.text }}
              </li>
            </ul>
          </div>
          <div>
            <h4>Due Soon</h4>
            <ul>
              <li v-for="todo in todayPlan.dueSoon" :key="todo.id">
                {{ todo.text }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';
const coreStatus = ref('checking...');
const vaultPath = ref<string | null>(null);
const vaultFiles = ref<string[]>([]);
const vaultError = ref('');
const editorError = ref('');
const activeFile = ref<string | null>(null);
const saving = ref(false);
const todoCount = ref<number | null>(null);
const editorEl = ref<HTMLDivElement | null>(null);

let editorView: any = null;
let editorApi: {
  EditorState: any;
  EditorView: any;
  basicSetup: any;
  markdown: any;
} | null = null;

type TodoItem = {
  id: string;
  text: string;
  checked: boolean;
  notePath: string;
  lineNo: number;
};

type TodayPlan = {
  tldr: string;
  overdue: TodoItem[];
  dueSoon: TodoItem[];
  nextActions: string[];
  quickWins: string[];
};

const todayPlan = ref<TodayPlan | null>(null);
const planLoading = ref(false);
const planError = ref('');

async function checkHealth() {
  try {
    const res = await fetch(`${CORE_BASE}/health`);
    const data = await res.json();
    coreStatus.value = data.status ?? 'unknown';
  } catch (error) {
    coreStatus.value = 'unreachable';
    console.error('Health check failed', error);
  }
}

async function loadEditorApi() {
  if (editorApi) {
    return editorApi;
  }
  const [stateModule, viewModule, setupModule, markdownModule] = await Promise.all([
    import(/* @vite-ignore */ 'https://esm.sh/@codemirror/state'),
    import(/* @vite-ignore */ 'https://esm.sh/@codemirror/view'),
    import(/* @vite-ignore */ 'https://esm.sh/@codemirror/basic-setup'),
    import(/* @vite-ignore */ 'https://esm.sh/@codemirror/lang-markdown')
  ]);
  editorApi = {
    EditorState: stateModule.EditorState,
    EditorView: viewModule.EditorView,
    basicSetup: setupModule.basicSetup,
    markdown: markdownModule.markdown
  };
  return editorApi;
}

async function ensureEditor(content: string) {
  const api = await loadEditorApi();
  await nextTick();
  if (!editorEl.value) {
    return;
  }
  if (!editorView) {
    const state = api.EditorState.create({
      doc: content,
      extensions: [api.basicSetup, api.markdown()]
    });
    editorView = new api.EditorView({
      state,
      parent: editorEl.value
    });
    return;
  }
  editorView.dispatch({
    changes: { from: 0, to: editorView.state.doc.length, insert: content }
  });
}

async function openVault() {
  vaultError.value = '';
  const selected = await window.cuenote.selectVault();
  if (!selected) {
    return;
  }
  vaultPath.value = selected;
  try {
    await fetch(`${CORE_BASE}/vault/open`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: selected })
    });
    await refreshFiles();
    await refreshTodoCount();
  } catch (error) {
    vaultError.value = 'Failed to load vault files.';
    console.error('Vault load failed', error);
  }
}

async function refreshFiles() {
  const res = await fetch(`${CORE_BASE}/vault/files`);
  const data = await res.json();
  vaultFiles.value = Array.isArray(data.files) ? data.files : [];
}

async function openFile(filePath: string) {
  editorError.value = '';
  activeFile.value = filePath;
  try {
    const res = await fetch(`${CORE_BASE}/vault/file?path=${encodeURIComponent(filePath)}`);
    const data = await res.json();
    const content = typeof data.content === 'string' ? data.content : '';
    await ensureEditor(content);
  } catch (error) {
    editorError.value = 'Failed to open file.';
    console.error('Open file failed', error);
  }
}

async function saveFile() {
  if (!activeFile.value || !editorView) {
    return;
  }
  saving.value = true;
  editorError.value = '';
  try {
    const content = editorView.state.doc.toString();
    await fetch(`${CORE_BASE}/vault/file`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: activeFile.value, content })
    });
    await refreshTodoCount();
  } catch (error) {
    editorError.value = 'Failed to save file.';
    console.error('Save file failed', error);
  } finally {
    saving.value = false;
  }
}

async function refreshTodoCount() {
  try {
    const res = await fetch(`${CORE_BASE}/todos?checked=false`);
    const data = await res.json();
    todoCount.value = Array.isArray(data.todos) ? data.todos.length : 0;
  } catch (error) {
    todoCount.value = null;
    console.error('Failed to fetch TODO count', error);
  }
}

async function generatePlan() {
  planError.value = '';
  planLoading.value = true;
  try {
    const res = await fetch(`${CORE_BASE}/ai/today-plan`, { method: 'POST' });
    const data = await res.json();
    todayPlan.value = data as TodayPlan;
  } catch (error) {
    planError.value = 'Failed to generate plan.';
    console.error('Plan generation failed', error);
  } finally {
    planLoading.value = false;
  }
}

onMounted(() => {
  checkHealth();
});
</script>

<style scoped>
.layout {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  padding: 1.5rem;
  background: #0f172a;
  min-height: 100vh;
  color: #e2e8f0;
}

header {
  margin-bottom: 1rem;
}

.panel {
  background: #1e293b;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.muted {
  color: #94a3b8;
}

.action {
  background: #38bdf8;
  border: none;
  border-radius: 6px;
  color: #0f172a;
  font-weight: 600;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.action:hover {
  background: #0ea5e9;
}

.path {
  margin-top: 0.75rem;
  font-size: 0.9rem;
  word-break: break-all;
}

.error {
  color: #f87171;
  margin-top: 0.5rem;
}

.files {
  margin-top: 1rem;
}

.workspace {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.files ul {
  max-height: 420px;
  overflow-y: auto;
}

.files li {
  cursor: pointer;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  color: #cbd5f5;
}

.files li.active {
  background: #334155;
  color: #e2e8f0;
}

.editor {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.editor-surface {
  min-height: 360px;
  background: #0b1120;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 0.75rem;
}

.plan {
  margin-top: 1rem;
  background: #0b1120;
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid #1e293b;
}

.plan-headline {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 0.25rem 0;
}
</style>
