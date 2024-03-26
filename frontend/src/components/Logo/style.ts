import { createStyles } from 'antd-style';

export const LOGO_3D = {
  path: 'assets/logo-3d.webp',
  pkg: '@lobehub/assets-logo',
  version: 'latest',
};
export const LOGO_FLAT = {
  path: 'assets/logo-flat.svg',
  pkg: '@lobehub/assets-logo',
  version: 'latest',
};

export const useStyles = createStyles(({ css }) => {
  return {
    extraTitle: css`
      font-weight: 300;
      white-space: nowrap;
    `,
  };
});
