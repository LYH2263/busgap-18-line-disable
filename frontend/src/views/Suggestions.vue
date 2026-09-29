<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { useActiveLine } from '../useLine'
const tips = ref<any[]>([])
const { line, lineId, refresh } = useActiveLine()
onMounted(async () => {
  await refresh()
  if (line.value && !line.value.is_active) { tips.value = []; return }
  try {
    tips.value = (await api(`/reports/suggestions?line_id=${lineId.value}`)).suggestions
  } catch { tips.value = [] }
})
</script>
<template>
  <h1>建议</h1>
  <p class="sub">针对串车与大间隔的调班提示</p>
  <p v-if="line && !line.is_active" class="notice">线路已停用：已暂停试算，启用后恢复检测。</p>
  <template v-else>
    <div class="card" v-for="(t,i) in tips" :key="i">
      <div><strong>{{ t.stop_name }}</strong> · {{ t.earlier_trip }} → {{ t.later_trip }} · 间隔 {{ t.gap_min }} 分</div>
      <p class="muted">{{ t.suggestion }}</p>
    </div>
    <p v-if="!tips.length" class="muted">暂无异常建议</p>
  </template>
</template>
