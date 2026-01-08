<template>
  <div class="editor-view">
    <div v-if="!activeFile" class="empty-state">
      <div class="empty-visual">
        <div class="empty-glow"></div>
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <line x1="10" y1="9" x2="8" y2="9"/>
          </svg>
        </div>
      </div>
      <h2>문서를 선택하세요</h2>
      <p>사이드바에서 마크다운 파일을 선택하여 편집을 시작하세요</p>
      <div class="empty-hint">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
        <span>왼쪽의 볼트에서 파일을 선택하세요</span>
      </div>
    </div>

    <div v-else class="editor-container">
      <div class="editor-header">
        <div class="file-info">
          <div class="file-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="file-details">
            <span class="file-name">{{ getFileName(activeFile) }}</span>
            <span class="file-ext">.md</span>
          </div>
        </div>
        <button class="save-btn" :class="{ saving }" :disabled="saving" @click="handleSave">
          <svg v-if="!saving" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          <span class="spinner" v-else></span>
          <span>{{ saving ? '저장 중...' : '저장' }}</span>
          <kbd>Ctrl+S</kbd>
        </button>
      </div>

      <EditorToolbar :editor="editor" />

      <div class="editor-content-wrapper">
        <EditorContent :editor="editor" class="editor-content" />
      </div>

      <p v-if="editorError" class="error-msg">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ editorError }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { Placeholder } from '@tiptap/extension-placeholder';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableCell } from '@tiptap/extension-table-cell';
import { TableHeader } from '@tiptap/extension-table-header';
import { Image } from '@tiptap/extension-image';
import { TaskList } from '@tiptap/extension-task-list';
import { TaskItem } from '@tiptap/extension-task-item';
import { Link } from '@tiptap/extension-link';
import { Highlight } from '@tiptap/extension-highlight';
import { Typography } from '@tiptap/extension-typography';
import { TextAlign } from '@tiptap/extension-text-align';
import { Underline } from '@tiptap/extension-underline';
import { CodeBlockLowlight } from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';
import EditorToolbar from './EditorToolbar.vue';

const lowlight = createLowlight(common);
const CORE_BASE = 'http://127.0.0.1:8787';

const props = defineProps<{
  activeFile: string | null;
}>();

const editorError = ref('');
const saving = ref(false);

const editor = useEditor({
  content: '',
  extensions: [
    StarterKit.configure({
      codeBlock: false,
    }),
    Placeholder.configure({
      placeholder: '내용을 입력하세요...',
    }),
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableCell,
    TableHeader,
    Image.configure({
      HTMLAttributes: {
        class: 'editor-image',
      },
    }),
    TaskList,
    TaskItem.configure({
      nested: true,
    }),
    Link.configure({
      openOnClick: false,
    }),
    Highlight.configure({
      multicolor: true,
    }),
    Typography,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Underline,
    CodeBlockLowlight.configure({
      lowlight,
    }),
  ],
});

function getFileName(path: string): string {
  const name = path.split(/[/\\]/).pop() || path;
  return name.replace(/\.md$/, '');
}

// Markdown to HTML conversion
function markdownToHtml(md: string): string {
  let html = md;

  // Code blocks first
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code class="language-${lang}">${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
  });

  // Headings
  html = html.replace(/^###### (.+)$/gm, '<h6>$1</h6>');
  html = html.replace(/^##### (.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Bold & Italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/~~(.+?)~~/g, '<s>$1</s>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  // Images
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

  // Task lists
  html = html.replace(/^- \[x\] (.+)$/gm, '<ul data-type="taskList"><li data-type="taskItem" data-checked="true"><label><input type="checkbox" checked><span></span></label><div>$1</div></li></ul>');
  html = html.replace(/^- \[ \] (.+)$/gm, '<ul data-type="taskList"><li data-type="taskItem" data-checked="false"><label><input type="checkbox"><span></span></label><div>$1</div></li></ul>');

  // Unordered lists
  html = html.replace(/^- (.+)$/gm, '<ul><li><p>$1</p></li></ul>');

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<ol><li><p>$1</p></li></ol>');

  // Blockquotes
  html = html.replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>');

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr>');
  html = html.replace(/^\*\*\*$/gm, '<hr>');

  // Tables
  const tableRegex = /^\|(.+)\|$/gm;
  let inTable = false;
  let tableRows: string[] = [];
  const lines = html.split('\n');
  const processedLines: string[] = [];

  for (const line of lines) {
    if (line.match(/^\|.+\|$/)) {
      if (!line.match(/^\|[\s\-:|]+\|$/)) {
        tableRows.push(line);
      }
      inTable = true;
    } else {
      if (inTable && tableRows.length > 0) {
        let tableHtml = '<table><tbody>';
        tableRows.forEach((row, idx) => {
          const cells = row.split('|').filter(c => c.trim());
          const tag = idx === 0 ? 'th' : 'td';
          tableHtml += '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
        });
        tableHtml += '</tbody></table>';
        processedLines.push(tableHtml);
        tableRows = [];
      }
      inTable = false;
      processedLines.push(line);
    }
  }

  if (tableRows.length > 0) {
    let tableHtml = '<table><tbody>';
    tableRows.forEach((row, idx) => {
      const cells = row.split('|').filter(c => c.trim());
      const tag = idx === 0 ? 'th' : 'td';
      tableHtml += '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
    });
    tableHtml += '</tbody></table>';
    processedLines.push(tableHtml);
  }

  html = processedLines.join('\n');

  // Paragraphs - wrap remaining text
  html = html.split('\n').map(line => {
    if (line.trim() && !line.match(/^<[a-z]/i)) {
      return `<p>${line}</p>`;
    }
    return line;
  }).join('');

  // Clean up consecutive same tags
  html = html.replace(/<\/ul>\s*<ul>/g, '');
  html = html.replace(/<\/ol>\s*<ol>/g, '');
  html = html.replace(/<\/blockquote>\s*<blockquote>/g, '');

  return html;
}

// HTML to Markdown conversion
function htmlToMarkdown(html: string): string {
  let md = html;

  // Headings
  md = md.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
  md = md.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
  md = md.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
  md = md.replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n\n');
  md = md.replace(/<h5[^>]*>(.*?)<\/h5>/gi, '##### $1\n\n');
  md = md.replace(/<h6[^>]*>(.*?)<\/h6>/gi, '###### $1\n\n');

  // Bold & Italic
  md = md.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
  md = md.replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**');
  md = md.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
  md = md.replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*');
  md = md.replace(/<u[^>]*>(.*?)<\/u>/gi, '<u>$1</u>');
  md = md.replace(/<s[^>]*>(.*?)<\/s>/gi, '~~$1~~');
  md = md.replace(/<del[^>]*>(.*?)<\/del>/gi, '~~$1~~');
  md = md.replace(/<mark[^>]*>(.*?)<\/mark>/gi, '==$1==');

  // Code
  md = md.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');
  md = md.replace(/<pre[^>]*><code[^>]*class="language-(\w*)"[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```$1\n$2```\n\n');
  md = md.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```\n$1```\n\n');

  // Links
  md = md.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');

  // Images
  md = md.replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*\/?>/gi, '![$2]($1)');
  md = md.replace(/<img[^>]*src="([^"]*)"[^>]*\/?>/gi, '![]($1)');

  // Task lists
  md = md.replace(/<ul[^>]*data-type="taskList"[^>]*>([\s\S]*?)<\/ul>/gi, (_, content) => {
    return content
      .replace(/<li[^>]*data-checked="true"[^>]*>[\s\S]*?<div>(.*?)<\/div>[\s\S]*?<\/li>/gi, '- [x] $1\n')
      .replace(/<li[^>]*data-checked="false"[^>]*>[\s\S]*?<div>(.*?)<\/div>[\s\S]*?<\/li>/gi, '- [ ] $1\n');
  });

  // Lists
  md = md.replace(/<ul[^>]*>([\s\S]*?)<\/ul>/gi, (_, content) => {
    return content.replace(/<li[^>]*>[\s\S]*?<p>(.*?)<\/p>[\s\S]*?<\/li>/gi, '- $1\n')
      .replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n') + '\n';
  });
  md = md.replace(/<ol[^>]*>([\s\S]*?)<\/ol>/gi, (_, content) => {
    let index = 0;
    return content.replace(/<li[^>]*>[\s\S]*?<p>(.*?)<\/p>[\s\S]*?<\/li>/gi, () => `${++index}. `)
      .replace(/<li[^>]*>(.*?)<\/li>/gi, () => `${++index}. `) + '\n';
  });

  // Blockquotes
  md = md.replace(/<blockquote[^>]*>([\s\S]*?)<\/blockquote>/gi, (_, content) => {
    const text = content.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1');
    return `> ${text}\n\n`;
  });

  // Horizontal rules
  md = md.replace(/<hr\s*\/?>/gi, '\n---\n\n');

  // Tables
  md = md.replace(/<table[^>]*>([\s\S]*?)<\/table>/gi, (_, tableContent) => {
    let result = '';
    const rows = tableContent.match(/<tr[^>]*>([\s\S]*?)<\/tr>/gi) || [];
    rows.forEach((row: string, index: number) => {
      const cells = row.match(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/gi) || [];
      const rowContent = cells.map((cell: string) => {
        return cell.replace(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/i, '$1').trim();
      }).join(' | ');
      result += `| ${rowContent} |\n`;
      if (index === 0) {
        result += `| ${cells.map(() => '---').join(' | ')} |\n`;
      }
    });
    return result + '\n';
  });

  // Paragraphs
  md = md.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
  md = md.replace(/<br\s*\/?>/gi, '\n');

  // Clean up
  md = md.replace(/<[^>]+>/g, '');
  md = md.replace(/&nbsp;/g, ' ');
  md = md.replace(/&lt;/g, '<');
  md = md.replace(/&gt;/g, '>');
  md = md.replace(/&amp;/g, '&');
  md = md.replace(/\n{3,}/g, '\n\n');

  return md.trim();
}

async function openFile(filePath: string) {
  editorError.value = '';

  try {
    const url = `${CORE_BASE}/vault/file?path=${encodeURIComponent(filePath)}`;
    const res = await fetch(url);

    if (!res.ok) {
      editorError.value = `파일 열기 실패: ${res.status}`;
      return;
    }

    const data = await res.json();
    const content = typeof data.content === 'string' ? data.content : '';
    const htmlContent = markdownToHtml(content);

    if (editor.value) {
      editor.value.commands.setContent(htmlContent);
    }
  } catch (error) {
    editorError.value = '파일 열기 실패. 백엔드가 실행 중인지 확인하세요.';
    console.error('Open file failed:', error);
  }
}

async function handleSave() {
  if (!props.activeFile || !editor.value) return;

  saving.value = true;
  editorError.value = '';

  try {
    const html = editor.value.getHTML();
    const content = htmlToMarkdown(html);

    const res = await fetch(`${CORE_BASE}/vault/file`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: props.activeFile, content })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (error) {
    editorError.value = '저장 실패.';
    console.error('Save file failed', error);
  } finally {
    saving.value = false;
  }
}

// Keyboard shortcut for save
function handleKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    handleSave();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  if (props.activeFile) {
    openFile(props.activeFile);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
  editor.value?.destroy();
});

watch(() => props.activeFile, (newFile) => {
  if (newFile) {
    openFile(newFile);
  }
});
</script>

<style scoped>
.editor-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.empty-visual {
  position: relative;
  width: 140px;
  height: 140px;
  margin-bottom: 32px;
}

.empty-glow {
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  opacity: 0.5;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.1); }
}

.empty-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  color: var(--text-muted);
}

.empty-state h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 15px;
  margin-bottom: 24px;
}

.empty-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: 13px;
}

.empty-hint svg {
  color: var(--accent-secondary);
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  border-radius: var(--radius-sm);
  color: white;
}

.file-details {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.file-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.file-ext {
  font-size: 13px;
  color: var(--text-muted);
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.save-btn:hover:not(:disabled) {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
}

.save-btn.saving {
  background: var(--gradient-primary);
  border-color: transparent;
  color: white;
}

.save-btn:disabled {
  cursor: not-allowed;
}

.save-btn kbd {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-family: var(--font-sans);
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.editor-content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 32px 48px;
  background: linear-gradient(180deg, var(--bg-primary) 0%, rgba(15, 15, 25, 0.95) 100%);
}

.editor-content {
  max-width: 800px;
  margin: 0 auto;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  margin: 16px 20px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  border-radius: var(--radius-md);
  color: var(--error);
  font-size: 13px;
}
</style>

<style>
/* TipTap Editor Global Styles */
.ProseMirror {
  outline: none;
  min-height: 500px;
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
}

.ProseMirror > * + * {
  margin-top: 0.75em;
}

/* Placeholder */
.ProseMirror p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: var(--text-muted);
  pointer-events: none;
  height: 0;
}

/* Headings */
.ProseMirror h1 {
  font-size: 2.25em;
  font-weight: 700;
  line-height: 1.3;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: var(--text-primary);
  font-family: var(--font-sans);
}

.ProseMirror h2 {
  font-size: 1.75em;
  font-weight: 600;
  line-height: 1.35;
  margin-top: 1.4em;
  margin-bottom: 0.5em;
  color: var(--text-primary);
}

.ProseMirror h3 {
  font-size: 1.4em;
  font-weight: 600;
  line-height: 1.4;
  margin-top: 1.3em;
  margin-bottom: 0.4em;
  color: var(--text-primary);
}

.ProseMirror h4,
.ProseMirror h5,
.ProseMirror h6 {
  font-size: 1.1em;
  font-weight: 600;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
}

/* Paragraphs */
.ProseMirror p {
  margin-bottom: 0.75em;
}

/* Links */
.ProseMirror a {
  color: var(--accent-secondary);
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.ProseMirror a:hover {
  color: var(--accent-tertiary);
}

/* Bold, Italic, etc */
.ProseMirror strong {
  font-weight: 600;
  color: var(--text-primary);
}

.ProseMirror em {
  font-style: italic;
}

.ProseMirror s {
  text-decoration: line-through;
  color: var(--text-muted);
}

.ProseMirror mark {
  background: rgba(250, 204, 21, 0.4);
  padding: 0 4px;
  border-radius: 2px;
}

/* Code */
.ProseMirror code {
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.9em;
}

.ProseMirror pre {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  overflow-x: auto;
  margin: 1em 0;
}

.ProseMirror pre code {
  background: transparent;
  padding: 0;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
}

/* Blockquote */
.ProseMirror blockquote {
  border-left: 3px solid var(--accent-primary);
  padding-left: 20px;
  margin: 1em 0;
  color: var(--text-secondary);
  font-style: italic;
}

/* Lists */
.ProseMirror ul,
.ProseMirror ol {
  padding-left: 24px;
  margin: 0.75em 0;
}

.ProseMirror li {
  margin: 0.25em 0;
}

.ProseMirror li p {
  margin: 0;
}

/* Task List */
.ProseMirror ul[data-type="taskList"] {
  list-style: none;
  padding-left: 0;
}

.ProseMirror ul[data-type="taskList"] li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 8px 0;
}

.ProseMirror ul[data-type="taskList"] li > label {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-top: 2px;
}

.ProseMirror ul[data-type="taskList"] li > label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--accent-primary);
  cursor: pointer;
}

.ProseMirror ul[data-type="taskList"] li[data-checked="true"] > div {
  text-decoration: line-through;
  color: var(--text-muted);
}

/* Horizontal Rule */
.ProseMirror hr {
  border: none;
  border-top: 1px solid var(--border-default);
  margin: 2em 0;
}

/* Images */
.ProseMirror img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: 1em 0;
}

.ProseMirror img.ProseMirror-selectednode {
  outline: 2px solid var(--accent-primary);
}

/* Tables */
.ProseMirror table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  overflow: hidden;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
}

.ProseMirror th,
.ProseMirror td {
  border: 1px solid var(--border-subtle);
  padding: 12px 16px;
  text-align: left;
  vertical-align: top;
}

.ProseMirror th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.ProseMirror td {
  background: var(--bg-primary);
}

.ProseMirror tr:hover td {
  background: var(--bg-hover);
}

.ProseMirror .selectedCell {
  background: rgba(99, 102, 241, 0.1);
}

/* Selection */
.ProseMirror ::selection {
  background: rgba(99, 102, 241, 0.3);
}
</style>
