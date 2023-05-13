<script setup lang='ts'>
import { NButton, NForm, NFormItem, NInput } from 'naive-ui'
import { onMounted, ref } from 'vue'
import filelist from './filelist.vue'
import { getfilelist } from '@/api/chat'
const items = ref<any>([])
onMounted(async () => {
  const res = await getfilelist({})
  res.data.data.forEach((item: any) => {
    items.value.push({
      value: item,
      show: false,
    })
  })
})
const formValue = ref({
  user: {
    name: '',
  },
})
const rules = {
  user: {
    name: {
      required: true,
      message: '请输入名称',
      trigger: 'blur',
    },
  },
}
const handleValidateClick = (item: any) => {
  items.value.forEach((res: { value: any; show: boolean }) => {
    if (res.value === item)
      res.show = !res.show
  },

  )
}
const handleClick = () => {
  if (formValue.value.user.name.trim() !== '') {
    items.value.push({
      value: formValue.value.user.name.trim(),
      show: false,
    })
  }
}
</script>

<template>
  <NForm
    ref="formRef"
    inline
    :label-width="80"
    :model="formValue"
    :rules="rules"
  >
    <NFormItem label="" path="user.name">
      <NInput v-model:value="formValue.user.name" placeholder="起个知识库名吧！" />
    </NFormItem>
    <NFormItem>
      <NButton attr-type="button" @click="handleClick">
        新增
      </NButton>
    </NFormItem>
  </NForm>
  <div v-for="item in items" :key="item.value">
    <NButton block size="large" @click="handleValidateClick(item.value)">
      {{ item.value }}
    </NButton>
    <div v-if="item.show" class="p-2 flex-1 min-h-0 pb-4 overflow-hidden">
      <filelist v-if="item.value" :knowledgebaseid="item.value" />
    </div>
    <br>
  </div>
</template>
