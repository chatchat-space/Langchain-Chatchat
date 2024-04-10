'use client';

import dynamic from 'next/dynamic';
import { memo } from 'react';

const KnowledgeBaseConfig = dynamic(() => import('./features/KnowledgeBaseConfig'));
const KnowledgeDetail = memo(() => {
  return <KnowledgeBaseConfig />;
});

export default KnowledgeDetail;
