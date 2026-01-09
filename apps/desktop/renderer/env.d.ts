/// <reference types="vite/client" />

interface SaveFontResult {
  success: boolean;
  path?: string;
  fileName?: string;
  error?: string;
}

interface DeleteFontResult {
  success: boolean;
  error?: string;
}

interface CueNoteApi {
  selectVault: () => Promise<string | null>;
  openExternal: (url: string) => Promise<void>;
  selectFont: () => Promise<string | null>;
  saveFont: (sourcePath: string, fontName: string) => Promise<SaveFontResult>;
  deleteFont: (fontPath: string) => Promise<DeleteFontResult>;
  getFontsPath: () => Promise<string>;
  setZoomFactor: (factor: number) => void;
  getZoomFactor: () => number;
}

interface Window {
  cuenote?: CueNoteApi;
}
