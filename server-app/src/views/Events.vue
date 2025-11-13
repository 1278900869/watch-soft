<template>
  <div>
    <!-- 拷入记录 -->
    <el-card class="rounded-xl" :body-style="{ padding: '16px' }">
      <template #header>
        <div class="flex items-center justify-between gap-6">
          <!-- 左侧:当天日期 -->
          <div class="flex items-center gap-1 text-base font-semibold whitespace-nowrap flex-shrink-0">
            <span class="text-gray-700">{{ dateYear }}</span>
            <span class="text-blue-600">{{ dateMonth }}</span>
            <span class="text-gray-700">{{ dateDay }}</span>
            <span class="text-purple-600 ml-2">{{ dateWeekday }}</span>
          </div>

          <!-- 右侧：搜索栏 + 操作按钮 -->
          <div class="flex items-center gap-2 flex-1 justify-end">
            <!-- 带图标的用户名输入框 -->
            <el-input
              v-model="searchForm.username"
              placeholder="用户名"
              size="small"
              :prefix-icon="UserIcon"
              class="w-28"
            />
            
            <el-date-picker
              v-model="searchForm.date"
              type="date"
              placeholder="选择日期"
              size="small"
              class="w-40"
            />

            <el-button size="small" type="primary" @click="handleSearch">
              <MagnifyingGlassIcon class="w-4 h-4 inline-block mr-1" />
              搜索
            </el-button>
            <el-button size="small" @click="handleReset">重置</el-button>

            <el-divider direction="vertical" class="h-6" />

            <el-button size="small" @click="handleExport">
              <ArrowDownTrayIcon class="w-4 h-4 inline-block mr-1" />
              导出
            </el-button>
            <el-button size="small" type="primary" @click="handleRefresh">
              <ArrowPathIcon class="w-4 h-4 inline-block mr-1" />
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 时间线布局 -->
      <el-timeline v-loading="loading" class="compact-timeline">
        <el-timeline-item
          v-for="item in groupedData"
          :key="item.id"
          :timestamp="formatTime(item.timestamp)"
          placement="top"
          size="large"
        >
          <!-- 记录卡片 -->
          <el-card class="event-card" shadow="hover" :body-style="{ padding: '12px 16px' }">
            <div class="flex items-start justify-between gap-4">
              <!-- 左侧信息 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <!-- 用户头像 -->
                  <el-avatar :size="32" class="bg-blue-500 flex-shrink-0">
                    <UserIcon class="w-4 h-4 text-white" />
                  </el-avatar>
                  
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-semibold">{{ item.username }}</span>
                      <span class="text-xs text-gray-500">
                        <CpuChipIcon class="w-3 h-3 inline-block" />
                        {{ item.machine_name }} · {{ item.drive_letter }}:
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 文件/文件夹信息 -->
                <div class="ml-9">
                  <div class="flex items-center gap-2 mb-1">
                    <component 
                      :is="item.is_folder ? FolderIcon : DocumentIcon" 
                      class="w-4 h-4 flex-shrink-0" 
                      :class="item.is_folder ? 'text-yellow-500' : 'text-blue-500'"
                    />
                    <span class="text-sm font-medium truncate">{{ item.file_name }}</span>
                    <el-tag :type="item.is_folder ? 'warning' : 'primary'" size="small">
                      {{ item.is_folder ? '文件夹' : '文件' }}
                    </el-tag>
                    <span class="text-xs text-gray-500">{{ formatSize(item.file_size) }}</span>
                  </div>

                  <!-- 文件夹展开按钮 -->
                  <div v-if="item.is_folder" class="mt-2">
                    <el-button 
                      size="small" 
                      type="primary"
                      text
                      @click="toggleFolder(item.id)"
                    >
                      <ChevronRightIcon 
                        class="w-3 h-3 inline-block transition-transform duration-200"
                        :class="{ 'rotate-90': expandedFolders.has(item.id) }"
                      />
                      {{ expandedFolders.has(item.id) ? '收起' : '查看' }}文件夹结构
                    </el-button>
                  </div>

                  <!-- 文件夹树形结构 -->
                  <el-collapse-transition>
                    <div v-if="item.is_folder && expandedFolders.has(item.id)" class="mt-3 p-3 bg-gray-50 rounded">
                      <el-tree
                        :data="getFolderTreeData(item)"
                        :props="treeProps"
                        default-expand-all
                        class="folder-tree"
                      >
                        <template #default="{ node, data }">
                          <span class="flex items-center gap-1.5 text-sm">
                            <component 
                              :is="data.isFolder ? FolderIcon : DocumentIcon" 
                              class="w-3.5 h-3.5 flex-shrink-0" 
                              :class="data.isFolder ? 'text-yellow-500' : 'text-gray-500'"
                            />
                            <span class="truncate">{{ node.label }}</span>
                            <span v-if="!data.isFolder" class="text-xs text-gray-400 flex-shrink-0">
                              ({{ formatSize(data.size) }})
                            </span>
                          </span>
                        </template>
                      </el-tree>
                    </div>
                  </el-collapse-transition>
                </div>
              </div>

              <!-- 右侧操作 -->
              <el-button size="small" text @click="handleDetail(item)">详情</el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <!-- 空状态 -->
      <el-empty v-if="!loading && groupedData.length === 0" description="暂无拷入记录" :image-size="80" />

      <!-- 分页 -->
      <div class="mt-4 flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          small
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { 
  MagnifyingGlassIcon, 
  ArrowDownTrayIcon, 
  ArrowPathIcon, 
  FolderIcon, 
  DocumentIcon,
  UserIcon,
  CpuChipIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

interface Event {
  id: number
  username: string
  file_name: string
  drive_letter: string
  file_size: number
  timestamp: string
  is_folder: boolean
  folder_structure?: string
  machine_name: string
}

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(3)
const expandedFolders = ref(new Set<number>())

// 模拟数据
const tableData = ref<Event[]>([
  {
    id: 1,
    username: '张三',
    file_name: '项目文档',
    drive_letter: 'H',
    file_size: 15728640, // 15MB
    timestamp: '2025-11-13T14:30:25',
    is_folder: true,
    folder_structure: JSON.stringify([
      {
        path: '',
        files: [
          { name: '需求文档.docx', size: 2097152, type: '.docx' },
          { name: '设计图.psd', size: 5242880, type: '.psd' }
        ],
        subfolders: ['前端代码', '后端代码', '数据库脚本']
      },
      {
        path: '前端代码',
        files: [
          { name: 'App.vue', size: 8192, type: '.vue' },
          { name: 'main.ts', size: 4096, type: '.ts' },
          { name: 'package.json', size: 2048, type: '.json' }
        ],
        subfolders: ['components', 'views']
      },
      {
        path: '前端代码/components',
        files: [
          { name: 'Header.vue', size: 6144, type: '.vue' },
          { name: 'Footer.vue', size: 4096, type: '.vue' }
        ],
        subfolders: []
      },
      {
        path: '前端代码/views',
        files: [
          { name: 'Home.vue', size: 10240, type: '.vue' },
          { name: 'About.vue', size: 8192, type: '.vue' }
        ],
        subfolders: []
      },
      {
        path: '后端代码',
        files: [
          { name: 'server.py', size: 15360, type: '.py' },
          { name: 'api.py', size: 12288, type: '.py' },
          { name: 'database.py', size: 8192, type: '.py' }
        ],
        subfolders: []
      },
      {
        path: '数据库脚本',
        files: [
          { name: 'init.sql', size: 4096, type: '.sql' },
          { name: 'update.sql', size: 2048, type: '.sql' }
        ],
        subfolders: []
      }
    ]),
    machine_name: 'DESKTOP-PC001'
  },
  {
    id: 2,
    username: '李四',
    file_name: '工作报告.pdf',
    drive_letter: 'G',
    file_size: 1048576, // 1MB
    timestamp: '2025-11-13T13:15:00',
    is_folder: false,
    machine_name: 'LAPTOP-WORK'
  },
  {
    id: 3,
    username: '王五',
    file_name: '图片素材',
    drive_letter: 'H',
    file_size: 52428800, // 50MB
    timestamp: '2025-11-13T11:45:30',
    is_folder: true,
    folder_structure: JSON.stringify([
      {
        path: '',
        files: [],
        subfolders: ['产品图', '宣传海报', 'Logo设计']
      },
      {
        path: '产品图',
        files: [
          { name: 'product_01.jpg', size: 3145728, type: '.jpg' },
          { name: 'product_02.jpg', size: 2621440, type: '.jpg' },
          { name: 'product_03.png', size: 4194304, type: '.png' }
        ],
        subfolders: []
      },
      {
        path: '宣传海报',
        files: [
          { name: 'poster_spring.psd', size: 15728640, type: '.psd' },
          { name: 'poster_summer.ai', size: 12582912, type: '.ai' }
        ],
        subfolders: []
      },
      {
        path: 'Logo设计',
        files: [
          { name: 'logo_v1.ai', size: 5242880, type: '.ai' },
          { name: 'logo_v2.svg', size: 524288, type: '.svg' },
          { name: 'logo_final.png', size: 2097152, type: '.png' }
        ],
        subfolders: []
      }
    ]),
    machine_name: 'DESIGN-STATION'
  }
])

const searchForm = reactive({
  username: '',
  date: new Date() // 默认当天
})

// 当前日期显示 - 分段显示以便着色
const dateYear = computed(() => {
  const date = searchForm.date || new Date()
  return new Date(date).getFullYear() + '年'
})

const dateMonth = computed(() => {
  const date = searchForm.date || new Date()
  return (new Date(date).getMonth() + 1) + '月'
})

const dateDay = computed(() => {
  const date = searchForm.date || new Date()
  return new Date(date).getDate() + '日'
})

const dateWeekday = computed(() => {
  const date = searchForm.date || new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekdays[new Date(date).getDay()]
})

// 树形结构配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 按时间分组的数据
const groupedData = computed(() => {
  return tableData.value
})

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const toggleFolder = (id: number) => {
  if (expandedFolders.value.has(id)) {
    expandedFolders.value.delete(id)
  } else {
    expandedFolders.value.add(id)
  }
}

const getFolderTreeData = (item: Event) => {
  if (!item.folder_structure) return []
  
  try {
    const structure = JSON.parse(item.folder_structure)
    return buildTreeData(structure)
  } catch (e) {
    console.error('解析文件夹结构失败:', e)
    return []
  }
}

const buildTreeData = (structure: any[]) => {
  const tree: any[] = []
  
  structure.forEach(folder => {
    const node: any = {
      label: folder.path || '根目录',
      isFolder: true,
      children: []
    }
    
    // 添加文件
    folder.files?.forEach((file: any) => {
      node.children.push({
        label: file.name,
        isFolder: false,
        size: file.size,
        type: file.type
      })
    })
    
    // 添加子文件夹
    folder.subfolders?.forEach((subfolder: string) => {
      node.children.push({
        label: subfolder,
        isFolder: true,
        children: []
      })
    })
    
    tree.push(node)
  })
  
  return tree
}

const handleSearch = () => {
  console.log('搜索', searchForm)
  // TODO: 调用API搜索
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.date = new Date()
}

const handleExport = () => {
  // TODO: 导出数据
}

const handleRefresh = () => {
  // TODO: 刷新数据
}

const handleDetail = (row: Event) => {
  console.log('查看详情', row)
}
</script>

<style scoped>
/* 紧凑时间线 */
.compact-timeline :deep(.el-timeline-item__wrapper) {
  padding-left: 24px;
}

.compact-timeline :deep(.el-timeline-item__tail) {
  left: 4px;
}

.compact-timeline :deep(.el-timeline-item__node) {
  left: 0;
}

.compact-timeline :deep(.el-timeline-item__timestamp) {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

/* 事件卡片 */
.event-card {
  border-radius: 8px;
  transition: all 0.3s;
  margin-bottom: 8px;
}

.event-card:hover {
  transform: translateY(-1px);
}

/* 文件树 */
.folder-tree :deep(.el-tree-node__content) {
  padding: 2px 0;
  height: auto;
  min-height: 24px;
}

.folder-tree :deep(.el-tree-node__label) {
  font-size: 13px;
}

.folder-tree :deep(.el-tree-node__expand-icon) {
  font-size: 12px;
}
</style>
