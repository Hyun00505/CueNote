import { nextTick, ref, type Ref } from 'vue';
import { useVault } from './useVault';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import { markdown } from '@codemirror/lang-markdown';
import { basicSetup } from 'codemirror';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags } from '@lezer/highlight';

// Custom dark theme for CodeMirror
const customTheme = EditorView.theme({
  '&': {
    backgroundColor: 'transparent',
    color: '#e4e4e7',
    fontSize: '17px',
    fontFamily: "'Crimson Pro', 'Playfair Display', Georgia, serif",
    letterSpacing: '0.01em'
  },
  '.cm-content': {
    caretColor: '#818cf8',
    lineHeight: '1.9',
    padding: '24px 0'
  },
  '.cm-cursor': {
    borderLeftColor: '#818cf8',
    borderLeftWidth: '2px'
  },
  '.cm-selectionBackground, &.cm-focused .cm-selectionBackground': {
    backgroundColor: 'rgba(99, 102, 241, 0.3) !important'
  },
  '.cm-activeLine': {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: '4px'
  },
  '.cm-activeLineGutter': {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    color: '#818cf8'
  },
  '.cm-gutters': {
    backgroundColor: 'transparent',
    borderRight: '1px solid rgba(255, 255, 255, 0.06)',
    color: '#52525b',
    paddingRight: '8px'
  },
  '.cm-lineNumbers .cm-gutterElement': {
    padding: '0 16px 0 8px',
    minWidth: '50px'
  },
  '.cm-foldGutter .cm-gutterElement': {
    padding: '0 4px',
    color: '#71717a',
    cursor: 'pointer'
  },
  '.cm-line': {
    padding: '0 24px'
  },
  '.cm-matchingBracket': {
    backgroundColor: 'rgba(99, 102, 241, 0.3)',
    color: '#a5b4fc !important',
    borderRadius: '2px'
  },
  '.cm-searchMatch': {
    backgroundColor: 'rgba(234, 179, 8, 0.3)',
    borderRadius: '2px'
  },
  '.cm-searchMatch.cm-searchMatch-selected': {
    backgroundColor: 'rgba(234, 179, 8, 0.5)'
  },
  '.cm-selectionMatch': {
    backgroundColor: 'rgba(99, 102, 241, 0.2)'
  },
  '.cm-foldPlaceholder': {
    backgroundColor: 'rgba(99, 102, 241, 0.2)',
    border: 'none',
    color: '#818cf8',
    borderRadius: '4px',
    padding: '0 8px',
    margin: '0 4px'
  },
  '.cm-tooltip': {
    backgroundColor: '#18181b',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)'
  },
  '.cm-tooltip-autocomplete': {
    '& > ul > li': {
      padding: '6px 12px'
    },
    '& > ul > li[aria-selected]': {
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      color: '#e4e4e7'
    }
  },
  '.cm-panels': {
    backgroundColor: '#18181b',
    color: '#e4e4e7'
  },
  '.cm-panel.cm-search': {
    padding: '8px 12px',
    backgroundColor: '#18181b',
    '& input, & button': {
      backgroundColor: '#27272a',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '4px',
      color: '#e4e4e7'
    }
  }
}, { dark: true });

// Syntax highlighting
const customHighlight = HighlightStyle.define([
  // Headers - elegant serif with gradient-like colors
  { tag: tags.heading1, color: '#c4b5fd', fontWeight: '600', fontSize: '1.8em', fontFamily: "'Playfair Display', Georgia, serif" },
  { tag: tags.heading2, color: '#a78bfa', fontWeight: '600', fontSize: '1.5em', fontFamily: "'Playfair Display', Georgia, serif" },
  { tag: tags.heading3, color: '#8b5cf6', fontWeight: '600', fontSize: '1.3em', fontFamily: "'Playfair Display', Georgia, serif" },
  { tag: tags.heading4, color: '#7c3aed', fontWeight: '600', fontSize: '1.15em', fontFamily: "'Playfair Display', Georgia, serif" },
  { tag: tags.heading5, color: '#6d28d9', fontWeight: '600', fontFamily: "'Playfair Display', Georgia, serif" },
  { tag: tags.heading6, color: '#5b21b6', fontWeight: '600', fontFamily: "'Playfair Display', Georgia, serif" },

  // Emphasis
  { tag: tags.strong, color: '#f0abfc', fontWeight: '600' },
  { tag: tags.emphasis, color: '#e879f9', fontStyle: 'italic' },
  { tag: tags.strikethrough, color: '#71717a', textDecoration: 'line-through' },

  // Links
  { tag: tags.link, color: '#60a5fa', textDecoration: 'underline' },
  { tag: tags.url, color: '#38bdf8' },

  // Code - use monospace font for code
  { tag: tags.monospace, color: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.1)', fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: '0.9em' },
  { tag: tags.processingInstruction, color: '#34d399', fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: '0.9em' },

  // Lists
  { tag: tags.list, color: '#fbbf24' },

  // Quotes - elegant italic
  { tag: tags.quote, color: '#a1a1aa', fontStyle: 'italic' },

  // Meta & special
  { tag: tags.meta, color: '#71717a' },
  { tag: tags.comment, color: '#52525b', fontStyle: 'italic' },
  { tag: tags.contentSeparator, color: '#3f3f46' },

  // Content
  { tag: tags.content, color: '#e4e4e7' },

  // Punctuation & formatting marks
  { tag: tags.punctuation, color: '#71717a' },
  { tag: tags.bracket, color: '#71717a' },
]);

import { API_ENDPOINTS } from '../config/api';

const activeFile = ref<string | null>(null);
const editorError = ref('');
const saving = ref(false);

let editorView: EditorView | null = null;
let currentParent: HTMLDivElement | null = null;

export function useEditor(editorEl: Ref<HTMLDivElement | null>) {
  const { refreshTodoCount } = useVault();

  async function ensureEditor(content: string) {
    await nextTick();

    // Wait for DOM element to be available
    if (!editorEl.value) {
      await new Promise(resolve => setTimeout(resolve, 100));
      await nextTick();
      if (!editorEl.value) {
        editorError.value = 'Editor element not ready';
        return;
      }
    }

    // If parent changed or editor doesn't exist, recreate
    if (!editorView || currentParent !== editorEl.value) {
      if (editorView) {
        editorView.destroy();
        editorView = null;
      }

      try {
        const state = EditorState.create({
          doc: content,
          extensions: [
            basicSetup,
            markdown(),
            customTheme,
            syntaxHighlighting(customHighlight),
            EditorView.lineWrapping
          ]
        });
        editorView = new EditorView({
          state,
          parent: editorEl.value
        });
        currentParent = editorEl.value;
      } catch (e) {
        console.error('Failed to create editor:', e);
        editorError.value = 'Failed to create editor';
      }
      return;
    }

    // Update existing editor content
    editorView.dispatch({
      changes: { from: 0, to: editorView.state.doc.length, insert: content }
    });
  }

  async function openFile(filePath: string) {
    editorError.value = '';
    activeFile.value = filePath;
    try {
      const url = `${API_ENDPOINTS.VAULT.FILE}?path=${encodeURIComponent(filePath)}`;
      const res = await fetch(url);

      if (!res.ok) {
        editorError.value = `Failed to open file: ${res.status}`;
        return;
      }

      const data = await res.json();
      const content = typeof data.content === 'string' ? data.content : '';
      await ensureEditor(content);
    } catch (error) {
      editorError.value = 'Failed to open file. Is the backend running?';
      console.error('Open file failed:', error);
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
      const res = await fetch(API_ENDPOINTS.VAULT.FILE, {
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
      const res = await fetch(API_ENDPOINTS.VAULT.FILE, {
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
    createNewFile,
    editorView
  };
}
