import { DeleteOutlined, EditOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { Card, Skeleton, message, Modal } from 'antd';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { useKnowledgeStore } from '@/store/knowledge';

const { Meta } = Card;

interface KnowLedgeCardProps {
  intro: string;
  name: string;
  vector_store_type?: string;
  embed_model?: string;
}
const KnowledgeCard: React.FC<KnowLedgeCardProps> = (props: KnowLedgeCardProps) => {


  const [useFetchKnowledgeDel, useFetchKnowledgeList, setEditKnowledge] = useKnowledgeStore((s) => [
    s.useFetchKnowledgeDel, s.useFetchKnowledgeList, s.setEditKnowledge
  ]);
  const { mutate } = useFetchKnowledgeList()

  const [loading, setLoading] = useState(false);
  const { name, intro } = props;
  const router = useRouter();
  const handleCardEditClick = () => {
    setEditKnowledge({
      knowledge_base_name: props.name,
      kb_info:  props.intro,
      vector_store_type: props.vector_store_type,
      embed_model:props.embed_model,
    });
    router.push(`/knowledge/${encodeURIComponent(name)}/base`);
  };
  const delClick = async () => {
    Modal.confirm({
      title: `确认 ${name} 删除吗?`,
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        const { code: resCode, msg: resMsg } = await useFetchKnowledgeDel(name)
        if (resCode !== 200) {
          message.error(resMsg)
        } else {
          message.success(resMsg)
          mutate()
        }
        return Promise.resolve();
      },
    });

  };
  return (
    <Card
      actions={[
        <EditOutlined key="edit" onClick={handleCardEditClick} />,
        <DeleteOutlined key="ellipsis" onClick={delClick} />,
      ]}
      bordered={false}
      style={{ marginTop: 16, width: 300 }}
    >
      <Skeleton active avatar loading={loading}>
        <Meta description={intro} title={name} />
      </Skeleton>
    </Card>
  );
};

export default KnowledgeCard;
