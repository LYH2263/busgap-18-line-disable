<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { useActiveLine } from '../useLine'
const trips = ref<any[]>([])
const events = ref<any[]>([])
const history = ref<any[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(false)
const { line, lineId, refresh } = useActiveLine()

const lineHistory = computed(() => history.value.filter((r) => r.line_id === lineId.value))
const isActive = computed(() => !line.value || line.value.is_active)
const viewingHistory = computed(() => history.value.find((r) => r.id === selectedId.value) || null)

async function loadHistory() {
  history.value = await api('/reports')
}

async function run() {
  if (!isActive.value) return
  loading.value = true
  try {
    events.value = (await api(`/reports/run?line_id=${lineId.value}`, { method: 'POST' })).events || []
    selectedId.value = null
    await loadHistory()
  } finally { loading.value = false }
}

function viewReport(r: any) {
  selectedId.value = r.id
  events.value = r.events || []
}

function backToLive() {
  selectedId.value = null
  events.value = []
}

onMounted(async () => {
  await refresh()
  trips.value = await api('/trips')
  await loadHistory()
  if (isActive.value) {
    await run()
  } else if (lineHistory.value.length) {
    // Deactivated: no new detection — surface the most recent historical report.
    viewReport(lineHistory.value[0])
  }
})
function stripClass(s: string) {
  return s === 'bunching' ? 'bg-bunch' : s === 'large_gap' ? 'bg-large' : ''
}
function label(s: string) {
  return s === 'bunching' ? '串车' : s === 'large_gap' ? '大间隔' : '正常'
}
</script>
<template>
  <h1>串车报告</h1>
  <p class="sub">按实际到站间隔对照计划发车间隔 · 竖直条带展示</p>

  <p v-if="line && !line.is_active" class="notice">
    线路已停用：已暂停检测与试算，不能生成新报告；以下可查看停用前生成的历史报告。
  </p>

  <div class="hist-row" style="margin-bottom:0.8rem;flex-wrap:wrap">
    <button v-if="isActive" class="btn" :disabled="loading || !!viewingHistory" @click="run">重新检测</button>
    <button v-if="viewingHistory && isActive" class="hist-btn" @click="backToLive">返回当前结果</button>
    <span class="muted" style="font-size:0.8rem">历史报告：</span>
    <button
      v-for="r in lineHistory" :key="r.id"
      class="hist-btn" :class="{ active: r.id === selectedId }"
      @click="viewReport(r)"
    >#{{ r.id }} · {{ r.created_at }}</button>
    <span v-if="!lineHistory.length" class="muted" style="font-size:0.8rem">暂无</span>
  </div>
  <p v-if="viewingHistory" class="muted" style="font-size:0.8rem;margin-top:0">
    正在查看历史报告 #{{ viewingHistory.id }}（生成于 {{ viewingHistory.created_at }}，站点 {{ viewingHistory.stop_name }}）
  </p>

  <div class="bg-split" style="margin-top:1rem">
    <aside class="bg-trip-col">
      <h2>关联班次</h2>
      <div v-for="r in trips" :key="r.id ?? r.trip_no" class="bg-trip-row">
        <div>
          <div>{{ r.trip_no }}</div>
          <div class="bg-trip-meta">{{ r.vehicle_no }}</div>
        </div>
        <div class="bg-trip-meta">{{ r.planned_depart }}</div>
      </div>
    </aside>
    <div class="bg-strip-col">
      <article
        v-for="(e, i) in events"
        :key="i"
        class="bg-gap-strip"
        :class="stripClass(e.status)"
      >
        <header>{{ e.stop_name }}</header>
        <div class="bg-gap-body">
          <div class="bg-gap-val">{{ e.gap_min }}′</div>
          <div>计划 {{ e.planned_headway_min }}′</div>
          <div>{{ e.earlier_trip }} → {{ e.later_trip }}</div>
          <span class="badge" :class="e.status === 'bunching' ? 'badge-bad' : e.status === 'large_gap' ? 'badge-warn' : 'badge-ok'">
            {{ label(e.status) }}
          </span>
        </div>
      </article>
      <p v-if="!events.length" class="muted">
        {{ isActive ? '暂无间隔事件' : '停用期间不生成新检测，可从上方选择历史报告。' }}
      </p>
    </div>
  </div>
</template>
