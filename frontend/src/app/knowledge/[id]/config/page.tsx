'use client';

import { Form, type ItemGroup } from '@lobehub/ui';
import { Form as AntForm, Input, InputNumber, Slider, Switch } from 'antd';
import { Settings } from 'lucide-react';
import { memo, useCallback } from 'react';

import { FORM_STYLE } from '@/const/layoutTokens';

const KnowledgeBaseConfig = memo(() => {
  const [form] = AntForm.useForm();

  const handleConfigChange = useCallback(() => {
    console.log(321);
  }, []);
  const system: ItemGroup = {
    children: [
      {
        children: <Input placeholder={'请为知识库命名'} />,
        desc: '名称',
        label: '知识库名称',
        name: 'name',
      },
      {
        children: <Input.TextArea placeholder={'请简单介绍你的知识库'} />,
        desc: '简介',
        label: '知识库简介',
        name: 'intro',
      },
      {
        children: <InputNumber placeholder={'请输入数字'} style={{ width: 200 }} />,
        desc: '321',
        label: '单段文本最大长度',
        name: 'paragraphMaxLength',
      },
      {
        children: <InputNumber placeholder={'请输入数字'} style={{ width: 200 }} />,
        desc: '321',
        label: '相邻文本重合长度',
        name: 'paragraphOverlapLength',
      },
      {
        children: <Slider style={{ width: 100 }} />,
        desc: '321',
        label: '文本匹配条数',
        name: 'paragraphMatchCount',
      },
      {
        children: <Switch style={{ width: 100 }} />,
        desc: '321',
        label: '开启中文标题加强',
        name: 'chineseTitleEnhance',
      },
    ],
    icon: Settings,
    title: '知识库设置',
  };

  return <Form form={form} items={[system]} onValuesChange={handleConfigChange} {...FORM_STYLE} />;
});

export default KnowledgeBaseConfig;
