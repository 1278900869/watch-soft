<template>
  <el-card class="rounded-xl" :body-style="{ padding: '0' }">
    <template #header>
      <div class="flex items-center justify-between">
        <span class="text-lg font-semibold">最近登录记录</span>
        <el-tag type="info" effect="plain">{{ total }} 条记录</el-tag>
      </div>
    </template>

    <el-table 
      :data="tableData" 
      style="width: 100%"
      :border="false"
      stripe
      class="custom-table"
    >
      <el-table-column prop="username" label="用户名" min-width="120">
        <template #default="{ row }">
          <div class="flex items-center gap-2">
            <el-avatar :size="32" class="bg-blue-500">
              {{ row.username[0] }}
            </el-avatar>
            <span class="font-medium">{{ row.username }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="drive_letter" label="驱动器" width="100">
        <template #default="{ row }">
          <el-tag type="warning" effect="plain">{{ row.drive_letter }}:</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="login_time" label="登录时间" width="180">
        <template #default="{ row }">
          <div class="text-gray-600">{{ formatTime(row.login_time) }}</div>
        </template>
      </el-table-column>

      <el-table-column prop="machine_name" label="机器名" width="150" />

      <el-table-column label="状态" width="100">
        <template #default>
          <el-tag type="success" effect="light" size="small">在线</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <div class="p-4 border-t">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface LoginRecord {
  id: number
  username: string
  drive_letter: string
  login_time: string
  machine_name: string
}

const tableData = ref<LoginRecord[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  // TODO: 重新加载数据
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // TODO: 重新加载数据
}

onMounted(() => {
  // TODO: 从API加载数据
  tableData.value = [
    {
      id: 1,
      username: '张三',
      drive_letter: 'H',
      login_time: new Date().toISOString(),
      machine_name: 'PC-001'
    }
  ]
  total.value = 1
})
</script>

<style scoped>
.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
