import type { ThemeMode } from 'antd-style';

import { LobeAgentTTSConfig } from '@/types/agent';
import { FewShots, LLMParams } from '@/types/llm';
import { MetaData } from '@/types/meta';
import { STTServer } from '@/types/settings';

interface V4LobeAgentConfig {
  autoCreateTopicThreshold: number;
  compressThreshold?: number;
  displayMode?: 'chat' | 'docs';
  enableAutoCreateTopic: boolean;
  /**
   * 历史消息长度压缩阈值
   */
  enableCompressThreshold?: boolean;
  /**
   * 开启历史记录条数
   */
  enableHistoryCount?: boolean;
  enableMaxTokens?: boolean;

  fewShots?: FewShots;
  /**
   * 历史消息条数
   */
  historyCount?: number;
  inputTemplate?: string;
  /**
   * 角色所使用的语言模型
   * @default gpt-3.5-turbo
   */
  model: string;
  /**
   * 语言模型参数
   */
  params: LLMParams;
  /**
   * 启用的插件
   */
  plugins?: string[];
  /**
   *  模型供应商
   */
  provider?: string;
  /**
   * 系统角色
   */
  systemRole: string;
  /**
   * 语音服务
   */
  tts: LobeAgentTTSConfig;
}

interface V4DefaultAgent {
  config: V4LobeAgentConfig;
  meta: MetaData;
}

interface V4OpenAIConfig {
  OPENAI_API_KEY: string;
  azureApiVersion?: string;
  customModelName?: string;
  endpoint?: string;
  models?: string[];
  useAzure?: boolean;
}

interface V4LLMConfig {
  openAI: V4OpenAIConfig;
}

interface V4Tool {
  dalle: {
    autoGenerate: boolean;
  };
}
interface V4TTSConfig {
  openAI: {
    sttModel: 'whisper-1';
    ttsModel: 'tts-1' | 'tts-1-hd';
  };
  sttAutoStop: boolean;
  sttServer: STTServer;
}

export interface V4Settings {
  avatar: string;
  defaultAgent: V4DefaultAgent;
  fontSize: number;
  language: string;
  languageModel: V4LLMConfig;
  neutralColor?: string;
  password: string;
  primaryColor?: string;
  themeMode: ThemeMode;
  tool: V4Tool;
  tts: V4TTSConfig;
}
