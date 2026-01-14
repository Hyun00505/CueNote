import { ref, computed } from 'vue';

export type Language = 'ko' | 'en';

// 번역 데이터 타입
type TranslationKeys = {
  // Common
  'common.back': string;
  'common.cancel': string;
  'common.save': string;
  'common.delete': string;
  'common.edit': string;
  'common.add': string;
  'common.done': string;
  'common.reset': string;
  'common.resetAll': string;
  'common.resetAppearance': string;
  'common.search': string;
  'common.loading': string;
  'common.error': string;
  'common.confirm': string;
  'common.close': string;
  'common.today': string;

  // Header
  'header.editor': string;
  'header.calendar': string;
  'header.graph': string;
  'header.selectNote': string;
  'header.clickToRename': string;

  // Settings
  'settings.title': string;
  'settings.language': string;
  'settings.languageDesc': string;
  'settings.theme': string;
  'settings.aiProvider': string;
  'settings.apiKey': string;
  'settings.apiKeyPlaceholder': string;
  'settings.validate': string;
  'settings.validKey': string;
  'settings.invalidKey': string;
  'settings.getApiKey': string;
  'settings.modelSelect': string;
  'settings.refresh': string;
  'settings.noModels': string;
  'settings.installHint': string;
  'settings.ocrModel': string;
  'settings.ocrDownloaded': string;
  'settings.ocrNeeded': string;
  'settings.downloadModel': string;
  'settings.downloading': string;
  'settings.ocrReady': string;
  'settings.ocrHint': string;
  'settings.supportedLangs': string;
  'settings.features': string;

  // Calendar
  'calendar.title': string;
  'calendar.subtitle': string;
  'calendar.aiExtract': string;
  'calendar.addSchedule': string;
  'calendar.loadMore': string;
  'calendar.noSchedules': string;
  'calendar.addFirst': string;

  // Schedule Modal
  'schedule.new': string;
  'schedule.edit': string;
  'schedule.titlePlaceholder': string;
  'schedule.date': string;
  'schedule.startTime': string;
  'schedule.endTime': string;
  'schedule.memo': string;
  'schedule.memoPlaceholder': string;
  'schedule.labelColor': string;
  'schedule.deleteConfirm': string;
  'schedule.deleteQuestion': string;

  // AI Extract
  'aiExtract.title': string;
  'aiExtract.selectNote': string;
  'aiExtract.directInput': string;
  'aiExtract.selectDesc': string;
  'aiExtract.inputDesc': string;
  'aiExtract.inputPlaceholder': string;
  'aiExtract.searchNotes': string;
  'aiExtract.noNotes': string;
  'aiExtract.noResults': string;
  'aiExtract.extractedCount': string;
  'aiExtract.confidence': string;
  'aiExtract.extractBtn': string;
  'aiExtract.extracting': string;
  'aiExtract.addSelected': string;
  'aiExtract.noSchedulesFound': string;
  'aiExtract.selectFile': string;
  'aiExtract.enterText': string;
  'aiExtract.searchPlaceholder': string;
  'aiExtract.noFilesFound': string;
  'aiExtract.loadingFile': string;
  'aiExtract.textPlaceholder': string;

  // Days
  'days.sun': string;
  'days.mon': string;
  'days.tue': string;
  'days.wed': string;
  'days.thu': string;
  'days.fri': string;
  'days.sat': string;

  // Months
  'months.jan': string;
  'months.feb': string;
  'months.mar': string;
  'months.apr': string;
  'months.may': string;
  'months.jun': string;
  'months.jul': string;
  'months.aug': string;
  'months.sep': string;
  'months.oct': string;
  'months.nov': string;
  'months.dec': string;

  // Calendar extended
  'calendar.loadPrevious': string;
  'calendar.loadNext': string;
  'calendar.total': string;
  'calendar.completed': string;
  'calendar.remaining': string;
  'calendar.loading': string;
  'calendar.addScheduleHint': string;
  'calendar.weekView': string;
  'calendar.monthView': string;
  'calendar.yearView': string;
  'calendar.previous': string;
  'calendar.next': string;

  // Days short
  'days.sunShort': string;
  'days.monShort': string;
  'days.tueShort': string;
  'days.wedShort': string;
  'days.thuShort': string;
  'days.friShort': string;
  'days.satShort': string;

  // Themes
  'theme.dark': string;
  'theme.light': string;
  'theme.dim': string;
  'theme.github': string;
  'theme.sepia': string;

  // AI Context Menu
  'ai.assistant': string;
  'ai.proofread': string;
  'ai.proofreading': string;
  'ai.transform': string;
  'ai.improve': string;
  'ai.expand': string;
  'ai.shorten': string;
  'ai.summarize': string;
  'ai.translate': string;
  'ai.toKorean': string;
  'ai.toEnglish': string;
  'ai.toJapanese': string;
  'ai.toChinese': string;
  'ai.style': string;
  'ai.professional': string;
  'ai.casual': string;
  'ai.academic': string;
  'ai.processing': string;
  'ai.noTextSelected': string;
  'ai.completed': string;
  'ai.revert': string;
  'ai.keep': string;
  'ai.customRequest': string;
  'ai.customPlaceholder': string;
  'ai.customHint': string;
  'ai.submitCustom': string;
  'ai.selectedText': string;
  'ai.noSelectionHint': string;
  'ai.enterPrompt': string;

  // Proofread Panel
  'proofread.title': string;
  'proofread.checking': string;
  'proofread.noErrors': string;
  'proofread.noErrorsDesc': string;
  'proofread.modified': string;
  'proofread.applied': string;
  'proofread.skipped': string;
  'proofread.ignoreAll': string;
  'proofread.applyAll': string;
  'proofread.spelling': string;
  'proofread.grammar': string;
  'proofread.punctuation': string;
  'proofread.spacing': string;
  'proofread.korean': string;
  'proofread.english': string;
  'proofread.mixed': string;

  // Environment
  'env.addNew': string;
  'env.name': string;
  'env.namePlaceholder': string;
  'env.folderPath': string;
  'env.folderPlaceholder': string;
  'env.browse': string;
  'env.remove': string;
  'env.removeBtn': string;
  'env.removeQuestion': string;
  'env.removeNote': string;

  // GitHub
  'github.disconnect': string;
  'github.disconnectQuestion': string;
  'github.disconnectWarning': string;
  'github.disconnectBtn': string;

  // File Delete
  'file.deleteQuestion': string;
  'file.deleteFolder': string;
  'file.deleteFile': string;
  'file.deleteWarning': string;

  // Fonts
  'fonts.title': string;
  'fonts.desc': string;
  'fonts.uiFont': string;
  'fonts.uiFontDesc': string;
  'fonts.editorFont': string;
  'fonts.editorFontDesc': string;
  'fonts.codeFont': string;
  'fonts.codeFontDesc': string;
  'fonts.customFonts': string;
  'fonts.customFontsDesc': string;
  'fonts.addFont': string;
  'fonts.fontFile': string;
  'fonts.fontFilePlaceholder': string;
  'fonts.selectFile': string;
  'fonts.fontName': string;
  'fonts.fontNamePlaceholder': string;
  'fonts.fontCategory': string;
  'fonts.categoryOptions': string;
  'fonts.noCustomFonts': string;
  'fonts.preview': string;
  'fonts.uiScale': string;
  
  // Shortcuts
  'shortcuts.title': string;
  'shortcuts.desc': string;
  'shortcuts.aiMenu': string;
  'shortcuts.aiMenuDesc': string;
  'shortcuts.edit': string;
  'shortcuts.pressKeys': string;
  'shortcuts.waitingForInput': string;
  'shortcuts.current': string;
  'shortcuts.addShortcut': string;
  'shortcuts.resetDefault': string;
};

// 한국어 번역
const ko: TranslationKeys = {
  // Common
  'common.back': '뒤로',
  'common.cancel': '취소',
  'common.save': '저장',
  'common.delete': '삭제',
  'common.edit': '수정',
  'common.add': '추가',
  'common.done': '완료',
  'common.reset': '초기화',
  'common.resetAll': '전체 초기화',
  'common.resetAppearance': '외관 초기화',
  'common.search': '검색',
  'common.loading': '로딩 중...',
  'common.error': '오류',
  'common.confirm': '확인',
  'common.close': '닫기',
  'common.today': '오늘',

  // Header
  'header.editor': '에디터',
  'header.calendar': '캘린더',
  'header.graph': '그래프',
  'header.selectNote': '노트를 선택하세요',
  'header.clickToRename': '클릭하여 이름 변경',

  // Settings
  'settings.title': '설정',
  'settings.language': '언어',
  'settings.languageDesc': 'UI 표시 언어를 선택합니다',
  'settings.theme': '테마',
  'settings.aiProvider': 'AI 모델 제공자',
  'settings.apiKey': 'API 키',
  'settings.apiKeyPlaceholder': 'Gemini API 키를 입력하세요',
  'settings.validate': '검증',
  'settings.validKey': 'API 키가 유효합니다',
  'settings.invalidKey': 'API 키가 유효하지 않습니다',
  'settings.getApiKey': 'Google AI Studio에서 API 키 발급받기',
  'settings.modelSelect': '모델 선택',
  'settings.refresh': '새로고침',
  'settings.noModels': '설치된 모델이 없습니다',
  'settings.installHint': '터미널에서 다음 명령어로 모델을 설치하세요:',
  'settings.ocrModel': 'OCR 모델 (문서 변환)',
  'settings.ocrDownloaded': '다운로드 완료 - 사용 가능',
  'settings.ocrNeeded': '다운로드 필요',
  'settings.downloadModel': '모델 다운로드',
  'settings.downloading': '다운로드 중...',
  'settings.ocrReady': 'PDF/이미지 문서 변환 기능 사용 가능',
  'settings.ocrHint': 'PDF나 이미지에서 텍스트를 추출하는 OCR 모델입니다. 에디터 툴바의 "문서 변환" 버튼으로 사용할 수 있습니다.',
  'settings.supportedLangs': '지원 언어:',
  'settings.features': '특징:',

  // Calendar
  'calendar.title': '달력',
  'calendar.subtitle': '  ',
  'calendar.aiExtract': 'AI 일정 추출',
  'calendar.addSchedule': '일정 추가',
  'calendar.loadMore': '더보기',
  'calendar.noSchedules': '일정이 없어요',
  'calendar.addFirst': '+ 새 일정',

  // Schedule Modal
  'schedule.new': '새 일정 만들기',
  'schedule.edit': '일정 수정',
  'schedule.titlePlaceholder': '무슨 일정인가요?',
  'schedule.date': '날짜',
  'schedule.startTime': '시작',
  'schedule.endTime': '종료',
  'schedule.memo': '메모',
  'schedule.memoPlaceholder': '메모를 남겨보세요 (선택)',
  'schedule.labelColor': '라벨 색상',
  'schedule.deleteConfirm': '일정 삭제',
  'schedule.deleteQuestion': '정말 이 일정을 삭제하시겠습니까?',

  // AI Extract
  'aiExtract.title': 'AI 일정 추출',
  'aiExtract.selectNote': '노트 선택',
  'aiExtract.directInput': '직접 입력',
  'aiExtract.selectDesc': '노트를 선택하면 AI가 내용에서 일정 정보를 자동으로 추출합니다.',
  'aiExtract.inputDesc': '텍스트를 직접 입력하면 AI가 날짜, 시간, 일정 정보를 자동으로 추출합니다.',
  'aiExtract.inputPlaceholder': '예: 내일 오후 3시에 팀 미팅이 있어요.',
  'aiExtract.searchNotes': '노트 검색...',
  'aiExtract.noNotes': '노트가 없습니다',
  'aiExtract.noResults': '검색 결과가 없습니다',
  'aiExtract.extractedCount': '추출된 일정',
  'aiExtract.confidence': '신뢰도',
  'aiExtract.extractBtn': '일정 추출하기',
  'aiExtract.extracting': '추출 중...',
  'aiExtract.addSelected': '선택한 일정 추가',
  'aiExtract.noSchedulesFound': '일정 정보를 찾을 수 없습니다.',
  'aiExtract.selectFile': '노트 선택',
  'aiExtract.enterText': '텍스트 입력',
  'aiExtract.searchPlaceholder': '노트 검색...',
  'aiExtract.noFilesFound': '노트를 찾을 수 없습니다.',
  'aiExtract.loadingFile': '파일을 불러오는 중...',
  'aiExtract.textPlaceholder': '일정이 포함된 텍스트를 입력하세요...',

  // Days
  'days.sun': '일요일',
  'days.mon': '월요일',
  'days.tue': '화요일',
  'days.wed': '수요일',
  'days.thu': '목요일',
  'days.fri': '금요일',
  'days.sat': '토요일',

  // Months
  'months.jan': '1월',
  'months.feb': '2월',
  'months.mar': '3월',
  'months.apr': '4월',
  'months.may': '5월',
  'months.jun': '6월',
  'months.jul': '7월',
  'months.aug': '8월',
  'months.sep': '9월',
  'months.oct': '10월',
  'months.nov': '11월',
  'months.dec': '12월',

  // Calendar extended
  'calendar.loadPrevious': '이전 달 보기',
  'calendar.loadNext': '다음 달 보기',
  'calendar.total': '전체',
  'calendar.completed': '완료',
  'calendar.remaining': '남음',
  'calendar.loading': '불러오는 중...',
  'calendar.addScheduleHint': '새로운 일정을 추가해보세요',
  'calendar.weekView': '주',
  'calendar.monthView': '월',
  'calendar.yearView': '연',
  'calendar.previous': '이전',
  'calendar.next': '다음',

  // Days short
  'days.sunShort': '일',
  'days.monShort': '월',
  'days.tueShort': '화',
  'days.wedShort': '수',
  'days.thuShort': '목',
  'days.friShort': '금',
  'days.satShort': '토',

  // Themes
  'theme.dark': '다크',
  'theme.light': '라이트',
  'theme.dim': '딤',
  'theme.github': 'GitHub',
  'theme.sepia': '세피아',

  // AI Context Menu
  'ai.assistant': 'AI 어시스턴트',
  'ai.proofread': '교정',
  'ai.proofreading': '맞춤법 수정',
  'ai.transform': '변환',
  'ai.improve': '글 다듬기',
  'ai.expand': '더 길게',
  'ai.shorten': '더 짧게',
  'ai.summarize': '요약하기',
  'ai.translate': '번역',
  'ai.toKorean': '한국어로',
  'ai.toEnglish': '영어로',
  'ai.toJapanese': '일본어로',
  'ai.toChinese': '중국어로',
  'ai.style': '스타일',
  'ai.professional': '전문적으로',
  'ai.casual': '친근하게',
  'ai.academic': '학술적으로',
  'ai.processing': 'AI가 처리 중...',
  'ai.noTextSelected': '선택된 텍스트가 없습니다.',
  'ai.completed': '완료',
  'ai.revert': '되돌리기',
  'ai.keep': '유지하기',
  'ai.customRequest': '직접 요청하기',
  'ai.customPlaceholder': '글 편집 또는 새 글 작성을 요청하세요...',
  'ai.customHint': 'Ctrl+Enter로 전송',
  'ai.submitCustom': '요청 전송',
  'ai.selectedText': '선택된 텍스트',
  'ai.noSelectionHint': '텍스트를 선택하지 않으면 새 글을 생성합니다',
  'ai.enterPrompt': '요청 내용을 입력해주세요',

  // Proofread Panel
  'proofread.title': '맞춤법 검사',
  'proofread.checking': '맞춤법을 검사하고 있습니다...',
  'proofread.noErrors': '맞춤법 오류가 없습니다!',
  'proofread.noErrorsDesc': '텍스트가 올바르게 작성되었습니다.',
  'proofread.modified': '수정됨',
  'proofread.applied': '적용됨',
  'proofread.skipped': '무시됨',
  'proofread.ignoreAll': '모두 무시',
  'proofread.applyAll': '모두 적용',
  'proofread.spelling': '맞춤법',
  'proofread.grammar': '문법',
  'proofread.punctuation': '구두점',
  'proofread.spacing': '띄어쓰기',
  'proofread.korean': '한국어',
  'proofread.english': '영어',
  'proofread.mixed': '혼합',

  // Environment
  'env.addNew': '새 환경 추가',
  'env.name': '환경 이름',
  'env.namePlaceholder': '예: 개인 노트, 업무 프로젝트...',
  'env.folderPath': '폴더 경로',
  'env.folderPlaceholder': '폴더 경로를 입력하세요',
  'env.browse': '찾아보기',
  'env.remove': '환경 제거',
  'env.removeBtn': '제거',
  'env.removeQuestion': '이 환경을 목록에서 제거하시겠습니까?',
  'env.removeNote': '실제 폴더와 파일은 삭제되지 않습니다.',

  // GitHub
  'github.disconnect': 'GitHub 연결 해제',
  'github.disconnectQuestion': '이 리포지토리 연결을 해제하시겠습니까?',
  'github.disconnectWarning': '로컬에 저장된 파일이 모두 삭제됩니다',
  'github.disconnectBtn': '연결 해제',

  // File Delete
  'file.deleteQuestion': '삭제할까요?',
  'file.deleteFolder': '폴더를 삭제할까요?',
  'file.deleteFile': '파일을 삭제할까요?',
  'file.deleteWarning': '실제 파일이 영구 삭제됩니다',

  // Fonts
  'fonts.title': '폰트',
  'fonts.desc': '앱과 에디터에 사용할 폰트를 선택하세요',
  'fonts.uiFont': 'UI 폰트',
  'fonts.uiFontDesc': '메뉴, 버튼 등 인터페이스에 사용',
  'fonts.editorFont': '에디터 폰트',
  'fonts.editorFontDesc': '노트 본문 작성에 사용',
  'fonts.codeFont': '코드 폰트',
  'fonts.codeFontDesc': '코드 블록에 사용',
  'fonts.customFonts': '커스텀 폰트',
  'fonts.customFontsDesc': 'Google Fonts 또는 웹폰트 URL을 추가하세요',
  'fonts.addFont': '폰트 추가',
  'fonts.fontFile': '폰트 파일',
  'fonts.fontFilePlaceholder': '폰트 파일을 선택하세요',
  'fonts.selectFile': '파일 선택',
  'fonts.fontName': '폰트 이름',
  'fonts.fontNamePlaceholder': '표시될 폰트 이름',
  'fonts.fontCategory': '폰트 종류',
  'fonts.categoryOptions': '카테고리 선택',
  'fonts.noCustomFonts': '추가된 커스텀 폰트가 없습니다',
  'fonts.preview': '미리보기',
  'fonts.uiScale': 'UI 크기',
  
  // Shortcuts
  'shortcuts.title': '단축키',
  'shortcuts.desc': 'AI 기능 및 자주 사용하는 작업의 단축키를 설정합니다',
  'shortcuts.aiMenu': 'AI 메뉴 열기',
  'shortcuts.aiMenuDesc': '에디터에서 AI 어시스턴트 메뉴를 엽니다',
  'shortcuts.edit': '단축키 편집',
  'shortcuts.pressKeys': '원하는 단축키를 누르세요',
  'shortcuts.waitingForInput': '입력 대기 중...',
  'shortcuts.current': '현재 단축키',
  'shortcuts.addShortcut': '단축키 추가',
  'shortcuts.resetDefault': '기본값으로 복원',
};

// 영어 번역
const en: TranslationKeys = {
  // Common
  'common.back': 'Back',
  'common.cancel': 'Cancel',
  'common.save': 'Save',
  'common.delete': 'Delete',
  'common.edit': 'Edit',
  'common.add': 'Add',
  'common.done': 'Done',
  'common.reset': 'Reset',
  'common.resetAll': 'Reset All',
  'common.resetAppearance': 'Reset Appearance',
  'common.search': 'Search',
  'common.loading': 'Loading...',
  'common.error': 'Error',
  'common.confirm': 'Confirm',
  'common.close': 'Close',
  'common.today': 'Today',

  // Header
  'header.editor': 'Editor',
  'header.calendar': 'Calendar',
  'header.graph': 'Graph',
  'header.selectNote': 'Select a note to begin',
  'header.clickToRename': 'Click to rename',

  // Settings
  'settings.title': 'Settings',
  'settings.language': 'Language',
  'settings.languageDesc': 'Select UI display language',
  'settings.theme': 'Theme',
  'settings.aiProvider': 'AI Model Provider',
  'settings.apiKey': 'API Key',
  'settings.apiKeyPlaceholder': 'Enter your Gemini API key',
  'settings.validate': 'Validate',
  'settings.validKey': 'API key is valid',
  'settings.invalidKey': 'API key is invalid',
  'settings.getApiKey': 'Get API key from Google AI Studio',
  'settings.modelSelect': 'Model Selection',
  'settings.refresh': 'Refresh',
  'settings.noModels': 'No models installed',
  'settings.installHint': 'Install a model with the following command:',
  'settings.ocrModel': 'OCR Model (Document Conversion)',
  'settings.ocrDownloaded': 'Downloaded - Ready to use',
  'settings.ocrNeeded': 'Download required',
  'settings.downloadModel': 'Download Model',
  'settings.downloading': 'Downloading...',
  'settings.ocrReady': 'PDF/Image conversion ready',
  'settings.ocrHint': 'OCR model extracts text from PDFs and images. Use the "Convert Document" button in the editor toolbar.',
  'settings.supportedLangs': 'Supported languages:',
  'settings.features': 'Features:',

  // Calendar
  'calendar.title': 'Schedule Manager',
  'calendar.subtitle': 'Scroll to view monthly schedules',
  'calendar.aiExtract': 'AI Extract',
  'calendar.addSchedule': 'Add Schedule',
  'calendar.loadMore': 'Load more',
  'calendar.noSchedules': 'No schedules',
  'calendar.addFirst': '+ New Schedule',

  // Schedule Modal
  'schedule.new': 'New Schedule',
  'schedule.edit': 'Edit Schedule',
  'schedule.titlePlaceholder': 'What\'s the schedule?',
  'schedule.date': 'Date',
  'schedule.startTime': 'Start',
  'schedule.endTime': 'End',
  'schedule.memo': 'Memo',
  'schedule.memoPlaceholder': 'Add a note (optional)',
  'schedule.labelColor': 'Label Color',
  'schedule.deleteConfirm': 'Delete Schedule',
  'schedule.deleteQuestion': 'Are you sure you want to delete this schedule?',

  // AI Extract
  'aiExtract.title': 'AI Schedule Extract',
  'aiExtract.selectNote': 'Select Note',
  'aiExtract.directInput': 'Direct Input',
  'aiExtract.selectDesc': 'Select a note and AI will automatically extract schedule information.',
  'aiExtract.inputDesc': 'Enter text and AI will automatically extract dates, times, and schedules.',
  'aiExtract.inputPlaceholder': 'e.g., Team meeting at 3pm tomorrow.',
  'aiExtract.searchNotes': 'Search notes...',
  'aiExtract.noNotes': 'No notes',
  'aiExtract.noResults': 'No results found',
  'aiExtract.extractedCount': 'Extracted schedules',
  'aiExtract.confidence': 'Confidence',
  'aiExtract.extractBtn': 'Extract Schedules',
  'aiExtract.extracting': 'Extracting...',
  'aiExtract.addSelected': 'Add Selected',
  'aiExtract.noSchedulesFound': 'No schedule information found.',
  'aiExtract.selectFile': 'Select Note',
  'aiExtract.enterText': 'Enter Text',
  'aiExtract.searchPlaceholder': 'Search notes...',
  'aiExtract.noFilesFound': 'No notes found.',
  'aiExtract.loadingFile': 'Loading file...',
  'aiExtract.textPlaceholder': 'Enter text containing schedule information...',

  // Days
  'days.sun': 'Sunday',
  'days.mon': 'Monday',
  'days.tue': 'Tuesday',
  'days.wed': 'Wednesday',
  'days.thu': 'Thursday',
  'days.fri': 'Friday',
  'days.sat': 'Saturday',

  // Months
  'months.jan': 'January',
  'months.feb': 'February',
  'months.mar': 'March',
  'months.apr': 'April',
  'months.may': 'May',
  'months.jun': 'June',
  'months.jul': 'July',
  'months.aug': 'August',
  'months.sep': 'September',
  'months.oct': 'October',
  'months.nov': 'November',
  'months.dec': 'December',

  // Calendar extended
  'calendar.loadPrevious': 'Load Previous Month',
  'calendar.loadNext': 'Load Next Month',
  'calendar.total': 'Total',
  'calendar.completed': 'Done',
  'calendar.remaining': 'Left',
  'calendar.loading': 'Loading...',
  'calendar.addScheduleHint': 'Add a new schedule',
  'calendar.weekView': 'Week',
  'calendar.monthView': 'Month',
  'calendar.yearView': 'Year',
  'calendar.previous': 'Previous',
  'calendar.next': 'Next',

  // Days short
  'days.sunShort': 'Sun',
  'days.monShort': 'Mon',
  'days.tueShort': 'Tue',
  'days.wedShort': 'Wed',
  'days.thuShort': 'Thu',
  'days.friShort': 'Fri',
  'days.satShort': 'Sat',

  // Themes
  'theme.dark': 'Dark',
  'theme.light': 'Light',
  'theme.dim': 'Dim',
  'theme.github': 'GitHub',
  'theme.sepia': 'Sepia',

  // AI Context Menu
  'ai.assistant': 'AI Assistant',
  'ai.proofread': 'Proofread',
  'ai.proofreading': 'Fix Spelling',
  'ai.transform': 'Transform',
  'ai.improve': 'Improve Writing',
  'ai.expand': 'Make Longer',
  'ai.shorten': 'Make Shorter',
  'ai.summarize': 'Summarize',
  'ai.translate': 'Translate',
  'ai.toKorean': 'To Korean',
  'ai.toEnglish': 'To English',
  'ai.toJapanese': 'To Japanese',
  'ai.toChinese': 'To Chinese',
  'ai.style': 'Style',
  'ai.professional': 'Professional',
  'ai.casual': 'Casual',
  'ai.academic': 'Academic',
  'ai.processing': 'AI is processing...',
  'ai.noTextSelected': 'No text selected.',
  'ai.completed': 'Complete',
  'ai.revert': 'Revert',
  'ai.keep': 'Keep',
  'ai.customRequest': 'Custom Request',
  'ai.customPlaceholder': 'Edit text or ask AI to write something...',
  'ai.customHint': 'Press Ctrl+Enter to send',
  'ai.submitCustom': 'Send Request',
  'ai.selectedText': 'Selected Text',
  'ai.noSelectionHint': 'No selection - will generate new text',
  'ai.enterPrompt': 'Please enter your request',

  // Proofread Panel
  'proofread.title': 'Spell Check',
  'proofread.checking': 'Checking spelling...',
  'proofread.noErrors': 'No spelling errors!',
  'proofread.noErrorsDesc': 'Your text is correct.',
  'proofread.modified': 'modified',
  'proofread.applied': 'Applied',
  'proofread.skipped': 'Skipped',
  'proofread.ignoreAll': 'Ignore All',
  'proofread.applyAll': 'Apply All',
  'proofread.spelling': 'Spelling',
  'proofread.grammar': 'Grammar',
  'proofread.punctuation': 'Punctuation',
  'proofread.spacing': 'Spacing',
  'proofread.korean': 'Korean',
  'proofread.english': 'English',
  'proofread.mixed': 'Mixed',

  // Environment
  'env.addNew': 'Add New Environment',
  'env.name': 'Environment Name',
  'env.namePlaceholder': 'e.g., Personal Notes, Work Project...',
  'env.folderPath': 'Folder Path',
  'env.folderPlaceholder': 'Enter folder path',
  'env.browse': 'Browse',
  'env.remove': 'Remove Environment',
  'env.removeBtn': 'Remove',
  'env.removeQuestion': 'Remove this environment from the list?',
  'env.removeNote': 'The actual folder and files will not be deleted.',

  // GitHub
  'github.disconnect': 'Disconnect GitHub',
  'github.disconnectQuestion': 'Disconnect this repository?',
  'github.disconnectWarning': 'All locally stored files will be deleted',
  'github.disconnectBtn': 'Disconnect',

  // File Delete
  'file.deleteQuestion': 'Delete?',
  'file.deleteFolder': 'Delete this folder?',
  'file.deleteFile': 'Delete this file?',
  'file.deleteWarning': 'Files will be permanently deleted',

  // Fonts
  'fonts.title': 'Fonts',
  'fonts.desc': 'Choose fonts for the app and editor',
  'fonts.uiFont': 'UI Font',
  'fonts.uiFontDesc': 'Used for menus, buttons, and interface',
  'fonts.editorFont': 'Editor Font',
  'fonts.editorFontDesc': 'Used for note content',
  'fonts.codeFont': 'Code Font',
  'fonts.codeFontDesc': 'Used for code blocks',
  'fonts.customFonts': 'Custom Fonts',
  'fonts.customFontsDesc': 'Add Google Fonts or web font URLs',
  'fonts.addFont': 'Add Font',
  'fonts.fontFile': 'Font File',
  'fonts.fontFilePlaceholder': 'Select a font file',
  'fonts.selectFile': 'Select File',
  'fonts.fontName': 'Font Name',
  'fonts.fontNamePlaceholder': 'Display name for the font',
  'fonts.fontCategory': 'Font Type',
  'fonts.categoryOptions': 'Select category',
  'fonts.noCustomFonts': 'No custom fonts added',
  'fonts.preview': 'Preview',
  'fonts.uiScale': 'UI Scale',
  
  // Shortcuts
  'shortcuts.title': 'Keyboard Shortcuts',
  'shortcuts.desc': 'Customize shortcuts for AI features and common actions',
  'shortcuts.aiMenu': 'Open AI Menu',
  'shortcuts.aiMenuDesc': 'Opens the AI assistant menu in the editor',
  'shortcuts.edit': 'Edit Shortcut',
  'shortcuts.pressKeys': 'Press the keys you want to use',
  'shortcuts.waitingForInput': 'Waiting for input...',
  'shortcuts.current': 'Current shortcuts',
  'shortcuts.addShortcut': 'Add Shortcut',
  'shortcuts.resetDefault': 'Reset to Default',
};

const translations: Record<Language, TranslationKeys> = { ko, en };

// 전역 언어 상태
const STORAGE_KEY = 'cuenote-language';
const currentLanguage = ref<Language>(loadLanguage());

function loadLanguage(): Language {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'ko' || stored === 'en') {
      return stored;
    }
  } catch (e) {
    console.error('Failed to load language:', e);
  }
  // 브라우저 언어 감지
  const browserLang = navigator.language.toLowerCase();
  return browserLang.startsWith('ko') ? 'ko' : 'en';
}

function saveLanguage(lang: Language) {
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch (e) {
    console.error('Failed to save language:', e);
  }
}

export function useI18n() {
  // 번역 함수
  function t(key: keyof TranslationKeys): string {
    return translations[currentLanguage.value][key] || key;
  }

  // 언어 변경
  function setLanguage(lang: Language) {
    currentLanguage.value = lang;
    saveLanguage(lang);
  }

  // 현재 번역 객체
  const messages = computed(() => translations[currentLanguage.value]);

  return {
    t,
    currentLanguage,
    setLanguage,
    messages,
    languages: ['ko', 'en'] as Language[],
    languageNames: {
      ko: '한국어',
      en: 'English',
    } as Record<Language, string>,
  };
}
