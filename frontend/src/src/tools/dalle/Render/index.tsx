import { ActionIcon, ImageGallery } from '@lobehub/ui';
import { Download } from 'lucide-react';
import { memo, useRef } from 'react';
import { Flexbox } from 'react-layout-kit';

import GalleyGrid from '@/components/GalleyGrid';
import { fileService } from '@/services/file';
import { BuiltinRenderProps } from '@/types/tool';
import { DallEImageItem } from '@/types/tool/dalle';

import ImageItem from './Item';

const DallE = memo<BuiltinRenderProps<DallEImageItem[]>>(({ content, messageId }) => {
  const currentRef = useRef(0);

  const handleDownload = async () => {
    // 1. Retrieve the blob URL of an image by its imageId
    const id = content[currentRef.current]?.imageId;
    if (!id) return;
    const { url, name } = await fileService.getFile(id);
    // 2. Download the image
    const link = document.createElement('a');
    link.href = url;
    link.download = name; // 设置下载的文件名
    link.click();
  };

  return (
    <Flexbox gap={16}>
      {/* 没想好工具条的作用 */}
      {/*<ToolBar content={content} messageId={messageId} />*/}
      <ImageGallery
        preview={{
          // 切换图片时设置
          onChange: (current: number) => {
            currentRef.current = current;
          },
          // 点击预览显示时设置
          onVisibleChange: (visible: boolean, _prevVisible: boolean, current: number) => {
            currentRef.current = current;
          },
          toolbarAddon: <ActionIcon color={'#fff'} icon={Download} onClick={handleDownload} />,
        }}
      >
        <GalleyGrid items={content.map((c) => ({ ...c, messageId }))} renderItem={ImageItem} />
      </ImageGallery>
    </Flexbox>
  );
});

export default DallE;
