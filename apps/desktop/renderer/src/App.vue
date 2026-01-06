<template>
  <main class="layout">
    <header>
      <h1>CueNote Desktop</h1>
      <p>Local core service: <strong>{{ coreStatus }}</strong></p>
    </header>

    <section class="panel">
      <h2>Live Events</h2>
      <p v-if="events.length === 0">Waiting for events...</p>
      <ul>
        <li v-for="(event, index) in events" :key="index">{{ event }}</li>
      </ul>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue';

const coreStatus = ref('checking...');
const events = ref<string[]>([]);
let eventSource: EventSource | undefined;

async function checkHealth() {
  try {
    const res = await fetch('http://127.0.0.1:8787/health');
    const data = await res.json();
    coreStatus.value = data.status ?? 'unknown';
  } catch (error) {
    coreStatus.value = 'unreachable';
    console.error('Health check failed', error);
  }
}

function connectEvents() {
  eventSource = new EventSource('http://127.0.0.1:8787/events');

  eventSource.onmessage = (event) => {
    events.value.unshift(event.data);
  };

  eventSource.onerror = () => {
    events.value.unshift('Connection lost');
    eventSource?.close();
  };
}

onMounted(() => {
  checkHealth();
  connectEvents();
});

onBeforeUnmount(() => {
  eventSource?.close();
});
</script>

<style scoped>
.layout {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  padding: 1.5rem;
  background: #0f172a;
  min-height: 100vh;
  color: #e2e8f0;
}

header {
  margin-bottom: 1rem;
}

.panel {
  background: #1e293b;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 0.25rem 0;
}
</style>
