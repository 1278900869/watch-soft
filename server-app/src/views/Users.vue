<template>
  <div>
    <el-card class="rounded-xl">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="text-lg font-semibold">人员管理</span>
          <el-button type="primary" size="small">
            <PlusIcon class="w-4 h-4 inline-block mr-1" />
            添加人员
          </el-button>
        </div>
      </template>

      <el-table :data="userData" stripe>
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="loginCount" label="登录次数" />
        <el-table-column prop="lastLogin" label="最后登录时间" />
        <el-table-column label="操作" width="200">
          <template #default>
            <el-button size="small" text>编辑</el-button>
            <el-button size="small" text type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
// Element Plus icons kept for future use
// import { Plus } from '@element-plus/icons-vue'

const userData = ref([
  { username: '张三', loginCount: 24, lastLogin: '2025-11-13 10:30' },
  { username: '李四', loginCount: 18, lastLogin: '2025-11-12 16:45' }
])
</script>
