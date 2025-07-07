/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_DISABLE_KIOSK_MODE: string;
  readonly VITE_MOCK_PAYMENT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  IS_PWA_MODE?: boolean;
} 