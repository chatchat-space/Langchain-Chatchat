import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { Modal, Upload, message } from 'antd';
import React, { memo } from 'react';

const { Dragger } = Upload;

type ModalAddFileProps = {
  open: boolean;
  setModalOpen: (open: boolean) => void;
};

const props: UploadProps = {
  action: 'https://660d2bd96ddfa2943b33731c.mockapi.io/api/upload',
  multiple: true,
  name: 'file',
  onChange(info) {
    const { status } = info.file;
    if (status !== 'uploading') {
      console.log(info.file, info.fileList);
    }
    if (status === 'done') {
      message.success(`${info.file.name} file uploaded successfully.`);
    } else if (status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  },
  onDrop(e) {
    console.log('Dropped files', e.dataTransfer.files);
  },
};

const ModalAddFile = memo<ModalAddFileProps>(({ open, setModalOpen }) => {
  return (
    <Modal onCancel={() => setModalOpen(false)} open={open} title="添加文件">
      <Dragger {...props}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Click or drag file to this area to upload</p>
        <p className="ant-upload-hint">
          Support for a single or bulk upload. Strictly prohibited from uploading company data or
          other banned files.
        </p>
      </Dragger>
    </Modal>
  );
});

export default ModalAddFile;
