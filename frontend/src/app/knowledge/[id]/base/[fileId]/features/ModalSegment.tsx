import { Input, Modal, message } from 'antd';
import { BaseSyntheticEvent, memo, useState } from 'react';
import { Center, Flexbox } from 'react-layout-kit';
import { useKnowledgeStore } from '@/store/knowledge';
import type { KnowledgeUpdateDocsParams, KnowledgeSearchDocsListItem } from '@/types/knowledge';

type ModalSegmentProps = {
  fileId: string;
  kbName: string;
  toggleOpen: (open: boolean) => void;
};

const ModalSegment = memo<ModalSegmentProps>(({ kbName, fileId, toggleOpen }) => {

  const [updateLoading, setUpdateLoading] = useState(false);
  const [editKnowledgeInfo, editContentInfo, useFetcUpdateDocs] = useKnowledgeStore((s) => [
    s.editKnowledgeInfo, s.editContentInfo, s.useFetcUpdateDocs
  ]);
  const [textValue, setTextValue] = useState<string>(editContentInfo?.page_content || "");

  const onOk = async () => { 
    console.log('editContentInfo', editContentInfo)
    const params: KnowledgeUpdateDocsParams = {
      knowledge_base_name: kbName,
      override_custom_docs: false,
      to_vector_store: true,
      zh_title_enhance: false,
      not_refresh_vs_cache: false,
      chunk_size: 250,
      chunk_overlap: 50,
      file_names: [decodeURIComponent(fileId)],
      docs: {
        file_name: [
          {
            ...editContentInfo,  
            page_content: textValue
          } as KnowledgeSearchDocsListItem
        ]
      }
    }
    setUpdateLoading(true)
    await useFetcUpdateDocs(params).catch(() => {
      message.error(`更新失败`);
    })
    setUpdateLoading(false)
  }
  const onChange = (event: BaseSyntheticEvent) => {
    setTextValue(event.target.value)
  }

  return (
    <Modal okText="确认修改" onOk={onOk} onCancel={() => toggleOpen(false)} open title="知识片段" confirmLoading={updateLoading}>
      <Flexbox padding={20}>
        <Center>
          <Input.TextArea autoSize={{ maxRows: 15, minRows: 10 }} style={{ width: 600 }} value={textValue} onChange={onChange} />
        </Center>
      </Flexbox>
    </Modal>
  );
});

export default ModalSegment;
