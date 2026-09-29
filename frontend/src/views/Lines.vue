<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const rows = ref<any[]>([])
const busyId = ref<number | null>(null)
const error = ref('')

onMounted(load)

async function load() {
  rows.value = await api('/lines')
}

async function toggle(r: any) {
  busyId.value = r.id
  error.value = ''
  try {
    const action = r.is_active ? 'deactivate' : 'activate'
    const updated = await api(`/lines/${r.id}/${action}`, { method: 'POST' })
    const idx = rows.value.findIndex((x) => x.id === r.id)
    if (idx !== -1) rows.value[idx] = updated
  } catch (e: any) {
    error.value = e?.message || '操作失败'
  } finally {
    busyId.value = null
  }
}
</script>
<template>
  <h1>线路</h1>
  <p class="sub">运营线路与串车 / 大间隔判定阈值 · 停用后不再对该线检测或试算</p>
  <p v-if="error" class="badge badge-bad">{{ error }}</p>
  <div class="card">
    <table>
      <thead><tr><th>编码</th><th>名称</th><th>计划间隔(分)</th><th>串车阈值</th><th>大间隔阈值</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id ?? JSON.stringify(r)">
          <td>{{ r.code }}</td>
          <td>{{ r.name }}</td>
          <td>{{ r.planned_headway_min }}</td>
          <td>{{ r.bunch_threshold }}</td>
          <td>{{ r.large_threshold }}</td>
          <td>
            <span class="badge" :class="r.is_active ? 'badge-ok' : 'badge-warn'">
              {{ r.is_active ? '运营中' : '已停用' }}
            </span>
          </td>
          <td>
            <button
              class="btn"
              :class="r.is_active ? 'btn-off' : 'btn-on'"
              :disabled="busyId === r.id"
              @click="toggle(r)"
            >{{ r.is_active ? '停用' : '启用' }}</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
