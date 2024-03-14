import { Highlighter } from '@lobehub/ui';
import { memo } from 'react';
import { Flexbox } from 'react-layout-kit';

import { ChatMessageError } from '@/types/message';

interface ErrorJSONViewerProps {
  error?: ChatMessageError;
  id: string;
}

const ErrorJsonViewer = memo<ErrorJSONViewerProps>(({ error, id }) => {
  const errorBody = error?.body || error;

  if (!errorBody) return;

  return (
    <Flexbox id={id} style={{ maxWidth: 600 }}>
      <Highlighter copyButtonSize={'small'} language={'json'}>
        {JSON.stringify(errorBody, null, 2)}
      </Highlighter>
    </Flexbox>
  );
});

export default ErrorJsonViewer;
