import { Settings2, Webhook } from 'lucide-react';
import Link from 'next/link';
import { memo } from 'react';

import { KnowledgeTabs } from '@/store/global/initialState';

import Item from './TabItem';

export interface KnowledgeTabsProps {
  activeTab?: KnowledgeTabs;
  params: Record<string, string>;
}

const KnowledgeTabsBox = memo<KnowledgeTabsProps>(({ activeTab, params }) => {
  console.log(params);
  const items = [
    { icon: Webhook, label: '知识库', value: KnowledgeTabs.Base },
    { icon: Settings2, label: '配置', value: KnowledgeTabs.Config },
  ];

  return items.map(({ value, icon, label }) => (
    <Link aria-label={label} href={`/knowledge/${params.id}/${value}`} key={value}>
      <Item active={activeTab === value} hoverable icon={icon} label={label} />
    </Link>
  ));
});

export default KnowledgeTabsBox;
