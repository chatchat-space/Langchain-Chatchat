import { Mock, describe, expect, it, vi } from 'vitest';

import { chatHelpers } from '@/store/chat/helpers';
import { globalHelpers } from '@/store/global/helpers';
import { OpenAIChatMessage } from '@/types/openai/chat';

import { chainSummaryTitle } from '../summaryTitle';

// Mock the getCurrentLanguage function
vi.mock('@/store/global/helpers', () => ({
  globalHelpers: {
    getCurrentLanguage: vi.fn(),
  },
}));

// Mock the chatHelpers.getMessagesTokenCount function
vi.mock('@/store/chat/helpers', () => ({
  chatHelpers: {
    getMessagesTokenCount: vi.fn(),
  },
}));

describe('chainSummaryTitle', () => {
  it('should create a payload with system and user messages and select the appropriate model based on token count', async () => {
    // Arrange
    const messages: OpenAIChatMessage[] = [
      { content: 'Hello, how can I assist you?', role: 'assistant' },
      { content: 'I need help with my account.', role: 'user' },
    ];
    const currentLanguage = 'en-US';
    const tokenCount = 17000; // Arbitrary token count above the GPT-3.5 limit
    (globalHelpers.getCurrentLanguage as Mock).mockReturnValue(currentLanguage);
    (chatHelpers.getMessagesTokenCount as Mock).mockResolvedValue(tokenCount);

    // Act
    const result = await chainSummaryTitle(messages);

    // Assert
    expect(result).toEqual({
      messages: [
        {
          content: '你是一名擅长会话的助理，你需要将用户的会话总结为 10 个字以内的标题',
          role: 'system',
        },
        {
          content: `assistant: Hello, how can I assist you?\nuser: I need help with my account.

请总结上述对话为10个字以内的标题，不需要包含标点符号，输出语言语种为：${currentLanguage}`,
          role: 'user',
        },
      ],
      model: 'gpt-4-turbo-preview',
    });

    // Verify that getMessagesTokenCount was called with the correct messages
    expect(chatHelpers.getMessagesTokenCount).toHaveBeenCalledWith([
      {
        content: '你是一名擅长会话的助理，你需要将用户的会话总结为 10 个字以内的标题',
        role: 'system',
      },
      {
        content: `assistant: Hello, how can I assist you?\nuser: I need help with my account.

请总结上述对话为10个字以内的标题，不需要包含标点符号，输出语言语种为：${currentLanguage}`,
        role: 'user',
      },
    ]);
  });

  it('should use the default model if the token count is below the GPT-3.5 limit', async () => {
    // Arrange
    const messages: OpenAIChatMessage[] = [
      { content: 'Hello, how can I assist you?', role: 'assistant' },
      { content: 'I need help with my account.', role: 'user' },
    ];
    const currentLanguage = 'en-US';
    const tokenCount = 10000; // Arbitrary token count below the GPT-3.5 limit
    (globalHelpers.getCurrentLanguage as Mock).mockReturnValue(currentLanguage);
    (chatHelpers.getMessagesTokenCount as Mock).mockResolvedValue(tokenCount);

    // Act
    const result = await chainSummaryTitle(messages);

    // Assert
    expect(result).toEqual({
      messages: [
        {
          content: '你是一名擅长会话的助理，你需要将用户的会话总结为 10 个字以内的标题',
          role: 'system',
        },
        {
          content: `assistant: Hello, how can I assist you?\nuser: I need help with my account.

请总结上述对话为10个字以内的标题，不需要包含标点符号，输出语言语种为：${currentLanguage}`,
          role: 'user',
        },
      ],
      // No model specified since the token count is below the limit
    });

    // Verify that getMessagesTokenCount was called with the correct messages
    expect(chatHelpers.getMessagesTokenCount).toHaveBeenCalledWith([
      {
        content: '你是一名擅长会话的助理，你需要将用户的会话总结为 10 个字以内的标题',
        role: 'system',
      },
      {
        content: `assistant: Hello, how can I assist you?\nuser: I need help with my account.

请总结上述对话为10个字以内的标题，不需要包含标点符号，输出语言语种为：${currentLanguage}`,
        role: 'user',
      },
    ]);
  });
});
