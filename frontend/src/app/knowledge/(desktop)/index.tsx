'use client';

import { FloatButton } from 'antd';
import { Plus } from 'lucide-react';
import dynamic from 'next/dynamic';
import { memo, useState } from 'react';
import { createStyles } from 'antd-style';

import KnowledgeCardList from './features/KnowledgeList'; 
import Layout from './layout.desktop';

const useStyle = createStyles(({ css, token }) => ({
  addButton: css`
    width: 20px;
  `,
}));

const ModalCreateKnowledge = dynamic(() => import('./features/ModalCreateKnowledge'));

const DesktopPage = memo(() => {
  const { styles } = useStyle();

  const [showModal, setShowModal] = useState(false);
  return (
    <>
      <Layout>
        <KnowledgeCardList />
        <FloatButton
          // className={styles.addButton}
          icon={<Plus />} onClick={() => setShowModal(true)}>
          新建知识库
        </FloatButton>
      </Layout>
      <ModalCreateKnowledge open={showModal} toggleModal={setShowModal} />
    </>
  );
});
export default DesktopPage;
