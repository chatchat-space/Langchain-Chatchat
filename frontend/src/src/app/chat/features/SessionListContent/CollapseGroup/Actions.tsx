import { ActionIcon, Icon } from '@lobehub/ui';
import { App, Dropdown, DropdownProps, MenuProps } from 'antd';
import { createStyles } from 'antd-style';
import { MoreVertical, PencilLine, Plus, Settings2, Trash } from 'lucide-react';
import { memo, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { useSessionStore } from '@/store/session';

const useStyles = createStyles(({ css }) => ({
  modalRoot: css`
    z-index: 2000;
  `,
}));
interface ActionsProps extends Pick<DropdownProps, 'onOpenChange'> {
  id?: string;
  isCustomGroup?: boolean;
  isPinned?: boolean;
  openConfigModal: () => void;
  openRenameModal?: () => void;
}

type ItemOfType<T> = T extends (infer Item)[] ? Item : never;
type MenuItemType = ItemOfType<MenuProps['items']>;

const Actions = memo<ActionsProps>(
  ({ id, openRenameModal, openConfigModal, onOpenChange, isCustomGroup, isPinned }) => {
    const { t } = useTranslation('chat');
    const { styles } = useStyles();
    const { modal } = App.useApp();

    const [createSession, removeSessionGroup] = useSessionStore((s) => [
      s.createSession,
      s.removeSessionGroup,
    ]);

    const sessionGroupConfigPublicItem: MenuItemType = {
      icon: <Icon icon={Settings2} />,
      key: 'config',
      label: t('sessionGroup.config'),
      onClick: ({ domEvent }) => {
        domEvent.stopPropagation();
        openConfigModal();
      },
    };

    const newAgentPublicItem: MenuItemType = {
      icon: <Icon icon={Plus} />,
      key: 'newAgent',
      label: t('newAgent'),
      onClick: ({ domEvent }) => {
        domEvent.stopPropagation();
        createSession({ group: id, pinned: isPinned });
      },
    };

    const customGroupItems: MenuProps['items'] = useMemo(
      () => [
        newAgentPublicItem,
        {
          type: 'divider',
        },
        {
          icon: <Icon icon={PencilLine} />,
          key: 'rename',
          label: t('sessionGroup.rename'),
          onClick: ({ domEvent }) => {
            domEvent.stopPropagation();
            openRenameModal?.();
          },
        },
        sessionGroupConfigPublicItem,
        {
          type: 'divider',
        },
        {
          danger: true,
          icon: <Icon icon={Trash} />,
          key: 'delete',
          label: t('delete', { ns: 'common' }),
          onClick: ({ domEvent }) => {
            domEvent.stopPropagation();
            modal.confirm({
              centered: true,
              okButtonProps: { danger: true },
              onOk: () => {
                if (!id) return;
                removeSessionGroup(id);
              },
              rootClassName: styles.modalRoot,
              title: t('sessionGroup.confirmRemoveGroupAlert'),
            });
          },
        },
      ],
      [],
    );

    const defaultItems: MenuProps['items'] = useMemo(
      () => [
        newAgentPublicItem,
        {
          type: 'divider',
        },
        sessionGroupConfigPublicItem,
      ],
      [],
    );

    return (
      <Dropdown
        arrow={false}
        menu={{
          items: isCustomGroup ? customGroupItems : defaultItems,
          onClick: ({ domEvent }) => {
            domEvent.stopPropagation();
          },
        }}
        onOpenChange={onOpenChange}
        trigger={['click']}
      >
        <ActionIcon
          icon={MoreVertical}
          onClick={(e) => {
            e.stopPropagation();
          }}
          size={{ blockSize: 22, fontSize: 16 }}
          style={{ marginRight: -8 }}
        />
      </Dropdown>
    );
  },
);

export default Actions;
