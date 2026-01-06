import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useVaultStore = defineStore('vault', () => {
  const vaultPath = ref<string | null>(null)

  function setVaultPath(path: string | null) {
    vaultPath.value = path
  }

  return {
    vaultPath,
    setVaultPath,
  }
})
