import { EditOutlined, EllipsisOutlined, SettingOutlined } from '@ant-design/icons';
import { Card, Skeleton } from 'antd';
import React, { useState } from 'react';

const { Meta } = Card;

interface KnowLedgeCardProps {
  intro: string;
  name: string;
}
const App: React.FC = (props: KnowLedgeCardProps) => {
  const [loading, setLoading] = useState(false);
  const { name, intro } = props;
  const onChange = (checked: boolean) => {
    setLoading(!checked);
  };

  return (
    <Card
      actions={[
        <SettingOutlined key="setting" />,
        <EditOutlined key="edit" />,
        <EllipsisOutlined key="ellipsis" />,
      ]}
      bordered={false}
      style={{ marginTop: 16, width: 300 }}
    >
      <Skeleton active avatar loading={loading}>
        <Meta
          // avatar={<Avatar src="https://api.dicebear.com/7.x/miniavs/svg?seed=2" />}
          description={intro}
          title={name}
        />
      </Skeleton>
    </Card>
  );
};

export default App;
