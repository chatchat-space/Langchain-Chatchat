'use client';

import { PropsWithChildren, memo } from 'react';
import { Center, Flexbox } from 'react-layout-kit';
import AppLayoutDesktop from '@/layout/AppLayout.desktop';
import { SidebarTabKey } from '@/store/global/initialState';
import { LeftOutlined } from "@ant-design/icons"
import { Button } from "antd"
import KnowledgeTabs from './tabs';
import { useRouter } from 'next/navigation';

interface LayoutProps extends PropsWithChildren {
  params: Record<string, string>;
}
export default memo<LayoutProps>(({ children, params }) => {
  // console.log(params); 
  const router = useRouter();
  
  function goBack(){ 
    router.push('/knowledge')
  }
  return (
    <AppLayoutDesktop sidebarKey={SidebarTabKey.Knowledge}>
      <Flexbox direction="horizontal" flex={1} gap={40} height={'100%'}>
        <Flexbox
          direction="vertical"
          gap={12}
          padding={20}
          style={{ borderInlineEnd: '1px solid #333333' }}
        >
          <Flexbox padding={10}>
            <Center>  
              <Button onClick={goBack} type="link" icon={<LeftOutlined />}>{params.id}</Button>
            </Center>
            {/* <Center>{params.id}</Center> */}
          </Flexbox>

          <KnowledgeTabs params={params} />
        </Flexbox>
        <Flexbox padding={40} width={'100%'}>
          <Center>{children}</Center>
        </Flexbox>
      </Flexbox>
    </AppLayoutDesktop>
  );
});
