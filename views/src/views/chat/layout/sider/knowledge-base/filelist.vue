<script setup lang='ts'>
import { onMounted, ref, toRef } from 'vue'
import { NInput, NP, NPopconfirm, NScrollbar, NText, NUpload, NUploadDragger } from 'naive-ui'
import { SvgIcon } from '@/components/common'
import { useChatStore } from '@/store'
import { deletefile, getfilelist, setapi, web_url } from '@/api/chat'
const knowledge = defineProps({
  knowledgebaseid: {
    type: String, // 类型字符串
  },
})
const knowledge_base_id = toRef(knowledge, 'knowledgebaseid')

const chatStore = useChatStore()
const dataSources = ref<any>([])

onMounted(async () => {
  const res = await getfilelist(knowledge_base_id.value)
  dataSources.value = res.data.data
})

/* function handleEdit({ uuid }: Chat.History, isEdit: boolean, event?: MouseEvent) {
  event?.stopPropagation()
  chatStore.updateHistory(uuid, { isEdit })
} */

async function handleDelete(item: any) {
  /* const mid =  */await deletefile({ knowledge_base_id: knowledge_base_id.value, doc_name: item })
  const res = await getfilelist(knowledge_base_id.value)
  dataSources.value = res.data.data
}

function handleEnter({ uuid }: Chat.History, isEdit: boolean, event: KeyboardEvent) {
  event?.stopPropagation()
  if (event.key === 'Enter')
    chatStore.updateHistory(uuid, { isEdit })
}
</script>

<template>
  <NUpload
    multiple
    directory-dnd
    :action="setapi() === undefined ? `${web_url()}/api/local_doc_qa/upload_file` : `${setapi()}local_doc_qa/upload_file`"
    :headers="{
      'naive-info': 'hello!',
    }"
    :data="{
      knowledge_base_id: knowledge.knowledgebaseid as string,
    }"
  >
    <NUploadDragger>
      <NText style="font-size: 16px">
        点击或者拖动文件到该区域来上传
      </NText>
      <NP depth="3" style="margin: 8px 0 0 0">
        在弹出的文件选择框，按住ctrl或shift进行多选
      </NP>
    </NUploadDragger>
  </NUpload>
  <NScrollbar class="px-4">
    <div class="flex flex-col gap-2 text-sm">
      <template v-if="!dataSources.length">
        <div class="flex flex-col items-center mt-4 text-center text-neutral-300">
          <SvgIcon icon="ri:inbox-line" class="mb-2 text-3xl" />
          <span>{{ $t('common.noData') }}</span>
        </div>
      </template>
      <template v-else>
        <div v-for="(item, index) of dataSources" :key="index" class="flex items-center">
          <a
            style="width:90%"
            class="relative flex items-center gap-3 px-3 py-3 break-all border rounded-md cursor-pointer hover:bg-neutral-100 group dark:border-neutral-800 dark:hover:bg-[#24272e]"
          >
            <span>
              <SvgIcon icon="ri:message-3-line" />
            </span>
            <div class="relative flex-1 overflow-hidden break-all text-ellipsis whitespace-nowrap">
              <NInput
                v-if="item.isEdit"
                v-model:value="item.title" size="tiny"
                @keypress="handleEnter(item, false, $event)"
              />
              <span v-else>{{ item }}</span>
            </div>

          </a>
          <div class="absolute z-10 flex visible right-1">
            <template v-if="item.isEdit">
              <!-- <button class="p-1" @click="handleEdit(item, false, $event)">
                  <SvgIcon icon="ri:save-line" />
                </button> -->
            </template>
            <template v-else>
              <!--  <button class="p-1">
                  <SvgIcon icon="ri:edit-line" @click="handleEdit(item, true, $event)" />
                </button> -->
              <NPopconfirm placement="bottom" @positive-click="handleDelete(item)">
                <template #trigger>
                  <button class="p-1">
                    <SvgIcon icon="ri:delete-bin-line" />
                  </button>
                </template>
                确定删除此文件？
              </NPopconfirm>
            </template>
          </div>
        </div>
      </template>
    </div>
  </NScrollbar>
</template>
