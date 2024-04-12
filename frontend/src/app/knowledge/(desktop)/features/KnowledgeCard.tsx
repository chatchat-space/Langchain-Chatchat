import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { Card, Skeleton } from 'antd';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

const { Meta } = Card;

interface KnowLedgeCardProps {
  intro: string;
  name: string;
}
const KnowledgeCard: React.FC = (props: KnowLedgeCardProps) => {
  const [loading, setLoading] = useState(false);
  const { name, intro } = props;
  const router = useRouter();
  const handleCardEditClick = () => {
    router.push('/knowledge/1/base');
  };
  return (
    <Card
      actions={[
        <EditOutlined key="edit" onClick={handleCardEditClick} />,
        <DeleteOutlined key="ellipsis" />,
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
