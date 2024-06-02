import { InboxOutlined } from '@ant-design/icons'; 
import { Form, Modal, Upload, InputNumber, Radio, message } from 'antd';
import React, { memo, useState } from 'react';
import { useKnowledgeStore } from '@/store/knowledge';
import type { GetProp, UploadFile, UploadProps } from 'antd';
 
type ModalAddFileProps = {
  kbName: string;
  open: boolean;
  setModalOpen: (open: boolean) => void;
};
 
type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const ModalAddFile = memo<ModalAddFileProps>(({ open, setModalOpen, kbName }) => {
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [antdFormInstance] = Form.useForm();
  const [useFetchKnowledgeUploadDocs, useFetchKnowledgeFilesList] = useKnowledgeStore((s) => [
    s.useFetchKnowledgeUploadDocs, s.useFetchKnowledgeFilesList
  ]);
  const { mutate } = useFetchKnowledgeFilesList(kbName)
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const antdUploadProps: UploadProps = {
    name: "files",
    onRemove: (file) => {
      const index = fileList.indexOf(file);
      const newFileList = fileList.slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
    },
    beforeUpload: (file) => {
      setFileList([...fileList, file]);
      return false;
    },
    fileList,
  };

  const onSubmit = async () => {
    if (!antdFormInstance) return;
    const fieldsError = await antdFormInstance.validateFields();
    if (fieldsError.length) return;
    const values = antdFormInstance.getFieldsValue(true);
    if(!fileList.length){
      message.error('请选择文件')
      return;
    }

    const formData = new FormData();
    fileList.forEach((file) => {
      formData.append('files', file as FileType);
    });
    for (const key in values) { 
      formData.append(key, values[key]);
    }
    formData.append('knowledge_base_name',  kbName);
    
    setConfirmLoading(true);
    const { code: resCode, data: resData, msg: resMsg } = await useFetchKnowledgeUploadDocs(formData)
    setConfirmLoading(true);

    if (resCode !== 200) {
      message.error(resMsg)
      return;
    }
    message.success(resMsg)
    mutate();
    setModalOpen(false);
  }
 

  const layout = {
    labelCol: { span: 10 },
    wrapperCol: { span: 14 },
  }

  return (
    <Modal
      onCancel={() => setModalOpen(false)}
      open={open} title="添加文件"
      onOk={onSubmit}
      confirmLoading={confirmLoading}
      width={600}
    > 

      <Form
        name="validate_other"
        initialValues={{
          override: true,
          chunk_size: 0,
          chunk_overlap: 0,
          to_vector_store: true,
        }}
        form={antdFormInstance}
      >
 
        <div style={{ padding: `24px 0px` }}>
          <Upload.Dragger {...antdUploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">单击或拖动文件到此区域进行上传</p>
            <p className="ant-upload-hint">支持单个或批量上传。</p>
          </Upload.Dragger>
        </div> 

        <Form.Item name="override" label="覆盖已有文件" {...layout}>
          <Radio.Group>
            <Radio value={true}>是</Radio>
            <Radio value={false}>否</Radio>
          </Radio.Group>
        </Form.Item>

        <Form.Item name="to_vector_store" label="上传文件后是否进行向量化" {...layout}>
          <Radio.Group>
            <Radio value={true}>是</Radio>
            <Radio value={false}>否</Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item name="zh_title_enhance" label="是否开启中文标题加强" {...layout}>
          <Radio.Group>
            <Radio value={true}>是</Radio>
            <Radio value={false}>否</Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item name="not_refresh_vs_cache" label="暂不保存向量库（用于FAISS）" {...layout}>
          <Radio.Group>
            <Radio value={true}>是</Radio>
            <Radio value={false}>否</Radio>
          </Radio.Group>
        </Form.Item>


        <Form.Item label="知识库中单段文本最大长度" {...layout} {...layout}>
          <Form.Item name="chunk_size">
            <InputNumber min={0} />
          </Form.Item>
        </Form.Item>

        <Form.Item label="知识库中相邻文本重合长度" {...layout} {...layout}>
          <Form.Item name="chunk_overlap">
            <InputNumber min={0} />
          </Form.Item>
        </Form.Item>
        {/* <Form.Item label="自定义的docs">
          <Form.Item name="docs">
            <Input />
          </Form.Item> 
        </Form.Item> */}

      </Form>
    </Modal>
  );
});

export default ModalAddFile;
