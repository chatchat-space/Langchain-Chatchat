'use client';

import { memo } from 'react';
import { Flexbox } from 'react-layout-kit';

import ResponsiveIndex from '@/components/ResponsiveIndex';

import KnowledgeCardList from './features/KnowledgeList';
import Layout from './layout.desktop';

// const Mobile: FC = dynamic(() => import('../(mobile)'), { ssr: false }) as FC;

const DesktopPage = memo(() => (
  <ResponsiveIndex Mobile={() => <div>321</div>}>
    <Layout>
      <Flexbox gap={20} horizontal justify="flex-start" wrap="wrap">
        <KnowledgeCardList />
      </Flexbox>
    </Layout>
  </ResponsiveIndex>
));
export default DesktopPage;
