import { Input, Modal } from 'antd';
import { memo } from 'react';
import { Center, Flexbox } from 'react-layout-kit';

type ModalSegmentProps = {
  open: boolean;
  toggleOpen: (open: boolean) => void;
};

const ModalSegment = memo<ModalSegmentProps>(({ open, toggleOpen }) => {
  return (
    <Modal okText="确认修改" onCancel={() => toggleOpen(false)} open={open} title="知识片段">
      <Flexbox padding={20}>
        <Center>
          <Input.TextArea autoSize={{ maxRows: 15, minRows: 10 }} style={{ width: 600 }} />
        </Center>
      </Flexbox>
    </Modal>
  );
});

export default ModalSegment;
