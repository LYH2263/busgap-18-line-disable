import { ref } from 'vue'
import { api } from './api'

// The app currently works against one line at a time (seeded B12, id 1).
// Resolve it and expose its active state so views can gate detection.
export function useActiveLine(preferredId = 1) {
  const line = ref<any>(null)
  const lineId = ref(preferredId)

  async function refresh() {
    const lines = await api<any[]>('/lines')
    line.value = lines.find((l) => l.id === lineId.value) || lines[0] || null
    if (line.value) lineId.value = line.value.id
    return line.value
  }

  return { line, lineId, refresh }
}
