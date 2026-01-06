export {}

declare global {
  interface Window {
    cuenote: {
      ping: () => string
      selectVault: () => Promise<string | null>
    }
  }
}
