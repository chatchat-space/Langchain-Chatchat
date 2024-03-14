import { describe, expect, it, vi } from 'vitest';

import { LobeAgentConfig } from '@/types/agent';
import { ChatMessage } from '@/types/message';
import { OpenAIChatMessage } from '@/types/openai/chat';
import { encodeAsync } from '@/utils/tokenizer';
import * as tokenizerObj from '@/utils/tokenizer';

import { chatHelpers } from './helpers';

// Mock encodeAsync function
vi.mock('@/utils/tokenizer', () => ({
  encodeAsync: vi.fn((text) => Promise.resolve(text.length)),
}));

describe('chatHelpers', () => {
  describe('getMessagesTokenCount', () => {
    it('returns token count for a list of messages', async () => {
      const messages = [{ content: 'Hello' }, { content: 'World' }] as OpenAIChatMessage[];
      const tokenCount = await chatHelpers.getMessagesTokenCount(messages);
      expect(tokenCount).toBe('HelloWorld'.length);
    });

    it('returns 0 for an empty array', async () => {
      const tokenCount = await chatHelpers.getMessagesTokenCount([]);
      expect(tokenCount).toBe(0);
    });

    it('handles messages with empty content', async () => {
      const messages = [
        { content: 'Hello' },
        { content: '' },
        { content: 'World' },
      ] as OpenAIChatMessage[];
      const tokenCount = await chatHelpers.getMessagesTokenCount(messages);
      expect(tokenCount).toBe('HelloWorld'.length);
    });

    it('throws an error when encodeAsync fails', async () => {
      vi.spyOn(tokenizerObj, 'encodeAsync').mockRejectedValue(new Error('Test error'));
      await expect(
        chatHelpers.getMessagesTokenCount([{ content: 'Hello' }] as OpenAIChatMessage[]),
      ).rejects.toThrow('Test error');
    });
  });

  describe('getMessageById', () => {
    const messages = [
      { id: '1', content: 'Hello' },
      { id: '2', content: 'World' },
    ] as ChatMessage[];

    it('finds a message by id', () => {
      const message = chatHelpers.getMessageById(messages, '1');
      expect(message).toEqual({ id: '1', content: 'Hello' });
    });

    it('returns undefined for an invalid id', () => {
      const message = chatHelpers.getMessageById(messages, '3');
      expect(message).toBeUndefined();
    });

    it('returns undefined for an empty array', () => {
      const message = chatHelpers.getMessageById([], '1');
      expect(message).toBeUndefined();
    });
  });

  describe('getSlicedMessagesWithConfig', () => {
    const messages = [
      { id: '1', content: 'First' },
      { id: '2', content: 'Second' },
      { id: '3', content: 'Third' },
    ] as ChatMessage[];

    it('returns all messages if history is disabled', () => {
      const config = { enableHistoryCount: false, historyCount: 0 } as LobeAgentConfig;
      const slicedMessages = chatHelpers.getSlicedMessagesWithConfig(messages, config);
      expect(slicedMessages).toEqual(messages);
    });

    it('returns last N messages based on historyCount', () => {
      const config = { enableHistoryCount: true, historyCount: 2 } as LobeAgentConfig;
      const slicedMessages = chatHelpers.getSlicedMessagesWithConfig(messages, config);
      expect(slicedMessages).toEqual([
        { id: '2', content: 'Second' },
        { id: '3', content: 'Third' },
      ]);
    });

    it('returns empty array when historyCount is negative', () => {
      const config = { enableHistoryCount: true, historyCount: -1 } as LobeAgentConfig;
      const slicedMessages = chatHelpers.getSlicedMessagesWithConfig(messages, config);
      expect(slicedMessages).toEqual([]);
    });

    it('returns all messages if historyCount exceeds the array length', () => {
      const config = { enableHistoryCount: true, historyCount: 5 } as LobeAgentConfig;
      const slicedMessages = chatHelpers.getSlicedMessagesWithConfig(messages, config);
      expect(slicedMessages).toEqual(messages);
    });

    it('returns an empty array for an empty message array', () => {
      const config = { enableHistoryCount: true, historyCount: 2 } as LobeAgentConfig;
      const slicedMessages = chatHelpers.getSlicedMessagesWithConfig([], config);
      expect(slicedMessages).toEqual([]);
    });
  });
});
