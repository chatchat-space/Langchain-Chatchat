import { act, renderHook } from '@testing-library/react';
import { Mock, afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { chainLangDetect } from '@/chains/langDetect';
import { chainTranslate } from '@/chains/translate';
import { chatService } from '@/services/chat';
import { messageService } from '@/services/message';

import { useChatStore } from '../../store';

// Mock messageService 和 chatService
vi.mock('@/services/message', () => ({
  messageService: {
    updateMessageTTS: vi.fn(),
    updateMessage: vi.fn(),
  },
}));

vi.mock('@/services/chat', () => ({
  chatService: {
    fetchPresetTaskResult: vi.fn(),
  },
}));

vi.mock('@/chains/langDetect', () => ({
  chainLangDetect: vi.fn(),
}));

vi.mock('@/chains/translate', () => ({
  chainTranslate: vi.fn(),
}));

// Mock supportLocales
vi.mock('@/locales/options', () => ({
  supportLocales: ['en-US', 'zh-CN'],
}));

beforeEach(() => {
  vi.clearAllMocks();
  useChatStore.setState(
    {
      // ... 初始状态
    },
    false,
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('ChatEnhanceAction', () => {
  describe('clearTTS', () => {
    it('should clear TTS for a message and refresh messages', async () => {
      const { result } = renderHook(() => useChatStore());
      const messageId = 'message-id';

      await act(async () => {
        await result.current.clearTTS(messageId);
      });

      expect(messageService.updateMessage).toHaveBeenCalledWith(messageId, { tts: false });
    });
  });

  describe('translateMessage', () => {
    it('should translate a message to the target language and refresh messages', async () => {
      const { result } = renderHook(() => useChatStore());
      const messageId = 'message-id';
      const targetLang = 'zh-CN';
      const messageContent = 'Hello World';
      const detectedLang = 'en-US';

      act(() => {
        useChatStore.setState({
          messages: [
            {
              id: messageId,
              content: messageContent,
              createdAt: Date.now(),
              updatedAt: Date.now(),
              role: 'user',
              sessionId: 'test',
              topicId: 'test',
              meta: {},
            },
          ],
        });
      });

      (chatService.fetchPresetTaskResult as Mock).mockImplementation(({ params }) => {
        if (params === chainLangDetect(messageContent)) {
          return Promise.resolve(detectedLang);
        }
        if (params === chainTranslate(messageContent, targetLang)) {
          return Promise.resolve('Hola Mundo');
        }
        return Promise.resolve(undefined);
      });

      await act(async () => {
        await result.current.translateMessage(messageId, targetLang);
      });

      expect(messageService.updateMessage).toHaveBeenCalled();
    });
  });

  describe('clearTranslate', () => {
    it('should clear translation for a message and refresh messages', async () => {
      const { result } = renderHook(() => useChatStore());
      const messageId = 'message-id';

      await act(async () => {
        await result.current.clearTranslate(messageId);
      });

      expect(messageService.updateMessage).toHaveBeenCalledWith(messageId, { translate: false });
    });
  });
});
