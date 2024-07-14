'use client';

import { PropsWithChildren, memo } from 'react';
import { Center, Flexbox } from 'react-layout-kit';
import AppLayoutDesktop from '@/layout/AppLayout.desktop';
import { SidebarTabKey } from '@/store/global/initialState';
import { LeftOutlined } from "@ant-design/icons"
import { Button, Breadcrumb } from "antd"
import KnowledgeTabs from './tabs';
import { useRouter, useParams } from 'next/navigation';
interface LayoutProps extends PropsWithChildren {
  params: Record<string, string>;
}
export default memo<LayoutProps>(({ children }) => {
  const router = useRouter();
  const params = useParams<Record<string, string>>();
  function goBack() {
    router.push('/knowledge')
  }
  function goRootBack() {
    router.push('/knowledge')
  }
  function goToFileList() {
    router.push(`/knowledge/${params.id}/base`)
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
          </Flexbox>

          <KnowledgeTabs params={params} />
        </Flexbox>
        <Flexbox padding={40} width={'100%'} height={"100%"}>
          <div style={{ paddingBlock: 12 }}>
            {params.id && <Breadcrumb items={[
              {
                title: <a onClick={goRootBack}>知识库</a>,
              },
              {
                title: <a onClick={goToFileList}>{params.id}</a>,
              },
              {
                title: params.fileId ? decodeURIComponent(params.fileId) : null,
              }
            ].filter((_) => _.title)} />}
          </div>
          <div style={{ height: "calc(100% - 12px)", overflow: "auto" }}>
            <Center>{children}</Center>
          </div>
        </Flexbox>
      </Flexbox>
    </AppLayoutDesktop>
  );
});
