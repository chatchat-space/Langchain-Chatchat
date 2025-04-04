import { DeleteOutlined, EditOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { Card, Modal, Skeleton, message } from 'antd';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

import { useKnowledgeStore } from '@/store/knowledge';

const { Meta } = Card;

interface KnowLedgeCardProps {
  embed_model?: string;
  intro: string;
  name: string;
  vector_store_type?: string;
}
const KnowledgeCard: React.FC<KnowLedgeCardProps> = (props: KnowLedgeCardProps) => {
  const [useFetchKnowledgeDel, useFetchKnowledgeList, setEditKnowledge] = useKnowledgeStore((s) => [
    s.useFetchKnowledgeDel,
    s.useFetchKnowledgeList,
    s.setEditKnowledge,
  ]);
  const { mutate } = useFetchKnowledgeList();

  const [loading, setLoading] = useState(false);
  const { name, intro } = props;
  const router = useRouter();
  const handleCardEditClick = () => {
    setEditKnowledge({
      embed_model: props.embed_model,
      kb_info: props.intro,
      knowledge_base_name: props.name,
      vector_store_type: props.vector_store_type,
    });
    router.push(`/knowledge/${encodeURIComponent(name)}/base`);
  };
  const delClick = async () => {
    Modal.confirm({
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        const { code: resCode, msg: resMsg } = await useFetchKnowledgeDel(name);
        if (resCode !== 200) {
          message.error(resMsg);
        } else {
          message.success(resMsg);
          mutate();
        }
        return;
      },
      title: `确认 ${name} 删除吗?`,
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
