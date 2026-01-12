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

interface PrintToPdfOptions {
  filename?: string;
  title?: string;
  htmlContent?: string;
  pdfOptions?: {
    pageSize?: string;
    printBackground?: boolean;
    marginsType?: number;
    landscape?: boolean;
  };
}

interface PrintToPdfResult {
  success: boolean;
  canceled?: boolean;
  filePath?: string;
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
  printToPDF: (options?: PrintToPdfOptions) => Promise<PrintToPdfResult>;
}

interface Window {
  cuenote?: CueNoteApi;
}
