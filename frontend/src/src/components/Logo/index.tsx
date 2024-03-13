import React from 'react';
import { ReactNode, memo } from 'react';
import { Flexbox } from 'react-layout-kit';
import LogoText from './LogoText';
import { useStyles } from './style';
import { useTheme } from 'antd-style';
import Divider from './Divider';
import LogoHighContrast from './LogoHighContrast';

export interface LogoProps  {
    /**
   * @description Additional React Node to be rendered next to the logo
   */
  extra?: ReactNode;
  /**
   * @description Size of the logo in pixels
   * @default 32
   */
  size?: number;
  /**
   * @description Type of the logo to be rendered
   * @default '3d'
   */
  type?: '3d' | 'flat' | 'high-contrast' | 'text' | 'combine';
  imageUrl?: string;
  localImage?: string;
}

const Logo = memo<LogoProps>(
  ({ type = 'flat', size = 32, style, extra, className, imageUrl, localImage, ...rest  }) => {
    let logoComponent: ReactNode;
    const { styles } = useStyles();
    const theme = useTheme();

    switch (type) {
      case 'flat': {
        logoComponent = (
          <img alt="chatchat" height={size} src={`/images/chathead.webp`} style={style} width={size} />
        );
        break;
      }
      case '3d': {
        if (!imageUrl) {
          console.error('Custom image type requires imageUrl prop.');
          return null;
        }

        logoComponent = (
          <img
            alt="image-reference"
            src={imageUrl}
            style={{ height: `${size}px`, width: `${size}px` }}
          />
        );
        break;
      }
      case 'combine': {
        logoComponent = (
          <>
            <img alt="chatchat" height={size} src={`/images/chatjump.webp`} style={style} width={size} />
            <LogoText style={{ height: size, marginLeft: Math.round(size / 4), width: 'auto' }} />
          </>
        );
        break;
      }
      case 'text': {
        logoComponent = (
          <LogoText
            className={className}
            height={size}
            style={style}
            width={size * 2.9375}
            {...rest}
          />
        );
        break;
      }
    }

    if (!extra) return logoComponent;

    const extraSize = Math.round((size / 3) * 1.9);

    return (
      <Flexbox align={'center'} className={className} horizontal style={style} {...rest}>
      {logoComponent}
      <Divider style={{ color: theme.colorFill, height: extraSize, width: extraSize }} />
      <div className={styles.extraTitle} style={{ fontSize: extraSize }}>
        {extra}
      </div>
    </Flexbox>
    );
  }
);

export default Logo;
