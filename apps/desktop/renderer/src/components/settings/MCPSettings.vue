<template>
    <div id="section-mcp" class="settings-category">
        <h2 class="category-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="6" height="6" rx="1" />
                <rect x="16" y="2" width="6" height="6" rx="1" />
                <rect x="9" y="16" width="6" height="6" rx="1" />
                <path d="M5 8v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8" />
                <path d="M12 13v3" />
            </svg>
            MCP 서버 관리
        </h2>

        <!-- ★ 추천 프리셋 -->
        <section class="settings-section">
            <h3 class="section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon
                        points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
                추천 MCP 서버 (원클릭 설치)
            </h3>
            <p class="preset-desc">CueNote 노트 앱에 유용한 MCP 서버들입니다. 클릭 한 번으로 등록할 수 있습니다.</p>

            <div class="preset-grid">
                <div v-for="preset in presets" :key="preset.id" class="preset-card"
                    :class="{ installed: isPresetInstalled(preset.id) }">
                    <div class="preset-icon">{{ preset.icon }}</div>
                    <div class="preset-info">
                        <div class="preset-name">{{ preset.name }}</div>
                        <div class="preset-description">{{ preset.description }}</div>
                        <div class="preset-tools-hint">
                            <span v-for="tool in preset.toolHints" :key="tool" class="tool-hint-tag">{{ tool }}</span>
                        </div>
                    </div>
                    <div class="preset-action">
                        <span v-if="isPresetInstalled(preset.id)" class="installed-badge">✓ 설치됨</span>
                        <button v-else class="preset-install-btn" :disabled="presetLoading[preset.id]"
                            @click="installPreset(preset)">
                            <span v-if="presetLoading[preset.id]" class="loading-spinner small" />
                            <span v-else>+ 설치</span>
                        </button>
                    </div>
                    <div v-if="preset.envNote" class="preset-env-note">
                        ⚠ {{ preset.envNote }}
                    </div>
                </div>
            </div>
        </section>

        <!-- 수동 서버 추가 폼 -->
        <section class="settings-section">
            <h3 class="section-title toggle-title" @click="showManualForm = !showManualForm">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="16" />
                    <line x1="8" y1="12" x2="16" y2="12" />
                </svg>
                수동으로 서버 추가
                <svg class="chevron" :class="{ open: showManualForm }" width="12" height="12" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9" />
                </svg>
            </h3>

            <div v-if="showManualForm" class="add-server-form">
                <div class="form-row">
                    <label class="form-label">서버 ID</label>
                    <input v-model="newServer.id" type="text" class="form-input" placeholder="예: filesystem, github">
                </div>
                <div class="form-row">
                    <label class="form-label">명령어</label>
                    <input v-model="newServer.command" type="text" class="form-input"
                        placeholder="예: npx, uvx, node, python">
                </div>
                <div class="form-row">
                    <label class="form-label">인수 (쉼표로 구분)</label>
                    <input v-model="newServer.argsStr" type="text" class="form-input"
                        placeholder="예: -y,@modelcontextprotocol/server-filesystem,C:/Users">
                </div>
                <div class="form-row">
                    <label class="form-label">설명</label>
                    <input v-model="newServer.description" type="text" class="form-input" placeholder="예: 파일 시스템 접근 서버">
                </div>
                <div class="form-row">
                    <label class="form-label">환경 변수 (KEY=VALUE, 쉼표로 구분)</label>
                    <input v-model="newServer.envStr" type="text" class="form-input"
                        placeholder="예: GITHUB_TOKEN=ghp_xxx,NODE_ENV=production">
                </div>
                <button class="add-btn" :disabled="!newServer.id || !newServer.command || isAdding" @click="addServer">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19" />
                        <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                    <span v-if="isAdding" class="loading-spinner" />
                    <span v-else>서버 추가</span>
                </button>
            </div>
        </section>

        <!-- 등록된 서버 목록 -->
        <section class="settings-section">
            <div class="section-header-with-action">
                <h3 class="section-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                        <line x1="8" y1="21" x2="16" y2="21" />
                        <line x1="12" y1="17" x2="12" y2="21" />
                    </svg>
                    등록된 서버
                </h3>
                <button class="refresh-btn" :disabled="isRefreshing" title="서버 목록 새로고침" @click="refreshServers">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                        :class="{ spinning: isRefreshing }">
                        <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                        <path d="M21 3v5h-5" />
                        <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                        <path d="M8 16H3v5" />
                    </svg>
                </button>
            </div>

            <div v-if="isLoading" class="servers-loading">
                <span class="loading-spinner" />
                <span>서버 목록 불러오는 중...</span>
            </div>

            <div v-else-if="Object.keys(servers).length === 0" class="no-servers">
                <p>등록된 MCP 서버가 없습니다.</p>
                <p class="hint-text">위의 추천 서버를 설치하거나 수동으로 추가하세요.</p>
            </div>

            <div v-else class="server-list">
                <div v-for="(config, serverId) in servers" :key="serverId" class="server-card"
                    :class="{ running: config.status === 'running' }">
                    <div class="server-header">
                        <div class="server-info">
                            <div class="server-name-row">
                                <span class="server-name">{{ serverId }}</span>
                                <span class="status-badge" :class="config.status">
                                    {{ config.status === 'running' ? '● 실행 중' : '○ 중지됨' }}
                                </span>
                            </div>
                            <span v-if="config.description" class="server-desc">{{ config.description }}</span>
                            <span class="server-cmd">{{ config.command }} {{ (config.args || []).join(' ') }}</span>
                        </div>
                        <div class="server-actions">
                            <button v-if="config.status !== 'running'" class="action-btn start-btn"
                                :disabled="actionLoading[serverId as string]" title="서버 시작"
                                @click="startServer(serverId as string)">
                                <span v-if="actionLoading[serverId as string]" class="loading-spinner small" />
                                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <polygon points="5 3 19 12 5 21 5 3" />
                                </svg>
                            </button>
                            <button v-else class="action-btn stop-btn" :disabled="actionLoading[serverId as string]"
                                title="서버 중지" @click="stopServer(serverId as string)">
                                <span v-if="actionLoading[serverId as string]" class="loading-spinner small" />
                                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <rect x="4" y="4" width="16" height="16" rx="2" />
                                </svg>
                            </button>
                            <button class="action-btn delete-btn" title="서버 삭제"
                                @click="deleteServer(serverId as string)">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <polyline points="3 6 5 6 21 6" />
                                    <path
                                        d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- 도구 목록 (실행 중일 때만) -->
                    <div v-if="config.status === 'running' && config.tools && config.tools.length > 0"
                        class="tools-section">
                        <div class="tools-header">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path
                                    d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                            </svg>
                            <span>도구 {{ config.tools.length }}개</span>
                        </div>
                        <div class="tools-list">
                            <div v-for="tool in config.tools" :key="tool.name" class="tool-item">
                                <div class="tool-item-header">
                                    <span class="tool-name">{{ tool.name }}</span>
                                    <button class="tool-test-btn" @click="toggleToolTest(serverId as string, tool)">
                                        {{ testingTool?.serverId === serverId && testingTool?.toolName === tool.name ?
                                            '닫기' : '테스트' }}
                                    </button>
                                </div>
                                <span v-if="tool.description" class="tool-desc">{{ tool.description }}</span>

                                <!-- 도구 테스트 패널 -->
                                <div v-if="testingTool?.serverId === serverId && testingTool?.toolName === tool.name"
                                    class="tool-test-panel">
                                    <div class="test-params">
                                        <div v-for="(prop, propName) in getToolProperties(tool)" :key="propName"
                                            class="test-param-row">
                                            <label class="test-param-label">{{ propName }}
                                                <span v-if="isRequired(tool, propName as string)"
                                                    class="required-mark">*</span>
                                            </label>
                                            <input v-if="prop.type === 'boolean'" type="checkbox"
                                                :checked="testArgs[propName as string] === true"
                                                @change="testArgs[propName as string] = ($event.target as HTMLInputElement).checked">
                                            <input v-else-if="prop.type === 'number' || prop.type === 'integer'"
                                                type="number" class="test-input" :placeholder="prop.description || ''"
                                                :value="testArgs[propName as string] ?? ''"
                                                @input="testArgs[propName as string] = Number(($event.target as HTMLInputElement).value)">
                                            <textarea v-else class="test-input test-textarea"
                                                :placeholder="prop.description || String(propName)"
                                                :value="String(testArgs[propName as string] ?? '')"
                                                @input="testArgs[propName as string] = ($event.target as HTMLInputElement).value" />
                                        </div>
                                        <div v-if="Object.keys(getToolProperties(tool)).length === 0"
                                            class="test-no-params">
                                            파라미터 없음 — 바로 실행할 수 있습니다.
                                        </div>
                                    </div>
                                    <button class="test-execute-btn" :disabled="isTestRunning"
                                        @click="executeToolTest(serverId as string, tool.name)">
                                        <span v-if="isTestRunning" class="loading-spinner" />
                                        <span>{{ isTestRunning ? '실행 중...' : '▶ 실행' }}</span>
                                    </button>
                                    <div v-if="testResult !== null" class="test-result"
                                        :class="{ 'test-error': testResultIsError }">
                                        <div class="test-result-header">{{ testResultIsError ? '❌ 오류' : '✅ 결과' }}</div>
                                        <pre class="test-result-content">{{ formatTestResult(testResult) }}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 에러 메시지 -->
        <div v-if="errorMessage" class="error-message">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{{ errorMessage }}</span>
            <button class="dismiss-btn" @click="errorMessage = ''">✕</button>
        </div>

        <!-- 성공 메시지 -->
        <div v-if="successMessage" class="success-message">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <span>{{ successMessage }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { API_ENDPOINTS } from '../../config/api';

interface MCPTool {
    name: string;
    description: string;
    inputSchema: Record<string, unknown>;
}

interface MCPServerInfo {
    command: string;
    args: string[];
    env: Record<string, string>;
    enabled: boolean;
    description: string;
    status: string;
    tools: MCPTool[];
}

interface MCPPreset {
    id: string;
    name: string;
    icon: string;
    description: string;
    command: string;
    args: string[];
    env: Record<string, string>;
    toolHints: string[];
    envNote?: string;
}

// ─── 추천 프리셋 정의 ────────────────────────────────────────────────

const presets: MCPPreset[] = [
    {
        id: 'filesystem',
        name: 'Filesystem',
        icon: '📁',
        description: '로컬 파일 시스템에 안전하게 접근합니다. 노트 파일 읽기/쓰기/검색에 활용됩니다.',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', 'C:/Users'],
        env: {},
        toolHints: ['read_file', 'write_file', 'list_directory', 'search_files'],
    },
    {
        id: 'memory',
        name: 'Memory',
        icon: '🧠',
        description: '지식 그래프 기반의 영구 메모리. AI가 대화 간 맥락을 기억하고 노트 관계를 파악합니다.',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-memory'],
        env: {},
        toolHints: ['create_entities', 'create_relations', 'search_nodes', 'open_nodes'],
    },
    {
        id: 'brave-search',
        name: 'Brave Search',
        icon: '🔍',
        description: '프라이버시 중심 웹 검색. 노트 작성 시 최신 정보를 검색하여 참고할 수 있습니다.',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-brave-search'],
        env: { BRAVE_API_KEY: '' },
        toolHints: ['brave_web_search', 'brave_local_search'],
        envNote: 'Brave API Key 필요 (brave.com/search/api 에서 무료 발급)',
    },
    {
        id: 'github',
        name: 'GitHub',
        icon: '🐙',
        description: 'GitHub 레포지토리 관리. 노트를 GitHub에 백업하거나 이슈/PR을 관리합니다.',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-github'],
        env: { GITHUB_PERSONAL_ACCESS_TOKEN: '' },
        toolHints: ['create_repository', 'push_files', 'create_issue', 'search_repositories'],
        envNote: 'GitHub Personal Access Token 필요',
    },
    {
        id: 'sequential-thinking',
        name: 'Sequential Thinking',
        icon: '💡',
        description: '단계적 사고 엔진. 복잡한 주제를 분석하고 구조화된 노트를 생성합니다.',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-sequential-thinking'],
        env: {},
        toolHints: ['sequentialthinking'],
    },
];

const servers = ref<Record<string, MCPServerInfo>>({});
const isLoading = ref(false);
const isRefreshing = ref(false);
const isAdding = ref(false);
const showManualForm = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const actionLoading = reactive<Record<string, boolean>>({});
const presetLoading = reactive<Record<string, boolean>>({});

const newServer = reactive({
    id: '',
    command: '',
    argsStr: '',
    description: '',
    envStr: '',
});

// ─── 프리셋 관련 ─────────────────────────────────────────────────────

function isPresetInstalled(presetId: string): boolean {
    return presetId in servers.value;
}

async function installPreset(preset: MCPPreset) {
    presetLoading[preset.id] = true;
    errorMessage.value = '';

    // 환경 변수가 필요한 프리셋의 경우 빈 값이 있으면 입력 요청
    const envKeys = Object.keys(preset.env);
    const filledEnv: Record<string, string> = {};
    for (const key of envKeys) {
        if (!preset.env[key]) {
            const value = prompt(`${preset.name} 서버에 필요한 환경 변수를 입력하세요:\n\n${key}`);
            if (!value) {
                presetLoading[preset.id] = false;
                return; // 취소하면 설치 안함
            }
            filledEnv[key] = value;
        } else {
            filledEnv[key] = preset.env[key];
        }
    }

    try {
        const res = await fetch(`${API_ENDPOINTS.MCP.SERVERS}/${preset.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: preset.command,
                args: preset.args,
                env: filledEnv,
                enabled: true,
                description: preset.description,
            }),
        });

        if (!res.ok) throw new Error('Failed to install preset');

        showSuccess(`'${preset.name}' 서버가 등록되었습니다! ▶ 시작 버튼으로 활성화하세요.`);
        await fetchServers();
    } catch (e: unknown) {
        errorMessage.value = `프리셋 설치 실패: ${e instanceof Error ? e.message : String(e)}`;
    } finally {
        presetLoading[preset.id] = false;
    }
}

// ─── API 호출 ────────────────────────────────────────────────────────

async function fetchServers() {
    try {
        const res = await fetch(API_ENDPOINTS.MCP.SERVERS);
        if (!res.ok) throw new Error('Failed to fetch servers');
        const data = await res.json();
        servers.value = data.servers || {};
    } catch (e: unknown) {
        errorMessage.value = `서버 목록 로드 실패: ${e instanceof Error ? e.message : String(e)}`;
    }
}

async function refreshServers() {
    isRefreshing.value = true;
    await fetchServers();
    isRefreshing.value = false;
}

function parseArgs(argsStr: string): string[] {
    if (!argsStr.trim()) return [];
    return argsStr.split(',').map((s) => s.trim()).filter(Boolean);
}

function parseEnv(envStr: string): Record<string, string> {
    if (!envStr.trim()) return {};
    const result: Record<string, string> = {};
    envStr.split(',').forEach((pair) => {
        const eqIdx = pair.indexOf('=');
        if (eqIdx > 0) {
            result[pair.slice(0, eqIdx).trim()] = pair.slice(eqIdx + 1).trim();
        }
    });
    return result;
}

async function addServer() {
    if (!newServer.id || !newServer.command) return;
    isAdding.value = true;
    errorMessage.value = '';

    try {
        const res = await fetch(`${API_ENDPOINTS.MCP.SERVERS}/${newServer.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: newServer.command,
                args: parseArgs(newServer.argsStr),
                env: parseEnv(newServer.envStr),
                enabled: true,
                description: newServer.description,
            }),
        });

        if (!res.ok) throw new Error('Failed to add server');

        showSuccess(`서버 '${newServer.id}' 추가 완료`);
        newServer.id = '';
        newServer.command = '';
        newServer.argsStr = '';
        newServer.description = '';
        newServer.envStr = '';
        await fetchServers();
    } catch (e: unknown) {
        errorMessage.value = `서버 추가 실패: ${e instanceof Error ? e.message : String(e)}`;
    } finally {
        isAdding.value = false;
    }
}

async function startServer(serverId: string) {
    actionLoading[serverId] = true;
    errorMessage.value = '';
    try {
        const res = await fetch(`${API_ENDPOINTS.MCP.SERVERS}/${serverId}/start`, {
            method: 'POST',
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Failed to start server');
        }
        showSuccess(`서버 '${serverId}' 시작됨`);
        await fetchServers();
    } catch (e: unknown) {
        errorMessage.value = `서버 시작 실패: ${e instanceof Error ? e.message : String(e)}`;
    } finally {
        actionLoading[serverId] = false;
    }
}

async function stopServer(serverId: string) {
    actionLoading[serverId] = true;
    errorMessage.value = '';
    try {
        const res = await fetch(`${API_ENDPOINTS.MCP.SERVERS}/${serverId}/stop`, {
            method: 'POST',
        });
        if (!res.ok) throw new Error('Failed to stop server');
        showSuccess(`서버 '${serverId}' 중지됨`);
        await fetchServers();
    } catch (e: unknown) {
        errorMessage.value = `서버 중지 실패: ${e instanceof Error ? e.message : String(e)}`;
    } finally {
        actionLoading[serverId] = false;
    }
}

async function deleteServer(serverId: string) {
    if (!confirm(`서버 '${serverId}'를 삭제하시겠습니까?`)) return;
    errorMessage.value = '';
    try {
        const res = await fetch(`${API_ENDPOINTS.MCP.SERVERS}/${serverId}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('Failed to delete server');
        showSuccess(`서버 '${serverId}' 삭제됨`);
        await fetchServers();
    } catch (e: unknown) {
        errorMessage.value = `서버 삭제 실패: ${e instanceof Error ? e.message : String(e)}`;
    }
}

function showSuccess(msg: string) {
    successMessage.value = msg;
    setTimeout(() => {
        successMessage.value = '';
    }, 3000);
}

// ─── 도구 테스트 ──────────────────────────────────────────────────────

const testingTool = ref<{ serverId: string; toolName: string } | null>(null);
const testArgs = reactive<Record<string, unknown>>({});
const testResult = ref<unknown>(null);
const testResultIsError = ref(false);
const isTestRunning = ref(false);

function toggleToolTest(serverId: string, tool: MCPTool) {
    if (testingTool.value?.serverId === serverId && testingTool.value?.toolName === tool.name) {
        testingTool.value = null;
        return;
    }
    testingTool.value = { serverId, toolName: tool.name };
    // testArgs 초기화
    Object.keys(testArgs).forEach(k => delete testArgs[k]);
    testResult.value = null;
    testResultIsError.value = false;
}

function getToolProperties(tool: MCPTool): Record<string, { type?: string; description?: string }> {
    const schema = tool.inputSchema as Record<string, unknown>;
    if (!schema || !schema.properties) return {};
    return schema.properties as Record<string, { type?: string; description?: string }>;
}

function isRequired(tool: MCPTool, propName: string): boolean {
    const schema = tool.inputSchema as Record<string, unknown>;
    const required = schema?.required;
    if (Array.isArray(required)) return required.includes(propName);
    return false;
}

async function executeToolTest(serverId: string, toolName: string) {
    isTestRunning.value = true;
    testResult.value = null;
    testResultIsError.value = false;
    try {
        const res = await fetch(API_ENDPOINTS.MCP.TOOLS_CALL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_id: serverId,
                tool_name: toolName,
                arguments: { ...testArgs },
            }),
        });
        const data = await res.json();
        if (!res.ok) {
            testResultIsError.value = true;
            testResult.value = data.detail || 'Tool call failed';
        } else {
            testResult.value = data.result;
        }
    } catch (e: unknown) {
        testResultIsError.value = true;
        testResult.value = e instanceof Error ? e.message : String(e);
    } finally {
        isTestRunning.value = false;
    }
}

function formatTestResult(result: unknown): string {
    if (typeof result === 'string') return result;
    try {
        return JSON.stringify(result, null, 2);
    } catch {
        return String(result);
    }
}

onMounted(async () => {
    isLoading.value = true;
    await fetchServers();
    isLoading.value = false;
});
</script>

<style scoped>
.settings-category {
    margin-bottom: 48px;
    padding-bottom: 32px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-primary);
}

.category-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--accent);
}

.category-title svg {
    color: var(--accent);
}

.settings-section {
    margin-bottom: 32px;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 14px;
}

.section-title svg {
    opacity: 0.7;
}

.toggle-title {
    cursor: pointer;
    user-select: none;
    transition: color 0.15s ease;
}

.toggle-title:hover {
    color: var(--text-primary);
}

.chevron {
    margin-left: auto;
    transition: transform 0.2s ease;
}

.chevron.open {
    transform: rotate(180deg);
}

.section-header-with-action {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.section-header-with-action .section-title {
    margin-bottom: 0;
}

/* ── Preset Cards ── */
.preset-desc {
    font-size: 12px;
    color: var(--text-muted);
    margin: -8px 0 14px 0;
}

.preset-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.preset-card {
    display: grid;
    grid-template-columns: 40px 1fr auto;
    grid-template-rows: auto auto;
    gap: 4px 14px;
    padding: 14px 16px;
    background: var(--surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    transition: all 0.15s ease;
}

.preset-card:hover {
    border-color: var(--border-default);
}

.preset-card.installed {
    opacity: 0.65;
}

.preset-icon {
    grid-row: 1 / 3;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    width: 40px;
    height: 40px;
    background: var(--bg-secondary);
    border-radius: 8px;
}

.preset-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
}

.preset-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

.preset-description {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.4;
}

.preset-tools-hint {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 2px;
}

.tool-hint-tag {
    padding: 1px 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    font-size: 10px;
    color: var(--text-muted);
    font-family: 'SF Mono', 'Fira Code', monospace;
}

.preset-action {
    display: flex;
    align-items: center;
    justify-content: center;
}

.preset-install-btn {
    padding: 6px 14px;
    background: transparent;
    border: 1px solid rgba(34, 197, 94, 0.4);
    border-radius: 6px;
    color: #22c55e;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}

.preset-install-btn:hover:not(:disabled) {
    background: rgba(34, 197, 94, 0.1);
    border-color: rgba(34, 197, 94, 0.6);
}

.preset-install-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.installed-badge {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    white-space: nowrap;
}

.preset-env-note {
    grid-column: 2 / 4;
    font-size: 11px;
    color: #f59e0b;
    opacity: 0.8;
    margin-top: 2px;
}

/* ── Add Server Form ── */
.add-server-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    background: var(--surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
}

.form-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.form-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
}

.form-input {
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 13px;
    font-family: 'SF Mono', 'Fira Code', monospace;
    transition: all 0.15s ease;
}

.form-input:focus {
    outline: none;
    border-color: var(--text-muted);
}

.form-input::placeholder {
    color: var(--text-muted);
    opacity: 0.5;
}

.add-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 18px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    align-self: flex-start;
}

.add-btn:hover:not(:disabled) {
    background: var(--bg-hover);
    border-color: var(--border-default);
    color: var(--text-primary);
}

.add-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* ── Server List ── */
.server-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.server-card {
    padding: 16px;
    background: var(--surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    transition: all 0.15s ease;
}

.server-card.running {
    border-color: rgba(34, 197, 94, 0.3);
}

.server-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}

.server-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 0;
}

.server-name-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.server-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

.status-badge {
    font-size: 11px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 10px;
}

.status-badge.running {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
}

.status-badge.stopped {
    background: rgba(156, 163, 175, 0.15);
    color: var(--text-muted);
}

.server-desc {
    font-size: 12px;
    color: var(--text-muted);
}

.server-cmd {
    font-size: 11px;
    color: var(--text-muted);
    font-family: 'SF Mono', 'Fira Code', monospace;
    opacity: 0.7;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.server-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
}

.action-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.action-btn:hover:not(:disabled) {
    background: var(--bg-hover);
    border-color: var(--border-default);
}

.action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.start-btn {
    color: #22c55e;
}

.start-btn:hover:not(:disabled) {
    border-color: rgba(34, 197, 94, 0.5);
}

.stop-btn {
    color: #f59e0b;
}

.stop-btn:hover:not(:disabled) {
    border-color: rgba(245, 158, 11, 0.5);
}

.delete-btn {
    color: #ef4444;
}

.delete-btn:hover:not(:disabled) {
    border-color: rgba(239, 68, 68, 0.5);
}

/* ── Tools Section ── */
.tools-section {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-subtle);
}

.tools-header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.tools-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.tool-item {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 6px 10px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
}

.tool-item-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}

.tool-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    font-family: 'SF Mono', 'Fira Code', monospace;
}

.tool-test-btn {
    font-size: 10px;
    padding: 2px 8px;
    border: 1px solid var(--accent);
    border-radius: 4px;
    background: transparent;
    color: var(--accent);
    cursor: pointer;
    transition: all 0.15s ease;
}

.tool-test-btn:hover {
    background: var(--accent);
    color: white;
}

.tool-desc {
    font-size: 10px;
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ── Tool Test Panel ── */
.tool-test-panel {
    margin-top: 8px;
    padding: 10px;
    background: var(--surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
}

.test-params {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 10px;
}

.test-param-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.test-param-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
}

.required-mark {
    color: #ef4444;
}

.test-input {
    padding: 6px 8px;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 12px;
    font-family: 'SF Mono', 'Fira Code', monospace;
}

.test-textarea {
    min-height: 50px;
    max-height: 120px;
    resize: vertical;
}

.test-no-params {
    font-size: 11px;
    color: var(--text-muted);
    font-style: italic;
}

.test-execute-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
    background: var(--accent);
    color: white;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s ease;
}

.test-execute-btn:hover:not(:disabled) {
    opacity: 0.9;
}

.test-execute-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.test-result {
    margin-top: 10px;
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 6px;
    overflow: hidden;
}

.test-result.test-error {
    border-color: rgba(239, 68, 68, 0.3);
}

.test-result-header {
    font-size: 11px;
    font-weight: 600;
    padding: 6px 10px;
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}

.test-error .test-result-header {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
}

.test-result-content {
    padding: 8px 10px;
    font-size: 11px;
    font-family: 'SF Mono', 'Fira Code', monospace;
    color: var(--text-secondary);
    max-height: 200px;
    overflow: auto;
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
    background: var(--bg-primary);
}

/* ── Loading / States ── */
.servers-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 30px;
    color: var(--text-muted);
    font-size: 13px;
}

.no-servers {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
    font-size: 13px;
}

.no-servers p {
    margin: 0;
}

.hint-text {
    font-size: 12px;
    opacity: 0.7;
    margin-top: 4px !important;
}

/* ── Messages ── */
.error-message,
.success-message {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px;
    border-radius: 8px;
    font-size: 13px;
    margin-top: 16px;
}

.error-message {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #f87171;
}

.success-message {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
    color: #22c55e;
}

.dismiss-btn {
    margin-left: auto;
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font-size: 14px;
    opacity: 0.7;
}

.dismiss-btn:hover {
    opacity: 1;
}

/* ── Refresh ── */
.refresh-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.15s ease;
}

.refresh-btn:hover:not(:disabled) {
    background: var(--bg-hover);
    border-color: var(--border-default);
    color: var(--text-primary);
}

.refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.refresh-btn svg.spinning {
    animation: spin 1s linear infinite;
}

/* ── Spinner ── */
.loading-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid var(--border-subtle);
    border-top-color: var(--text-primary);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

.loading-spinner.small {
    width: 12px;
    height: 12px;
    border-width: 1.5px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
