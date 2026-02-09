import { ref } from 'vue';
import { useEditor, type Editor } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { Table } from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Image from '@tiptap/extension-image';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import Link from '@tiptap/extension-link';
import Highlight from '@tiptap/extension-highlight';
import Typography from '@tiptap/extension-typography';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';

const lowlight = createLowlight(common);

import { API_ENDPOINTS } from '../config/api';
// Assuming htmlToMarkdown is not exported from anywhere else, we use the local function.
// But the local function is defined inside useTiptapEditor which is fine.

export function useTiptapEditor() {
  const activeFile = ref<string | null>(null);
  const editorError = ref('');
  const saving = ref(false);
  const editor = ref<Editor | null>(null);

  function createEditor(content: string = '') {
    return useEditor({
      content,
      extensions: [
        StarterKit.configure({
          codeBlock: false,
        }),
        Placeholder.configure({
          placeholder: '내용을 입력하세요...',
        }),
        Table.configure({
          resizable: true,
          HTMLAttributes: {
            class: 'tiptap-table',
          },
        }),
        TableRow,
        TableCell,
        TableHeader,
        Image.configure({
          HTMLAttributes: {
            class: 'tiptap-image',
          },
        }),
        TaskList.configure({
          HTMLAttributes: {
            class: 'tiptap-task-list',
          },
        }),
        TaskItem.configure({
          nested: true,
        }),
        Link.configure({
          openOnClick: false,
          HTMLAttributes: {
            class: 'tiptap-link',
          },
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
      editorProps: {
        attributes: {
          class: 'tiptap-editor-content',
        },
      },
    });
  }

  // Placeholder system to protect code blocks from corruption
  const CB_PREFIX = '\u0000CB_PH_';
  const CB_SUFFIX = '\u0000';
  const IC_PREFIX = '\u0000IC_PH_';

  function makePlaceholder(prefix: string, index: number): string {
    return `${prefix}${index}${CB_SUFFIX}`;
  }

  // HTML to Markdown conversion
  function htmlToMarkdown(html: string): string {
    let md = html;

    // Step 1: Extract code blocks FIRST (before any other processing)
    const codeBlocks: string[] = [];

    // Handle <pre><code class="language-xxx">...</code></pre>
    md = md.replace(/<pre[^>]*>\s*<code[^>]*class="language-(\w*)"[^>]*>([\s\S]*?)<\/code>\s*<\/pre>/gi, (_, lang, code) => {
      let cleanCode = code.replace(/<br\s*\/?>/gi, '\n');
      cleanCode = cleanCode.replace(/<[^>]+>/g, '');
      cleanCode = cleanCode.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ');
      cleanCode = cleanCode.replace(/\s+$/, '');
      const block = `\`\`\`${lang}\n${cleanCode}\n\`\`\``;
      const index = codeBlocks.length;
      codeBlocks.push(block);
      return makePlaceholder(CB_PREFIX, index);
    });

    // Handle <pre><code>...</code></pre> (no language)
    md = md.replace(/<pre[^>]*>\s*<code[^>]*>([\s\S]*?)<\/code>\s*<\/pre>/gi, (_, code) => {
      let cleanCode = code.replace(/<br\s*\/?>/gi, '\n');
      cleanCode = cleanCode.replace(/<[^>]+>/g, '');
      cleanCode = cleanCode.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ');
      cleanCode = cleanCode.replace(/\s+$/, '');
      const block = `\`\`\`\n${cleanCode}\n\`\`\``;
      const index = codeBlocks.length;
      codeBlocks.push(block);
      return makePlaceholder(CB_PREFIX, index);
    });

    // Step 2: Apply other transformations (code blocks are safe)

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

    // Inline code (safe now - code blocks already extracted)
    md = md.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');

    // Links
    md = md.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');

    // Images
    md = md.replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*\/?>/gi, '![$2]($1)');
    md = md.replace(/<img[^>]*src="([^"]*)"[^>]*\/?>/gi, '![]($1)');

    // Task lists
    md = md.replace(/<li[^>]*data-checked="true"[^>]*>(.*?)<\/li>/gi, '- [x] $1\n');
    md = md.replace(/<li[^>]*data-checked="false"[^>]*>(.*?)<\/li>/gi, '- [ ] $1\n');

    // Lists
    md = md.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (_, content) => {
      return content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n') + '\n';
    });
    md = md.replace(/<ol[^>]*>(.*?)<\/ol>/gis, (_, content) => {
      let index = 0;
      return content.replace(/<li[^>]*>(.*?)<\/li>/gi, () => `${++index}. `) + '\n';
    });

    // Paragraphs & line breaks
    md = md.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
    md = md.replace(/<br\s*\/?>/gi, '\n');

    // Blockquotes
    md = md.replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gis, (_, content) => {
      return content.split('\n').map((line: string) => `> ${line}`).join('\n') + '\n\n';
    });

    // Horizontal rules
    md = md.replace(/<hr\s*\/?>/gi, '\n---\n\n');

    // Tables
    md = md.replace(/<table[^>]*>(.*?)<\/table>/gis, (_, tableContent) => {
      let result = '';
      const rows = tableContent.match(/<tr[^>]*>(.*?)<\/tr>/gis) || [];
      rows.forEach((row: string, index: number) => {
        const cells = row.match(/<t[hd][^>]*>(.*?)<\/t[hd]>/gi) || [];
        const rowContent = cells.map((cell: string) => {
          let content = cell.replace(/<t[hd][^>]*>(.*?)<\/t[hd]>/i, '$1').trim();
          // Strip <p> tags that Tiptap wraps cell content with
          content = content.replace(/<p[^>]*>([\s\S]*?)<\/p>/gi, '$1').trim();
          // Strip any remaining HTML tags
          content = content.replace(/<[^>]+>/g, '').trim();
          return content;
        }).join(' | ');
        result += `| ${rowContent} |\n`;
        if (index === 0) {
          result += `| ${cells.map(() => '---').join(' | ')} |\n`;
        }
      });
      return result + '\n';
    });

    // Clean up remaining HTML tags
    md = md.replace(/<[^>]+>/g, '');
    md = md.replace(/&nbsp;/g, ' ');
    md = md.replace(/&lt;/g, '<');
    md = md.replace(/&gt;/g, '>');
    md = md.replace(/&amp;/g, '&');
    md = md.replace(/\n{3,}/g, '\n\n');

    // Step 3: Restore code block placeholders
    md = md.replace(new RegExp(CB_PREFIX.replace('\u0000', '\\u0000') + '(\\d+)' + CB_SUFFIX.replace('\u0000', '\\u0000'), 'g'), (_, idx) => {
      return codeBlocks[parseInt(idx)] || '';
    });

    return md.trim();
  }

  // Markdown to HTML conversion
  function markdownToHtml(md: string): string {
    let html = md;

    // Normalize line endings
    html = html.replace(/\r\n|\r/g, '\n');

    // Step 1: Extract code blocks FIRST
    const codeBlocks: string[] = [];
    html = html.replace(/```(\w*)\s*\n([\s\S]*?)```/g, (_, lang, code) => {
      const cleanCode = code.replace(/\s+$/, '');
      const htmlBlock = `<pre><code class="language-${lang}">${cleanCode.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
      const index = codeBlocks.length;
      codeBlocks.push(htmlBlock);
      return makePlaceholder(CB_PREFIX, index);
    });

    // Step 2: Extract inline code
    const inlineCodes: string[] = [];
    html = html.replace(/`([^`]+)`/g, (_, code) => {
      const inlineHtml = `<code>${code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code>`;
      const index = inlineCodes.length;
      inlineCodes.push(inlineHtml);
      return makePlaceholder(IC_PREFIX, index);
    });

    // Step 3: Apply other transformations (code is protected)

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

    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

    // Images
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

    // Task lists
    html = html.replace(/^- \[x\] (.+)$/gm, '<ul data-type="taskList"><li data-type="taskItem" data-checked="true">$1</li></ul>');
    html = html.replace(/^- \[ \] (.+)$/gm, '<ul data-type="taskList"><li data-type="taskItem" data-checked="false">$1</li></ul>');

    // Unordered lists
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    // Blockquotes
    html = html.replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>');

    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr>');

    // Tables
    html = html.replace(/^\|(.+)\|$/gm, (match, content) => {
      if (content.match(/^[\s\-|]+$/)) return '';
      const cells = content.split('|').map((cell: string) => cell.trim());
      const cellHtml = cells.map((cell: string) => `<td>${cell}</td>`).join('');
      return `<tr>${cellHtml}</tr>`;
    });
    html = html.replace(/(<tr>.*<\/tr>\n?)+/g, '<table><tbody>$&</tbody></table>');

    // Paragraphs
    html = html.replace(/^(?!<[a-z]|$)(.+)$/gm, '<p>$1</p>');

    // Clean up
    html = html.replace(/<\/ul>\n*<ul>/g, '');
    html = html.replace(/<\/blockquote>\n*<blockquote>/g, '');

    // Step 4: Restore inline code placeholders
    html = html.replace(new RegExp(IC_PREFIX.replace('\u0000', '\\u0000') + '(\\d+)' + CB_SUFFIX.replace('\u0000', '\\u0000'), 'g'), (_, idx) => {
      return inlineCodes[parseInt(idx)] || '';
    });

    // Step 5: Restore code block placeholders
    html = html.replace(new RegExp(CB_PREFIX.replace('\u0000', '\\u0000') + '(\\d+)' + CB_SUFFIX.replace('\u0000', '\\u0000'), 'g'), (_, idx) => {
      return codeBlocks[parseInt(idx)] || '';
    });

    return html;
  }

  async function openFile(filePath: string, editorInstance: Editor | null) {
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
      const htmlContent = markdownToHtml(content);

      if (editorInstance) {
        editorInstance.commands.setContent(htmlContent);
      }
    } catch (error) {
      editorError.value = 'Failed to open file. Is the backend running?';
      console.error('Open file failed:', error);
    }
  }

  async function saveFile(editorInstance: Editor | null) {
    if (!activeFile.value || !editorInstance) {
      return;
    }

    saving.value = true;
    editorError.value = '';

    try {
      const html = editorInstance.getHTML();
      // Use the local function defined in this scope
      const content = htmlToMarkdown(html);
      const res = await fetch(API_ENDPOINTS.VAULT.FILE, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: activeFile.value, content })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
    } catch (error) {
      editorError.value = 'Failed to save file.';
      console.error('Save file failed', error);
    } finally {
      saving.value = false;
    }
  }

  async function createNewFile(fileName: string, editorInstance: Editor | null) {
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

      await openFile(fileName, editorInstance);
      return true;
    } catch (error) {
      editorError.value = 'Failed to create file.';
      console.error('Create file failed', error);
      return false;
    }
  }

  function addImage(editorInstance: Editor | null, url: string) {
    if (editorInstance) {
      editorInstance.chain().focus().setImage({ src: url }).run();
    }
  }

  function insertTable(editorInstance: Editor | null, rows = 3, cols = 3) {
    if (editorInstance) {
      editorInstance.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run();
    }
  }

  return {
    activeFile,
    editorError,
    saving,
    createEditor,
    openFile,
    saveFile,
    createNewFile,
    addImage,
    insertTable,
    markdownToHtml,
    htmlToMarkdown,
  };
}
