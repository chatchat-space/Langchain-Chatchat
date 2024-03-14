import OpenAI, { ClientOptions } from 'openai';
import urlJoin from 'url-join';

import { getServerConfig } from '@/config/server';
import { ChatErrorType } from '@/types/fetch';

// create Azure OpenAI Instance
export const createAzureOpenai = (params: {
  apiVersion?: string | null;
  endpoint?: string | null;
  model: string;
  userApiKey?: string | null;
}) => {
  const { OPENAI_PROXY_URL = '', AZURE_API_VERSION, AZURE_API_KEY } = getServerConfig();

  const endpoint = !params.endpoint ? OPENAI_PROXY_URL : params.endpoint;
  const baseURL = urlJoin(endpoint, `/openai/deployments/${params.model.replace('.', '')}`); // refs: https://test-001.openai.azure.com/openai/deployments/gpt-35-turbo

  const defaultApiVersion = AZURE_API_VERSION || '2023-08-01-preview';
  const apiVersion = !params.apiVersion ? defaultApiVersion : params.apiVersion;
  const apiKey = !params.userApiKey ? AZURE_API_KEY : params.userApiKey;

  if (!apiKey) throw new Error('AZURE_API_KEY is empty', { cause: ChatErrorType.NoOpenAIAPIKey });

  const config: ClientOptions = {
    apiKey,
    baseURL,
    defaultHeaders: { 'api-key': apiKey },
    defaultQuery: { 'api-version': apiVersion },
  };

  return new OpenAI(config);
};
