import React, { memo } from 'react';

import KnowledgeCard from './KnowledgeCard';

const list = [
  { intro: '知识库简介', name: '知识库名称' },
  { intro: '知识库简介', name: '知识库名称' },
  { intro: '知识库简介', name: '知识库名称' },
  { intro: '知识库简介', name: '知识库名称' },
  { intro: '知识库简介', name: '知识库名称' },
  { intro: '知识库简介', name: '知识库名称' },
  { intro: '知识库简介', name: '知识库名称' },
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
