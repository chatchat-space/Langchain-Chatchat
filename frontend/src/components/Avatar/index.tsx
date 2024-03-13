import { Avatar as AntAvatar, type AvatarProps as AntAvatarProps } from 'antd';
import { type ReactNode, isValidElement, memo, useMemo } from 'react';

import { useStyles } from './style';

export interface AvatarProps extends AntAvatarProps {
  animation?: boolean;
  /**
   * @description The URL or base64 data of the avatar image
   */
  avatar?: string | ReactNode;
  /**
   * @description The background color of the avatar
   */
  background?: string;
  /**
   * @description The shape of the avatar
   * @default 'circle'
   */
  shape?: 'circle' | 'square';
  /**
   * @description The size of the avatar in pixels
   * @default 40
   */
  size?: number;
  /**
   * @description The title text to display if avatar is not provided
   */
  title?: string;
}

const Avatar = memo<AvatarProps>(
  ({
    className,
    avatar,
    title,
    animation,
    size = 40,
    shape = 'circle',
    background = 'rgba(0,0,0,0)',
    style,
    ...rest
  }) => {
    const isStringAvatar = typeof avatar === 'string';
    // const isDefaultAntAvatar = Boolean(
    //   avatar &&
    //     (['/', 'http', 'data:'].some((index) => isStringAvatar && avatar.startsWith(index)) ||
    //       isValidElement(avatar)),
    // );
    const isDefaultAntAvatar = true;
    const { styles, cx } = useStyles({ background, isEmoji:false , size });

    const text = String(isDefaultAntAvatar ? title : avatar);
    const defaultAvatarPath = `/images/logo.png`;

    const avatarProps = {
      className: cx(styles.avatar, className),
      shape,
      size,
      style: rest?.onClick ? style : { cursor: 'default', ...style },
      ...rest,
    };

    return isDefaultAntAvatar ? (
      <AntAvatar src={defaultAvatarPath} {...avatarProps} />
    ) : (
      <AntAvatar {...avatarProps}>
        {(
          text?.toUpperCase().slice(0, 2)
        )}
      </AntAvatar>
    );
  },
);

export default Avatar;
