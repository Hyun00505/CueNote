import { nextTick, ref, type Ref } from 'vue';
import { useVault } from './useVault';

const CORE_BASE = 'http://127.0.0.1:8787';

const activeFile = ref<string | null>(null);
const editorError = ref('');
const saving = ref(false);

let editorView: any = null;
let editorApi: {
  EditorState: any;
  EditorView: any;
  basicSetup: any;
  markdown: any;
} | null = null;

export function useEditor(editorEl: Ref<HTMLDivElement | null>) {
  const { refreshTodoCount } = useVault();

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
      const res = await fetch(`${CORE_BASE}/vault/file`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: activeFile.value, content })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      await refreshTodoCount();
    } catch (error) {
      editorError.value = 'Failed to save file.';
      console.error('Save file failed', error);
    } finally {
      saving.value = false;
    }
  }

  async function createNewFile(fileName: string) {
    if (!fileName.endsWith('.md')) {
      fileName = fileName + '.md';
    }
    editorError.value = '';
    try {
      // 빈 파일 생성
      const res = await fetch(`${CORE_BASE}/vault/file`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: fileName, content: '' })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      // 새 파일 열기
      await openFile(fileName);
      return true;
    } catch (error) {
      editorError.value = 'Failed to create file.';
      console.error('Create file failed', error);
      return false;
    }
  }

  return {
    activeFile,
    editorError,
    saving,
    openFile,
    saveFile,
    createNewFile
  };
}

