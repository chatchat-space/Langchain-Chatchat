import { Input, Modal, type ModalProps } from '@lobehub/ui';
import { App } from 'antd';
import isEqual from 'fast-deep-equal';
import { memo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useSessionStore } from '@/store/session';
import { sessionGroupSelectors } from '@/store/session/selectors';

interface RenameGroupModalProps extends ModalProps {
  id: string;
}

const RenameGroupModal = memo<RenameGroupModalProps>(({ id, open, onCancel }) => {
  const { t } = useTranslation('chat');

  const updateSessionGroupName = useSessionStore((s) => s.updateSessionGroupName);
  const group = useSessionStore((s) => sessionGroupSelectors.getGroupById(id)(s), isEqual);

  const [input, setInput] = useState<string>();

  const { message } = App.useApp();
  return (
    <Modal
      allowFullscreen
      onCancel={onCancel}
      onOk={(e) => {
        if (!input) return;
        if (input.length === 0 || input.length > 20)
          return message.warning(t('sessionGroup.tooLong'));
        updateSessionGroupName(id, input);
        message.success(t('sessionGroup.renameSuccess'));
        onCancel?.(e);
      }}
      open={open}
      title={t('sessionGroup.rename')}
      width={400}
    >
      <Input
        autoFocus
        defaultValue={group?.name}
        onChange={(e) => setInput(e.target.value)}
        placeholder={t('sessionGroup.inputPlaceholder')}
        value={input}
      />
    </Modal>
  );
});

export default RenameGroupModal;
