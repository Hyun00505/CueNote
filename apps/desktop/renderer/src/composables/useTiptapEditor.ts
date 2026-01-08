import { ref } from 'vue';
import { useEditor, type Editor } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Table from '@tiptap/extension-table';
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

const CORE_BASE = 'http://127.0.0.1:8787';

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

  // HTML to Markdown conversion (basic)
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

    // Code
    md = md.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');
    md = md.replace(/<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/gis, '```\n$1\n```\n\n');

    // Links
    md = md.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');

    // Images
    md = md.replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*\/?>/gi, '![$2]($1)');
    md = md.replace(/<img[^>]*src="([^"]*)"[^>]*\/?>/gi, '![]($1)');

    // Lists
    md = md.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (_, content) => {
      return content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n') + '\n';
    });
    md = md.replace(/<ol[^>]*>(.*?)<\/ol>/gis, (_, content) => {
      let index = 0;
      return content.replace(/<li[^>]*>(.*?)<\/li>/gi, () => `${++index}. `) + '\n';
    });

    // Task lists
    md = md.replace(/<li[^>]*data-checked="true"[^>]*>(.*?)<\/li>/gi, '- [x] $1\n');
    md = md.replace(/<li[^>]*data-checked="false"[^>]*>(.*?)<\/li>/gi, '- [ ] $1\n');

    // Paragraphs & line breaks
    md = md.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
    md = md.replace(/<br\s*\/?>/gi, '\n');

    // Blockquotes
    md = md.replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gis, (_, content) => {
      return content.split('\n').map((line: string) => `> ${line}`).join('\n') + '\n\n';
    });

    // Horizontal rules
    md = md.replace(/<hr\s*\/?>/gi, '\n---\n\n');

    // Tables (simplified)
    md = md.replace(/<table[^>]*>(.*?)<\/table>/gis, (_, tableContent) => {
      let result = '';
      const rows = tableContent.match(/<tr[^>]*>(.*?)<\/tr>/gis) || [];
      rows.forEach((row: string, index: number) => {
        const cells = row.match(/<t[hd][^>]*>(.*?)<\/t[hd]>/gi) || [];
        const rowContent = cells.map((cell: string) => {
          return cell.replace(/<t[hd][^>]*>(.*?)<\/t[hd]>/i, '$1').trim();
        }).join(' | ');
        result += `| ${rowContent} |\n`;
        if (index === 0) {
          result += `| ${cells.map(() => '---').join(' | ')} |\n`;
        }
      });
      return result + '\n';
    });

    // Clean up extra whitespace and HTML tags
    md = md.replace(/<[^>]+>/g, '');
    md = md.replace(/&nbsp;/g, ' ');
    md = md.replace(/&lt;/g, '<');
    md = md.replace(/&gt;/g, '>');
    md = md.replace(/&amp;/g, '&');
    md = md.replace(/\n{3,}/g, '\n\n');

    return md.trim();
  }

  // Markdown to HTML conversion (basic)
  function markdownToHtml(md: string): string {
    let html = md;

    // Escape HTML
    html = html.replace(/&/g, '&amp;');
    html = html.replace(/</g, '&lt;');
    html = html.replace(/>/g, '&gt;');

    // Code blocks (before other processing)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>');

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
      if (content.match(/^[\s\-|]+$/)) return ''; // Skip separator row
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

    return html;
  }

  async function openFile(filePath: string, editorInstance: Editor | null) {
    editorError.value = '';
    activeFile.value = filePath;

    try {
      const url = `${CORE_BASE}/vault/file?path=${encodeURIComponent(filePath)}`;
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
      const content = htmlToMarkdown(html);

      const res = await fetch(`${CORE_BASE}/vault/file`, {
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
      const res = await fetch(`${CORE_BASE}/vault/file`, {
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
