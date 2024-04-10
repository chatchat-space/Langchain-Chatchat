import { Form, type ItemGroup } from '@lobehub/ui';
import { Form as AntForm, Input } from 'antd';
import { AppWindow } from 'lucide-react';
import { memo, useCallback } from 'react';

import { FORM_STYLE } from '@/const/layoutTokens';

// 参考settings/llm/Anthropic/index.tsx的代码生成一个名为KnowledgeBaseConfig.tsx的表单组件
const KnowledgeBaseConfig = memo(() => {
  const [form] = AntForm.useForm();

  const handleConfigChange = useCallback(() => {
    console.log(321);
  }, []);
  const system: ItemGroup = {
    children: [
      {
        children: <Input placeholder={'321'} />,
        desc: '知识库名称321',
        label: '知识库名称',
        name: 'password',
      },
    ],
    icon: AppWindow,
    title: '321',
  };

  return <Form form={form} items={[system]} onValuesChange={handleConfigChange} {...FORM_STYLE} />;
});

export default KnowledgeBaseConfig;
