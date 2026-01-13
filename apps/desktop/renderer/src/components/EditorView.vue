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
            <span v-if="isDirty" class="unsaved-dot" title="저장되지 않은 변경사항"></span>
          </div>
        </div>
        <button class="save-btn" :class="{ saving, saved }" :disabled="saving" @click="handleSave">
          <svg v-if="saved" class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
          <svg v-else-if="!saving" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          <span class="spinner" v-else></span>
          <span v-if="saved">{{ t('common.save') }} ✓</span>
          <span v-else-if="saving">{{ t('common.loading') }}</span>
          <span v-else>{{ t('common.save') }}</span>
          <kbd v-if="!saved">Ctrl+S</kbd>
        </button>
      </div>
      
      <EditorToolbar 
        :editor="editor as Editor" 
        :summarizing="summarizing"
        :note-name="getFileName(activeFile)"
        :active-file="activeFile"
        @summarize="handleSummarize"
        @extract-result="handleExtractResult"
      />

      <!-- AI 요약 결과 패널 -->
      <Transition name="slide">
        <div v-if="summaryResult" class="summary-panel">
          <div class="summary-header">
            <div class="summary-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
              </svg>
              <span>AI 요약</span>
              <span class="word-count">{{ summaryResult.wordCount }}자</span>
            </div>
            <div class="summary-actions">
              <button class="action-btn" @click="copySummary" :title="copied ? '복사됨!' : '요약 복사'">
                <svg v-if="!copied" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </button>
              <button class="action-btn insert-btn" @click="insertSummary" title="노트 상단에 삽입">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12h14"/>
                </svg>
                <span>삽입</span>
              </button>
              <button class="close-btn" @click="summaryResult = null" title="닫기">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="summary-content">
            <p class="summary-text">{{ summaryResult.summary }}</p>
            <div v-if="summaryResult.keyPoints.length > 0" class="key-points">
              <h4>핵심 포인트</h4>
              <ul>
                <li v-for="(point, index) in summaryResult.keyPoints" :key="index">
                  {{ point }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </Transition>

      <div 
        ref="editorWrapperRef" 
        class="editor-content-wrapper" 
        :class="{ 'drag-over': isDraggingOver }"
        @contextmenu="handleContextMenu"
        @dragenter="handleDragEnter"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <EditorContent :editor="editor" class="editor-content" />
        
        <!-- AI 스트리밍 프리뷰 (실시간으로 생성 중인 텍스트 표시) -->
        <div v-if="isAIStreaming" class="ai-streaming-preview">
          <div class="streaming-header">
            <div class="streaming-dots">
              <span class="streaming-dot"></span>
              <span class="streaming-dot"></span>
              <span class="streaming-dot"></span>
            </div>
            <span class="streaming-label">AI {{ getActionLabel(aiStreamingAction) }}...</span>
          </div>
          <div class="streaming-content" v-html="streamPreviewHtml"></div>
        </div>
        
        <!-- AI 완료 후 액션 바 -->
        <Transition name="action-bar-slide">
          <div v-if="showAIActionBar" class="ai-action-bar">
            <div class="action-bar-indicator"></div>
            <span class="action-bar-label">AI {{ getActionLabel(aiStreamingAction) }} {{ t('ai.completed') }}</span>
            <div class="action-bar-buttons">
              <button class="action-btn reject" @click="handleAIReject">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                  <path d="M3 3v5h5"/>
                </svg>
                {{ t('ai.revert') }}
              </button>
              <button class="action-btn accept" @click="handleAIAccept">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
                {{ t('ai.keep') }}
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- AI 컨텍스트 메뉴 -->
      <AIContextMenu
        :visible="showAIMenu"
        :position="aiMenuPosition"
        :selected-text="selectedText"
        @close="closeAIMenu"
        @result="handleAIResult"
        @stream-start="handleStreamStart"
        @stream-chunk="handleStreamChunk"
        @stream-end="handleStreamEnd"
        @error="handleAIError"
        @proofread="handleProofread"
      />

      <!-- 맞춤법 검사 패널 -->
      <AIProofreadPanel
        :visible="showProofreadPanel"
        :loading="proofreadLoading"
        :original-text="proofreadOriginalText"
        :corrected-text="proofreadCorrectedText"
        :items="proofreadItems"
        :language-detected="proofreadLanguage"
        @close="handleProofreadClose"
        @apply-item="handleProofreadApplyItem"
        @apply-all="handleProofreadApplyAll"
        @skip-item="handleProofreadSkipItem"
        @skip-all="handleProofreadSkipAll"
        @focus-item="handleProofreadFocusItem"
      />

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
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue';
import { useEditor, EditorContent, type Editor } from '@tiptap/vue-3';
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
import { DOMSerializer } from '@tiptap/pm/model';
import EditorToolbar from './EditorToolbar.vue';
import AIContextMenu from './AIContextMenu.vue';
import AIInlineDiff from './AIInlineDiff.vue';
import AIProofreadPanel from './AIProofreadPanel.vue';
import { useSettings, useI18n, useShortcuts } from '../composables';

const lowlight = createLowlight(common);
const CORE_BASE = 'http://127.0.0.1:8787';

// LLM 설정 가져오기
const { settings: llmSettings } = useSettings();
const { t } = useI18n();
const { isAIMenuShortcut } = useShortcuts();

const props = defineProps<{
  activeFile: string | null;
}>();

const emit = defineEmits<{
  'dirty-change': [isDirty: boolean];
  'dirty-files-change': [files: string[]];
}>();

// dirty 파일 목록을 부모에게 전달하는 함수
function emitDirtyFiles() {
  const dirtyFiles: string[] = [];
  fileContentCache.forEach((value, key) => {
    if (value.isDirty) {
      dirtyFiles.push(key);
    }
  });
  // 현재 파일도 dirty이면 추가
  if (currentFilePath.value && isDirty.value && !dirtyFiles.includes(currentFilePath.value)) {
    dirtyFiles.push(currentFilePath.value);
  }
  emit('dirty-files-change', dirtyFiles);
}

const editorError = ref('');
const saving = ref(false);
const saved = ref(false);
const summarizing = ref(false);
const isDirty = ref(false);

interface SummaryResult {
  summary: string;
  keyPoints: string[];
  wordCount: number;
}
const summaryResult = ref<SummaryResult | null>(null);
const copied = ref(false);

// AI 컨텍스트 메뉴 상태
const showAIMenu = ref(false);
const aiMenuPosition = ref({ x: 0, y: 0 });
const selectedText = ref('');

// AI 스트리밍 상태 (노션 AI 스타일)
const isAIStreaming = ref(false);
const aiStreamingAction = ref('');
const originalText = ref('');  // 취소용 원본 텍스트 저장
const streamInsertPos = ref(0);  // 스트리밍 삽입 시작 위치
const showAIActionBar = ref(false);  // AI 완료 후 액션 바 표시
const streamedContent = ref('');  // 스트리밍 중 누적된 텍스트
const hasSelectionForAI = ref(true);  // AI 요청 시 선택이 있었는지

// 스트리밍 프리뷰 HTML (실시간 미리보기)
const streamPreviewHtml = computed(() => {
  if (!streamedContent.value) return '';
  return markdownToHtml(streamedContent.value);
});

// 선택 영역 저장 (나중에 적용할 때 사용)
const savedSelection = ref<{ from: number; to: number } | null>(null);

// 에디터 wrapper ref
const editorWrapperRef = ref<HTMLElement | null>(null);

// 드래그 앤 드롭 상태
const isDraggingOver = ref(false);
let dragCounter = 0;

// 레거시 diff 뷰 상태 (비활성화)
const showDiffView = ref(false);
const diffData = ref<any>(null);
const diffPosition = ref({ x: 0, y: 0 });

// 맞춤법 패널 상태
interface ProofreadItem {
  original: string;
  corrected: string;
  reason: string;
  type: string;
  applied?: boolean;
  skipped?: boolean;
  positions?: Array<{ from: number; to: number }>; // 에디터에서의 위치들
}

const showProofreadPanel = ref(false);
const proofreadLoading = ref(false);
const proofreadOriginalText = ref('');
const proofreadCorrectedText = ref('');
const proofreadItems = ref<ProofreadItem[]>([]);
const proofreadLanguage = ref('');

// 에디터에서 텍스트의 모든 위치 찾기 (범위 지정 가능)
function findTextPositions(
  searchText: string, 
  rangeStart?: number, 
  rangeEnd?: number
): Array<{ from: number; to: number }> {
  if (!editor.value) return [];
  
  const positions: Array<{ from: number; to: number }> = [];
  const doc = editor.value.state.doc;
  
  doc.descendants((node, pos) => {
    if (node.isText && node.text) {
      let index = 0;
      while (true) {
        const foundIndex = node.text.indexOf(searchText, index);
        if (foundIndex === -1) break;
        
        const from = pos + foundIndex;
        const to = pos + foundIndex + searchText.length;
        
        // 범위가 지정되었으면 범위 내 위치만 추가
        if (rangeStart !== undefined && rangeEnd !== undefined) {
          if (from >= rangeStart && to <= rangeEnd) {
            positions.push({ from, to });
          }
        } else {
          positions.push({ from, to });
        }
        index = foundIndex + 1;
      }
    }
    return true;
  });
  
  return positions;
}

// 맞춤법 오류 하이라이트 적용 (각 오류당 하나의 위치만)
function applyProofreadHighlights() {
  if (!editor.value) return;
  
  // 선택 범위 가져오기
  const rangeStart = savedSelection.value?.from;
  const rangeEnd = savedSelection.value?.to;
  
  // 이미 매칭된 위치를 추적 (같은 단어의 다른 오류 구분)
  const usedPositions: Set<string> = new Set();
  
  // 원본 텍스트에서 각 오류의 순서대로 위치를 찾음
  const originalText = proofreadOriginalText.value;
  
  proofreadItems.value.forEach((item, index) => {
    if (!item.applied && !item.skipped) {
      // 선택 범위 내에서 위치 찾기
      const positions = findTextPositions(item.original, rangeStart, rangeEnd);
      
      // 아직 사용되지 않은 첫 번째 위치 찾기
      let selectedPosition: { from: number; to: number } | null = null;
      
      for (const pos of positions) {
        const posKey = `${pos.from}-${pos.to}`;
        if (!usedPositions.has(posKey)) {
          selectedPosition = pos;
          usedPositions.add(posKey);
          break;
        }
      }
      
      // 범위 내에서 못 찾았으면 원본 텍스트에서 오프셋으로 계산
      if (!selectedPosition && rangeStart !== undefined) {
        let searchStart = 0;
        // 원본 텍스트에서 이 오류의 발생 횟수만큼 건너뛰기
        const sameItems = proofreadItems.value.slice(0, index).filter(
          i => i.original === item.original
        );
        
        for (let i = 0; i <= sameItems.length; i++) {
          const offset = originalText.indexOf(item.original, searchStart);
          if (offset === -1) break;
          
          if (i === sameItems.length) {
            const from = rangeStart + offset;
            const to = from + item.original.length;
            const posKey = `${from}-${to}`;
            if (!usedPositions.has(posKey)) {
              selectedPosition = { from, to };
              usedPositions.add(posKey);
            }
            break;
          }
          searchStart = offset + item.original.length;
        }
      }
      
      // 위치를 찾았으면 하이라이트 적용
      if (selectedPosition) {
        proofreadItems.value[index].positions = [selectedPosition];
        
        editor.value?.chain()
          .setTextSelection({ from: selectedPosition.from, to: selectedPosition.to })
          .setHighlight({ color: '#ef444480' })
          .run();
      } else {
        proofreadItems.value[index].positions = [];
      }
    }
  });
  
  // 선택 해제
  editor.value.commands.blur();
}

// 특정 항목의 하이라이트 제거 (위치 기반)
function removeItemHighlight(index: number) {
  if (!editor.value) return;
  
  const item = proofreadItems.value[index];
  if (!item.positions || item.positions.length === 0) return;
  
  // 해당 위치의 텍스트에서 하이라이트 제거
  const { from, to } = item.positions[0];
  const docSize = editor.value.state.doc.content.size;
  
  if (from < docSize && to <= docSize) {
    editor.value.chain()
      .setTextSelection({ from, to })
      .unsetHighlight()
      .setTextSelection(from) // 선택 해제
      .run();
  }
}

// 모든 맞춤법 하이라이트 제거 (전체 문서에서)
function removeAllProofreadHighlights() {
  if (!editor.value) return;
  
  // 전체 문서를 선택하고 모든 하이라이트 제거
  const { doc } = editor.value.state;
  const docSize = doc.content.size;
  
  if (docSize > 0) {
    editor.value.chain()
      .setTextSelection({ from: 0, to: docSize })
      .unsetHighlight()
      .setTextSelection(0) // 커서를 문서 시작으로
      .blur()
      .run();
  }
}

// 파일별 변경사항 캐시 (저장하지 않은 상태 유지)
const fileContentCache = new Map<string, { html: string; isDirty: boolean }>();
const currentFilePath = ref<string | null>(null);

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
  onUpdate: () => {
    if (!isDirty.value) {
      isDirty.value = true;
      emit('dirty-change', true);
      emitDirtyFiles();
    }
  },
});

function getFileName(path: string): string {
  const name = path.split(/[/\\]/).pop() || path;
  return name.replace(/\.md$/, '');
}

// Markdown to HTML conversion
function markdownToHtml(md: string): string {
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
  html = html.replace(/!\[([^\]]*)\]\((data:[^)]+|[^)]+)\)/g, '<img src="$2" alt="$1">');

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

  // Code blocks first (before inline code to prevent breaking)
  md = md.replace(/<pre[^>]*><code[^>]*class="language-(\w*)"[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```$1\n$2```\n\n');
  md = md.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```\n$1```\n\n');
  // Inline code (after code blocks)
  md = md.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');

  // Links
  md = md.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');

  // Images - 다양한 속성 순서와 Base64 이미지 지원
  md = md.replace(/<img[^>]+>/gi, (match) => {
    const srcMatch = match.match(/src="([^"]+)"/i);
    const altMatch = match.match(/alt="([^"]*)"/i);
    const src = srcMatch ? srcMatch[1] : '';
    const alt = altMatch ? altMatch[1] : '';
    if (!src) return ''; // src가 없으면 무시
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

async function openFile(filePath: string) {
  editorError.value = '';

  // 현재 파일의 변경사항을 캐시에 저장 (다른 파일로 전환 시)
  if (currentFilePath.value && editor.value && isDirty.value) {
    fileContentCache.set(currentFilePath.value, {
      html: editor.value.getHTML(),
      isDirty: true
    });
    emitDirtyFiles();
  }

  // 현재 파일 경로 업데이트
  currentFilePath.value = filePath;

  // 캐시에 저장된 내용이 있는지 확인
  const cachedContent = fileContentCache.get(filePath);
  
  if (cachedContent) {
    // 캐시된 내용 사용
    if (editor.value) {
      editor.value.commands.setContent(cachedContent.html, { emitUpdate: false });
    }
    isDirty.value = cachedContent.isDirty;
    emit('dirty-change', cachedContent.isDirty);
    return;
  }

  // 캐시에 없으면 서버에서 로드
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
      // 새 파일을 열 때 에디터 내용을 설정
      // emitUpdate: false로 히스토리에 추가되지 않도록 함
      editor.value.commands.setContent(htmlContent, { emitUpdate: false });
    }
    
    // 새 파일을 열면 dirty 상태 초기화
    isDirty.value = false;
    emit('dirty-change', false);
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
    
    // 저장 성공 시 dirty 상태 초기화
    isDirty.value = false;
    emit('dirty-change', false);
    
    // 저장 후 캐시에서 해당 파일 제거 (더 이상 저장되지 않은 변경사항 아님)
    fileContentCache.delete(props.activeFile);
    emitDirtyFiles();
    
    // 저장 완료 표시 (2초간)
    saved.value = true;
    setTimeout(() => {
      saved.value = false;
    }, 2000);
  } catch (error) {
    editorError.value = '저장 실패.';
    console.error('Save file failed', error);
  } finally {
    saving.value = false;
  }
}

// AI 요약 기능
async function handleSummarize() {
  if (!editor.value) return;
  
  summarizing.value = true;
  summaryResult.value = null;
  
  try {
    const html = editor.value.getHTML();
    const content = htmlToMarkdown(html);
    
    if (!content.trim()) {
      editorError.value = '요약할 내용이 없습니다.';
      return;
    }
    
    // 스트리밍 API를 사용하여 요약 (LLM 설정 포함)
    // language: 'auto'로 설정하여 원문과 같은 언어로 응답
    const body = {
      content,
      action: 'summarize',
      language: 'auto',
      provider: llmSettings.value.llm.provider,
      api_key: llmSettings.value.llm.apiKey,
      model: llmSettings.value.llm.model
    };
    
    const res = await fetch(`${CORE_BASE}/ai/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    const data = await res.json();
    summaryResult.value = {
      summary: data.summary,
      keyPoints: data.keyPoints || [],
      wordCount: data.wordCount
    };
  } catch (error) {
    const providerName = llmSettings.value.llm.provider === 'gemini' ? 'Gemini API' : 'Ollama';
    editorError.value = `요약 생성에 실패했습니다. ${providerName}가 올바르게 설정되었는지 확인하세요.`;
    console.error('Summarize failed:', error);
  } finally {
    summarizing.value = false;
  }
}

// 요약 복사
function copySummary() {
  if (!summaryResult.value) return;
  
  const text = formatSummaryAsMarkdown();
  navigator.clipboard.writeText(text).then(() => {
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  });
}

// 요약을 마크다운 형식으로 포맷
function formatSummaryAsMarkdown(): string {
  if (!summaryResult.value) return '';
  
  let md = `## 📝 요약\n\n${summaryResult.value.summary}\n`;
  
  if (summaryResult.value.keyPoints.length > 0) {
    md += `\n### 핵심 포인트\n\n`;
    summaryResult.value.keyPoints.forEach(point => {
      md += `- ${point}\n`;
    });
  }
  
  return md;
}

// 요약을 노트 상단에 삽입
function insertSummary() {
  if (!editor.value || !summaryResult.value) return;
  
  const summaryHtml = formatSummaryAsHtml();
  
  // 에디터의 시작 위치에 삽입
  editor.value.chain()
    .focus()
    .insertContentAt(0, summaryHtml + '<hr><p></p>')
    .run();
  
  // 패널 닫기
  summaryResult.value = null;
}

// 요약을 HTML 형식으로 포맷
function formatSummaryAsHtml(): string {
  if (!summaryResult.value) return '';
  
  let html = `<h2>📝 요약</h2><p>${summaryResult.value.summary}</p>`;
  
  if (summaryResult.value.keyPoints.length > 0) {
    html += `<h3>핵심 포인트</h3><ul>`;
    summaryResult.value.keyPoints.forEach(point => {
      html += `<li><p>${point}</p></li>`;
    });
    html += `</ul>`;
  }
  
  return html;
}

// Keyboard shortcut for save
function handleKeydown(e: KeyboardEvent) {
  // 저장: Ctrl/Cmd + S
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    handleSave();
    return;
  }
  
  // AI 메뉴 단축키 확인
  if (isAIMenuShortcut(e)) {
    // 에디터에 포커스가 있을 때만 동작
    if (!editor.value?.isFocused) return;
    
    // / 키는 빈 줄에서만 동작 (텍스트 입력 중에는 / 입력 허용)
    if (e.key === '/') {
      const { state } = editor.value;
      const { from } = state.selection;
      const $pos = state.doc.resolve(from);
      const lineStart = $pos.start();
      const lineText = state.doc.textBetween(lineStart, from, '', '');
      
      // 현재 줄에 내용이 있으면 / 입력 허용
      if (lineText.trim()) return;
    }
    
    e.preventDefault();
    openAIMenuAtCursor();
  }
}

// 커서 위치에서 AI 메뉴 열기
function openAIMenuAtCursor() {
  if (!editor.value) return;
  
  const { state } = editor.value;
  const { from, to } = state.selection;
  
  // 선택된 텍스트가 있으면 저장
  if (from !== to) {
    const markdown = getSelectedMarkdown();
    selectedText.value = markdown;
  } else {
    selectedText.value = '';
  }
  
  // 커서 위치 가져오기
  const coords = editor.value.view.coordsAtPos(from);
  
  // 메뉴 위치 설정
  const menuWidth = 260;
  const menuHeight = 500;
  let x = coords.left;
  let y = coords.bottom + 8;  // 커서 아래에 약간 여백
  
  if (x + menuWidth > window.innerWidth) {
    x = window.innerWidth - menuWidth - 10;
  }
  if (y + menuHeight > window.innerHeight) {
    y = coords.top - menuHeight - 8;  // 위에 표시
  }
  if (y < 10) {
    y = 10;
  }
  
  aiMenuPosition.value = { x, y };
  showAIMenu.value = true;
}

// 문서 추출 결과 처리
function handleExtractResult(markdown: string) {
  if (!editor.value) return;
  
  // 마크다운을 HTML로 변환
  const html = markdownToHtml(markdown);
  
  // 현재 커서 위치에 삽입
  editor.value.chain()
    .focus()
    .insertContent(html)
    .run();
  
  // 자동 저장
  handleSave();
}

// 선택된 영역의 텍스트를 마크다운으로 가져오기
function getSelectedMarkdown(): string {
  if (!editor.value) return '';
  
  const { from, to } = editor.value.state.selection;
  if (from === to) return '';
  
  try {
    // 선택된 부분의 slice를 가져와서 HTML로 변환 후 마크다운으로 변환
    const { state } = editor.value;
    const slice = state.doc.slice(from, to);
    
    // slice를 임시 fragment로 만들어서 HTML 생성
    const serializer = DOMSerializer.fromSchema(state.schema);
    const fragment = slice.content;
    
    // DOM으로 변환
    const div = document.createElement('div');
    fragment.forEach(node => {
      const domNode = serializer.serializeNode(node);
      div.appendChild(domNode);
    });
    
    // HTML을 마크다운으로 변환
    const html = div.innerHTML;
    const markdown = htmlToMarkdown(html);
    
    // 결과가 비어있으면 plain text 사용
    if (!markdown.trim()) {
      return state.doc.textBetween(from, to, '\n');
    }
    
    return markdown;
  } catch (e) {
    console.warn('Failed to get markdown, using plain text:', e);
    return editor.value.state.doc.textBetween(from, to, '\n');
  }
}

// 우클릭 컨텍스트 메뉴 처리
function handleContextMenu(e: MouseEvent) {
  if (!editor.value) return;
  
  e.preventDefault();
  
  const { state } = editor.value;
  const { from, to } = state.selection;
  
  // 텍스트가 선택되어 있으면 선택된 텍스트 저장
  if (from !== to) {
    const markdown = getSelectedMarkdown();
    selectedText.value = markdown;
  } else {
    // 선택된 텍스트 없음
    selectedText.value = '';
  }
  
  // 메뉴 위치 설정 (화면 경계 고려)
  const menuWidth = 260;
  const menuHeight = 500;
  let x = e.clientX;
  let y = e.clientY;
  
  if (x + menuWidth > window.innerWidth) {
    x = window.innerWidth - menuWidth - 10;
  }
  if (y + menuHeight > window.innerHeight) {
    y = window.innerHeight - menuHeight - 10;
  }
  
  aiMenuPosition.value = { x, y };
  showAIMenu.value = true;
}

// AI 메뉴 닫기
function closeAIMenu() {
  showAIMenu.value = false;
  selectedText.value = '';
}

// AI 결과 처리
interface AIResult {
  action: string;
  original: string;
  result: string;
  meta?: any;
}

function handleAIResult(data: AIResult) {
  if (!editor.value) return;
  
  // 현재 선택 영역 저장
  const { from, to } = editor.value.state.selection;
  savedSelection.value = { from, to };
  
  // 선택 영역의 DOM 위치 계산
  const coords = editor.value.view.coordsAtPos(from);
  const wrapper = editorWrapperRef.value;
  
  if (coords && wrapper) {
    const editorRect = wrapper.getBoundingClientRect();
    const scrollTop = wrapper.scrollTop;
    
    // 선택 영역 시작 위치 기준으로 diff 뷰 위치 설정 (스크롤 고려)
    diffPosition.value = {
      x: 48, // 에디터 패딩과 일치
      y: coords.top - editorRect.top + scrollTop
    };
  }
  
  // diff 데이터 설정
  diffData.value = {
    action: data.action,
    original: data.original,
    result: data.result,
    meta: data.meta
  };
  
  // diff 뷰 표시
  showDiffView.value = true;
  
  // 선택 해제 (diff 뷰에서 원본을 보여주므로)
  editor.value.commands.setTextSelection(from);
}

// 원본 HTML 저장 (되돌리기용)
const originalHtml = ref('');

// 스트리밍 시작 처리 - 원본 유지, 프리뷰만 표시
function handleStreamStart(data: { action: string; original: string; hasSelection?: boolean }) {
  if (!editor.value) {
    console.warn('Editor not available for AI streaming');
    return;
  }
  
  // 전체 문서의 현재 HTML 저장 (되돌리기용)
  originalHtml.value = editor.value.getHTML();
  
  // 현재 선택 영역 저장 (에디터 상태가 있을 때만)
  try {
    const { from, to } = editor.value.state.selection;
    savedSelection.value = { from, to };
  } catch (e) {
    // 에디터 상태를 가져올 수 없으면 문서 끝에 삽입
    const docEnd = editor.value.state.doc.content.size;
    savedSelection.value = { from: docEnd, to: docEnd };
  }
  
  // 원본 텍스트 저장 (선택 없으면 빈 문자열)
  originalText.value = data.original || '';
  aiStreamingAction.value = data.action;
  streamedContent.value = '';
  hasSelectionForAI.value = data.hasSelection !== false && !!data.original;
  
  // 원본은 삭제하지 않음 - 스트리밍 완료 후 교체
  isAIStreaming.value = true;
  showAIActionBar.value = false;
}

// 스트리밍 청크 수신 처리 - 누적만 (에디터에 삽입하지 않음)
function handleStreamChunk(chunk: string) {
  if (!isAIStreaming.value) return;
  
  // \r (캐리지 리턴) 제거 - Ollama가 각 토큰마다 \r을 추가하는 문제 해결
  const cleanedChunk = chunk.replace(/\r/g, '');
  
  // 청크 누적만 (에디터 삽입은 종료 시 한 번에)
  streamedContent.value += cleanedChunk;
}

// AI 모델 출력 보정 (잘못된 줄바꿈/공백 정리)
function cleanupAIOutput(text: string): string {
  let result = text;
  
  // 글자마다 줄바꿈이 있는지 감지
  // 방법 1: 평균 줄 길이가 5자 미만이면 비정상
  // 방법 2: 줄바꿈 개수가 전체 문자 수의 20% 이상이면 비정상
  const lines = text.split('\n').filter(l => l.trim());
  const avgLineLength = lines.length > 0 
    ? lines.reduce((a, l) => a + l.length, 0) / lines.length 
    : 100;
  
  const newlineCount = (text.match(/\n/g) || []).length;
  const totalChars = text.replace(/\s/g, '').length;
  const newlineRatio = totalChars > 0 ? newlineCount / totalChars : 0;
  
  const isCharByCharNewline = avgLineLength < 5 || newlineRatio > 0.2;
  
  if (isCharByCharNewline) {
    // 글자마다 줄바꿈이 있는 경우 → 공격적으로 정리
    
    // 1. 마크다운 헤더를 임시 마커로 변환 (보존용)
    result = result.replace(/^(#{1,6})\s*/gm, '___HEADER$1___');
    
    // 2. 모든 줄바꿈과 공백을 하나의 공백으로
    result = result.replace(/[\n\r]+/g, ' ');
    result = result.replace(/\s+/g, ' ');
    
    // 3. 한글 문자 사이 공백 제거 (반복 적용)
    let prev = '';
    let iterations = 0;
    while (prev !== result && iterations < 50) {
      prev = result;
      // 한글-한글
      result = result.replace(/([가-힣])\s+([가-힣])/g, '$1$2');
      // 한글-숫자, 숫자-한글
      result = result.replace(/([가-힣])\s+(\d)/g, '$1$2');
      result = result.replace(/(\d)\s+([가-힣])/g, '$1$2');
      // 숫자-숫자
      result = result.replace(/(\d)\s+(\d)/g, '$1$2');
      // 한글-구두점
      result = result.replace(/([가-힣])\s+([,.!?:;])/g, '$1$2');
      // 구두점-한글
      result = result.replace(/([,.!?:;])\s+([가-힣])/g, '$1$2');
      // 괄호 처리
      result = result.replace(/\(\s+/g, '(');
      result = result.replace(/\s+\)/g, ')');
      result = result.replace(/\[\s+/g, '[');
      result = result.replace(/\s+\]/g, ']');
      iterations++;
    }
    
    // 4. 영어 단어는 공백 유지 (영어-영어 사이만)
    // 이미 공백이 하나로 정리되어 있으므로 추가 처리 불필요
    
    // 5. 마크다운 헤더 복원
    result = result.replace(/___HEADER(#{1,6})___\s*/g, '\n\n$1 ');
    
    // 6. 문장 끝 뒤에 줄바꿈 추가 (한국어 문장 끝)
    result = result.replace(/([.!?。])\s*(?=[가-힣A-Z#\[])/g, '$1\n\n');
    
    // 7. 리스트 마커 앞에 줄바꿈
    result = result.replace(/\s*(-|\*|\d+\.)\s+/g, '\n$1 ');
    
    // 8. 앵커/인용 태그 처리
    result = result.replace(/\[([^\]]+)\]/g, (match, content) => {
      // 대괄호 안의 내용에서 공백 제거
      return '[' + content.replace(/\s+/g, '') + ']';
    });
    
  } else {
    // 정상적인 출력 → 가벼운 정리만
    
    // 1. 3개 이상 연속 줄바꿈을 2개로
    result = result.replace(/\n{3,}/g, '\n\n');
    
    // 2. 연속 공백 하나로
    result = result.replace(/ +/g, ' ');
    
    // 3. 줄 끝 공백 제거
    result = result.replace(/ +$/gm, '');
  }
  
  // 공통: 시작/끝 정리
  result = result.replace(/^\s+/, '');
  result = result.replace(/\s+$/, '');
  
  // 연속 줄바꿈 정리
  result = result.replace(/\n{3,}/g, '\n\n');
  
  return result.trim();
}

// 스트리밍 종료 처리 - 선택 영역을 AI 결과로 교체
function handleStreamEnd() {
  isAIStreaming.value = false;
  
  if (!editor.value) {
    console.warn('Editor not available for AI result');
    return;
  }
  
  // 스트리밍된 텍스트를 마크다운 HTML로 변환
  if (streamedContent.value.trim()) {
    const html = markdownToHtml(streamedContent.value);
    
    try {
      if (savedSelection.value && hasSelectionForAI.value) {
        // 선택 영역이 있었으면 교체
        const { from, to } = savedSelection.value;
        editor.value.chain()
          .focus()
          .setTextSelection({ from, to })
          .deleteSelection()
          .insertContent(html)
          .run();
      } else if (savedSelection.value) {
        // 선택 영역이 없었으면 저장된 커서 위치에 삽입
        const { from } = savedSelection.value;
        editor.value.chain()
          .focus()
          .setTextSelection(from)
          .insertContent(html)
          .run();
      } else {
        // savedSelection이 없으면 문서 끝에 삽입
        editor.value.chain()
          .focus()
          .insertContent(html)
          .run();
      }
    } catch (e) {
      console.error('Failed to insert AI content:', e);
      // 에러 발생 시 문서 끝에 삽입 시도
      editor.value.chain()
        .focus()
        .insertContent(html)
        .run();
    }
  }
  
  showAIActionBar.value = true;
}

// AI 변경 적용
function handleAIAccept() {
  showAIActionBar.value = false;
  originalText.value = '';
  originalHtml.value = '';
  streamedContent.value = '';
  savedSelection.value = null;
  handleSave();
}

// AI 변경 취소 (원본 복원)
function handleAIReject() {
  if (!editor.value) return;
  
  // 저장해둔 원본 HTML로 전체 문서 복원
  if (originalHtml.value) {
    editor.value.commands.setContent(originalHtml.value);
  }
  
  showAIActionBar.value = false;
  originalText.value = '';
  originalHtml.value = '';
  streamedContent.value = '';
  savedSelection.value = null;
}

// ─────────────────────────────────────────────────────────────────────────────
// 맞춤법 검사 관련 함수
// ─────────────────────────────────────────────────────────────────────────────

// 맞춤법 검사 시작
async function handleProofread(text: string) {
  if (!text.trim()) return;
  
  proofreadOriginalText.value = text;
  proofreadLoading.value = true;
  showProofreadPanel.value = true;
  proofreadItems.value = [];
  proofreadCorrectedText.value = '';
  proofreadLanguage.value = '';
  
  // 현재 선택 영역 저장
  if (editor.value) {
    const { from, to } = editor.value.state.selection;
    savedSelection.value = { from, to };
  }
  
  try {
    const body = {
      content: text,
      language: 'auto',
      provider: llmSettings.value.llm.provider,
      api_key: llmSettings.value.llm.apiKey,
      model: llmSettings.value.llm.model
    };
    
    const res = await fetch(`${CORE_BASE}/ai/proofread`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    const data = await res.json();
    proofreadCorrectedText.value = data.corrected || text;
    proofreadLanguage.value = data.language_detected || '';
    proofreadItems.value = (data.items || []).map((item: ProofreadItem) => ({
      ...item,
      applied: false,
      skipped: false,
      positions: []
    }));
    
    // 오류 항목에 하이라이트 적용
    if (proofreadItems.value.length > 0) {
      setTimeout(() => {
        applyProofreadHighlights();
      }, 100);
    }
    
  } catch (error) {
    console.error('Proofread failed:', error);
    const providerName = llmSettings.value.llm.provider === 'gemini' ? 'Gemini API' : 'Ollama';
    handleAIError(`맞춤법 검사에 실패했습니다. ${providerName}가 올바르게 설정되었는지 확인하세요.`);
    showProofreadPanel.value = false;
  } finally {
    proofreadLoading.value = false;
  }
}

// 개별 맞춤법 수정 적용
function handleProofreadApplyItem(data: { index: number; original: string; corrected: string }) {
  if (!editor.value) return;
  
  const { index, original, corrected } = data;
  const item = proofreadItems.value[index];
  
  // 저장된 위치가 있으면 해당 위치에서 교체
  if (item.positions && item.positions.length > 0) {
    // 첫 번째 위치만 교체 (같은 오류가 여러 번 있을 수 있음)
    const { from, to } = item.positions[0];
    const docSize = editor.value.state.doc.content.size;
    
    if (from < docSize && to <= docSize) {
      // 해당 위치의 텍스트가 여전히 원본과 일치하는지 확인
      const currentText = editor.value.state.doc.textBetween(from, to);
      
      if (currentText === original) {
        // 하이라이트 제거 후 텍스트 교체
        editor.value.chain()
          .setTextSelection({ from, to })
          .unsetHighlight()
          .deleteSelection()
          .insertContent(corrected)
          .blur()
          .run();
        
        proofreadItems.value[index].applied = true;
        
        // 위치가 변경되었으므로 다른 항목들의 위치 업데이트 필요
        updateProofreadPositions(index, corrected.length - original.length);
        return;
      }
    }
  }
  
  // 저장된 위치가 없거나 변경되었으면 텍스트로 직접 검색
  // 이미 적용된 항목들의 위치를 제외한 위치를 찾음
  const appliedPositions = new Set<string>();
  proofreadItems.value.forEach((i, idx) => {
    if (idx !== index && i.applied && i.positions && i.positions.length > 0) {
      // 이미 적용된 위치 추적
    }
    if (idx !== index && !i.applied && !i.skipped && i.positions && i.positions.length > 0) {
      appliedPositions.add(`${i.positions[0].from}-${i.positions[0].to}`);
    }
  });
  
  const positions = findTextPositions(original);
  
  // 다른 항목에 할당되지 않은 첫 번째 위치 찾기
  let targetPos: { from: number; to: number } | null = null;
  for (const pos of positions) {
    const posKey = `${pos.from}-${pos.to}`;
    if (!appliedPositions.has(posKey)) {
      targetPos = pos;
      break;
    }
  }
  
  if (targetPos) {
    const { from, to } = targetPos;
    
    editor.value.chain()
      .setTextSelection({ from, to })
      .unsetHighlight()
      .deleteSelection()
      .insertContent(corrected)
      .blur()
      .run();
    
    proofreadItems.value[index].applied = true;
    updateProofreadPositions(index, corrected.length - original.length);
  } else {
    // 텍스트를 찾을 수 없는 경우 (이미 수정되었거나 없음)
    console.warn(`Could not find text to replace: "${original}"`);
    proofreadItems.value[index].applied = true;
  }
}

// 텍스트 교체 후 다른 항목들의 위치 업데이트
function updateProofreadPositions(appliedIndex: number, lengthDiff: number) {
  const appliedItem = proofreadItems.value[appliedIndex];
  const appliedFrom = appliedItem.positions?.[0]?.from ?? 0;
  
  proofreadItems.value.forEach((item, index) => {
    if (index !== appliedIndex && item.positions && !item.applied && !item.skipped) {
      item.positions = item.positions.map(pos => {
        if (pos.from > appliedFrom) {
          return {
            from: pos.from + lengthDiff,
            to: pos.to + lengthDiff
          };
        }
        return pos;
      });
    }
  });
}

// 모든 맞춤법 수정 적용
function handleProofreadApplyAll() {
  if (!editor.value) return;
  
  // 뒤에서부터 적용하여 위치 변경 문제 방지
  const sortedIndices = proofreadItems.value
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => !item.applied && !item.skipped && item.positions && item.positions.length > 0)
    .sort((a, b) => {
      const posA = a.item.positions?.[0]?.from ?? 0;
      const posB = b.item.positions?.[0]?.from ?? 0;
      return posB - posA; // 뒤에서부터 처리
    });
  
  sortedIndices.forEach(({ item, index }) => {
    if (item.positions && item.positions.length > 0) {
      const { from, to } = item.positions[0];
      const docSize = editor.value!.state.doc.content.size;
      
      if (from < docSize && to <= docSize) {
        editor.value!.chain()
          .setTextSelection({ from, to })
          .unsetHighlight()
          .deleteSelection()
          .insertContent(item.corrected)
          .run();
        
        proofreadItems.value[index].applied = true;
      }
    }
  });
  
  editor.value.commands.blur();
}

// 개별 맞춤법 수정 무시
function handleProofreadSkipItem(index: number) {
  // 하이라이트 제거
  removeItemHighlight(index);
  proofreadItems.value[index].skipped = true;
  editor.value?.commands.blur();
}

// 모든 맞춤법 수정 무시
function handleProofreadSkipAll() {
  proofreadItems.value.forEach((item, index) => {
    if (!item.applied && !item.skipped) {
      removeItemHighlight(index);
      proofreadItems.value[index].skipped = true;
    }
  });
  editor.value?.commands.blur();
}

// 맞춤법 패널 닫기
function handleProofreadClose() {
  // 남은 하이라이트 모두 제거
  removeAllProofreadHighlights();
  
  showProofreadPanel.value = false;
  proofreadItems.value = [];
  proofreadOriginalText.value = '';
  proofreadCorrectedText.value = '';
  savedSelection.value = null;
}

// 특정 맞춤법 항목으로 포커스 이동
function handleProofreadFocusItem(index: number) {
  if (!editor.value) return;
  
  const item = proofreadItems.value[index];
  if (!item.positions || item.positions.length === 0) {
    // 위치 정보가 없으면 다시 찾기
    const positions = findTextPositions(item.original);
    if (positions.length > 0) {
      proofreadItems.value[index].positions = positions;
    }
  }
  
  if (item.positions && item.positions.length > 0) {
    const { from, to } = item.positions[0];
    const docSize = editor.value.state.doc.content.size;
    
    if (from < docSize && to <= docSize) {
      // 해당 위치로 스크롤 및 선택
      editor.value.chain()
        .focus()
        .setTextSelection({ from, to })
        .scrollIntoView()
        .run();
    }
  }
}

// AI 액션 라벨 반환
function getActionLabel(action: string): string {
  const labels: Record<string, string> = {
    translate: '번역',
    improve: '다듬기',
    expand: '확장',
    shorten: '축약',
    summarize: '요약',
    proofread: '맞춤법'
  };
  return labels[action] || '변환';
}

// diff Accept 처리
function handleDiffAccept() {
  if (!editor.value || !diffData.value || !savedSelection.value) return;
  
  const { action, result, meta } = diffData.value;
  const { from, to } = savedSelection.value;
  
  // 요약의 경우 특별 처리 (교체하지 않고 아래에 추가)
  if (action === 'summarize') {
    let summaryContent = `\n\n> **📝 요약:** ${result}`;
    if (meta?.keyPoints && meta.keyPoints.length > 0) {
      summaryContent += '\n>\n> **핵심 포인트:**';
      meta.keyPoints.forEach((point: string) => {
        summaryContent += `\n> - ${point}`;
      });
    }
    
    // 선택 영역 끝에 요약 추가
    editor.value.chain()
      .focus()
      .insertContentAt(to, summaryContent)
      .run();
  } else {
    // 다른 작업들은 선택된 텍스트를 결과로 교체
    editor.value.chain()
      .focus()
      .setTextSelection({ from, to })
      .deleteSelection()
      .insertContent(result)
      .run();
  }
  
  // diff 뷰 닫기
  closeDiffView();
}

// diff Reject 처리
function handleDiffReject() {
  closeDiffView();
}

// diff 뷰 닫기
function closeDiffView() {
  showDiffView.value = false;
  diffData.value = null;
  savedSelection.value = null;
}

// AI 에러 처리
function handleAIError(message: string) {
  editorError.value = message;
  setTimeout(() => {
    editorError.value = '';
  }, 5000);
}

// 드래그 앤 드롭 핸들러
function handleDragEnter(e: DragEvent) {
  e.preventDefault();
  e.stopPropagation();
  dragCounter++;
  
  if (e.dataTransfer?.types.includes('Files')) {
    isDraggingOver.value = true;
  }
}

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  e.stopPropagation();
  
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'copy';
  }
}

function handleDragLeave(e: DragEvent) {
  e.preventDefault();
  e.stopPropagation();
  dragCounter--;
  
  if (dragCounter === 0) {
    isDraggingOver.value = false;
  }
}

async function handleDrop(e: DragEvent) {
  e.preventDefault();
  e.stopPropagation();
  
  dragCounter = 0;
  isDraggingOver.value = false;
  
  if (!editor.value || !e.dataTransfer?.files.length) return;
  
  const files = Array.from(e.dataTransfer.files);
  const imageFiles = files.filter(file => file.type.startsWith('image/'));
  
  if (imageFiles.length === 0) {
    handleAIError('이미지 파일만 드롭할 수 있습니다.');
    return;
  }
  
  // 드롭 위치 계산
  const view = editor.value.view;
  const pos = view.posAtCoords({ left: e.clientX, top: e.clientY });
  
  for (const file of imageFiles) {
    try {
      // 파일을 Base64로 변환 후 서버에 업로드
      const base64 = await fileToBase64(file);
      const imageUrl = await uploadImage(base64);
      
      if (!imageUrl) {
        handleAIError('이미지 업로드에 실패했습니다.');
        continue;
      }
      
      // 에디터에 이미지 삽입 (서버 URL 사용)
      if (pos) {
        editor.value.chain()
          .focus()
          .setTextSelection(pos.pos)
          .setImage({ src: imageUrl })
          .run();
      } else {
        // 위치를 찾을 수 없으면 현재 커서 위치에 삽입
        editor.value.chain()
          .focus()
          .setImage({ src: imageUrl })
          .run();
      }
    } catch (error) {
      console.error('Image drop failed:', error);
      handleAIError('이미지 삽입에 실패했습니다.');
    }
  }
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// 이미지를 서버에 업로드하고 URL 반환
async function uploadImage(base64Data: string): Promise<string | null> {
  try {
    // 현재 편집 중인 파일명 추출
    const noteName = props.activeFile || undefined;
    
    const res = await fetch(`${CORE_BASE}/vault/image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        data: base64Data,
        note_name: noteName  // 이미지 파일명에 노트 이름 포함
      })
    });
    
    if (!res.ok) {
      console.error('Image upload failed:', res.status);
      return null;
    }
    
    const data = await res.json();
    // 서버에서 반환한 URL 사용 (예: /vault/image/xxx.png)
    return `${CORE_BASE}${data.url}`;
  } catch (error) {
    console.error('Image upload error:', error);
    return null;
  }
}

// Electron에서 파일 드롭 시 새 창 열리는 것 방지
function preventDefaultDrop(e: DragEvent) {
  e.preventDefault();
  e.stopPropagation();
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  
  // 전역 드래그 앤 드롭 기본 동작 방지 (Electron에서 새 창 열리는 것 방지)
  document.addEventListener('dragover', preventDefaultDrop);
  document.addEventListener('drop', preventDefaultDrop);
  
  if (props.activeFile) {
    openFile(props.activeFile);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
  document.removeEventListener('dragover', preventDefaultDrop);
  document.removeEventListener('drop', preventDefaultDrop);
  editor.value?.destroy();
});

watch(() => props.activeFile, (newFile) => {
  if (newFile) {
    openFile(newFile);
  }
});

// 외부에서 접근 가능한 메서드/상태 노출
defineExpose({
  isDirty,
  save: handleSave,
  saveFile: handleSave
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
}

.empty-visual {
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 24px;
}

.empty-glow {
  display: none;
}

.empty-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  color: var(--text-muted);
}

.empty-state h2 {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 20px;
}

.empty-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 12px;
}

.empty-hint svg {
  color: var(--accent-secondary);
  opacity: 0.7;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(232, 213, 183, 0.1);
  border-radius: 6px;
  color: #e8d5b7;
}

.file-details {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.file-ext {
  font-size: 12px;
  color: var(--text-muted);
}

.unsaved-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #f59e0b;
  border-radius: 50%;
  margin-left: 8px;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.save-btn:hover:not(:disabled) {
  background: rgba(232, 213, 183, 0.15);
  border-color: rgba(232, 213, 183, 0.3);
  color: #e8d5b7;
}

.save-btn.saving {
  background: rgba(232, 213, 183, 0.1);
  color: #e8d5b7;
}

.save-btn.saved {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.3);
  color: #4ade80;
}

.save-btn.saved .check-icon {
  color: #4ade80;
  animation: check-pop 0.3s ease;
}

@keyframes check-pop {
  0% { transform: scale(0.5); opacity: 0; }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

.save-btn.saved kbd {
  display: none;
}

.save-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.save-btn kbd {
  padding: 2px 5px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(232, 213, 183, 0.2);
  border-top-color: #e8d5b7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.editor-content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 32px 48px;
  background: var(--bg-primary);
  position: relative;
  transition: all 0.2s ease;
}

.editor-content-wrapper.drag-over {
  background: rgba(201, 167, 108, 0.05);
  outline: 2px dashed rgba(201, 167, 108, 0.5);
  outline-offset: -8px;
}

.editor-content-wrapper.drag-over::after {
  content: '이미지를 여기에 드롭하세요';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 40px;
  background: rgba(30, 30, 35, 0.95);
  border: 2px dashed rgba(201, 167, 108, 0.6);
  border-radius: 16px;
  color: #e8d5b7;
  font-size: 16px;
  font-weight: 500;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.editor-content {
  max-width: 760px;
  margin: 0 auto;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  margin: 12px 20px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 6px;
  color: #dc2626;
  font-size: 13px;
}

/* AI Summary Panel */
.summary-panel {
  margin: 0 20px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(99, 102, 241, 0.05));
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 10px;
  overflow: hidden;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(139, 92, 246, 0.1);
  border-bottom: 1px solid rgba(139, 92, 246, 0.15);
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a78bfa;
  font-size: 13px;
  font-weight: 600;
}

.summary-title svg {
  opacity: 0.8;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 28px;
  padding: 0 10px;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 6px;
  color: #a78bfa;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: rgba(139, 92, 246, 0.25);
  border-color: rgba(139, 92, 246, 0.4);
  color: #c4b5fd;
}

.action-btn.insert-btn {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.25);
  color: #4ade80;
}

.action-btn.insert-btn:hover {
  background: rgba(34, 197, 94, 0.25);
  border-color: rgba(34, 197, 94, 0.4);
  color: #86efac;
}

.word-count {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.summary-content {
  padding: 16px;
}

.summary-text {
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.7;
  margin: 0 0 16px 0;
}

.key-points h4 {
  color: #a78bfa;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 10px 0;
}

.key-points ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.key-points li {
  position: relative;
  padding-left: 18px;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.key-points li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #a78bfa;
  font-weight: bold;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

</style>

<style>
/* TipTap Editor Global Styles */
.ProseMirror {
  outline: none;
  min-height: 500px;
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.75;
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
  font-style: italic;
}

/* Headings */
.ProseMirror h1 {
  font-family: var(--font-serif);
  font-size: 2em;
  font-weight: 600;
  line-height: 1.3;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.ProseMirror h2 {
  font-family: var(--font-serif);
  font-size: 1.5em;
  font-weight: 600;
  line-height: 1.35;
  margin-top: 1.4em;
  margin-bottom: 0.5em;
  color: var(--text-primary);
}

.ProseMirror h3 {
  font-size: 1.25em;
  font-weight: 600;
  line-height: 1.4;
  margin-top: 1.3em;
  margin-bottom: 0.4em;
  color: var(--text-primary);
}

.ProseMirror h4,
.ProseMirror h5,
.ProseMirror h6 {
  font-size: 1.05em;
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
  color: #c9a76c;
  text-decoration: underline;
  text-decoration-color: rgba(201, 167, 108, 0.4);
  text-underline-offset: 2px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.ProseMirror a:hover {
  color: #e8d5b7;
  text-decoration-color: rgba(232, 213, 183, 0.6);
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
  background: rgba(201, 167, 108, 0.25);
  padding: 1px 4px;
  border-radius: 2px;
}

/* 맞춤법 오류 하이라이트 - 빨간색 물결 밑줄 효과 */
.ProseMirror mark[data-color="#ef444480"] {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.15) 100%);
  border-bottom: 2px wavy #ef4444;
  padding: 0 2px;
  border-radius: 2px;
  animation: proofread-pulse 2s ease-in-out infinite;
}

@keyframes proofread-pulse {
  0%, 100% { 
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.15) 100%);
  }
  50% { 
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.3) 0%, rgba(239, 68, 68, 0.25) 100%);
  }
}

/* Inline Code */
.ProseMirror code {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-primary);
  padding: 3px 7px;
  border-radius: 5px;
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
  font-size: 0.88em;
  border: 1px solid var(--border-default);
}

/* Light mode inline code */
[data-theme="light"] .ProseMirror code {
  background: rgba(107, 114, 128, 0.1);
  color: #1f2937;
  border-color: rgba(0, 0, 0, 0.15);
}

/* Code Block Container */
.ProseMirror pre {
  background: linear-gradient(135deg, #0d0d12 0%, #12121a 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  margin: 1.5em 0;
  overflow: hidden;
}

.ProseMirror pre code {
  display: block;
  background: transparent;
  padding: 16px 20px;
  color: #e4e4e7;
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
  font-size: 13.5px;
  line-height: 1.7;
  tab-size: 2;
  border: none;
  overflow-x: auto;
}

/* Syntax Highlighting Colors */
.ProseMirror pre code .hljs-keyword,
.ProseMirror pre code .hljs-selector-tag,
.ProseMirror pre code .hljs-built_in {
  color: #c792ea;
}

.ProseMirror pre code .hljs-string,
.ProseMirror pre code .hljs-attr {
  color: #c3e88d;
}

.ProseMirror pre code .hljs-number,
.ProseMirror pre code .hljs-literal {
  color: #f78c6c;
}

.ProseMirror pre code .hljs-function,
.ProseMirror pre code .hljs-title {
  color: #82aaff;
}

.ProseMirror pre code .hljs-comment {
  color: #676e95;
  font-style: italic;
}

.ProseMirror pre code .hljs-variable,
.ProseMirror pre code .hljs-template-variable {
  color: #f07178;
}

.ProseMirror pre code .hljs-type,
.ProseMirror pre code .hljs-class {
  color: #ffcb6b;
}

.ProseMirror pre code .hljs-meta {
  color: #89ddff;
}

.ProseMirror pre code .hljs-tag {
  color: #f07178;
}

.ProseMirror pre code .hljs-name {
  color: #ff5370;
}

.ProseMirror pre code .hljs-attribute {
  color: #c792ea;
}

.ProseMirror pre code .hljs-symbol,
.ProseMirror pre code .hljs-bullet {
  color: #89ddff;
}

.ProseMirror pre code .hljs-addition {
  color: #c3e88d;
  background: rgba(195, 232, 141, 0.1);
}

.ProseMirror pre code .hljs-deletion {
  color: #ff5370;
  background: rgba(255, 83, 112, 0.1);
}

/* Code Block Scrollbar */
.ProseMirror pre code::-webkit-scrollbar {
  height: 6px;
}

.ProseMirror pre code::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 3px;
}

.ProseMirror pre code::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.ProseMirror pre code::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Blockquote */
.ProseMirror blockquote {
  border-left: 2px solid #c9a76c;
  padding-left: 16px;
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
  margin: 6px 0;
}

.ProseMirror ul[data-type="taskList"] li > label {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  margin-top: 3px;
}

.ProseMirror ul[data-type="taskList"] li > label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #c9a76c;
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
  border-radius: 8px;
  margin: 1em 0;
}

.ProseMirror img.ProseMirror-selectednode {
  outline: 2px solid #c9a76c;
}

/* Tables */
.ProseMirror table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid var(--border-default);
}

.ProseMirror th,
.ProseMirror td {
  border: 1px solid var(--border-subtle);
  padding: 10px 14px;
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
  background: rgba(201, 167, 108, 0.1);
}

/* Selection */
.ProseMirror ::selection {
  background: rgba(201, 167, 108, 0.25);
}

/* AI 스트리밍 프리뷰 - 우아한 글래스모피즘 디자인 */
/* AI 스트리밍 프리뷰 - 테마 적용 */
.ai-streaming-preview {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  width: 85%;
  max-width: 680px;
  max-height: 400px;
  overflow-y: auto;
  background: var(--bg-secondary, #16161a);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  z-index: 100;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.03),
    0 0 80px -30px rgba(139, 92, 246, 0.25);
}

.ai-streaming-preview .streaming-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 20px;
  background: linear-gradient(90deg, rgba(139, 92, 246, 0.12) 0%, transparent 100%);
  border-bottom: 1px solid rgba(139, 92, 246, 0.15);
}

.ai-streaming-preview .streaming-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ai-streaming-preview .streaming-label {
  font-size: 13px;
  font-weight: 600;
  color: #a78bfa;
  letter-spacing: 0.3px;
}

.ai-streaming-preview .streaming-content {
  padding: 20px 24px;
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary, #e8e8ec);
  font-family: var(--font-sans);
}

.ai-streaming-preview .streaming-content p {
  margin: 0 0 12px 0;
}

.ai-streaming-preview .streaming-content p:last-child {
  margin-bottom: 0;
}

.ai-streaming-preview .streaming-content h1,
.ai-streaming-preview .streaming-content h2,
.ai-streaming-preview .streaming-content h3 {
  color: var(--text-primary, #fff);
  font-weight: 600;
}

.ai-streaming-preview .streaming-content h1 { font-size: 1.5em; margin: 0 0 12px 0; }
.ai-streaming-preview .streaming-content h2 { font-size: 1.3em; margin: 0 0 10px 0; }
.ai-streaming-preview .streaming-content h3 { font-size: 1.1em; margin: 0 0 8px 0; }

.ai-streaming-preview .streaming-content ul,
.ai-streaming-preview .streaming-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.ai-streaming-preview .streaming-content li {
  margin: 4px 0;
}

.ai-streaming-preview .streaming-content code {
  background: rgba(139, 92, 246, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  color: #c4b5fd;
}

.ai-streaming-preview .streaming-content blockquote {
  border-left: 3px solid #a78bfa;
  padding-left: 16px;
  margin: 12px 0;
  color: var(--text-muted, #b0b0b8);
  font-style: italic;
}

/* 애니메이션 점 */
.ai-streaming-preview .streaming-dot {
  width: 6px;
  height: 6px;
  background: #a78bfa;
  border-radius: 50%;
  animation: ai-dot-bounce 1.4s ease-in-out infinite;
}

.ai-streaming-preview .streaming-dot:nth-child(1) { animation-delay: 0s; }
.ai-streaming-preview .streaming-dot:nth-child(2) { animation-delay: 0.2s; }
.ai-streaming-preview .streaming-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes ai-dot-bounce {
  0%, 80%, 100% { 
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 스크롤바 */
.ai-streaming-preview::-webkit-scrollbar {
  width: 6px;
}

.ai-streaming-preview::-webkit-scrollbar-track {
  background: transparent;
}

.ai-streaming-preview::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

.ai-streaming-preview::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}

/* AI 액션 바 - 테마 적용 */
.ai-action-bar {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: var(--bg-secondary, #16161a);
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
  border-radius: 14px;
  box-shadow: 
    0 20px 40px -12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  z-index: 100;
}

.action-bar-indicator {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #a78bfa, #8b5cf6);
  border-radius: 50%;
  animation: indicator-pulse 2s ease-in-out infinite;
}

@keyframes indicator-pulse {
  0%, 100% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.action-bar-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary, #a0a0a8);
}

.action-bar-buttons {
  display: flex;
  gap: 8px;
}

.ai-action-bar .action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.ai-action-bar .action-btn.reject {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.ai-action-bar .action-btn.reject:hover {
  background: rgba(239, 68, 68, 0.18);
  border-color: rgba(239, 68, 68, 0.3);
}

.ai-action-bar .action-btn.accept {
  background: rgba(34, 197, 94, 0.12);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.ai-action-bar .action-btn.accept:hover {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.35);
}

/* 액션 바 트랜지션 */
.action-bar-slide-enter-active,
.action-bar-slide-leave-active {
  transition: all 0.25s ease;
}

.action-bar-slide-enter-from,
.action-bar-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

/* Light mode styles */
[data-theme="light"] .ProseMirror pre {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-color: rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

[data-theme="light"] .ProseMirror pre::before {
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.02) 0%, rgba(0, 0, 0, 0.01) 100%);
  border-bottom-color: rgba(0, 0, 0, 0.08);
}

[data-theme="light"] .ProseMirror pre::after {
  color: rgba(0, 0, 0, 0.2);
}

[data-theme="light"] .ProseMirror pre code {
  color: #1e293b;
}

[data-theme="light"] .ProseMirror blockquote {
  border-left-color: var(--text-muted);
}

[data-theme="light"] .ProseMirror a {
  color: #374151;
}

[data-theme="light"] .ProseMirror mark {
  background: rgba(107, 114, 128, 0.2);
}

[data-theme="light"] .ProseMirror mark[data-color="#ef444480"] {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.1) 100%);
  border-bottom: 2px wavy #dc2626;
}

/* Dim theme code styles */
[data-theme="dim"] .ProseMirror code {
  background: rgba(139, 148, 158, 0.15);
  color: #adbac7;
  border-color: rgba(139, 148, 158, 0.2);
}

[data-theme="dim"] .ProseMirror pre {
  background: linear-gradient(135deg, #171717 0%, #1c1c1c 100%);
  border-color: rgba(255, 255, 255, 0.1);
}

/* GitHub Dark theme code styles */
[data-theme="github-dark"] .ProseMirror code {
  background: rgba(88, 166, 255, 0.1);
  color: #79c0ff;
  border-color: rgba(88, 166, 255, 0.2);
}

[data-theme="github-dark"] .ProseMirror pre {
  background: linear-gradient(135deg, #010409 0%, #0d1117 100%);
  border-color: rgba(240, 246, 252, 0.1);
}

[data-theme="github-dark"] .ProseMirror a {
  color: #58a6ff;
}

/* Sepia theme code styles */
[data-theme="sepia"] .ProseMirror code {
  background: rgba(92, 75, 55, 0.1);
  color: #5c4b37;
  border-color: rgba(92, 75, 55, 0.2);
}

[data-theme="sepia"] .ProseMirror pre {
  background: linear-gradient(135deg, #ebe3cf 0%, #f4ecd8 100%);
  border-color: rgba(92, 75, 55, 0.15);
  box-shadow: 0 2px 8px rgba(92, 75, 55, 0.1);
}

[data-theme="sepia"] .ProseMirror pre::before {
  background: linear-gradient(90deg, rgba(92, 75, 55, 0.03) 0%, rgba(92, 75, 55, 0.01) 100%);
  border-bottom-color: rgba(92, 75, 55, 0.1);
}

[data-theme="sepia"] .ProseMirror pre::after {
  color: rgba(92, 75, 55, 0.25);
}

[data-theme="sepia"] .ProseMirror pre code {
  color: #3d3327;
}

[data-theme="sepia"] .ProseMirror blockquote {
  border-left-color: #9c8b78;
}

[data-theme="sepia"] .ProseMirror a {
  color: #5c4b37;
}

[data-theme="sepia"] .ProseMirror mark {
  background: rgba(92, 75, 55, 0.15);
}

[data-theme="sepia"] .ProseMirror mark[data-color="#ef444480"] {
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
  border-bottom: 2px wavy #b91c1c;
}
</style>
