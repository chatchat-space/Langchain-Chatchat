'use client';

import { FloatButton } from 'antd';
import { Plus } from 'lucide-react';
import dynamic from 'next/dynamic';
import { memo, useEffect, useState } from 'react';
import { Flexbox } from 'react-layout-kit';

import ResponsiveIndex from '@/components/ResponsiveIndex';

import KnowledgeCardList from './features/KnowledgeList';
// import CreateKnowledgeBase from './features/createKnowledgeBase';
import Layout from './layout.desktop';

const CreateKnowledgeBase = dynamic(() => import('./features/CreateKnowledgeBase'));
// const Mobile: FC = dynamic(() => import('../(mobile)'), { ssr: false }) as FC;

const DesktopPage = memo(() => {
  const [showModal, setShowModal] = useState(false);
  useEffect(() => {
    setShowModal(true);
  }, []);
  const onClose = () => setShowModal(false);
  return (
    <ResponsiveIndex Mobile={() => <div>321</div>}>
      <Layout>
        <Flexbox gap={20} horizontal justify="flex-start" wrap="wrap">
          <KnowledgeCardList />
          <CreateKnowledgeBase onClose={onClose} open={showModal} />
        </Flexbox>
        <FloatButton icon={<Plus />} onClick={() => setShowModal(true)}>
          新建知识库
        </FloatButton>
      </Layout>
    </ResponsiveIndex>
  );
});
export default DesktopPage;
