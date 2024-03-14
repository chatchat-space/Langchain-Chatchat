import { LobeAgentConfig } from '@/types/agent';

import { BaseDataModel, MetaData } from './meta';

export enum LobeSessionType {
  Agent = 'agent',
  Group = 'group',
}

export type SessionGroupId = SessionDefaultGroup | string;

export enum SessionDefaultGroup {
  Default = 'default',
  Pinned = 'pinned',
}

export interface SessionGroupItem {
  createdAt: number;
  id: string;
  name: string;
  sort?: number;
  updatedAt: number;
}

export type SessionGroups = SessionGroupItem[];

/**
 * Lobe Agent
 */
export interface LobeAgentSession extends BaseDataModel {
  config: LobeAgentConfig;
  group?: SessionGroupId;
  pinned?: boolean;
  type: LobeSessionType.Agent;
}

export interface LobeAgentSettings {
  /**
   * 语言模型角色设定
   */
  config: LobeAgentConfig;
  meta: MetaData;
}

export type LobeSessions = LobeAgentSession[];

export interface CustomSessionGroup {
  children: LobeSessions;
  id: SessionGroupId;
  name: string;
}

export interface ChatSessionList {
  all: LobeSessions;
  customGroup: CustomSessionGroup[];
  default: LobeSessions;
  pinned: LobeSessions;
}
