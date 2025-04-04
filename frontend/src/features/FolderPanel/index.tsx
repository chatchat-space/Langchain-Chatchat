// @ts-nocheck
import { Folder } from '@lobehub/icons';
import { Button, Input, Modal } from 'antd';
import { memo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { FormAction } from '@/features/Conversation/Error/style';
import { useGlobalStore } from '@/store/global';
import { folderSelectors } from '@/store/global/selectors';

const FolderPanel = memo(() => {
  const { t } = useTranslation('error');
  const [showModal, setShowModal] = useState(false);

  const [folderName, setConfig] = useGlobalStore((s) => [
    folderSelectors.folderName(s),
    s.setFolderConfig,
  ]);

  return (
    <FormAction
      avatar={<Folder size={56} />}
      description={t('unlock.folder.Folder.description')}
      title={t('unlock.folder.Folder.title')}
    >
      <Input
        onChange={(e) => {
          setConfig({ folderName: e.target.value });
        }}
        placeholder={'My Folder'}
        type={'block'}
        value={folderName}
      />
      <Button
        onClick={() => {
          setShowModal(true);
        }}
        type={'primary'}
      >
        {t('unlock.folder.createFolder')}
      </Button>
      <Modal
        onCancel={() => {
          setShowModal(false);
        }}
        onOk={() => {
          setShowModal(false);
        }}
        open={showModal}
        title={t('unlock.folder.createFolder')}
      >
        <Input
          onChange={(e) => {
            setConfig({ folderName: e.target.value });
          }}
          placeholder={'My Folder'}
          type={'block'}
          value={folderName}
        />
      </Modal>
    </FormAction>
  );
});

export default FolderPanel;
