import { ChatModelCard } from "../llm";

export type CustomModels = { displayName: string; id: string }[];

export interface OpenAIConfig {
  OPENAI_API_KEY: string;
  azureApiVersion?: string;
  /**
   * custom mode name for fine-tuning or openai like model
   */
  customModelName?: string;
  enabled: boolean;
  endpoint?: string;
  /**
   * @deprecated
   */
  models?: string[];
  useAzure?: boolean;
}

export interface AzureOpenAIConfig {
  apiKey: string;
  apiVersion?: string;
  deployments: string;
  enabled: boolean;
  endpoint?: string;
  models?: ChatModelCard[]
}

export interface ZhiPuConfig {
  apiKey?: string;
  enabled: boolean;
  endpoint?: string;
  models?: ChatModelCard[]
}

export interface MoonshotConfig {
  apiKey?: string;
  enabled: boolean;
  models?: ChatModelCard[]
}

export interface GoogleConfig {
  apiKey?: string;
  enabled: boolean;
  endpoint?: string;
  models?: ChatModelCard[]
}

export interface AWSBedrockConfig {
  accessKeyId?: string;
  enabled: boolean;
  region?: string;
  secretAccessKey?: string;
  models?: ChatModelCard[]
}

export interface OllamaConfig {
  customModelName?: string;
  enabled?: boolean;
  endpoint?: string;
  models?: ChatModelCard[]
}

export interface PerplexityConfig {
  apiKey?: string;
  enabled: boolean;
  endpoint?: string;
  models?: ChatModelCard[]
}

export interface AnthropicConfig {
  apiKey?: string;
  enabled: boolean;
  models?: ChatModelCard[]
}

export interface MistralConfig {
  apiKey?: string;
  enabled: boolean;
  models?: ChatModelCard[]
}

export interface ChatChatConfig {
  customModelName?: string;
  enabled?: boolean;
  endpoint?: string;
  models?: ChatModelCard[]
}

export interface GlobalLLMConfig {
  anthropic: AnthropicConfig;
  azure: AzureOpenAIConfig;
  bedrock: AWSBedrockConfig;
  google: GoogleConfig;
  mistral: MistralConfig;
  moonshot: MoonshotConfig;
  ollama: OllamaConfig;
  openAI: OpenAIConfig;
  perplexity: PerplexityConfig;
  zhipu: ZhiPuConfig;
  chatchat: ChatChatConfig;
}

export type GlobalLLMProviderKey = keyof GlobalLLMConfig;
