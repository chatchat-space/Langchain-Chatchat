interface Model {
  id: string;
  created: number; // 时间戳
  platform_name: string;
  owned_by: string;
  object: string;
  tokens?: number;
  displayName?: string;
}

export interface ModelsResponse {
  object?: 'list';
  data?: Model[];
  error?: string;
}