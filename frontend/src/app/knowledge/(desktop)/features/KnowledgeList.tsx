import React, { memo } from 'react';
import { Empty, Spin } from 'antd';
import { createStyles } from 'antd-style';
import KnowledgeCard from './KnowledgeCard';
import { useKnowledgeStore } from '@/store/knowledge';
import { Flexbox } from 'react-layout-kit';

const useStyles = createStyles(({ css, token, stylish }) => ({
  wrap: css`
  min-height: 200px;
  height: 100%;
  width: 100%; 
  `,
  null: css`
    display: block;
    position: absolute;
    top: 0px; bottom: 0px; left: 0px; right: 0px;
    margin: auto;
    height: 100px;
  `,
}));

const RenderList = memo(() => {
  const { styles } = useStyles();
  const [listData, useFetchKnowledgeList] = useKnowledgeStore((s) => [
    s.listData, s.useFetchKnowledgeList
  ]);
  const { isLoading } = useFetchKnowledgeList();

  const list = listData.map(({ kb_info, kb_name }) => ({
    intro: kb_info, 
    name: kb_name
  }))
  // const list = [
  //   { intro: '知识库简介', name: '知识库名称' },
  //   { intro: '知识库简介', name: '知识库名称' }, 
  // ];
  
  if (!isLoading && !listData.length) {
    return <div className={styles.null}>
      <Empty />
    </div>
  }
  return <div className={styles.wrap}>
    <Spin tip="Loading..." spinning={isLoading}>
      <div className={styles.wrap}>
        <Flexbox gap={20} horizontal justify="flex-start" wrap="wrap">
          {list.map((item, index) => {
            return <KnowledgeCard key={index} {...item} />;
          })}
        </Flexbox> 
      </div>
    </Spin>
  </div>
});

const KnowledgeCardList = memo(() => {
  return <RenderList />;
});

export default KnowledgeCardList;
