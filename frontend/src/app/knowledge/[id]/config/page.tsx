'use client';

import { Form, type ItemGroup } from '@lobehub/ui';
import { Form as AntForm, Button, Input, InputNumber, Switch } from 'antd';
import { Settings } from 'lucide-react';
import { memo, useCallback } from 'react';
import { Flexbox } from 'react-layout-kit';

import { FORM_STYLE } from '@/const/layoutTokens';

const KnowledgeBaseConfig = memo(() => {
  const [form] = AntForm.useForm();

  const handleConfigChange = useCallback(async () => {
    try {
      const values = await form.validateFields();
      console.log('Success:', values);
    } catch (errorInfo) {
      console.log('Failed:', errorInfo);
    }
  }, [form]);
  const system: ItemGroup = {
    children: [
      {
        children: <Input placeholder={'请为知识库命名'} />,
        label: '知识库名称',
        name: 'name',
        rules: [{ message: '请输入知识库名称', required: true }],
      },
      {
        children: <Input.TextArea placeholder={'请简单介绍你的知识库'} />,
        label: '知识库简介',
        name: 'intro',
        rules: [{ message: '请输入知识库简介', required: true }],
      },
      {
        children: <InputNumber placeholder={'请输入数字'} style={{ width: 200 }} />,
        label: '单段文本最大长度',
        name: 'paragraphMaxLength',
        rules: [{ message: '请输入知识库名称', required: true }],
      },
      {
        children: <InputNumber placeholder={'请输入数字'} style={{ width: 200 }} />,
        label: '相邻文本重合长度',
        name: 'paragraphOverlapLength',
        rules: [{ message: '请输入知识库名称', required: true }],
      },
      {
        children: <InputNumber style={{ width: 200 }} />,
        label: '文本匹配条数',
        name: 'paragraphMatchCount',
        rules: [{ message: '请输入知识库名称', required: true }],
      },
      {
        children: <Switch style={{ width: 50 }} />,
        label: '开启中文标题加强',
        name: 'chineseTitleEnhance',
      },
    ],
    icon: Settings,
    title: '知识库设置',
  };

  return (
    <>
      <Form form={form} items={[system]} onValuesChange={handleConfigChange} {...FORM_STYLE} />
      <Flexbox padding={50}>
        <Button size="large" style={{ width: 400 }}>
          保存
        </Button>
      </Flexbox>
    </>
  );
});

export default KnowledgeBaseConfig;
