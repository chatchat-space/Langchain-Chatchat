import { createStyles } from 'antd-style';
import { readableColor } from 'polished';

export const useStyles = createStyles(
  (
    { css, token, prefixCls },
    { background, size, isEmoji }: { background?: string; isEmoji?: boolean; size: number },
  ) => {
    const backgroundColor = background ?? token.colorBgContainer;
    const color = readableColor(backgroundColor);

    return {
      avatar: css`
        cursor: pointer;

        display: flex;
        align-items: center;
        justify-content: center;

        background: ${backgroundColor};
        border: 1px solid ${background ? 'transparent' : token.colorSplit};

        > .${prefixCls}-avatar-string {
          font-size: ${size * (isEmoji ? 0.7 : 0.5)}px;
          font-weight: 700;
          line-height: 1 !important;
          color: ${color};
        }

        > * {
          cursor: pointer;
        }
      `,
    };
  },
);
