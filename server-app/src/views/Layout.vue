<template>
  <div>
    <!-- Mobile sidebar -->
    <TransitionRoot as="template" :show="sidebarOpen">
      <Dialog class="relative z-50 lg:hidden" @close="sidebarOpen = false">
        <TransitionChild
          as="template"
          enter="transition-opacity ease-linear duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="transition-opacity ease-linear duration-300"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-900/80" />
        </TransitionChild>

        <div class="fixed inset-0 flex">
          <TransitionChild
            as="template"
            enter="transition ease-in-out duration-300 transform"
            enter-from="-translate-x-full"
            enter-to="translate-x-0"
            leave="transition ease-in-out duration-300 transform"
            leave-from="translate-x-0"
            leave-to="-translate-x-full"
          >
            <DialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
              <TransitionChild
                as="template"
                enter="ease-in-out duration-300"
                enter-from="opacity-0"
                enter-to="opacity-100"
                leave="ease-in-out duration-300"
                leave-from="opacity-100"
                leave-to="opacity-0"
              >
                <div class="absolute left-full top-0 flex w-16 justify-center pt-5">
                  <button type="button" class="-m-2.5 p-2.5" @click="sidebarOpen = false">
                    <span class="sr-only">关闭侧边栏</span>
                    <XMarkIcon class="h-6 w-6 text-white" aria-hidden="true" />
                  </button>
                </div>
              </TransitionChild>

              <!-- Mobile sidebar content -->
              <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-gray-900 px-6 pb-4 ring-1 ring-white/10">
                <div class="flex h-16 shrink-0 items-center gap-3">
                  <MagnifyingGlassIcon class="h-8 w-8 text-blue-400" />
                  <h1 class="text-xl font-bold text-white">USB监控系统</h1>
                </div>
                <nav class="flex flex-1 flex-col">
                  <ul role="list" class="flex flex-1 flex-col gap-y-7">
                    <li>
                      <ul role="list" class="-mx-2 space-y-2">
                        <li v-for="item in navigation" :key="item.name">
                          <a
                            :href="item.href"
                            @click.prevent="router.push(item.href)"
                            :class="[
                              item.current
                                ? 'bg-white/5 text-white'
                                : 'text-gray-400 hover:bg-white/5 hover:text-white',
                              'group flex gap-x-3 rounded-md p-3 text-sm font-semibold leading-6'
                            ]"
                          >
                            <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                            {{ item.name }}
                          </a>
                        </li>
                      </ul>
                    </li>
                    <!-- 底部功能区 -->
                    <li class="mt-auto">
                      <div class="mb-4 border-t border-white/10 pt-4">
                        <a
                          href="#"
                          class="group -mx-2 flex gap-x-3 rounded-md p-3 text-sm font-semibold leading-6 text-gray-400 hover:bg-white/5 hover:text-white"
                        >
                          <CogIcon class="h-6 w-6 shrink-0" aria-hidden="true" />
                          系统设置
                        </a>
                      </div>
                    </li>
                  </ul>
                </nav>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Desktop sidebar (collapsible) -->
    <div
      :class="[
        'hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:flex-col bg-gray-900 ring-1 ring-white/10 transition-all duration-300 ease-in-out',
        isCollapse ? 'lg:w-16' : 'lg:w-72'
      ]"
    >
      <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-black/10 px-6 pb-4">
        <div class="flex h-16 shrink-0 items-center justify-center overflow-hidden">
          <transition
            enter-active-class="transition-opacity duration-300 delay-150"
            leave-active-class="transition-opacity duration-150"
            enter-from-class="opacity-0"
            enter-to-class="opacity-100"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
          >
            <div v-if="!isCollapse" class="flex items-center gap-3">
              <MagnifyingGlassIcon class="h-8 w-8 text-blue-400" />
              <h1 class="text-xl font-bold text-white whitespace-nowrap">USB监控系统</h1>
            </div>
            <MagnifyingGlassIcon v-else class="h-6 w-6 text-blue-400" />
          </transition>
        </div>
        <nav class="flex flex-1 flex-col">
          <ul role="list" class="flex flex-1 flex-col gap-y-7">
            <li>
              <ul role="list" class="-mx-2 space-y-2">
                <li v-for="item in navigation" :key="item.name">
                  <a
                    :href="item.href"
                    @click.prevent="router.push(item.href)"
                    :class="[
                      item.current
                        ? 'bg-white/5 text-white'
                        : 'text-gray-400 hover:bg-white/5 hover:text-white',
                      'group flex gap-x-3 rounded-md p-3 text-sm font-semibold leading-6 overflow-hidden',
                      isCollapse ? 'justify-center' : ''
                    ]"
                    :title="isCollapse ? item.name : ''"
                  >
                    <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                    <span
                      :class="[
                        'whitespace-nowrap transition-all duration-300 ease-in-out',
                        isCollapse ? 'opacity-0 w-0' : 'opacity-100 w-auto'
                      ]"
                    >
                      {{ item.name }}
                    </span>
                  </a>
                </li>
              </ul>
            </li>
            <!-- 底部功能区 -->
            <li class="mt-auto">
              <div :class="['border-t border-white/10 pt-4', isCollapse ? '' : 'mb-4']">
                <a
                  href="#"
                  :class="[
                    'group -mx-2 flex gap-x-3 rounded-md p-3 text-sm font-semibold leading-6 text-gray-400 hover:bg-white/5 hover:text-white overflow-hidden',
                    isCollapse ? 'justify-center' : ''
                  ]"
                  :title="isCollapse ? '系统设置' : ''"
                >
                  <CogIcon class="h-6 w-6 shrink-0" aria-hidden="true" />
                  <span
                    :class="[
                      'whitespace-nowrap transition-all duration-300 ease-in-out',
                      isCollapse ? 'opacity-0 w-0' : 'opacity-100 w-auto'
                    ]"
                  >
                    系统设置
                  </span>
                </a>
              </div>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Main content -->
    <div :class="['transition-all duration-300', isCollapse ? 'lg:pl-16' : 'lg:pl-72']">
      <!-- Top header -->
      <div class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
        <!-- Mobile menu button -->
        <button
          type="button"
          class="-m-2.5 p-2.5 text-gray-700 hover:text-gray-900 lg:hidden"
          @click="sidebarOpen = true"
        >
          <span class="sr-only">打开侧边栏</span>
          <Bars3Icon class="h-6 w-6" aria-hidden="true" />
        </button>

        <!-- Desktop collapse button -->
        <button
          type="button"
          class="hidden lg:block -m-2.5 p-2.5 text-gray-700 hover:text-gray-900"
          @click="toggleCollapse"
        >
          <span class="sr-only">{{ isCollapse ? '展开' : '收缩' }}侧边栏</span>
          <component
            :is="isCollapse ? ChevronDoubleRightIcon : ChevronDoubleLeftIcon"
            class="h-5 w-5"
          />
        </button>

        <!-- Separator -->
        <div class="h-6 w-px bg-gray-900/10" aria-hidden="true" />

        <div class="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
          <div class="flex flex-1 items-center">
            <div class="text-xl font-semibold text-gray-800">
              {{ currentTitle }}
            </div>
          </div>
          <div class="flex items-center gap-x-4 lg:gap-x-6">
            <!-- Notifications -->
            <button type="button" class="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 relative">
              <span class="sr-only">查看通知</span>
              <BellIcon class="h-6 w-6" aria-hidden="true" />
              <span class="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
            </button>

            <!-- Separator -->
            <div class="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-900/10" aria-hidden="true" />

            <!-- Profile dropdown -->
            <Menu as="div" class="relative">
              <MenuButton class="flex items-center gap-2">
                <span class="sr-only">打开用户菜单</span>
                <div class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-500">
                  <UserIcon class="h-5 w-5 text-white" />
                </div>
                <span class="hidden lg:flex lg:items-center">
                  <span class="text-sm font-semibold text-gray-900">管理员</span>
                  <ChevronDownIcon class="ml-2 h-5 w-5 text-gray-400" aria-hidden="true" />
                </span>
              </MenuButton>
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="absolute right-0 z-10 mt-2.5 w-48 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                  <MenuItem v-slot="{ active }">
                    <a
                      href="#"
                      :class="[
                        active ? 'bg-gray-50' : '',
                        'flex items-center gap-2 px-3 py-2 text-sm text-gray-900'
                      ]"
                    >
                      <CogIcon class="h-4 w-4" />
                      <span>个人设置</span>
                    </a>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <a
                      href="#"
                      :class="[
                        active ? 'bg-gray-50' : '',
                        'flex items-center gap-2 px-3 py-2 text-sm text-gray-900'
                      ]"
                    >
                      <ArrowRightOnRectangleIcon class="h-4 w-4" />
                      <span>退出登录</span>
                    </a>
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>
        </div>
      </div>

      <!-- Main content area -->
      <main class="bg-gray-50 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Dialog,
  DialogPanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot
} from '@headlessui/vue'
import {
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  UsersIcon,
  DocumentTextIcon,
  CpuChipIcon,
  BellIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon
} from '@heroicons/vue/24/outline'
import { CogIcon } from '@heroicons/vue/24/solid'
import { ChevronDownIcon } from '@heroicons/vue/20/solid'
// Element Plus components kept for future use
// import ElementPlus components if needed

const router = useRouter()
const route = useRoute()

const sidebarOpen = ref(false)
const isCollapse = ref(false)
const currentTitle = computed(() => (route.meta.title as string) || '数据概览')

const navigation = computed(() => [
  {
    name: '数据概览',
    href: '/dashboard',
    icon: ChartBarIcon,
    current: route.path === '/dashboard'
  },
  {
    name: '拷入记录',
    href: '/events',
    icon: DocumentTextIcon,
    current: route.path === '/events'
  },
  {
    name: '人员管理',
    href: '/users',
    icon: UsersIcon,
    current: route.path === '/users'
  },
  {
    name: 'USB设备',
    href: '/devices',
    icon: CpuChipIcon,
    current: route.path === '/devices'
  }
])

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
/* Custom styles if needed */
</style>
