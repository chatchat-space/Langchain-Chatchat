import { Modal, type ModalProps } from '@lobehub/ui';
import { Form, Input, Select, FormInstance, message } from 'antd';
import { memo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Flexbox } from 'react-layout-kit';

import { useKnowledgeStore } from '@/store/knowledge'; 

const DEFAULT_FIELD_VALUE = {
  vector_store_type: "faiss",
  embed_model: "bge-large-zh-v1.5"
};
interface ModalCreateKnowledgeProps extends ModalProps {
  toggleModal: (open: boolean) => void;
}
const CreateKnowledgeBase = memo<ModalCreateKnowledgeProps>(({ toggleModal, open }) => {
  const [confirmLoading, setConfirmLoading] = useState(false);
  const { t } = useTranslation('chat');
  const antdFormInstance = useRef<FormInstance>();
  const [useFetchKnowledgeAdd, useFetchKnowledgeList] = useKnowledgeStore((s) => [
    s.useFetchKnowledgeAdd, s.useFetchKnowledgeList
  ]);
  const { mutate } = useFetchKnowledgeList()

  const onSubmit = async () => {
    if (!antdFormInstance.current) return;
    const fieldsError = await antdFormInstance.current.validateFields();
    if (fieldsError.length) return;
    const values = antdFormInstance.current.getFieldsValue(true);

    setConfirmLoading(true);
    const { code: resCode, data: resData, msg: resMsg } = await useFetchKnowledgeAdd({ ...values })
    setConfirmLoading(true);

    if (resCode !== 200) {
      message.error(resMsg)
      return;
    }
    mutate();
    toggleModal(false); 
  }

  return (
    <Modal
      allowFullscreen
      centered={false}
      maxHeight={false}
      onCancel={() => toggleModal(false)}
      onOk={onSubmit}
      open={open}
      title="创建知识库"
      confirmLoading={confirmLoading}
    >
      <Form initialValues={DEFAULT_FIELD_VALUE} layout="vertical" ref={antdFormInstance}>
        <Form.Item label="知识库名称" name="knowledge_base_name" rules={[{ required: true, message: '请输入知识库名称' }]}>
          <Input autoFocus />
        </Form.Item>
        <Form.Item label="知识库简介" name="kb_info">
          <Input />
        </Form.Item>
        <Flexbox direction="horizontal" gap={10} justify="space-between">
          <div style={{ flex: '1' }}>
            <Form.Item label="向量库类型" name="vector_store_type" rules={[{ required: true, message: '请选择向量库类型' }]}>
              <Select>
                <Select.Option value="faiss">faiss</Select.Option>
                <Select.Option value="milvus">milvus</Select.Option>
                <Select.Option value="zilliz">zilliz</Select.Option>
                <Select.Option value="pg">pg</Select.Option>
                <Select.Option value="es">es</Select.Option>
                <Select.Option value="chromadb">chromadb</Select.Option>
              </Select>
            </Form.Item>
          </div>
          <div style={{ flex: '1' }}>
            <Form.Item label="Embedding模型" name="embed_model" rules={[{ required: true, message: '请选择Embedding模型' }]}>
              <Select>
                <Select.Option value="bce-embedding-base_v1">bce-embedding-base_v1</Select.Option>
                <Select.Option value="bge-large-zh-v1.5">bge-large-zh-v1.5</Select.Option>
                <Select.Option value="text-embedding-v1">text-embedding-v1</Select.Option>
                <Select.Option value="Bert">Bert</Select.Option>
                <Select.Option value="Word2Vec">Word2Vec</Select.Option>
                <Select.Option value="FastText">FastText</Select.Option>
              </Select>
            </Form.Item>
          </div>
        </Flexbox>
      </Form>
    </Modal>
  );
});

export default CreateKnowledgeBase;
