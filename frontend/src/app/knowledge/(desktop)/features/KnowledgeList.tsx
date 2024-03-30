import React, { memo } from 'react';

import KnowledgeCard from './KnowledgeCard';

const list = [
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
  { intro: 'aaaaa', name: '321' },
];

const RenderList = memo(() =>
  list.map((item, index) => {
    return <KnowledgeCard key={index} {...item} />;
  }),
);

const KnowledgeCardList = memo(() => {
  return <RenderList />;
});

export default KnowledgeCardList;
