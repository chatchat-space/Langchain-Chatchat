'use client';

import { FloatButton } from 'antd';
import { Plus } from 'lucide-react';
import dynamic from 'next/dynamic';
import { memo, useState } from 'react';

import KnowledgeCardList from './features/KnowledgeList';
// import CreateKnowledgeBase from './features/createKnowledgeBase';
import Layout from './layout.desktop';

const ModalCreateKnowledge = dynamic(() => import('./features/ModalCreateKnowledge'));

const DesktopPage = memo(() => {
  const [showModal, setShowModal] = useState(false);
  return (
    <>
      <Layout>
        <KnowledgeCardList />
        <FloatButton
          icon={<Plus style={{ width: 20 }} />} onClick={() => setShowModal(true)}>
          新建知识库
        </FloatButton>
      </Layout>
      <ModalCreateKnowledge open={showModal} toggleModal={setShowModal} />
    </>
  );
});
export default DesktopPage;
