---

## 🎯 CueNote vs Obsidian 기능 비교 및 차별화 전략

### 현재 CueNote의 강점 (옵시디언에 없는 것)
| 기능 | 설명 |
|------|------|
| **AI 텍스트 처리** | 요약, 번역, 개선, 확장, 축약, 맞춤법 검사 (실시간 스트리밍) |
| **AI 스케줄 추출** | 노트에서 자동으로 일정 감지 → 캘린더 추가 |
| **OCR/PDF 처리** | 이미지/PDF에서 텍스트 추출 후 마크다운 변환 |
| **로컬 LLM 지원** | Ollama를 통한 완전 오프라인 AI |

---

## 🔗 옵시디언 핵심 기능 → CueNote 차별화 버전

### 1. **노트 링킹 (Wikilink) + AI 자동 링크 제안**

옵시디언의 `[[노트명]]` 문법을 지원하되, **AI가 자동으로 관련 노트를 제안**하는 기능으로 차별화:

```typescript
// 에디터에서 [[를 입력하면 자동완성 + AI 관련 노트 제안
const linkSuggestions = {
  manual: vaultFiles.filter(f => f.includes(query)),  // 기존 검색
  aiSuggested: await getAIRelatedNotes(currentContent) // AI 추천
}
```

**차별점**: 
- 옵시디언은 수동 링크만 지원
- CueNote는 **"이 노트와 연관될 수 있는 노트"를 AI가 제안** (내용 기반 유사도 분석)

---

### 2. **그래프 뷰 + AI 클러스터링**

단순 링크 기반 그래프 대신, **AI가 노트를 주제별로 자동 클러스터링**:

```typescript
// 백엔드 API 예시
@router.post("/ai/cluster-notes")
async def cluster_notes(payload: ClusterPayload):
    """노트들을 의미 기반으로 클러스터링"""
    embeddings = await get_embeddings(payload.notes)
    clusters = perform_clustering(embeddings)
    return {"clusters": clusters, "suggested_tags": generate_tags(clusters)}
```

**차별점**:
- 옵시디언: 연결된 노트만 그래프에 표시
- CueNote: **링크 없이도 AI가 관련 노트 그룹화** + 자동 태그 제안

---

### 3. **콜아웃 + AI 자동 생성**

옵시디언의 콜아웃 문법 지원 + **AI가 적절한 콜아웃 제안**:

```markdown
> [!important] 핵심 포인트
> AI가 문서를 분석해 중요한 부분을 자동 하이라이트

> [!summary] 자동 요약
> 이 섹션의 핵심 내용을 AI가 요약합니다
```

**구현 아이디어**:
```typescript
// AI 콜아웃 자동 생성
const generateCallouts = async (content: string) => {
  const analysis = await aiAnalyze(content);
  return {
    warnings: analysis.potentialIssues.map(i => `> [!warning] ${i}`),
    tips: analysis.suggestions.map(s => `> [!tip] ${s}`),
    summary: `> [!summary]\n> ${analysis.summary}`
  };
};
```

---

### 4. **백링크 + AI 맥락 분석**

```typescript
interface Backlink {
  notePath: string;
  linkedText: string;
  context: string;  // 링크 주변 문맥
  aiRelevance: number;  // AI가 평가한 관련성 점수
  aiSummary: string;  // 왜 관련있는지 AI 설명
}
```

**차별점**:
- 옵시디언: 단순히 어떤 노트가 링크했는지 표시
- CueNote: **왜 연결되었는지 AI가 맥락 설명** + 관련성 점수

---

### 5. **태그 시스템 + AI 자동 태깅**

```typescript
// 노트 저장 시 AI가 자동으로 태그 제안
const suggestTags = async (content: string, existingTags: string[]) => {
  const response = await fetch('/ai/suggest-tags', {
    method: 'POST',
    body: JSON.stringify({ content, existingTags })
  });
  return response.json(); // ['#프로젝트', '#회의록', '#중요']
};
```

---

### 6. **Daily Notes + AI 하루 정리**

```typescript
// 데일리 노트 생성 시 AI가 자동으로 섹션 구성
const createDailyNote = async (date: string) => {
  const previousNotes = await getRecentNotes(7);
  const pendingTasks = await getPendingTodos();
  const todaySchedules = await getSchedules(date);
  
  return `# ${date}

## 📅 오늘의 일정
${todaySchedules.map(s => `- ${s.time} ${s.title}`).join('\n')}

## ✅ 진행 중인 할 일
${pendingTasks.map(t => `- [ ] ${t.text}`).join('\n')}

## 📝 이어서 작업할 노트
${await aiSuggestContinueNotes(previousNotes)}

## 💭 오늘의 메모

`;
};
```

---

### 7. **플러그인 시스템 대안: AI 워크플로우**

복잡한 플러그인 시스템 대신, **AI 기반 워크플로우 자동화**:

```typescript
// 사용자 정의 AI 워크플로우
const workflows = [
  {
    name: "회의록 정리",
    trigger: "meeting" // 파일명이나 태그 기반
    actions: [
      { type: "ai", action: "summarize" },
      { type: "ai", action: "extract-action-items" },
      { type: "ai", action: "extract-schedules" },
      { type: "create", template: "action-items" }
    ]
  },
  {
    name: "학습 노트 정리",
    actions: [
      { type: "ai", action: "generate-quiz" },
      { type: "ai", action: "create-flashcards" },
      { type: "link", action: "find-related-notes" }
    ]
  }
];
```

---


## 💡 핵심 차별화 슬로건

> **옵시디언은 "연결된 메모"를, CueNote는 "지능적으로 연결되는 메모"를 제공합니다.**

- 옵시디언: 사용자가 직접 링크/그래프/태그 관리
- **CueNote**: AI가 **자동으로 연결**, **자동으로 분류**, **자동으로 정리**

---