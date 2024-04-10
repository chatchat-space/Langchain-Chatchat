'use client';

import { createStyles } from 'antd-style';
import { PropsWithChildren, memo } from 'react';
import { Center, Flexbox } from 'react-layout-kit';

import AppLayoutDesktop from '@/layout/AppLayout.desktop';
import { SidebarTabKey } from '@/store/global/initialState';

import KnowledgeTabs from './tabs';

const useStyles = createStyles(({ stylish, token, css }) => ({
  container: {
    paddingLeft: 20,
    paddingRight: 20,
    position: 'relative',
  },
}));

export default memo(({ children, params }: PropsWithChildren) => {
  console.log(params);
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
            <Center>图标占位</Center>
            <Center>知识库名称</Center>
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
