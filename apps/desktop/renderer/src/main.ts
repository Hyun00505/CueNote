import { createApp } from 'vue';
import App from './App.vue';

// 테마 초기화 (앱 로드 시 즉시 적용하여 깜빡임 방지)
const savedTheme = localStorage.getItem('cuenote-theme');
const validThemes = ['dark', 'dim', 'github-dark'];
if (savedTheme && validThemes.includes(savedTheme)) {
  document.documentElement.setAttribute('data-theme', savedTheme);
} else if (savedTheme) {
  // 유효하지 않은 테마는 dark로 마이그레이션
  localStorage.setItem('cuenote-theme', 'dark');
}

createApp(App).mount('#app');
