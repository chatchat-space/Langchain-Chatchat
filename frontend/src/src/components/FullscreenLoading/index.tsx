import { Icon } from '@lobehub/ui';
import { Loader2 } from 'lucide-react';
import { memo } from 'react';
import { Center, Flexbox } from 'react-layout-kit';
import Logo from '@/components/Logo';
const FullscreenLoading = memo<{ title?: string }>(({ title }) => {
  return (
    <Flexbox height={'100%'} style={{ userSelect: 'none' }} width={'100%'}>
      <Center flex={1} gap={12} width={'100%'}>
        <Logo extra={'Chat'} size={48} type={'combine'} />
        <Center gap={16} horizontal>
          <Icon icon={Loader2} spin />
          {title}
        </Center>
      </Center>
    </Flexbox>
  );
});

export default FullscreenLoading;
