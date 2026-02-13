<template>
  <div class="editor-view">
    <EditorEmptyState v-if="!activeFile" />

    <div v-else class="editor-container">
      <EditorHeader :active-file="activeFile" :is-github-file="isGithubFile" :is-dirty="isDirty"
        :staging-saving="stagingSaving" :staging-saved="stagingSaved" :saving="saving" :saved="saved" @save="handleSave"
        @save-github="handleSaveGitHubFile" />

      <EditorToolbar :editor="editor as Editor" :summarizing="summarizing" :note-name="getFileName(activeFile)"
        :active-file="activeFile" :show-source-view="showSourceView" @summarize="handleSummarize"
        @extract-result="handleExtractResult" @toggle-source-view="toggleSourceView" />

      <!-- AI 요약 결과 패널 -->
      <EditorSummaryPanel :summary-result="summaryResult" @close="summaryResult = null" @copy="copySummary"
        @insert="insertSummary" />

      <div v-if="showSourceView" class="editor-content-wrapper source-view-wrapper">
        <div class="source-view-container">
          <textarea class="source-view-textarea" :value="sourceContent" @input="handleSourceInput" spellcheck="false" />
        </div>
      </div>

      <div v-else ref="editorWrapperRef" class="editor-content-wrapper" :class="{ 'drag-over': isDraggingOver }"
        @contextmenu="handleContextMenu" @dragenter="handleDragEnter" @dragover="handleDragOver"
        @dragleave="handleDragLeave" @drop="handleDrop" @paste="handlePaste">
        <EditorContent :editor="editor" class="editor-content" />
      </div>

      <!-- AI 스트리밍 프리뷰 (하단 고정 패널 - Teleport to body) -->
      <EditorAIPreview :is-a-i-streaming="isAIStreaming" :ai-streaming-action="aiStreamingAction"
        :stream-preview-html="streamPreviewHtml" :show-a-i-action-bar="showAIActionBar" @reject="handleAIReject"
        @accept="handleAIAccept" />

      <!-- AI 컨텍스트 메뉴 -->
      <AIContextMenu :visible="showAIMenu" :position="aiMenuPosition" :selected-text="selectedText" @close="closeAIMenu"
        @result="handleAIResult" @stream-start="handleStreamStart" @stream-chunk="handleStreamChunk"
        @stream-end="handleStreamEnd" @error="handleAIError" @proofread="handleProofread" @mcp-used="handleMcpUsed" />

      <!-- 맞춤법 검사 패널 -->
      <AIProofreadPanel :visible="showProofreadPanel" :loading="proofreadLoading" :original-text="proofreadOriginalText"
        :corrected-text="proofreadCorrectedText" :items="proofreadItems" :language-detected="proofreadLanguage"
        @close="handleProofreadClose" @apply-item="handleProofreadApplyItem" @apply-all="handleProofreadApplyAll"
        @skip-item="handleProofreadSkipItem" @skip-all="handleProofreadSkipAll"
        @focus-item="handleProofreadFocusItem" />

      <p v-if="editorError" class="error-msg">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        {{ editorError }}
      </p>

      <!-- MCP 도구 사용 알림 토스트 -->
      <Transition name="mcp-toast">
        <div v-if="mcpNotification" class="mcp-toast">
          <span class="mcp-toast-icon">🔧</span>
          <div class="mcp-toast-body">
            <div class="mcp-toast-title">MCP 도구 사용됨</div>
            <div class="mcp-toast-tools">
              <span v-for="t in mcpNotification.tools" :key="t.tool" class="mcp-toast-tool">
                {{ t.server }} → {{ t.tool }}
              </span>
            </div>
          </div>
          <button class="mcp-toast-close" @click="mcpNotification = null">✕</button>
        </div>
      </Transition>
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

// Components
import EditorToolbar from './EditorToolbar.vue';
import AIContextMenu from './AIContextMenu.vue';
import AIInlineDiff from './AIInlineDiff.vue';
import AIProofreadPanel from './AIProofreadPanel.vue';
import EditorEmptyState from './editor/EditorEmptyState.vue';
import EditorHeader from './editor/EditorHeader.vue';
import EditorSummaryPanel from './editor/EditorSummaryPanel.vue';
import EditorAIPreview from './editor/EditorAIPreview.vue';

// Composables & Utils
import { useSettings, useI18n, useShortcuts, useGitHub } from '../composables';
import { markdownToHtml as convertMarkdownToHtml, htmlToMarkdown as convertHtmlToMarkdown } from '../utils/markdown';

const lowlight = createLowlight(common);
const CORE_BASE = 'http://127.0.0.1:8787';

// LLM 설정 가져오기
const { settings: llmSettings } = useSettings();
const { t } = useI18n();
const { isAIMenuShortcut } = useShortcuts();
const { saveFile: saveGitHubFile, checkGitStatus, uploadImage: uploadGitHubImage, getImageUrl: getGitHubImageUrl, selectedRepo } = useGitHub();

const props = defineProps<{
  activeFile: string | null;
  isGithubFile?: boolean;
  githubContent?: string | null;
}>();

const emit = defineEmits<{
  'dirty-change': [isDirty: boolean];
  'dirty-files-change': [files: string[]];
}>();

// Wrapper functions for markdown conversion to inject context
function markdownToHtml(md: string): string {
  return convertMarkdownToHtml(md, isGithubFile.value, selectedRepo.value, CORE_BASE);
}

function htmlToMarkdown(html: string): string {
  return convertHtmlToMarkdown(html, isGithubFile.value, selectedRepo.value, CORE_BASE);
}

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

// 마크다운 원본 보기 상태
const showSourceView = ref(false);
const sourceContent = ref('');

// GitHub 스테이징 관련 상태
const stagingSaving = ref(false);
const stagingSaved = ref(false);

// GitHub 파일 여부 (computed)
const isGithubFile = computed(() => props.isGithubFile ?? false);

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

// MCP 알림 상태
const mcpNotification = ref<{ tools: Array<{ server: string; tool: string }> } | null>(null);

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
      link: false,
      underline: false,
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
      HTMLAttributes: {
        class: 'editor-link',
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
    handleClick(view, pos, event) {
      const marks = view.state.doc.resolve(pos).marks();
      const linkMark = marks.find(m => m.type.name === 'link');

      if (linkMark) {
        // Ctrl+Click → 외부 브라우저에서 열기
        if (event.ctrlKey || event.metaKey) {
          const href = linkMark.attrs.href;
          if (href) {
            event.preventDefault();
            if (window.cuenote?.openExternal) {
              window.cuenote.openExternal(href);
            } else {
              window.open(href, '_blank');
            }
            return true;
          }
        }
        // 일반 클릭 → 이동 차단 (커서만 위치)
        event.preventDefault();
        return false;
      }
      return false;
    },
  },
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

// 마크다운 원본 보기 토글
function toggleSourceView() {
  if (!editor.value) return;

  if (!showSourceView.value) {
    // WYSIWYG → 소스 뷰: 현재 에디터 내용을 마크다운으로 변환
    const html = editor.value.getHTML();
    sourceContent.value = htmlToMarkdown(html);
  } else {
    // 소스 뷰 → WYSIWYG: 마크다운을 HTML로 변환하여 에디터에 설정
    const html = markdownToHtml(sourceContent.value);
    editor.value.commands.setContent(html, { emitUpdate: false });
  }

  showSourceView.value = !showSourceView.value;
}

// 소스 뷰에서 내용 변경 시 dirty 처리
function handleSourceInput(e: Event) {
  const target = e.target as HTMLTextAreaElement;
  sourceContent.value = target.value;
  if (!isDirty.value) {
    isDirty.value = true;
    emit('dirty-change', true);
    emitDirtyFiles();
  }
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

  // 캐시에 없으면 서버에서 로드 (로컬 & GitHub 모두 /vault/file 사용)
  // 백엔드의 get_current_vault_path()가 GitHub 환경에서도 클론 경로를 반환
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
    const content = showSourceView.value
      ? sourceContent.value
      : htmlToMarkdown(editor.value.getHTML());

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

// GitHub 파일 저장 (클론된 로컬 파일에 저장)
async function handleSaveGitHubFile() {
  if (!props.activeFile || !editor.value) return;

  stagingSaving.value = true;
  editorError.value = '';

  try {
    const content = showSourceView.value
      ? sourceContent.value
      : htmlToMarkdown(editor.value.getHTML());

    // 클론된 로컬 파일에 저장
    const success = await saveGitHubFile(props.activeFile, content);

    if (!success) {
      throw new Error('저장 실패');
    }

    // 저장 성공 시 dirty 상태 초기화
    isDirty.value = false;
    emit('dirty-change', false);

    // Git 상태 업데이트
    await checkGitStatus();

    // 완료 표시 (2초간)
    stagingSaved.value = true;
    setTimeout(() => {
      stagingSaved.value = false;
    }, 2000);
  } catch (error) {
    editorError.value = '저장 실패.';
    console.error('Save GitHub file failed', error);
  } finally {
    stagingSaving.value = false;
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
    // MCP 도구 사용 알림
    if (data.mcp_used && data.mcp_used.length > 0) {
      handleMcpUsed(data.mcp_used);
    }
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
    // GitHub 파일이면 GitHub 저장, 아니면 로컬 저장
    if (isGithubFile.value) {
      handleSaveGitHubFile();
    } else {
      handleSave();
    }
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
  if (isGithubFile.value) {
    handleSaveGitHubFile();
  } else {
    handleSave();
  }
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

// MCP 도구 사용 알림
function handleMcpUsed(tools: Array<{ server: string; tool: string; status: string }>) {
  mcpNotification.value = { tools };
  // 5초 후 자동 숨김
  setTimeout(() => {
    mcpNotification.value = null;
  }, 5000);
}

// AI 변경 적용
function handleAIAccept() {
  showAIActionBar.value = false;
  originalText.value = '';
  originalHtml.value = '';
  streamedContent.value = '';
  savedSelection.value = null;
  // GitHub 파일이면 GitHub 저장, 아니면 로컬 저장
  if (isGithubFile.value) {
    handleSaveGitHubFile();
  } else {
    handleSave();
  }
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
  const rangeStart = savedSelection.value?.from;
  const rangeEnd = savedSelection.value?.to;

  // 현재 문서 전체에서 다시 검색
  const positions = findTextPositions(original, rangeStart, rangeEnd);

  // 사용되지 않은 첫 번째 위치 찾기 (정확도가 떨어질 수 있음)
  if (positions.length > 0) {
    const { from, to } = positions[0];

    editor.value.chain()
      .setTextSelection({ from, to })
      .unsetHighlight()
      .deleteSelection()
      .insertContent(corrected)
      .blur()
      .run();

    proofreadItems.value[index].applied = true;
    updateProofreadPositions(index, corrected.length - original.length);
  }
}

// 위치 업데이트 (수정 후 오프셋 조정)
function updateProofreadPositions(appliedIndex: number, offsetDiff: number) {
  if (offsetDiff === 0) return;

  // 적용된 항목 이후의 모든 항목에 대해 위치 조정
  // 주의: 이는 단순화된 로직으로, 복잡한 편집이 발생하면 위치가 틀어질 수 있음
  // 실무에서는 ProseMirror의 트랜잭션 매핑을 사용하는 것이 좋음
}

// 개별 맞춤법 수정 건너뛰기
function handleProofreadSkipItem(index: number) {
  proofreadItems.value[index].skipped = true;
  removeItemHighlight(index);
}

// 모든 맞춤법 수정 적용
function handleProofreadApplyAll() {
  if (!editor.value) return;

  // 뒤에서부터 적용하여 인덱스 밀림 방지
  const itemsToApply = proofreadItems.value
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => !item.applied && !item.skipped)
    .reverse();

  for (const { item, index } of itemsToApply) {
    handleProofreadApplyItem({
      index,
      original: item.original,
      corrected: item.corrected
    });
  }

  removeAllProofreadHighlights();
  showProofreadPanel.value = false;
}

// 모든 맞춤법 수정 건너뛰기 (패널 닫기)
function handleProofreadSkipAll() {
  removeAllProofreadHighlights();
  showProofreadPanel.value = false;
}

// 맞춤법 패널 닫기
function handleProofreadClose() {
  removeAllProofreadHighlights();
  showProofreadPanel.value = false;
}

// 항목에 포커스 (하이라이트 및 스크롤)
function handleProofreadFocusItem(index: number) {
  if (!editor.value) return;

  const item = proofreadItems.value[index];
  if (item.positions && item.positions.length > 0) {
    const { from, to } = item.positions[0];

    editor.value.chain()
      .setTextSelection({ from, to })
      .scrollIntoView()
      .run();
  }
}

// AI 에러 처리
function handleAIError(message: string) {
  editorError.value = message;
  isAIStreaming.value = false;
  showAIActionBar.value = false;

  if (originalHtml.value) {
    // 에러 발생 시 원본 복원
    editor.value?.commands.setContent(originalHtml.value);
  }

  // 3초 후 에러 메시지 초기화
  setTimeout(() => {
    editorError.value = '';
  }, 3000);
}

// 드래그 앤 드롭 핸들러
function handleDragEnter(e: DragEvent) {
  e.preventDefault();
  dragCounter++;
  if (e.dataTransfer?.items && e.dataTransfer.items.length > 0) {
    isDraggingOver.value = true;
  }
}

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  isDraggingOver.value = true;
}

function handleDragLeave(e: DragEvent) {
  e.preventDefault();
  dragCounter--;
  if (dragCounter === 0) {
    isDraggingOver.value = false;
  }
}

async function handleDrop(e: DragEvent) {
  e.preventDefault();
  isDraggingOver.value = false;
  dragCounter = 0;

  const files = e.dataTransfer?.files;
  if (!files || files.length === 0) return;

  // 이미지만 처리
  const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
  if (imageFiles.length === 0) return;

  for (const file of imageFiles) {
    await handleImageUpload(file);
  }
}

async function handlePaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of Array.from(items)) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile();
      if (file) {
        e.preventDefault(); // 기본 붙여넣기 방지
        await handleImageUpload(file);
      }
    }
  }
}

// 이미지 업로드 처리
async function handleImageUpload(file: File) {
  if (!editor.value) return;

  // placeholder 삽입
  const { state } = editor.value;
  const { from } = state.selection;
  const id = `uploading-${Date.now()}`;

  editor.value.chain().insertContent('![Uploading image...](' + id + ')').run();

  try {
    let imageUrl = '';

    if (isGithubFile.value) {
      // GitHub 파일인 경우 GitHub 저장소에 이미지 업로드
      // File 객체를 Base64로 변환
      const reader = new FileReader();
      const base64Data = await new Promise<string>((resolve, reject) => {
        reader.onload = () => {
          const result = reader.result as string;
          // data:image/png;base64, 부분 제거
          const base64 = result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      const result = await uploadGitHubImage(base64Data, getFileName(props.activeFile || ''));

      if (result) {
        // result는 업로드된 이미지의 상대 경로 (img/filename.png)
        // 에디터에는 로컬 프록시 URL을 사용하여 표시
        if (selectedRepo.value) {
          imageUrl = `${CORE_BASE}/github/repo/image/${selectedRepo.value.owner}/${selectedRepo.value.name}/${result.replace('img/', '')}`;
        } else {
          imageUrl = result;
        }
      } else {
        throw new Error('GitHub 이미지 업로드 실패');
      }
    } else {
      // 로컬 파일인 경우 로컬 서버에 업로드
      const formData = new FormData();
      formData.append('image', file);

      const res = await fetch(`${CORE_BASE}/vault/image`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error('Image upload failed');

      const data = await res.json();
      imageUrl = `${CORE_BASE}/vault/image/${data.filename}`;
    }

    // placeholder를 실제 이미지로 교체
    // 단순히 텍스트 치환을 하면 다른 'uploading-...' 텍스트도 바뀔 수 있으므로 주의 필요
    // 여기서는 간단히 전체 내용에서 치환 (더 정교하게 하려면 노드 위치를 추적해야 함)
    const currentHtml = editor.value.getHTML();
    // 이미지 마크다운을 HTML img 태그로 변환된 상태에서 src 치환은 아래와 같이 동작하지 않을 수 있음
    // Tiptap에서는 이미지를 node로 관리하므로, transaction을 사용하는 것이 가장 좋음

    // 간단한 방법: 마크다운 텍스트 치환은 어려우므로, 이미지를 삽입하는 방식으로 변경
    // 업로드 중 텍스트를 찾아서 교체 (이전 커서 위치 근처일 가능성 높음)

    // 에디터 내용을 다시 설정하는 것은 위험하므로 (커서 위치 등), 
    // undo/redo 스택을 사용하여 교체하거나, 
    // 가장 쉬운 방법: 업로드 완료 후 커서 위치에 이미지 삽입 (placeholder 없이)

    // 여기서는 placeholder를 사용했으므로, 해당 텍스트를 찾아서 교체 시도
    let content = editor.value.getHTML();
    // ![Uploading image...](id) -> <img src="id" alt="Uploading image...">
    // Tiptap이 자동으로 변환했을 것임

    // 이미지 태그의 src가 id인 것을 찾아서 실제 url로 변경
    // DOM 조작이 필요할 수 있음

    // Tiptap chain 명령어로 교체 시도 (전체 문서 갱신이 안전)
    // 하지만 전체 갱신은 깜빡임이 있을 수 있음.

    // 여기서는 간단히: 업로드 성공 시 해당 이미지 태그의 src를 수정
    // HTML string replace
    const newHtml = content.replace(`src="${id}"`, `src="${imageUrl}"`);
    editor.value.commands.setContent(newHtml, { emitUpdate: false });

  } catch (error) {
    console.error('Image upload failed:', error);
    editorError.value = '이미지 업로드 실패';

    // 실패 시 placeholder 제거
    const content = editor.value.getHTML();
    const newHtml = content.replace(new RegExp(`<img[^>]*src="${id}"[^>]*>`, 'g'), ''); // 이미지 태그 제거
    editor.value.commands.setContent(newHtml, { emitUpdate: false });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Watchers 및 Lifecycle
// ─────────────────────────────────────────────────────────────────────────────

watch(() => props.activeFile, async (newFile) => {
  // 파일 전환 시 소스 뷰를 닫고 WYSIWYG로 복원
  if (showSourceView.value) {
    showSourceView.value = false;
    sourceContent.value = '';
  }

  if (newFile) {
    await openFile(newFile);
  } else {
    currentFilePath.value = null;
    editor.value?.commands.setContent('');
  }
});

// 외부에서 로드된 GitHub 컨텐츠가 변경되면 에디터 업데이트
watch(() => props.githubContent, (newContent) => {
  if (props.isGithubFile && newContent && editor.value) {
    // 이미 내용이 있고 dirty 상태라면 덮어쓰지 않음 (충돌 방지 로직 필요할 수 있음)
    if (editor.value.isEmpty || !isDirty.value) {
      const html = markdownToHtml(newContent);
      editor.value.commands.setContent(html, { emitUpdate: false });

      // 저장된 상태로 간주
      stagingSaved.value = true;
      setTimeout(() => {
        stagingSaved.value = false;
      }, 1000);
    }
  }
});

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
  if (props.activeFile) {
    openFile(props.activeFile);
  }
});

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown);

  // 컴포넌트 해제 시 현재 변경사항 캐시
  if (currentFilePath.value && editor.value && isDirty.value) {
    fileContentCache.set(currentFilePath.value, {
      html: editor.value.getHTML(),
      isDirty: true
    });
  }

  editor.value?.destroy();
});
</script>

<style scoped>
.editor-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--bg-primary);
  position: relative;
}

.editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.editor-content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 0 10%;
  padding-bottom: 2rem;
  scrollbar-gutter: stable;
  position: relative;
  /* 스트리밍 프리뷰 위치 기준 */
}

/* 드래그 오버 스타일 */
.editor-content-wrapper.drag-over {
  background-color: rgba(var(--primary-rgb), 0.05);
  box-shadow: inset 0 0 0 2px var(--primary);
}

.editor-content {
  max-width: 900px;
  margin: 0 auto;
  min-height: 100%;
  padding: 48px;
  outline: none;
}

/* 에디터 내부 스타일 (Tiptap) */
:deep(.ProseMirror) {
  outline: none;
  min-height: 300px;
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  color: var(--text-muted);
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

/* Typography styles */
:deep(h1) {
  font-size: 2.25em;
  margin-bottom: 0.5em;
  font-weight: 700;
  color: var(--text-primary);
}

:deep(h2) {
  font-size: 1.75em;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  color: var(--text-primary);
}

:deep(h3) {
  font-size: 1.5em;
  margin-top: 1.25em;
  margin-bottom: 0.5em;
  font-weight: 600;
  color: var(--text-primary);
}

:deep(p) {
  margin-bottom: 1.2em;
  line-height: 1.7;
  color: var(--text-primary);
}

:deep(ul),
:deep(ol) {
  margin-bottom: 1.2em;
  padding-left: 1.5em;
  color: var(--text-primary);
}

:deep(li) {
  margin-bottom: 0.5em;
}

:deep(pre) {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 1.5em 0;
  border: 1px solid var(--border-default);
}

:deep(code) {
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

:deep(blockquote) {
  border-left: 4px solid var(--primary);
  margin-left: 0;
  padding-left: 16px;
  color: var(--text-secondary);
  font-style: italic;
}

:deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 1.5em 0;
  box-shadow: var(--shadow-md);
}

:deep(a) {
  color: var(--primary);
  text-decoration: none;
}

:deep(a:hover) {
  text-decoration: underline;
}

:deep(hr) {
  border: none;
  border-top: 1px solid var(--border-default);
  margin: 2em 0;
}

/* Table styles */
:deep(table) {
  border-collapse: collapse;
  margin: 0;
  overflow: hidden;
  table-layout: fixed;
  width: 100%;
  margin: 1.5em 0;
}

:deep(td),
:deep(th) {
  border: 1px solid var(--border-default);
  box-sizing: border-box;
  min-width: 1em;
  padding: 8px 12px;
  position: relative;
  vertical-align: top;
}

:deep(th) {
  background-color: var(--bg-secondary);
  font-weight: bold;
  text-align: left;
}

/* Task list styles */
:deep(ul[data-type="taskList"]) {
  list-style: none;
  padding: 0;
}

:deep(li[data-type="taskItem"]) {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 8px;
}

:deep(li[data-type="taskItem"] label) {
  margin-right: 12px;
  user-select: none;
  margin-top: 3px;
}

:deep(li[data-type="taskItem"] div) {
  flex: 1;
}

/* Source view (마크다운 원본 보기) */
.source-view-wrapper {
  display: flex;
  justify-content: center;
}

.source-view-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 48px;
  min-height: 100%;
}

.source-view-textarea {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 200px);
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  color: var(--text-primary);
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.7;
  tab-size: 2;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.source-view-textarea::placeholder {
  color: var(--text-muted);
}

/* Error message */
.error-msg {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--error-glow);
  color: var(--error);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--error);
  z-index: 100;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translate(-50%, 20px);
    opacity: 0;
  }

  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

/* Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  max-height: 500px;
  opacity: 1;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  margin-bottom: 0;
  transform: translateY(-10px);
}

/* MCP Toast Notification */
.mcp-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid rgba(139, 92, 246, 0.4);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 20px rgba(139, 92, 246, 0.1);
  z-index: 9999;
  max-width: 360px;
}

.mcp-toast-icon {
  font-size: 18px;
}

.mcp-toast-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.mcp-toast-title {
  font-size: 12px;
  font-weight: 600;
  color: #c4b5fd;
}

.mcp-toast-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.mcp-toast-tool {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.mcp-toast-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  opacity: 0.6;
}

.mcp-toast-close:hover {
  opacity: 1;
}

.mcp-toast-enter-active,
.mcp-toast-leave-active {
  transition: all 0.3s ease;
}

.mcp-toast-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.mcp-toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Editor Link Styles */
:deep(.editor-link) {
  color: var(--accent-primary, #8b5cf6);
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--accent-primary, #8b5cf6) 40%, transparent);
  text-underline-offset: 2px;
  cursor: pointer;
  position: relative;
  transition: color 0.15s ease, text-decoration-color 0.15s ease;
  border-radius: 2px;
}

:deep(.editor-link:hover) {
  color: var(--accent-primary, #8b5cf6);
  text-decoration-color: var(--accent-primary, #8b5cf6);
  background: color-mix(in srgb, var(--accent-primary, #8b5cf6) 8%, transparent);
}

:deep(.editor-link:hover::after) {
  content: 'Ctrl + 클릭으로 열기';
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 10px;
  background: var(--bg-primary, #1a1a2e);
  border: 1px solid var(--border-subtle, #333);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-secondary, #aaa);
  white-space: nowrap;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>
