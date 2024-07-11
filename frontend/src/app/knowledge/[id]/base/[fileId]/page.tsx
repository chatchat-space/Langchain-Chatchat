'use client';

import { Card, List, Empty, Spin } from 'antd';
import { createStyles } from 'antd-style';
import dynamic from 'next/dynamic';
import React, { memo, useEffect, useState } from 'react';
import { useKnowledgeStore } from '@/store/knowledge';

const ModalSegment = dynamic(() => import('./features/ModalSegment'));


const useStyle = createStyles(({ css, token }) => ({
  page: css`
    width: 100%;  
    padding-top: 12px;
  `,
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
  null: css`
  display: block;
  position: absolute;
  top: 0px; bottom: 0px; left: 0px; right: 0px;
  margin: auto;
  height: 100px;
`,
}));

const App = memo((props: { params: { id: string; fileId: string } }) => {
  const { params: { id, fileId } } = props;
  const { styles } = useStyle();
  const [isModalOpen, toggleOpen] = useState(false);
  const [fileSearchData, useFetchSearchDocs, setEditContentInfo] = useKnowledgeStore((s) => [
    s.fileSearchData, s.useFetchSearchDocs, s.setEditContentInfo
  ]);
  // const fileSearchData = [
  //   {
  //     id: 1,
  //     page_content: "This is a test", 
  //   },
  //   {
  //     id: 2,
  //     page_content: "This is a test22", 
  //   },  
  // ] 
  const { isLoading, mutate } = useFetchSearchDocs({
    query: "", 
    top_k: 3,
    score_threshold: 1,
    knowledge_base_name: id, 
    file_name: decodeURIComponent(fileId)
  });

  useEffect(()=>{
    !isModalOpen && mutate();
  }, [isModalOpen])

  const handleSegmentCardClick: typeof setEditContentInfo = (item) => {
    setEditContentInfo({...item})
    toggleOpen(true);
  };


  if (!isLoading && !fileSearchData.length) {
    return <div className={styles.null}>
      <Empty />
    </div>
  }

  return (
    <div className={styles.page} >
      <Spin tip="Loading..." spinning={isLoading}>
        <List
          dataSource={fileSearchData}
          grid={{
            gutter: 16,
            lg: 2,
            xl: 2,
            xxl: 2,
          }}
          renderItem={(item) => (
            <List.Item>
              <Card className={styles.card} onClick={() => handleSegmentCardClick(item)}>
                {item.page_content}
              </Card>
            </List.Item>
          )}
          size="large"
        />
        {isModalOpen && <ModalSegment dataSource={[...fileSearchData]} toggleOpen={toggleOpen} kbName={props.params.id} fileId={props.params.fileId} />}
      </Spin>
    </div>
  );
});

export default App;
