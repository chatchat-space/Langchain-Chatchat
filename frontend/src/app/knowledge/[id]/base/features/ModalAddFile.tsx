import { InboxOutlined } from '@ant-design/icons';
import { Form, InputNumber, Modal, Radio, Upload, message } from 'antd';
import type { GetProp, UploadFile, UploadProps } from 'antd';
import React, { memo, useState } from 'react';

import { useKnowledgeStore } from '@/store/knowledge';
import type { KnowledgeUplodDocsParams } from '@/types/knowledge';

type ModalAddFileProps = {
  initialValue?: KnowledgeUplodDocsParams;
  isRebuildVectorDB?: boolean;
  kbName: string;
  open: boolean;

  selectedRowKeys: string[];
  setModalOpen: (open: boolean) => void;
  setSelectedRowKeys: React.Dispatch<React.SetStateAction<string[]>>;
};

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const ModalAddFile = memo<ModalAddFileProps>(
  ({
    open,
    setModalOpen,
    setSelectedRowKeys,
    selectedRowKeys,
    kbName,
    initialValue,
    isRebuildVectorDB,
  }) => {
    const [confirmLoading, setConfirmLoading] = useState(false);
    const [antdFormInstance] = Form.useForm();
    const [useFetchKnowledgeUploadDocs, useFetchKnowledgeFilesList, useFetcReAddVectorDB] =
      useKnowledgeStore((s) => [
        s.useFetchKnowledgeUploadDocs,
        s.useFetchKnowledgeFilesList,
        s.useFetcReAddVectorDB,
      ]);
    const { mutate } = useFetchKnowledgeFilesList(kbName);
    const [fileList, setFileList] = useState<UploadFile[]>([]);

    const antdUploadProps: UploadProps = {
      beforeUpload: (file) => {
        setFileList([...fileList, file]);
        return false;
      },
      
      fileList,
      
name: 'files',
      // multiple: true,
onRemove: (file) => {
        const index = fileList.indexOf(file);
        const newFileList = fileList.slice();
        newFileList.splice(index, 1);
        setFileList(newFileList);
      },
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
          file_names: selectedRowKeys,
          knowledge_base_name: kbName,
        }).catch(() => {
          message.error(`更新知识库失败`);
        });
        setConfirmLoading(false);
        setSelectedRowKeys([]);
        return;
      }

      if (!fileList.length) {
        message.error('请选择文件');
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
        const { code: resCode, msg: resMsg } = await useFetchKnowledgeUploadDocs(formData);
        setConfirmLoading(false);

        if (resCode !== 200) {
          message.error(resMsg);
          return;
        }
        message.success(resMsg);
        mutate();
        setModalOpen(false);
      } catch (err) {
        message.error(`${err}`);
        setConfirmLoading(false);
      }
    };

    const layout = {
      labelCol: { span: 10 },
      wrapperCol: { span: 14 },
    };

    return (
      <Modal
        afterOpenChange={(open) => {
          !open && setFileList([]);
        }}
        confirmLoading={confirmLoading}
        destroyOnClose
        onCancel={() => setModalOpen(false)}
        onOk={onSubmit}
        open={open}
        title={isRebuildVectorDB ? '重新添加至向量库' : '添加文件'}
        width={600}
      >
        <Form
          form={antdFormInstance}
          initialValues={{
            chunk_overlap: 50,
            chunk_size: 250,
            override: true,
            to_vector_store: true,
            ...initialValue,
          }}
          name="validate_other"
        >
          {!isRebuildVectorDB && (
            <>
              <div style={{ padding: `24px 0px` }}>
                <Upload.Dragger {...antdUploadProps}>
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">单击或拖动文件到此区域进行上传</p>
                  {/* <p className="ant-upload-hint">支持单个或批量上传。</p> */}
                </Upload.Dragger>
              </div>
              <Form.Item label="覆盖已有文件" name="override" {...layout}>
                <Radio.Group>
                  <Radio value={true}>是</Radio>
                  <Radio value={false}>否</Radio>
                </Radio.Group>
              </Form.Item>
            </>
          )}

          <Form.Item label="进行向量化" name="to_vector_store" {...layout}>
            <Radio.Group>
              <Radio value={true}>是</Radio>
              <Radio value={false}>否</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item label="开启中文标题加强" name="zh_title_enhance" {...layout}>
            <Radio.Group>
              <Radio value={true}>是</Radio>
              <Radio value={false}>否</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item label="暂不保存向量库（用于FAISS）" name="not_refresh_vs_cache" {...layout}>
            <Radio.Group>
              <Radio value={true}>是</Radio>
              <Radio value={false}>否</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item label="单段文本最大长度" name="chunk_size" {...layout} {...layout}>
            <InputNumber min={0} style={{ width: 200 }} />
          </Form.Item>

          <Form.Item label="相邻文本重合长度" name="chunk_overlap" {...layout} {...layout}>
            <InputNumber min={0} style={{ width: 200 }} />
          </Form.Item>
          {/* <Form.Item name="docs" label="自定义的docs" {...layout} {...layout}>
          <Input style={{ width: 200 }} />
        </Form.Item> */}
        </Form>
      </Modal>
    );
  },
);

export default ModalAddFile;
