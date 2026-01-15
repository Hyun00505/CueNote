
// Markdown to HTML conversion
export function markdownToHtml(md: string, isGithubFile = false, selectedRepo: any = null, coreBase = 'http://127.0.0.1:8787'): string {
  let html = md;
  
  // Normalize all line endings to \n (Windows uses \r\n, old Mac uses \r)
  html = html.replace(/\r\n|\r/g, '\n');

  // Code blocks first - handle with or without language, with flexible whitespace
  html = html.replace(/```(\w*)\s*\n([\s\S]*?)\n?```/g, (_, lang, code) => {
    // Remove trailing whitespace from code
    const cleanCode = code.replace(/\s+$/, '');
    return `<pre><code class="language-${lang}">${cleanCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
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

  // Images - Base64 이미지도 지원 (긴 URL 처리)
  // GitHub 파일일 때 상대 경로(img/...)를 로컬 서버 URL로 변환하여 에디터에서 표시
  html = html.replace(/!\[([^\]]*)\]\((data:[^)]+|[^)]+)\)/g, (match, alt, src) => {
    // GitHub 파일이고 상대 경로(img/...)인 경우 로컬 서버 URL로 변환
    if (isGithubFile && selectedRepo && src.startsWith('img/')) {
      const filename = src.replace('img/', '');
      src = `${coreBase}/github/repo/image/${selectedRepo.owner}/${selectedRepo.name}/${filename}`;
    }
    return `<img src="${src}" alt="${alt}">`;
  });

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
export function htmlToMarkdown(html: string, isGithubFile = false, selectedRepo: any = null, coreBase = 'http://127.0.0.1:8787'): string {
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

  // Code blocks first (before inline code to prevent breaking)
  md = md.replace(/<pre[^>]*><code[^>]*class="language-(\w*)"[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```$1\n$2```\n\n');
  md = md.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```\n$1```\n\n');
  // Inline code (after code blocks)
  md = md.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');

  // Links
  md = md.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');

  // Images - 다양한 속성 순서와 Base64 이미지 지원
  // GitHub 파일일 때 로컬 서버 URL을 상대 경로로 변환하여 저장 (GitHub에서 표시되도록)
  md = md.replace(/<img[^>]+>/gi, (match) => {
    const srcMatch = match.match(/src="([^"]+)"/i);
    const altMatch = match.match(/alt="([^"]*)"/i);
    let src = srcMatch ? srcMatch[1] : '';
    const alt = altMatch ? altMatch[1] : '';
    if (!src) return ''; // src가 없으면 무시
    
    // GitHub 파일일 때 로컬 서버 URL을 상대 경로로 변환
    if (isGithubFile && selectedRepo) {
      const githubImagePrefix = `${coreBase}/github/repo/image/${selectedRepo.owner}/${selectedRepo.name}/`;
      if (src.startsWith(githubImagePrefix)) {
        src = 'img/' + src.replace(githubImagePrefix, '');
      }
    }
    
    return `![${alt}](${src})`;
  });

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
