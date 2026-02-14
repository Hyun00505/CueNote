import { ref } from 'vue';
import { API_ENDPOINTS } from '../config/api';
import type { ChatMessage, ToolCallInfo } from '../types';

// 전역 메시지 저장 (세션 내 유지)
const messages = ref<ChatMessage[]>([]);
const isLoading = ref(false);
const currentStreamText = ref('');

let messageIdCounter = 0;
function nextId(): string {
  return `msg-${Date.now()}-${++messageIdCounter}`;
}

export function useChatbot() {
  function addMessage(role: ChatMessage['role'], content: string, extra?: {
    toolCall?: ToolCallInfo;
    toolResult?: Record<string, unknown>;
  }): ChatMessage {
    const msg: ChatMessage = {
      id: nextId(),
      role,
      content,
      timestamp: Date.now(),
      ...extra,
    };
    messages.value.push(msg);
    // 반드시 reactive proxy를 반환해야 content 변경이 UI에 반영됨
    return messages.value[messages.value.length - 1];
  }

  function buildHistory(): { role: string; content: string }[] {
    return messages.value
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .slice(-10)
      .map(m => ({ role: m.role, content: m.content }));
  }

  async function sendMessage(
    text: string,
    provider: string,
    apiKey: string,
    model: string,
    activeNotePath?: string | null,
    activeNoteContent?: string | null,
  ) {
    if (!text.trim() || isLoading.value) return;

    // 히스토리를 먼저 빌드 (현재 메시지 추가 전에!)
    const history = buildHistory();

    // 사용자 메시지 추가
    addMessage('user', text.trim());
    isLoading.value = true;
    currentStreamText.value = '';

    // 어시스턴트 placeholder
    const assistantMsg = addMessage('assistant', '');

    try {
      const payload: Record<string, unknown> = {
        message: text.trim(),
        provider,
        api_key: apiKey,
        model,
        history,
      };
      if (activeNotePath) {
        payload.active_note_path = activeNotePath;
      }
      if (activeNoteContent) {
        // 너무 긴 내용은 잘라서 전송 (토큰 절약)
        payload.active_note_content = activeNoteContent.slice(0, 5000);
      }
      const body = JSON.stringify(payload);

      const response = await fetch(API_ENDPOINTS.CHATBOT.CHAT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        assistantMsg.content = `⚠️ 오류: ${errData.detail || response.statusText}`;
        isLoading.value = false;
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        assistantMsg.content = '⚠️ 스트리밍을 시작할 수 없습니다.';
        isLoading.value = false;
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let streamedText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE 이벤트 파싱
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = '';
        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith('data:')) {
            const data = line.slice(5).trim();
            handleSSEEvent(currentEvent, data, assistantMsg, () => {
              streamedText = currentStreamText.value;
            });
          }
        }
      }

      // 최종 텍스트 반영
      if (streamedText || currentStreamText.value) {
        assistantMsg.content = currentStreamText.value || streamedText;
      }
      if (!assistantMsg.content) {
        assistantMsg.content = '(응답을 생성할 수 없었습니다.)';
      }
    } catch (err: any) {
      assistantMsg.content = `⚠️ 연결 오류: ${err.message}`;
    } finally {
      isLoading.value = false;
      currentStreamText.value = '';
    }
  }

  function handleSSEEvent(
    event: string,
    data: string,
    assistantMsg: ChatMessage,
    onStreamUpdate: () => void,
  ) {
    switch (event) {
      case 'thinking':
        assistantMsg.content = `💭 ${data}`;
        break;

      case 'tool_call': {
        try {
          const toolCall = JSON.parse(data) as ToolCallInfo;
          const toolNames: Record<string, string> = {
            create_note: '📝 노트 생성',
            list_notes: '📋 노트 목록',
            read_note: '📖 노트 읽기',
            save_note: '💾 노트 저장',
            delete_note: '🗑️ 노트 삭제',
            search_notes: '🔍 노트 검색',
            create_schedule: '📅 일정 생성',
            list_schedules: '📆 일정 목록',
            delete_schedule: '❌ 일정 삭제',
            list_todos: '✅ TODO 목록',
            summarize_text: '📝 텍스트 요약',
            translate_text: '🌐 텍스트 번역',
            create_folder: '📁 폴더 생성',
            web_search: '🔍 웹 검색',
            smart_search_notes: '🧠 스마트 검색',
            organize_notes: '📂 노트 정리',
            move_note: '📦 노트 이동',
          };
          const label = toolNames[toolCall.name] || `🔧 ${toolCall.name}`;
          addMessage('tool_call', label, { toolCall });
          assistantMsg.content = `⏳ ${label} 실행 중...`;
        } catch {
          // ignore parse error
        }
        break;
      }

      case 'tool_result': {
        try {
          const result = JSON.parse(data);
          addMessage('tool_result', result.message || '도구 실행 완료', { toolResult: result });
          assistantMsg.content = '';  // 스트리밍 응답 대기
        } catch {
          // ignore
        }
        break;
      }

      case 'message': {
        const unescaped = data.replace(/\\n/g, '\n');
        currentStreamText.value += unescaped;
        assistantMsg.content = currentStreamText.value;
        onStreamUpdate();
        break;
      }

      case 'done':
        break;

      case 'error':
        assistantMsg.content = `⚠️ ${data}`;
        break;
    }
  }

  function clearMessages() {
    messages.value = [];
  }

  return {
    messages,
    isLoading,
    currentStreamText,
    sendMessage,
    clearMessages,
  };
}
