<script setup lang='ts'>
import type { CSSProperties } from 'vue'
import { computed, ref, watch } from 'vue'
import { NButton, NLayoutSider, NRadioButton, NRadioGroup } from 'naive-ui'
import List from './List.vue'
import Knowledge from './knowledge-base/index.vue'
import Footer from './Footer.vue'
import { useAppStore, useChatStore } from '@/store'
import { useBasicLayout } from '@/hooks/useBasicLayout'

const appStore = useAppStore()
const chatStore = useChatStore()

const { isMobile } = useBasicLayout()

const menu = ref(1)

const collapsed = computed(() => appStore.siderCollapsed)

function handleAdd() {
  menu.value = 1
  chatStore.addHistory({ title: 'New Chat', uuid: Date.now(), isEdit: false })
  if (isMobile.value)
    appStore.setSiderCollapsed(true)
}

function handleUpdateCollapsed() {
  appStore.setSiderCollapsed(!collapsed.value)
}

const getMobileClass = computed<CSSProperties>(() => {
  if (isMobile.value) {
    return {
      position: 'fixed',
      zIndex: 50,
    }
  }
  return {}
})

const mobileSafeArea = computed(() => {
  if (isMobile.value) {
    return {
      paddingBottom: 'env(safe-area-inset-bottom)',
    }
  }
  return {}
})

const songs = [
  {
    value: 1,
    label: '会话',
  },
  {
    value: 2,
    label: '模型',
  },
  {
    value: 3,
    label: '知识库',
  },
  {
    value: 4,
    label: '提示词',
  },
]
//
watch(
  isMobile,
  (val) => {
    appStore.setSiderCollapsed(val)
  },
  {
    immediate: true,
    flush: 'post',
  },
)
</script>

<template>
  <NLayoutSider
    :collapsed="collapsed"
    :collapsed-width="0"
    :width="260"
    :show-trigger="isMobile ? false : 'arrow-circle'"
    collapse-mode="transform"
    position="absolute"
    bordered
    :style="getMobileClass"
    @update-collapsed="handleUpdateCollapsed"
  >
    <Footer />
    <div class="flex flex-col h-full " :style="mobileSafeArea">
      <main class="flex flex-col flex-1 min-h-0">
        <div class="  flex justify-between">
          <NRadioGroup v-model:value="menu" name="radiobuttongroup1">
            <NRadioButton
              v-for="song in songs"
              :key="song.value"
              :value="song.value"
              :label="song.label"
            />
          </NRadioGroup>
        </div>

        <!-- 知识库界面 -->
        <div v-if="menu === 3">
          <div class="p-4">
            <Knowledge />
          </div>
        </div>
        <!-- 会话界面 -->
        <div v-if="menu === 1">
          <div class="p-4">
            <NButton block @click="handleAdd">
              新建聊天
            </NButton>
          </div>
          <div class="p-2 flex-1 min-h-0 pb-4 overflow-hidden">
            <List />
          </div>
        </div>
      </main>
    </div>
  </NLayoutSider>
  <template v-if="isMobile">
    <div v-show="!collapsed" class="fixed inset-0 z-40 w-full h-full bg-black/40" @click="handleUpdateCollapsed" />
  </template>
  <!-- <PromptStore v-model:visible="show" /> -->
</template>
