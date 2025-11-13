<template>
  <el-card class="stat-card hover:shadow-lg transition-shadow duration-300" :body-style="{ padding: '20px' }">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-gray-500 text-sm mb-2">{{ title }}</p>
        <p class="text-3xl font-bold" :class="valueClass">{{ value }}</p>
        <p v-if="subtitle" class="text-xs text-gray-400 mt-2">{{ subtitle }}</p>
      </div>
      <div 
        class="w-16 h-16 rounded-full flex items-center justify-center"
        :class="iconBgClass"
      >
        <component :is="icon" class="w-8 h-8" />
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  title: string
  value: string | number
  subtitle?: string
  icon: Component
  iconBgClass?: string
  valueClass?: string
}>()
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
}
</style>
