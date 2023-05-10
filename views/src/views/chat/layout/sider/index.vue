<script setup lang='ts'>
import type { CSSProperties } from 'vue'
import { computed, ref, watch } from 'vue'
import { NButton, NLayoutSider, NUpload } from 'naive-ui'
import List from './List.vue'
import filelist from './filelist.vue'
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
          <NButton dashed @click="menu = 1">
            会话
          </NButton>
          <NButton dashed @click="menu = 2">
            模型
          </NButton>
          <NButton dashed @click="menu = 3">
            知识库
          </NButton>
          <NButton dashed @click="menu = 4">
            提示词
          </NButton>
        </div>

        <!-- 知识库界面 -->
        <div v-if="menu === 3">
          <div class="p-4">
            <NUpload
              action="http://127.0.0.1:1002/api/chat-docs/uploadone"
              :headers="{
                'naive-info': 'hello!',
              }"
              :data="{
                knowledge_base_id: '123',
              }"
            >
              <NButton block>
                文件上传
              </NButton>
            </NUpload>
          </div>
          <div class="p-2 flex-1 min-h-0 pb-4 overflow-hidden">
            <filelist />
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
        <!--  <div class="p-4">
          <NButton block @click="show = true">
            {{ $t('store.siderButton') }}
          </NButton>
        </div> -->
      </main>
    </div>
  </NLayoutSider>
  <template v-if="isMobile">
    <div v-show="!collapsed" class="fixed inset-0 z-40 w-full h-full bg-black/40" @click="handleUpdateCollapsed" />
  </template>
  <!-- <PromptStore v-model:visible="show" /> -->
</template>
