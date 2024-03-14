import { ActionIcon } from '@lobehub/ui';
import { Popconfirm } from 'antd';
import { Eraser } from 'lucide-react';
import { memo, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';

import HotKeys from '@/components/HotKeys';
import { CLEAN_MESSAGE_KEY, META_KEY, PREFIX_KEY } from '@/const/hotkeys';
import { useChatStore } from '@/store/chat';
import { useFileStore } from '@/store/file';

const Clear = memo(() => {
  const { t } = useTranslation('setting');
  const [clearMessage] = useChatStore((s) => [s.clearMessage]);
  const [clearImageList] = useFileStore((s) => [s.clearImageList]);
  const hotkeys = [META_KEY, PREFIX_KEY, CLEAN_MESSAGE_KEY].join('+');
  const [confirmOpened, updateConfirmOpened] = useState(false);

  const resetConversation = useCallback(() => {
    clearMessage();
    clearImageList();
  }, []);

  const actionTitle: any = confirmOpened ? (
    void 0
  ) : (
    <HotKeys desc={t('clearCurrentMessages', { ns: 'chat' })} keys={hotkeys} />
  );

  return (
    <Popconfirm
      arrow={false}
      okButtonProps={{ danger: true, type: 'primary' }}
      onConfirm={resetConversation}
      onOpenChange={updateConfirmOpened}
      open={confirmOpened}
      placement={'topRight'}
      title={t('confirmClearCurrentMessages', { ns: 'chat' })}
    >
      <ActionIcon icon={Eraser} placement={'bottom'} title={actionTitle} />
    </Popconfirm>
  );
});

export default Clear;
