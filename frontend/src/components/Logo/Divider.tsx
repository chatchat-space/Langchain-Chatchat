import { memo } from 'react';

import { SvgProps } from '@/types';

const Divider = memo<SvgProps | any>(({ ...rest }) => (
  <svg
    fill="none"
    shapeRendering="geometricPrecision"
    stroke="currentColor"
    strokeLinecap="round"
    strokeLinejoin="round"
    viewBox="0 0 24 24"
    {...rest}
  >
    <path d="M16.88 3.549L7.12 20.451" />
  </svg>
));

export default Divider;
