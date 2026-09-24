/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_USE_MOCK_DATA?: string;
  readonly VITE_PROXY_TARGET?: string;
  readonly VITE_GRAFANA_URL?: string;
  readonly VITE_PROMETHEUS_URL?: string;
  readonly VITE_METRICS_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
