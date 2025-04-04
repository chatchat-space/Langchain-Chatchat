import { Input, Modal, message } from 'antd';
import { BaseSyntheticEvent, memo, useState } from 'react';
import { Center, Flexbox } from 'react-layout-kit';

import { useKnowledgeStore } from '@/store/knowledge';
import type {
  KnowledgeSearchDocsList,
  KnowledgeUpdateDocsParams,
} from '@/types/knowledge';

type ModalSegmentProps = {
  dataSource: KnowledgeSearchDocsList;
  fileId: string;
  kbName: string;
  toggleOpen: (open: boolean) => void;
};

const ModalSegment = memo<ModalSegmentProps>(({ kbName, fileId, dataSource = [], toggleOpen }) => {
  const [updateLoading, setUpdateLoading] = useState(false);
  const [editKnowledgeInfo, editContentInfo, useFetcUpdateDocs] = useKnowledgeStore((s) => [
    s.editKnowledgeInfo,
    s.editContentInfo,
    s.useFetcUpdateDocs,
  ]);
  const [textValue, setTextValue] = useState<string>(editContentInfo?.page_content || '');

  const onOk = async () => {
    const newDataSource = dataSource.map((item) => ({
      ...item,
      page_content: item.id === editContentInfo?.id ? textValue : item.page_content,
    }));
    const params: KnowledgeUpdateDocsParams = {
      chunk_overlap: 50,
      chunk_size: 250,
      docs: JSON.stringify({
        [decodeURIComponent(fileId)]: [...newDataSource],
      }),
      file_names: [decodeURIComponent(fileId)],
      knowledge_base_name: kbName,
      not_refresh_vs_cache: false,
      override_custom_docs: false,
      to_vector_store: true,
      zh_title_enhance: false,
    };

    try {
      setUpdateLoading(true);
      const { code: resCode, msg: resMsg } = await useFetcUpdateDocs(params);
      setUpdateLoading(false);
      toggleOpen(false);

      if (resCode !== 200) {
        message.error(resMsg);
        return;
      }
      message.success(resMsg);
    } catch (err) {
      message.error(`${err}`);
      setUpdateLoading(false);
    }
  };
  const onChange = (event: BaseSyntheticEvent) => {
    setTextValue(event.target.value);
  };

  return (
    <Modal
      confirmLoading={updateLoading}
      okText="确认修改"
      onCancel={() => toggleOpen(false)}
      onOk={onOk}
      open
      title="知识片段"
    >
      <Flexbox padding={20}>
        <Center>
          <Input.TextArea
            autoSize={{ maxRows: 15, minRows: 10 }}
            onChange={onChange}
            style={{ width: 600 }}
            value={textValue}
          />
        </Center>
      </Flexbox>
    </Modal>
  );
});

export default ModalSegment;
