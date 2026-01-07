/// <reference types="vite/client" />

interface CueNoteApi {
  selectVault: () => Promise<string | null>;
}

interface Window {
  cuenote: CueNoteApi;
}
