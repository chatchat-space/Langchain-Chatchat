import { Empty, Spin } from 'antd';
import { createStyles } from 'antd-style';
import React, { memo } from 'react';
import { Flexbox } from 'react-layout-kit';

import { useKnowledgeStore } from '@/store/knowledge';

import KnowledgeCard from './KnowledgeCard';

const useStyles = createStyles(({ css, token, stylish }) => ({
  null: css`
    position: absolute;
    inset: 0;

    display: block;

    height: 100px;
    margin: auto;
  `,
  wrap: css`
    width: 100%;
    height: 100%;
    min-height: 200px;
  `,
}));

const RenderList = memo(() => {
  const { styles } = useStyles();
  const [listData, useFetchKnowledgeList] = useKnowledgeStore((s) => [
    s.listData,
    s.useFetchKnowledgeList,
  ]);
  const { isLoading } = useFetchKnowledgeList();

  const list = listData.map(({ kb_info, kb_name }) => ({
    intro: kb_info,
    name: kb_name,
  }));
  // const list = [
  //   { intro: '知识库简介', name: '知识库名称' },
  //   { intro: '知识库简介', name: '知识库名称' },
  // ];

  if (!isLoading && !listData.length) {
    return (
      <div className={styles.null}>
        <Empty />
      </div>
    );
  }
  return (
    <div className={styles.wrap}>
      <Spin spinning={isLoading} tip="Loading...">
        <div className={styles.wrap}>
          <Flexbox gap={20} horizontal justify="flex-start" wrap="wrap">
            {list.map((item, index) => {
              return <KnowledgeCard key={index} {...item} />;
            })}
          </Flexbox>
        </div>
      </Spin>
    </div>
  );
});

const KnowledgeCardList = memo(() => {
  return <RenderList />;
});

export default KnowledgeCardList;
