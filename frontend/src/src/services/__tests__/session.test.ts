import { Mock, beforeEach, describe, expect, it, vi } from 'vitest';

import { SessionModel } from '@/database/models/session';
import { SessionGroupModel } from '@/database/models/sessionGroup';
import { LobeAgentConfig } from '@/types/agent';
import { LobeAgentSession, LobeSessionType, SessionGroups } from '@/types/session';

import { sessionService } from '../session';

// Mock the SessionModel
vi.mock('@/database/models/session', () => {
  return {
    SessionModel: {
      create: vi.fn(),
      query: vi.fn(),
      delete: vi.fn(),
      clearTable: vi.fn(),
      update: vi.fn(),
      batchCreate: vi.fn(),
      isEmpty: vi.fn(),
      queryByKeyword: vi.fn(),
      updateConfig: vi.fn(),
      queryByGroupIds: vi.fn(),
      updatePinned: vi.fn(),
      duplicate: vi.fn(),
      queryWithGroups: vi.fn(),
    },
  };
});

// Mock the SessionGroupModel
vi.mock('@/database/models/sessionGroup', () => {
  return {
    SessionGroupModel: {
      create: vi.fn(),
      query: vi.fn(),
      delete: vi.fn(),
      clear: vi.fn(),
      update: vi.fn(),
      batchCreate: vi.fn(),
      isEmpty: vi.fn(),
      updateOrder: vi.fn(),
      queryByKeyword: vi.fn(),
      updateConfig: vi.fn(),
      queryByGroupIds: vi.fn(),
    },
  };
});

describe('SessionService', () => {
  const mockSessionId = 'mock-session-id';
  const mockSession = {
    id: mockSessionId,
    type: 'agent',
    meta: { title: 'Mock Session' },
  } as LobeAgentSession;
  const mockSessions = [mockSession];

  beforeEach(() => {
    // Reset all mocks before running each test case
    vi.resetAllMocks();
  });

  describe('createNewSession', () => {
    it('should create a new session and return its id', async () => {
      // Setup
      const sessionType = LobeSessionType.Agent;
      const defaultValue = { meta: { title: 'New Session' } } as Partial<LobeAgentSession>;
      (SessionModel.create as Mock).mockResolvedValue(mockSession);

      // Execute
      const sessionId = await sessionService.createNewSession(sessionType, defaultValue);

      // Assert
      expect(SessionModel.create).toHaveBeenCalledWith(sessionType, defaultValue);
      expect(sessionId).toBe(mockSessionId);
    });

    it('should throw an error if session creation fails', async () => {
      // Setup
      const sessionType = LobeSessionType.Agent;
      const defaultValue = { meta: { title: 'New Session' } } as Partial<LobeAgentSession>;
      (SessionModel.create as Mock).mockResolvedValue(null);

      // Execute & Assert
      await expect(sessionService.createNewSession(sessionType, defaultValue)).rejects.toThrow(
        'session create Error',
      );
    });
  });

  describe('batchCreateSessions', () => {
    it('should batch create sessions', async () => {
      // Setup
      (SessionModel.batchCreate as Mock).mockResolvedValue(mockSessions);

      // Execute
      const result = await sessionService.batchCreateSessions(mockSessions);

      // Assert
      expect(SessionModel.batchCreate).toHaveBeenCalledWith(mockSessions);
      expect(result).toBe(mockSessions);
    });
  });

  describe('getSessions', () => {
    it('should retrieve sessions with their group ids', async () => {
      // Setup
      (SessionModel.query as Mock).mockResolvedValue(mockSessions);

      // Execute
      const sessions = await sessionService.getSessions();

      // Assert
      expect(SessionModel.query).toHaveBeenCalled();
      expect(sessions).toBe(mockSessions);
    });
  });

  describe('getAllAgents', () => {
    it('should retrieve all agent sessions', async () => {
      // Setup
      // Assuming that SessionModel.query has been modified to accept filters
      const agentSessions = mockSessions.filter((session) => session.type === 'agent');
      (SessionModel.query as Mock).mockResolvedValue(agentSessions);

      // Execute
      const result = await sessionService.getAllAgents();

      // Assert
      // Assuming that SessionModel.query would be called with a filter for agents
      expect(SessionModel.query).toHaveBeenCalled(); // Add filter argument if applicable
      expect(result).toBe(agentSessions);
    });
  });

  describe('removeSession', () => {
    it('should remove a session by its id', async () => {
      // Setup
      (SessionModel.delete as Mock).mockResolvedValue(true);

      // Execute
      const result = await sessionService.removeSession(mockSessionId);

      // Assert
      expect(SessionModel.delete).toHaveBeenCalledWith(mockSessionId);
      expect(result).toBe(true);
    });
  });

  describe('removeAllSessions', () => {
    it('should clear all sessions from the table', async () => {
      // Setup
      (SessionModel.clearTable as Mock).mockResolvedValue(true);

      // Execute
      const result = await sessionService.removeAllSessions();

      // Assert
      expect(SessionModel.clearTable).toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });

  describe('updateSessionGroupId', () => {
    it('should update the group of a session', async () => {
      // Setup
      const groupId = 'new-group';
      (SessionModel.update as Mock).mockResolvedValue({ ...mockSession, group: groupId });

      // Execute
      const result = await sessionService.updateSessionGroupId(mockSessionId, groupId);

      // Assert
      expect(SessionModel.update).toHaveBeenCalledWith(mockSessionId, { group: groupId });
      expect(result).toEqual({ ...mockSession, group: groupId });
    });
  });

  describe('updateSessionMeta', () => {
    it('should update the meta of a session', async () => {
      // Setup
      const newMeta = { description: 'Updated description' };
      (SessionModel.update as Mock).mockResolvedValue({ ...mockSession, meta: newMeta });

      // Execute
      const result = await sessionService.updateSessionMeta(mockSessionId, newMeta);

      // Assert
      expect(SessionModel.update).toHaveBeenCalledWith(mockSessionId, { meta: newMeta });
      expect(result).toEqual({ ...mockSession, meta: newMeta });
    });
  });

  describe('updateSessionConfig', () => {
    it('should update the config of a session', async () => {
      // Setup
      const newConfig = { compressThreshold: 2 } as LobeAgentConfig;
      (SessionModel.updateConfig as Mock).mockResolvedValue({ ...mockSession, config: newConfig });

      // Execute
      const result = await sessionService.updateSessionConfig(mockSessionId, newConfig);

      // Assert
      expect(SessionModel.updateConfig).toHaveBeenCalledWith(mockSessionId, newConfig);
      expect(result).toEqual({ ...mockSession, config: newConfig });
    });
  });

  describe('hasSessions', () => {
    it('should return false if no sessions exist', async () => {
      // Setup
      (SessionModel.isEmpty as Mock).mockResolvedValue(true);

      // Execute
      const result = await sessionService.hasSessions();

      // Assert
      expect(SessionModel.isEmpty).toHaveBeenCalled();
      expect(result).toBe(false);
    });

    it('should return true if sessions exist', async () => {
      // Setup
      (SessionModel.isEmpty as Mock).mockResolvedValue(false);

      // Execute
      const result = await sessionService.hasSessions();

      // Assert
      expect(SessionModel.isEmpty).toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });

  describe('searchSessions', () => {
    it('should return sessions that match the keyword', async () => {
      // Setup
      const keyword = 'search';
      (SessionModel.queryByKeyword as Mock).mockResolvedValue(mockSessions);

      // Execute
      const result = await sessionService.searchSessions(keyword);

      // Assert
      expect(SessionModel.queryByKeyword).toHaveBeenCalledWith(keyword);
      expect(result).toBe(mockSessions);
    });
  });

  describe('duplicateSession', () => {
    it('should duplicate a session and return its id', async () => {
      // Setup
      const newTitle = 'Duplicated Session';
      (SessionModel.duplicate as Mock).mockResolvedValue({
        ...mockSession,
        id: 'duplicated-session-id',
      });

      // Execute
      const duplicatedSessionId = await sessionService.duplicateSession(mockSessionId, newTitle);

      // Assert
      expect(SessionModel.duplicate).toHaveBeenCalledWith(mockSessionId, newTitle);
      expect(duplicatedSessionId).toBe('duplicated-session-id');
    });
  });

  describe('getSessionsWithGroup', () => {
    it('should retrieve sessions with their group', async () => {
      // Setup
      (SessionModel.queryWithGroups as Mock).mockResolvedValue(mockSessions);

      // Execute
      const sessionsWithGroup = await sessionService.getSessionsWithGroup();

      // Assert
      expect(SessionModel.queryWithGroups).toHaveBeenCalled();
      expect(sessionsWithGroup).toBe(mockSessions);
    });
  });

  describe('updateSessionPinned', () => {
    it('should update the pinned status of a session', async () => {
      // Setup
      const pinned = true;
      (SessionModel.updatePinned as Mock).mockResolvedValue({ ...mockSession, pinned });

      // Execute
      const result = await sessionService.updateSessionPinned(mockSessionId, pinned);

      // Assert
      expect(SessionModel.updatePinned).toHaveBeenCalledWith(mockSessionId, pinned);
      expect(result).toEqual({ ...mockSession, pinned });
    });
  });

  // SessionGroup related tests
  describe('createSessionGroup', () => {
    it('should create a new session group and return its id', async () => {
      // Setup
      const groupName = 'New Group';
      const sort = 1;
      (SessionGroupModel.create as Mock).mockResolvedValue({
        id: 'new-group-id',
        name: groupName,
        sort,
      });

      // Execute
      const groupId = await sessionService.createSessionGroup(groupName, sort);

      // Assert
      expect(SessionGroupModel.create).toHaveBeenCalledWith(groupName, sort);
      expect(groupId).toBe('new-group-id');
    });
  });

  describe('batchCreateSessionGroups', () => {
    it('should batch create session groups', async () => {
      // Setup
      const groups = [
        { id: 'group-1', name: 'Group 1', sort: 1 },
        { id: 'group-2', name: 'Group 2', sort: 2 },
      ] as SessionGroups;

      (SessionGroupModel.batchCreate as Mock).mockResolvedValue(groups);

      // Execute
      const result = await sessionService.batchCreateSessionGroups(groups);

      // Assert
      expect(SessionGroupModel.batchCreate).toHaveBeenCalledWith(groups);
      expect(result).toBe(groups);
    });
  });

  describe('removeSessionGroup', () => {
    it('should remove a session group by its id', async () => {
      // Setup
      const removeChildren = true;
      (SessionGroupModel.delete as Mock).mockResolvedValue(true);

      // Execute
      const result = await sessionService.removeSessionGroup('group-id', removeChildren);

      // Assert
      expect(SessionGroupModel.delete).toHaveBeenCalledWith('group-id', removeChildren);
      expect(result).toBe(true);
    });
  });

  describe('clearSessionGroups', () => {
    it('should clear all session groups', async () => {
      // Setup
      (SessionGroupModel.clear as Mock).mockResolvedValue(true);

      // Execute
      const result = await sessionService.clearSessionGroups();

      // Assert
      expect(SessionGroupModel.clear).toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });

  describe('getSessionGroups', () => {
    it('should retrieve all session groups', async () => {
      // Setup
      const groups = [
        { id: 'group-1', name: 'Group 1', sort: 1 },
        { id: 'group-2', name: 'Group 2', sort: 2 },
      ];
      (SessionGroupModel.query as Mock).mockResolvedValue(groups);

      // Execute
      const result = await sessionService.getSessionGroups();

      // Assert
      expect(SessionGroupModel.query).toHaveBeenCalled();
      expect(result).toBe(groups);
    });
  });

  describe('updateSessionGroup', () => {
    it('should update a session group', async () => {
      // Setup
      const groupId = 'group-1';
      const data = { name: 'Updated Group', sort: 2 };
      (SessionGroupModel.update as Mock).mockResolvedValue({ id: groupId, ...data });

      // Execute
      const result = await sessionService.updateSessionGroup(groupId, data);

      // Assert
      expect(SessionGroupModel.update).toHaveBeenCalledWith(groupId, data);
      expect(result).toEqual({ id: groupId, ...data });
    });
  });

  describe('updateSessionGroupOrder', () => {
    it('should update the order of session groups', async () => {
      // Setup
      const sortMap = [
        { id: 'group-1', sort: 2 },
        { id: 'group-2', sort: 1 },
      ];
      (SessionGroupModel.updateOrder as Mock).mockResolvedValue(true);

      // Execute
      const result = await sessionService.updateSessionGroupOrder(sortMap);

      // Assert
      expect(SessionGroupModel.updateOrder).toHaveBeenCalledWith(sortMap);
      expect(result).toBe(true);
    });
  });
});
