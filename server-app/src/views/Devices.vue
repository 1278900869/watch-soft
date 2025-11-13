<template>
  <div>
    <el-card class="rounded-xl">
      <template #header>
        <span class="text-lg font-semibold">USB设备监控</span>
      </template>

      <el-table :data="devices" stripe>
        <el-table-column prop="drive" label="驱动器" width="100">
          <template #default="{ row }">
            <el-tag type="warning" effect="plain">{{ row.drive }}:</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="user" label="使用用户" />

        <el-table-column prop="insertTime" label="插入时间" width="180" />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.online ? 'success' : 'info'" size="small">
              {{ row.online ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="fileCount" label="拷入文件数" width="120" />

        <el-table-column label="操作" width="150">
          <template #default>
            <el-button size="small" text type="primary">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const devices = ref([
  { drive: 'H', user: '张三', insertTime: '2025-11-13 09:15', online: true, fileCount: 12 },
  { drive: 'G', user: '李四', insertTime: '2025-11-13 10:20', online: true, fileCount: 8 }
])
</script>
