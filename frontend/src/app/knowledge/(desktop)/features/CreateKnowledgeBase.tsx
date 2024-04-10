import { Modal, type ModalProps } from '@lobehub/ui';
import { Form, Input, Select } from 'antd';
import { memo } from 'react';
import { useTranslation } from 'react-i18next';
import { Flexbox } from 'react-layout-kit';

// export const imageTypeOptions: SegmentedProps['options'] = [
//   {
//     label: 'JPG',
//     value: ImageType.JPG,
//   },
//   {
//     label: 'PNG',
//     value: ImageType.PNG,
//   },
//   {
//     label: 'SVG',
//     value: ImageType.SVG,
//   },
//   {
//     label: 'WEBP',
//     value: ImageType.WEBP,
//   },
// ];

const DEFAULT_FIELD_VALUE = {
  // imageType: ImageType.JPG,
  withBackground: true,
  withFooter: false,
  withPluginInfo: false,
  withSystemRole: false,
};

const CreateKnowledgeBase = memo<ModalProps>(({ onClose, open }) => {
  const { t } = useTranslation('chat');

  return (
    <Modal
      allowFullscreen
      centered={false}
      maxHeight={false}
      onCancel={onClose}
      onOk={onClose}
      open={open}
      title="创建知识库"
    >
      <Form initialValues={DEFAULT_FIELD_VALUE} layout="vertical">
        <Form.Item label="知识库名称" name="base_name">
          <Input />
        </Form.Item>
        <Form.Item label="知识库简介" name="base_intro">
          <Input />
        </Form.Item>
        <Flexbox direction="horizontal" gap={10} justify="space-between">
          <div style={{ flex: '1' }}>
            <Form.Item label="向量库类型" name="base_type">
              <Select>
                <Select.Option value="0">文本</Select.Option>
                <Select.Option value="1">图片</Select.Option>
              </Select>
            </Form.Item>
          </div>
          <div style={{ flex: '1' }}>
            <Form.Item label="Embedding模型" name="embedding_model">
              <Select>
                <Select.Option value="0">Bert</Select.Option>
                <Select.Option value="1">Word2Vec</Select.Option>
                <Select.Option value="2">FastText</Select.Option>
              </Select>
            </Form.Item>
          </div>
        </Flexbox>
      </Form>
    </Modal>
  );
});

export default CreateKnowledgeBase;
