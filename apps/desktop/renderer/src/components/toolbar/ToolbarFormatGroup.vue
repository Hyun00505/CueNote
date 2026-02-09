<template>
  <div class="toolbar-wrapper">
    <!-- Heading Group -->
    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('heading', { level: 1 }) }"
        title="제목 1"
        @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
      >
        <span class="heading-icon">H1</span>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('heading', { level: 2 }) }"
        title="제목 2"
        @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
      >
        <span class="heading-icon">H2</span>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('heading', { level: 3 }) }"
        title="제목 3"
        @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
      >
        <span class="heading-icon">H3</span>
      </button>
    </div>

    <div class="toolbar-divider" />

    <!-- Formatting Group -->
    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('bold') }"
        title="굵게 (Ctrl+B)"
        @click="editor?.chain().focus().toggleBold().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
          <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('italic') }"
        title="기울임 (Ctrl+I)"
        @click="editor?.chain().focus().toggleItalic().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line
            x1="19"
            y1="4"
            x2="10"
            y2="4"
          />
          <line
            x1="14"
            y1="20"
            x2="5"
            y2="20"
          />
          <line
            x1="15"
            y1="4"
            x2="9"
            y2="20"
          />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('underline') }"
        title="밑줄 (Ctrl+U)"
        @click="editor?.chain().focus().toggleUnderline().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3" />
          <line
            x1="4"
            y1="21"
            x2="20"
            y2="21"
          />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('strike') }"
        title="취소선"
        @click="editor?.chain().focus().toggleStrike().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M16 4H9a3 3 0 0 0-2.83 4" />
          <path d="M14 12a4 4 0 0 1 0 8H6" />
          <line
            x1="4"
            y1="12"
            x2="20"
            y2="12"
          />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('highlight') }"
        title="형광펜"
        @click="editor?.chain().focus().toggleHighlight().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="m9 11-6 6v3h9l3-3" />
          <path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4" />
        </svg>
      </button>
    </div>

    <div class="toolbar-divider" />

    <!-- List Group -->
    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('bulletList') }"
        title="글머리 기호"
        @click="editor?.chain().focus().toggleBulletList().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line
            x1="8"
            y1="6"
            x2="21"
            y2="6"
          />
          <line
            x1="8"
            y1="12"
            x2="21"
            y2="12"
          />
          <line
            x1="8"
            y1="18"
            x2="21"
            y2="18"
          />
          <circle
            cx="4"
            cy="6"
            r="1"
            fill="currentColor"
          />
          <circle
            cx="4"
            cy="12"
            r="1"
            fill="currentColor"
          />
          <circle
            cx="4"
            cy="18"
            r="1"
            fill="currentColor"
          />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('orderedList') }"
        title="번호 매기기"
        @click="editor?.chain().focus().toggleOrderedList().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line
            x1="10"
            y1="6"
            x2="21"
            y2="6"
          />
          <line
            x1="10"
            y1="12"
            x2="21"
            y2="12"
          />
          <line
            x1="10"
            y1="18"
            x2="21"
            y2="18"
          />
          <text
            x="3"
            y="7"
            font-size="6"
            fill="currentColor"
          >1</text>
          <text
            x="3"
            y="13"
            font-size="6"
            fill="currentColor"
          >2</text>
          <text
            x="3"
            y="19"
            font-size="6"
            fill="currentColor"
          >3</text>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('taskList') }"
        title="할 일 목록"
        @click="editor?.chain().focus().toggleTaskList().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <rect
            x="3"
            y="5"
            width="6"
            height="6"
            rx="1"
          />
          <path d="m5 8 1 1 2-2" />
          <line
            x1="12"
            y1="8"
            x2="21"
            y2="8"
          />
          <rect
            x="3"
            y="13"
            width="6"
            height="6"
            rx="1"
          />
          <line
            x1="12"
            y1="16"
            x2="21"
            y2="16"
          />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('blockquote') }"
        title="인용문"
        @click="editor?.chain().focus().toggleBlockquote().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"
          />
          <path
            d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"
          />
        </svg>
      </button>
    </div>

    <div class="toolbar-divider" />

    <!-- Code & Link Group -->
    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('code') }"
        title="인라인 코드"
        @click="editor?.chain().focus().toggleCode().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="16 18 22 12 16 6" />
          <polyline points="8 6 2 12 8 18" />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('codeBlock') }"
        title="코드 블록"
        @click="editor?.chain().focus().toggleCodeBlock().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <rect
            x="3"
            y="3"
            width="18"
            height="18"
            rx="2"
          />
          <polyline points="9 9 6 12 9 15" />
          <polyline points="15 9 18 12 15 15" />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('link') }"
        title="링크 삽입"
        @click="setLink"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
      </button>
    </div>

    <div class="toolbar-divider" />

    <!-- Undo/Redo Group -->
    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :disabled="!editor?.can().undo()"
        title="실행 취소 (Ctrl+Z)"
        @click="editor?.chain().focus().undo().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M3 7v6h6" />
          <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :disabled="!editor?.can().redo()"
        title="다시 실행 (Ctrl+Y)"
        @click="editor?.chain().focus().redo().run()"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M21 7v6h-6" />
          <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Editor } from '@tiptap/vue-3';

const props = defineProps<{
  editor: Editor | null;
}>();

function setLink() {
  if (!props.editor) return;

  const previousUrl = props.editor.getAttributes('link').href;
  const url = window.prompt('링크 URL을 입력하세요:', previousUrl);

  if (url === null) return;

  if (url === '') {
    props.editor.chain().focus().extendMarkRange('link').unsetLink().run();
    return;
  }

  props.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
}
</script>

<style scoped>
.toolbar-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-subtle);
  margin: 0 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s ease;
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--surface-2);
  color: var(--text-primary);
}

.toolbar-btn:active:not(:disabled) {
  background: var(--surface-4);
}

.toolbar-btn.active {
  background: var(--bg-active);
  color: var(--accent);
}

.toolbar-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.heading-icon {
  font-size: 10px;
  font-weight: 700;
  font-family: var(--font-mono);
  letter-spacing: -0.5px;
}

.toolbar-btn svg {
  width: 15px;
  height: 15px;
  opacity: 0.85;
}

.toolbar-btn.active svg {
  opacity: 1;
}
</style>
