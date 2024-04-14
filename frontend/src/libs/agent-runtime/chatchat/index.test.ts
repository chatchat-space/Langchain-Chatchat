// @vitest-environment node
import OpenAI from 'openai';
import { Mock, afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ChatStreamCallbacks } from '@/libs/agent-runtime';

import * as debugStreamModule from '../utils/debugStream';
import { LobeChatChatAI } from './index';

const provider = 'knowledge';
const defaultBaseURL = 'http://localhost:7861/v1';
const bizErrorType = 'knowledgeBizError';
const invalidErrorType = 'InvalidKnowledgeArgs';

// Mock the console.error to avoid polluting test output
vi.spyOn(console, 'error').mockImplementation(() => {});

let instance: LobeChatChatAI;

beforeEach(() => {
  instance = new LobeChatChatAI({ apiKey: 'knowledge', baseURL: defaultBaseURL });

  // 使用 vi.spyOn 来模拟 chat.completions.create 方法
  vi.spyOn(instance['client'].chat.completions, 'create').mockResolvedValue(
    new ReadableStream() as any,
  );
});

afterEach(() => {
  vi.clearAllMocks();
});

describe('LobeChatChatAI', () => {

  describe('init', ()=>{
    it('should init with default baseURL', () => {
      expect(instance.baseURL).toBe(defaultBaseURL);
    });
  })

  describe('chat', () => {
    it('should return a StreamingTextResponse on successful API call', async () => {
      // Arrange
      const mockStream = new ReadableStream();
      const mockResponse = Promise.resolve(mockStream);

      (instance['client'].chat.completions.create as Mock).mockResolvedValue(mockResponse);

      // Act
      const result = await instance.chat({
        messages: [{ content: 'Hello', role: 'user' }],
        model: 'gpt-3.5-turbo',
        temperature: 0,
      });

      // Assert
      expect(result).toBeInstanceOf(Response);
    });

    it('should return a StreamingTextResponse on successful API call', async () => {
      // Arrange
      const mockResponse = Promise.resolve({
        "id": "chatcmpl-98QIb3NiYLYlRTB6t0VrJ0wntNW6K",
        "object": "chat.completion",
        "created": 1711794745,
        "model": "gpt-3.5-turbo-0125",
        "choices": [
          {
            "index": 0,
            "message": {
              "role": "assistant",
              "content": "你好！有什么可以帮助你的吗？"
            },
            "logprobs": null,
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 9,
          "completion_tokens": 17,
          "total_tokens": 26
        },
        "system_fingerprint": "fp_b28b39ffa8"
      });

      (instance['client'].chat.completions.create as Mock).mockResolvedValue(mockResponse);

      // Act
      const result = await instance.chat({
        messages: [{ content: 'Hello', role: 'user' }],
        model: 'gpt-3.5-turbo',
        stream: false,
        temperature: 0,
      });

      // Assert
      expect(result).toBeInstanceOf(Response);
    });
  })


});