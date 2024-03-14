import { TextAreaRef } from 'antd/es/input/TextArea';
import { useCallback, useRef, useState } from 'react';

import { useChatStore } from '@/store/chat';
import { useGlobalStore } from '@/store/global';
import { modelProviderSelectors } from '@/store/global/selectors';
import { useSessionStore } from '@/store/session';
import { agentSelectors } from '@/store/session/selectors';

import { useSendMessage } from './useSend';

export const useChatInput = () => {
  const ref = useRef<TextAreaRef>(null);
  const [expand, setExpand] = useState<boolean>(false);
  const onSend = useSendMessage();

  const model = useSessionStore(agentSelectors.currentAgentModel);
  const canUpload = useGlobalStore(modelProviderSelectors.modelEnabledUpload(model));

  const [loading, value, onInput, onStop] = useChatStore((s) => [
    !!s.chatLoadingId,
    s.inputMessage,
    s.updateInputMessage,
    s.stopGenerateMessage,
  ]);

  const handleSend = useCallback(() => {
    setExpand(false);

    onSend();
  }, [onSend]);

  return {
    canUpload,
    expand,
    loading,
    onInput,
    onSend: handleSend,
    onStop,
    ref,
    setExpand,
    value,
  };
};
