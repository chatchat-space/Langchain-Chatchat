import { LogoProps, StoryBook, useControls, useCreateStore } from '@lobehub/ui';
import Logo from '@/components/Logo';

export default () => {
  const store = useCreateStore();
  const control: LogoProps | any = useControls(
    {
      size: {
        max: 240,
        min: 16,
        step: 4,
        value: 64,
      },
      type: {
        options: ['3d', 'flat', 'high-contrast', 'text', 'combine'],
        value: '3d',
      },
    },
    { store },
  );

  return (
    <StoryBook levaStore={store}>
      <Logo {...control} />
    </StoryBook>
  );
};
