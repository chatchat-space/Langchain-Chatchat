import { memo, useEffect } from 'react';

const PageTitle = memo<{ title: string }>(({ title }) => {
  useEffect(() => {
    document.title = title ? `${title} · ChatChat` : 'ChatChat';
  }, [title]);

  return null;
});

export default PageTitle;
