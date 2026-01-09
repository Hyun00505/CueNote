import { createApp } from 'vue';
import App from './App.vue';

// 테마 초기화 (앱 로드 시 즉시 적용하여 깜빡임 방지)
const savedTheme = localStorage.getItem('cuenote-theme');
if (savedTheme) {
  document.documentElement.setAttribute('data-theme', savedTheme);
}

createApp(App).mount('#app');
