import { OpenAIStream, StreamingTextResponse } from 'ai';
import OpenAI, { ClientOptions } from 'openai';

import { LobeRuntimeAI } from '../BaseAI';
import { AgentRuntimeErrorType } from '../error';
import { ChatCompetitionOptions, ChatStreamPayload, ModelProvider } from '../types';
import { AgentRuntimeError } from '../utils/createError';
import { debugStream } from '../utils/debugStream';
import { desensitizeUrl } from '../utils/desensitizeUrl';
import { handleOpenAIError } from '../utils/handleOpenAIError';
import { Stream } from 'openai/streaming';

const DEFAULT_BASE_URL = 'http://localhost:7861/v1';
// const DEFAULT_BASE_URL = 'https://beige-points-count.loca.lt/v1';


export class LobeChatChatAI implements LobeRuntimeAI {
  private client: OpenAI;

  baseURL: string;

  constructor({ apiKey = 'chatChat', baseURL = DEFAULT_BASE_URL, ...res }: ClientOptions) {
    if (!baseURL) throw AgentRuntimeError.createError(AgentRuntimeErrorType.InvalidChatChatArgs);

    this.client = new OpenAI({ apiKey, baseURL, ...res });
    this.baseURL = baseURL;
  }

  async chat(payload: ChatStreamPayload, options?: ChatCompetitionOptions) {

    try {
      const response = await this.client.chat.completions.create(
        payload as unknown as (OpenAI.ChatCompletionCreateParamsStreaming | OpenAI.ChatCompletionCreateParamsNonStreaming),
      );

      if (LobeChatChatAI.isStream(response)) {

        const [prod, debug] = response.tee();

        if (process.env.DEBUG_OLLAMA_CHAT_COMPLETION === '1') {
          debugStream(debug.toReadableStream()).catch(console.error);
        }

        return new StreamingTextResponse(OpenAIStream(prod, options?.callback), {
          headers: options?.headers,
        });
      } else {

        if (process.env.DEBUG_OLLAMA_CHAT_COMPLETION === '1') {
          console.debug(JSON.stringify(response));
        }

        const stream = LobeChatChatAI.createChatCompletionStream(response?.choices[0].message.content || '');

        return new StreamingTextResponse(stream);
      }
    } catch (error) {
      let desensitizedEndpoint = this.baseURL;

      if (this.baseURL !== DEFAULT_BASE_URL) {
        desensitizedEndpoint = desensitizeUrl(this.baseURL);
      }

      if ('status' in (error as any)) {
        switch ((error as Response).status) {
          case 401: {
            throw AgentRuntimeError.chat({
              endpoint: desensitizedEndpoint,
              error: error as any,
              errorType: AgentRuntimeErrorType.InvalidChatChatArgs,
              provider: ModelProvider.ChatChat,
            });
          }

          default: {
            break;
          }
        }
      }

      const { errorResult, RuntimeError } = handleOpenAIError(error);

      const errorType = RuntimeError || AgentRuntimeErrorType.ChatChatBizError;

      throw AgentRuntimeError.chat({
        endpoint: desensitizedEndpoint,
        error: errorResult,
        errorType,
        provider: ModelProvider.ChatChat,
      });
    }
  }

  static isStream(obj: unknown): obj is Stream<OpenAI.Chat.Completions.ChatCompletionChunk> {
    return typeof Stream !== 'undefined' && (obj instanceof Stream || obj instanceof ReadableStream);
  }


  // 创建一个类型为 Stream<string> 的流
  static createChatCompletionStream(text: string): ReadableStream<string> {

    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(text);
        controller.close();
      },
    });

    return stream;
  }

}