interface Model {
  created: number;
  displayName?: string; 
  id: string;
  object: string;
  owned_by: string;
  // 时间戳
  platform_name: string;
  tokens?: number;
}

export interface ModelsResponse {
  data?: Model[];
  error?: string;
  object?: 'list';
}
