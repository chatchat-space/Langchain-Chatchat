import { Settings2, Webhook } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { memo, useState } from 'react';

import Item from './TabItem';

export enum KnowledgeTabs {
  Base = 'base',
  Config = 'config',
}

export interface KnowledgeTabsProps {
  activeTab?: KnowledgeTabs;
  params: Record<string, string>;
}

const KnowledgeTabsBox = memo<KnowledgeTabsProps>(({ params }) => { 
  const [activeTab, setActiveTab] = useState<KnowledgeTabs>(KnowledgeTabs.Base);
  const items = [
    { icon: Webhook, label: '知识库', value: KnowledgeTabs.Base },
    { icon: Settings2, label: '配置', value: KnowledgeTabs.Config },
  ];
  const router = useRouter();
  const handleTabClick = (value: KnowledgeTabs) => {
    setActiveTab(value);
    router.push(`/knowledge/${params.id}/${value}`);
  };
  return items.map(({ value, icon, label }) => (
    <div aria-label={label} key={value} onClick={() => handleTabClick(value)}>
      <Item active={activeTab === value} hoverable icon={icon} label={label} />
    </div>
  ));
});

export default KnowledgeTabsBox;
