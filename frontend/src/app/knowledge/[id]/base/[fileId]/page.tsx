'use client';

import { Card, List } from 'antd';
import { createStyles } from 'antd-style';
import React, { memo, useState } from 'react';

import ModalSegment from './features/ModalSegment';

const data = [
  {
    title: 'Title 1',
  },
  {
    title: 'Title 2',
  },
  {
    title: 'Title 3',
  },
  {
    title: 'Title 4',
  },
  {
    title: 'Title 5',
  },
  {
    title: 'Title 6',
  },
];
const useStyle = createStyles(({ css, token }) => ({
  card: css`
    cursor: pointer;
    overflow: hidden;
    &:hover {
      box-shadow: 0 0 0 1px ${token.colorText};
    }

    &:active {
      scale: 0.95;
    }
  `,
}));

const App = memo(() => {
  const { styles } = useStyle();
  const [isShowModal, setModal] = useState();
  return (
    <>
      <List
        dataSource={data}
        grid={{
          gutter: 16,
          lg: 2,
          xl: 2,
          xxl: 2,
        }}
        renderItem={() => (
          <List.Item>
            <Card className={styles.card} onClick={() => console.log(1)}>
              Card content
            </Card>
          </List.Item>
        )}
        size="large"
      />
      <ModalSegment />
    </>
  );
});

export default App;
