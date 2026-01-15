<template>
  <NodeViewWrapper class="resizable-image-wrapper" :class="{ 'is-selected': selected, 'is-resizing': isResizing }">
    <div class="image-container" :style="containerStyle" ref="containerRef">
      <img :src="node.attrs.src" :alt="node.attrs.alt || ''" :title="node.attrs.title || ''" class="resizable-image" draggable="false" @click="selectImage" />

      <!-- 리사이즈 핸들 (선택됐을 때만 표시) -->
      <template v-if="selected || isResizing">
        <div class="resize-handle resize-handle-right" @mousedown.stop.prevent="startResize($event, 'right')"></div>
        <div class="resize-handle resize-handle-left" @mousedown.stop.prevent="startResize($event, 'left')"></div>
        <div class="resize-handle resize-handle-bottom-right" @mousedown.stop.prevent="startResize($event, 'corner')"></div>
        <div class="resize-handle resize-handle-bottom-left" @mousedown.stop.prevent="startResize($event, 'corner-left')"></div>
      </template>

      <!-- 크기 표시 (리사이징 중) -->
      <div v-if="isResizing" class="size-indicator">{{ displayWidth }}px</div>
    </div>
  </NodeViewWrapper>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from "vue";
import { NodeViewWrapper, nodeViewProps } from "@tiptap/vue-3";

const props = defineProps(nodeViewProps);

const containerRef = ref<HTMLElement | null>(null);
const isResizing = ref(false);
const displayWidth = ref(0);

// 리사이징 상태 저장 (반응성 없이)
let resizeState = {
  startX: 0,
  startWidth: 0,
  direction: "right" as "left" | "right" | "corner" | "corner-left",
  rafId: 0,
  lastWidth: 0,
};

// 이미지 너비 계산 (초기 및 저장된 값)
const containerStyle = computed(() => {
  if (isResizing.value) {
    return { width: `${displayWidth.value}px` };
  }
  const width = props.node.attrs.width;
  if (!width) return { width: "100%" };
  if (typeof width === "number") return { width: `${width}px` };
  return { width };
});

// 이미지 선택
function selectImage() {
  props.editor.commands.setNodeSelection(props.getPos());
}

// 리사이즈 시작
function startResize(event: MouseEvent, direction: "left" | "right" | "corner" | "corner-left") {
  if (!containerRef.value) return;

  isResizing.value = true;
  resizeState.direction = direction;
  resizeState.startX = event.clientX;
  resizeState.startWidth = containerRef.value.offsetWidth;
  resizeState.lastWidth = resizeState.startWidth;
  displayWidth.value = resizeState.startWidth;

  // 에디터 선택 유지
  props.editor.commands.setNodeSelection(props.getPos());

  document.addEventListener("mousemove", handleResize, { passive: true });
  document.addEventListener("mouseup", stopResize);
  document.body.style.cursor = direction.includes("corner") ? "nwse-resize" : "ew-resize";
  document.body.style.userSelect = "none";
  document.body.style.pointerEvents = "none";

  // 컨테이너만 포인터 이벤트 허용
  if (containerRef.value) {
    containerRef.value.style.pointerEvents = "auto";
  }
}

// 리사이즈 중 (requestAnimationFrame 사용)
function handleResize(event: MouseEvent) {
  if (!isResizing.value) return;

  // 이전 프레임 취소
  if (resizeState.rafId) {
    cancelAnimationFrame(resizeState.rafId);
  }

  resizeState.rafId = requestAnimationFrame(() => {
    const diff = event.clientX - resizeState.startX;
    let newWidth: number;

    // 방향에 따라 너비 계산
    if (resizeState.direction === "left" || resizeState.direction === "corner-left") {
      newWidth = resizeState.startWidth - diff;
    } else {
      newWidth = resizeState.startWidth + diff;
    }

    // 최소/최대 너비 제한
    const minWidth = 80;
    const maxWidth = containerRef.value?.parentElement?.offsetWidth || 760;
    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

    // 변화량이 너무 작으면 무시 (부드러운 움직임)
    if (Math.abs(newWidth - resizeState.lastWidth) < 1) return;

    resizeState.lastWidth = newWidth;
    displayWidth.value = Math.round(newWidth);

    // 직접 DOM 업데이트 (Vue 반응성 우회)
    if (containerRef.value) {
      containerRef.value.style.width = `${newWidth}px`;
    }
  });
}

// 리사이즈 종료
function stopResize() {
  if (!isResizing.value) return;

  // RAF 취소
  if (resizeState.rafId) {
    cancelAnimationFrame(resizeState.rafId);
    resizeState.rafId = 0;
  }

  const finalWidth = Math.round(resizeState.lastWidth);

  // 이벤트 리스너 제거
  document.removeEventListener("mousemove", handleResize);
  document.removeEventListener("mouseup", stopResize);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";
  document.body.style.pointerEvents = "";

  // 에디터에 너비 저장
  if (finalWidth > 0 && finalWidth !== props.node.attrs.width) {
    props.updateAttributes({
      width: finalWidth,
    });
  }

  isResizing.value = false;
}

// 컴포넌트 언마운트 시 정리
onBeforeUnmount(() => {
  if (resizeState.rafId) {
    cancelAnimationFrame(resizeState.rafId);
  }
  document.removeEventListener("mousemove", handleResize);
  document.removeEventListener("mouseup", stopResize);
});
</script>

<style scoped>
.resizable-image-wrapper {
  display: block;
  margin: 1em 0;
  line-height: 0;
}

.image-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
  line-height: 0;
  will-change: width;
}

.resizable-image {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 8px;
  cursor: pointer;
  user-select: none;
  -webkit-user-drag: none;
}

/* 리사이징 중일 때 트랜지션 비활성화 */
.resizable-image-wrapper.is-resizing .image-container {
  transition: none !important;
}

.resizable-image-wrapper.is-selected .resizable-image,
.resizable-image-wrapper.is-resizing .resizable-image {
  outline: 2px solid #c9a76c;
  outline-offset: 2px;
}

/* 리사이즈 핸들 */
.resize-handle {
  position: absolute;
  background: #c9a76c;
  border: 2px solid #1a1a1f;
  border-radius: 4px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.15s ease, transform 0.15s ease, background 0.15s ease;
}

.resizable-image-wrapper.is-selected .resize-handle,
.resizable-image-wrapper.is-resizing .resize-handle {
  opacity: 1;
}

.resize-handle:hover {
  background: #e8d5b7;
  transform: scale(1.15);
}

.resize-handle:active {
  background: #f0e6d6;
}

.resize-handle-right {
  width: 8px;
  height: 40px;
  right: -6px;
  top: 50%;
  transform: translateY(-50%);
  cursor: ew-resize;
}

.resize-handle-right:hover {
  transform: translateY(-50%) scale(1.15);
}

.resize-handle-left {
  width: 8px;
  height: 40px;
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
  cursor: ew-resize;
}

.resize-handle-left:hover {
  transform: translateY(-50%) scale(1.15);
}

.resize-handle-bottom-right {
  width: 14px;
  height: 14px;
  right: -6px;
  bottom: -6px;
  cursor: nwse-resize;
  border-radius: 50%;
}

.resize-handle-bottom-left {
  width: 14px;
  height: 14px;
  left: -6px;
  bottom: -6px;
  cursor: nesw-resize;
  border-radius: 50%;
}

/* 크기 표시 */
.size-indicator {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 12px;
  background: rgba(26, 26, 31, 0.95);
  border: 1px solid rgba(201, 167, 108, 0.4);
  border-radius: 8px;
  color: #e8d5b7;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-mono);
  pointer-events: none;
  z-index: 20;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>
