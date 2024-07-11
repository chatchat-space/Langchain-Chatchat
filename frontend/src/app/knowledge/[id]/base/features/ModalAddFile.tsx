import { InboxOutlined } from '@ant-design/icons';
import { Form, Modal, Upload, InputNumber, Radio, message, Input } from 'antd';
import React, { memo, useState } from 'react';
import { useKnowledgeStore } from '@/store/knowledge';
import type { GetProp, UploadFile, UploadProps } from 'antd';
import type { KnowledgeUplodDocsParams } from '@/types/knowledge';

type ModalAddFileProps = {
  kbName: string;
  open: boolean;
  setModalOpen: (open: boolean) => void;
  setSelectedRowKeys: React.Dispatch<React.SetStateAction<string[]>>;

  selectedRowKeys: string[];
  isRebuildVectorDB?: boolean;
  initialValue?: KnowledgeUplodDocsParams;
};

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const ModalAddFile = memo<ModalAddFileProps>(({ open, setModalOpen, setSelectedRowKeys, selectedRowKeys, kbName, initialValue, isRebuildVectorDB }) => {
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [antdFormInstance] = Form.useForm();
  const [useFetchKnowledgeUploadDocs, useFetchKnowledgeFilesList, useFetcReAddVectorDB] = useKnowledgeStore((s) => [
    s.useFetchKnowledgeUploadDocs, s.useFetchKnowledgeFilesList,
    s.useFetcReAddVectorDB
  ]);
  const { mutate } = useFetchKnowledgeFilesList(kbName)
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const antdUploadProps: UploadProps = {
    name: "files",
    // multiple: true,
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

    if (isRebuildVectorDB) {
      // Re-add to vector library
      setConfirmLoading(true);
      await useFetcReAddVectorDB({
        ...values,
        "knowledge_base_name": kbName,
        "file_names": selectedRowKeys,
      }).catch(() => {
        message.error(`更新知识库失败`);
      })
      setConfirmLoading(false);
      setSelectedRowKeys([]);
      return;
    }

    if (!fileList.length) {
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
    formData.append('knowledge_base_name', kbName);

    try {
      setConfirmLoading(true);
      const { code: resCode, msg: resMsg } = await useFetchKnowledgeUploadDocs(formData)
      setConfirmLoading(false);

      if (resCode !== 200) {
        message.error(resMsg)
        return;
      }
      message.success(resMsg)
      mutate();
      setModalOpen(false);
    } catch (err) {
      message.error(`${err}`)
      setConfirmLoading(false);
    }
  }


  const layout = {
    labelCol: { span: 10 },
    wrapperCol: { span: 14 },
  }

  return (
    <Modal
      onCancel={() => setModalOpen(false)}
      open={open}
      title={isRebuildVectorDB ? "重新添加至向量库" : "添加文件"}
      onOk={onSubmit}
      confirmLoading={confirmLoading}
      width={600}
      destroyOnClose
      afterOpenChange={(open) => { 
        !open && setFileList([])
      }}
    >

      <Form
        name="validate_other"
        initialValues={{
          override: true,
          chunk_size: 250,
          chunk_overlap: 50,
          to_vector_store: true,
          ...initialValue
        }}
        form={antdFormInstance}
      >

        {!isRebuildVectorDB && <>
          <div style={{ padding: `24px 0px` }}>
            <Upload.Dragger {...antdUploadProps}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">单击或拖动文件到此区域进行上传</p>
              {/* <p className="ant-upload-hint">支持单个或批量上传。</p> */}
            </Upload.Dragger>
          </div>
          <Form.Item name="override" label="覆盖已有文件" {...layout}>
            <Radio.Group>
              <Radio value={true}>是</Radio>
              <Radio value={false}>否</Radio>
            </Radio.Group>
          </Form.Item>
        </>}

        <Form.Item name="to_vector_store" label="进行向量化" {...layout}>
          <Radio.Group>
            <Radio value={true}>是</Radio>
            <Radio value={false}>否</Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item name="zh_title_enhance" label="开启中文标题加强" {...layout}>
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

        <Form.Item name="chunk_size" label="单段文本最大长度" {...layout} {...layout}>
          <InputNumber min={0} style={{ width: 200 }} />
        </Form.Item>

        <Form.Item name="chunk_overlap" label="相邻文本重合长度" {...layout} {...layout}>
          <InputNumber min={0} style={{ width: 200 }} />
        </Form.Item>
        {/* <Form.Item name="docs" label="自定义的docs" {...layout} {...layout}>
          <Input style={{ width: 200 }} />
        </Form.Item> */}
      </Form>
    </Modal>
  );
});

export default ModalAddFile;
