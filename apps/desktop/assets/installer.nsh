; CueNote - Custom NSIS Installer Script
; Modern UI 2 based installer customization

!include "MUI2.nsh"

; ─────────────────────────────────────────────────────────────────
; UI Configuration
; ─────────────────────────────────────────────────────────────────

; Modern UI settings
!define MUI_ABORTWARNING
!define MUI_ICON "${BUILD_RESOURCES_DIR}\icon.ico"
!define MUI_UNICON "${BUILD_RESOURCES_DIR}\icon.ico"

; Welcome page settings
!define MUI_WELCOMEPAGE_TITLE "CueNote 설치 마법사"
!define MUI_WELCOMEPAGE_TEXT "CueNote - AI 기반 로컬 마크다운 노트 앱$\r$\n$\r$\n이 마법사가 CueNote 설치를 안내합니다.$\r$\n$\r$\n설치를 시작하려면 '다음'을 클릭하세요."

; Finish page settings  
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXECUTABLE_FILENAME}"
!define MUI_FINISHPAGE_RUN_TEXT "CueNote 실행"
!define MUI_FINISHPAGE_TITLE "설치 완료"
!define MUI_FINISHPAGE_TEXT "CueNote가 성공적으로 설치되었습니다.$\r$\n$\r$\n'마침'을 클릭하여 설치를 종료하세요."
!define MUI_FINISHPAGE_LINK "CueNote GitHub"
!define MUI_FINISHPAGE_LINK_LOCATION "https://github.com/cuenote"

; ─────────────────────────────────────────────────────────────────
; Custom macros
; ─────────────────────────────────────────────────────────────────

; Create AppData directory for CueNote data
!macro customInstall
  ; Create app data directories
  CreateDirectory "$APPDATA\cuenote"
  CreateDirectory "$APPDATA\cuenote\data"
  CreateDirectory "$APPDATA\cuenote\data\.graph_cache"
!macroend

; Clean up on uninstall (optional data removal)
!macro customUnInstall
  ; Don't remove user data by default
  ; Users can manually delete %APPDATA%\cuenote if needed
!macroend
