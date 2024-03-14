import { message } from 'antd';
import { t } from 'i18next';
import useSWR, { SWRResponse, mutate } from 'swr';
import { DeepPartial } from 'utility-types';
import { StateCreator } from 'zustand/vanilla';

import { INBOX_SESSION_ID } from '@/const/session';
import { SESSION_CHAT_URL } from '@/const/url';
import { sessionService } from '@/services/session';
import { useGlobalStore } from '@/store/global';
import { settingsSelectors } from '@/store/global/selectors';
import { SessionStore } from '@/store/session';
import { ChatSessionList, LobeAgentSession, LobeSessionType, LobeSessions } from '@/types/session';
import { merge } from '@/utils/merge';
import { setNamespace } from '@/utils/storeDebug';

import { agentSelectors } from '../agent/selectors';
import { initLobeSession } from './initialState';
import { sessionSelectors } from './selectors';

const n = setNamespace('session');

const FETCH_SESSIONS_KEY = 'fetchSessions';

export interface SessionAction {
  /**
   * active the session
   * @param sessionId
   */
  activeSession: (sessionId: string) => void;
  /**
   * reset sessions to default
   */
  clearSessions: () => Promise<void>;
  /**
   * create a new session
   * @param agent
   * @returns sessionId
   */
  createSession: (
    session?: DeepPartial<LobeAgentSession>,
    isSwitchSession?: boolean,
  ) => Promise<string>;
  duplicateSession: (id: string) => Promise<void>;
  /**
   * Pins or unpins a session.
   */
  pinSession: (id: string, pinned: boolean) => Promise<void>;
  /**
   * re-fetch the data
   */
  refreshSessions: () => Promise<void>;
  /**
   * remove session
   * @param id - sessionId
   */
  removeSession: (id: string) => void;
  /**
   * switch session url
   */
  switchSession: (sessionId?: string) => void;
  /**
   * A custom hook that uses SWR to fetch sessions data.
   */
  useFetchSessions: () => SWRResponse<any>;
  useSearchSessions: (keyword?: string) => SWRResponse<any>;
}

export const createSessionSlice: StateCreator<
  SessionStore,
  [['zustand/devtools', never]],
  [],
  SessionAction
> = (set, get) => ({
  activeSession: (sessionId) => {
    if (get().activeId === sessionId) return;

    set({ activeId: sessionId }, false, n(`activeSession/${sessionId}`));
  },

  clearSessions: async () => {
    await sessionService.removeAllSessions();

    get().refreshSessions();
  },

  createSession: async (agent, isSwitchSession = true) => {
    const { switchSession, refreshSessions } = get();

    // 合并 settings 里的 defaultAgent
    const defaultAgent = merge(
      initLobeSession,
      settingsSelectors.defaultAgent(useGlobalStore.getState()),
    );

    const newSession: LobeAgentSession = merge(defaultAgent, agent);

    const id = await sessionService.createNewSession(LobeSessionType.Agent, newSession);
    await refreshSessions();

    // 创建后是否跳转到对应会话，默认跳转
    if (isSwitchSession) switchSession(id);

    return id;
  },

  duplicateSession: async (id) => {
    const { switchSession, refreshSessions } = get();
    const session = sessionSelectors.getSessionById(id)(get());

    if (!session) return;
    const title = agentSelectors.getTitle(session.meta);

    const newTitle = t('duplicateTitle', { ns: 'chat', title: title });

    const newId = await sessionService.duplicateSession(id, newTitle);

    // duplicate Session Error
    if (!newId) {
      message.error(t('copyFail', { ns: 'common' }));
      return;
    }

    await refreshSessions();
    switchSession(newId);
  },

  pinSession: async (sessionId, pinned) => {
    await sessionService.updateSessionPinned(sessionId, pinned);

    await get().refreshSessions();
  },

  refreshSessions: async () => {
    await mutate(FETCH_SESSIONS_KEY);
  },

  removeSession: async (sessionId) => {
    await sessionService.removeSession(sessionId);
    await get().refreshSessions();

    if (sessionId === get().activeId) {
      get().switchSession();
    }
  },

  switchSession: (sessionId = INBOX_SESSION_ID) => {
    const { isMobile, router } = get();

    get().activeSession(sessionId);

    // TODO: 后续可以把 router 移除
    router?.push(SESSION_CHAT_URL(sessionId, isMobile));
  },

  useFetchSessions: () =>
    useSWR<ChatSessionList>(FETCH_SESSIONS_KEY, sessionService.getSessionsWithGroup, {
      onSuccess: (data) => {
        // 由于 https://github.com/lobehub/lobe-chat/pull/541 的关系
        // 只有触发了 refreshSessions 才会更新 sessions，进而触发页面 rerender
        // 因此这里不能补充 equal 判断，否则会导致页面不更新
        // if (get().isSessionsFirstFetchFinished && isEqual(get().sessions, data)) return;

        // TODO：后续的根本解法应该是解除 inbox 和 session 的数据耦合
        // 避免互相依赖的情况出现

        set(
          {
            customSessionGroups: data.customGroup,
            defaultSessions: data.default,
            isSessionsFirstFetchFinished: true,
            pinnedSessions: data.pinned,
            sessions: data.all,
          },
          false,
          n('useFetchSessions/onSuccess', data),
        );
      },
    }),

  useSearchSessions: (keyword) =>
    useSWR<LobeSessions>(keyword, sessionService.searchSessions, {
      onSuccess: (data) => {
        set({ searchSessions: data }, false, n('useSearchSessions(success)', data));
      },
      revalidateOnFocus: false,
    }),
});
