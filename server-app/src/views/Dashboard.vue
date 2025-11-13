<template>
  <div class="space-y-6">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <StatCard 
          title="今日登录"
          :value="stats.todayLogins"
          subtitle="较昨日 +12%"
          :icon="UserIcon"
          icon-bg-class="bg-blue-100 text-blue-600"
          value-class="text-blue-600"
        />
      </el-col>

      <el-col :span="6">
        <StatCard 
          title="拷入操作"
          :value="stats.todayEvents"
          subtitle="今日新增"
          :icon="DocumentDuplicateIcon"
          icon-bg-class="bg-green-100 text-green-600"
          value-class="text-green-600"
        />
      </el-col>

      <el-col :span="6">
        <StatCard 
          title="在线设备"
          :value="stats.onlineDevices"
          subtitle="活跃中"
          :icon="ComputerDesktopIcon"
          icon-bg-class="bg-purple-100 text-purple-600"
          value-class="text-purple-600"
        />
      </el-col>

      <el-col :span="6">
        <StatCard 
          title="总用户数"
          :value="stats.totalUsers"
          subtitle="累计注册"
          :icon="UserGroupIcon"
          icon-bg-class="bg-orange-100 text-orange-600"
          value-class="text-orange-600"
        />
      </el-col>
    </el-row>

    <!-- 图表和表格 -->
    <el-row :gutter="20">
      <!-- 最近登录记录 -->
      <el-col :span="24">
        <UserLoginTable />
      </el-col>
    </el-row>

    <!-- 拷入趋势 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="rounded-xl">
          <template #header>
            <span class="font-semibold">文件拷入趋势</span>
          </template>
          <div class="h-64 flex items-center justify-center text-gray-400">
            <p>图表区域 (可集成 ECharts)</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="rounded-xl">
          <template #header>
            <span class="font-semibold">文件类型分布</span>
          </template>
          <div class="h-64 flex items-center justify-center text-gray-400">
            <p>图表区域 (可集成 ECharts)</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { UserIcon, DocumentDuplicateIcon, ComputerDesktopIcon, UserGroupIcon } from '@heroicons/vue/24/solid'
// Element Plus icons kept for future use
// import { UserFilled, DocumentCopy, Monitor, Avatar } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import UserLoginTable from '@/components/UserLoginTable.vue'

const stats = reactive({
  todayLogins: 24,
  todayEvents: 156,
  onlineDevices: 8,
  totalUsers: 42
})
</script>
