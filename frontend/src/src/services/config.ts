import { messageService } from '@/services/message';
import { sessionService } from '@/services/session';
import { topicService } from '@/services/topic';
import { useGlobalStore } from '@/store/global';
import { settingsSelectors } from '@/store/global/selectors';
import { useSessionStore } from '@/store/session';
import { sessionSelectors } from '@/store/session/selectors';
import { ConfigFile } from '@/types/exportConfig';
import { ChatMessage } from '@/types/message';
import { LobeSessions, SessionGroupItem } from '@/types/session';
import { GlobalSettings } from '@/types/settings';
import { ChatTopic } from '@/types/topic';
import { createConfigFile, exportConfigFile } from '@/utils/config';

export interface ImportResult {
  added: number;
  errors: number;
  skips: number;
}
export interface ImportResults {
  messages?: ImportResult;
  sessionGroups?: ImportResult;
  sessions: ImportResult;
  topics?: ImportResult;
}

class ConfigService {
  /**
   * import sessions from files
   * @param sessions
   */
  importSessions = async (sessions: LobeSessions) => {
    return await sessionService.batchCreateSessions(sessions);
  };
  importMessages = async (messages: ChatMessage[]) => {
    return messageService.batchCreate(messages);
  };
  importSettings = async (settings: GlobalSettings) => {
    useGlobalStore.getState().importAppSettings(settings);
  };
  importTopics = async (topics: ChatTopic[]) => {
    return topicService.batchCreateTopics(topics);
  };
  importSessionGroups = async (sessionGroups: SessionGroupItem[]) => {
    return sessionService.batchCreateSessionGroups(sessionGroups);
  };

  importConfigState = async (config: ConfigFile): Promise<ImportResults | undefined> => {
    switch (config.exportType) {
      case 'settings': {
        await this.importSettings(config.state.settings);

        break;
      }

      case 'agents': {
        const sessionGroups = await this.importSessionGroups(config.state.sessionGroups);

        const data = await this.importSessions(config.state.sessions);
        return {
          sessionGroups: this.mapImportResult(sessionGroups),
          sessions: this.mapImportResult(data),
        };
      }

      case 'all': {
        await this.importSettings(config.state.settings);

        const sessionGroups = await this.importSessionGroups(config.state.sessionGroups);

        const [sessions, messages, topics] = await Promise.all([
          this.importSessions(config.state.sessions),
          this.importMessages(config.state.messages),
          this.importTopics(config.state.topics),
        ]);

        return {
          messages: this.mapImportResult(messages),
          sessionGroups: this.mapImportResult(sessionGroups),
          sessions: this.mapImportResult(sessions),
          topics: this.mapImportResult(topics),
        };
      }

      case 'sessions': {
        const sessionGroups = await this.importSessionGroups(config.state.sessionGroups);

        const [sessions, messages, topics] = await Promise.all([
          this.importSessions(config.state.sessions),
          this.importMessages(config.state.messages),
          this.importTopics(config.state.topics),
        ]);

        return {
          messages: this.mapImportResult(messages),
          sessionGroups: this.mapImportResult(sessionGroups),
          sessions: this.mapImportResult(sessions),
          topics: this.mapImportResult(topics),
        };
      }
    }
  };

  /**
   * export all agents
   */
  exportAgents = async () => {
    const agents = await sessionService.getAllAgents();
    const sessionGroups = await sessionService.getSessionGroups();

    const config = createConfigFile('agents', { sessionGroups, sessions: agents });

    exportConfigFile(config, 'agents');
  };

  /**
   * export all sessions
   */
  exportSessions = async () => {
    const sessions = await sessionService.getSessions();
    const sessionGroups = await sessionService.getSessionGroups();
    const messages = await messageService.getAllMessages();
    const topics = await topicService.getAllTopics();

    const config = createConfigFile('sessions', { messages, sessionGroups, sessions, topics });

    exportConfigFile(config, 'sessions');
  };

  /**
   * export a session
   */
  exportSingleSession = async (id: string) => {
    const session = this.getSession(id);
    if (!session) return;

    const messages = await messageService.getAllMessagesInSession(id);
    const topics = await topicService.getTopics({ sessionId: id });

    const config = createConfigFile('singleSession', { messages, sessions: [session], topics });

    exportConfigFile(config, `${session.meta?.title}-session`);
  };

  /**
   * export a topic
   */
  exportSingleTopic = async (sessionId: string, topicId: string) => {
    const session = this.getSession(sessionId);
    if (!session) return;

    const messages = await messageService.getMessages(sessionId, topicId);
    const topics = await topicService.getTopics({ sessionId });

    const topic = topics.find((item) => item.id === topicId);
    if (!topic) return;

    const config = createConfigFile('singleSession', {
      messages,
      sessions: [session],
      topics: [topic],
    });

    exportConfigFile(config, `${topic.title}-topic`);
  };

  exportSingleAgent = async (id: string) => {
    const agent = this.getAgent(id);
    if (!agent) return;

    const config = createConfigFile('agents', { sessionGroups: [], sessions: [agent] });

    exportConfigFile(config, agent.meta?.title || 'agent');
  };

  /**
   * export settings
   */
  exportSettings = async () => {
    const settings = this.getSettings();

    const config = createConfigFile('settings', { settings });

    exportConfigFile(config, 'settings');
  };

  /**
   * export all data
   */
  exportAll = async () => {
    const sessions = await sessionService.getSessions();
    const sessionGroups = await sessionService.getSessionGroups();
    const messages = await messageService.getAllMessages();
    const topics = await topicService.getAllTopics();
    const settings = this.getSettings();

    const config = createConfigFile('all', { messages, sessionGroups, sessions, settings, topics });

    exportConfigFile(config, 'config');
  };

  private getSettings = () => settingsSelectors.exportSettings(useGlobalStore.getState());

  private getSession = (id: string) =>
    sessionSelectors.getSessionById(id)(useSessionStore.getState());

  private getAgent = (id: string) =>
    sessionSelectors.getSessionById(id)(useSessionStore.getState());

  private mapImportResult = (input: {
    added: number;
    errors?: Error[];
    skips: string[];
  }): ImportResult => {
    return {
      added: input.added,
      errors: input.errors?.length || 0,
      skips: input.skips.length,
    };
  };
}

export const configService = new ConfigService();
