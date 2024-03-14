import { Mock, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';

import { CreateTopicParams, TopicModel } from '@/database/models/topic';
import { ChatTopic } from '@/types/topic';

import { topicService } from '../topic';

// Mock the TopicModel
vi.mock('@/database/models/topic', () => {
  return {
    TopicModel: {
      create: vi.fn(),
      query: vi.fn(),
      delete: vi.fn(),
      batchDeleteBySessionId: vi.fn(),
      batchDelete: vi.fn(),
      clearTable: vi.fn(),
      toggleFavorite: vi.fn(),
      batchCreate: vi.fn(),
      update: vi.fn(),
      queryAll: vi.fn(),
      queryByKeyword: vi.fn(),
    },
  };
});

describe('TopicService', () => {
  // Mock data
  const mockTopicId = 'mock-topic-id';
  const mockTopic: ChatTopic = {
    createdAt: 100,
    updatedAt: 100,
    id: mockTopicId,
    title: 'Mock Topic',
  };
  const mockTopics = [mockTopic];

  beforeEach(() => {
    // Reset all mocks before running each test case
    vi.resetAllMocks();
  });

  describe('createTopic', () => {
    it('should create a topic and return its id', async () => {
      // Setup
      const createParams: CreateTopicParams = {
        title: 'New Topic',
        sessionId: '1',
      };
      (TopicModel.create as Mock).mockResolvedValue(mockTopic);

      // Execute
      const topicId = await topicService.createTopic(createParams);

      // Assert
      expect(TopicModel.create).toHaveBeenCalledWith(createParams);
      expect(topicId).toBe(mockTopicId);
    });
    it('should throw an error if topic creation fails', async () => {
      // Setup
      const createParams: CreateTopicParams = {
        title: 'New Topic',
        sessionId: '1',
      };

      (TopicModel.create as Mock).mockResolvedValue(null);

      // Execute & Assert
      await expect(topicService.createTopic(createParams)).rejects.toThrow('topic create Error');
    });
  });

  describe('getTopics', () => {
    // Example for getTopics
    it('should query topics with given parameters', async () => {
      // Setup
      const queryParams = { sessionId: 'session-id' };
      (TopicModel.query as Mock).mockResolvedValue(mockTopics);

      // Execute
      const topics = await topicService.getTopics(queryParams);

      // Assert
      expect(TopicModel.query).toHaveBeenCalledWith(queryParams);
      expect(topics).toBe(mockTopics);
    });
  });

  describe('updateFavorite', () => {
    // Example for updateFavorite
    it('should toggle favorite status of a topic', async () => {
      // Setup
      const newState = true;
      (TopicModel.toggleFavorite as Mock).mockResolvedValue({ ...mockTopic, favorite: newState });

      // Execute
      const result = await topicService.updateFavorite(mockTopicId, newState);

      // Assert
      expect(TopicModel.toggleFavorite).toHaveBeenCalledWith(mockTopicId, newState);
      expect(result).toEqual({ ...mockTopic, favorite: newState });
    });
  });

  describe('removeTopic', () => {
    it('should remove a topic by id', async () => {
      // Setup
      (TopicModel.delete as Mock).mockResolvedValue(true);

      // Execute
      const result = await topicService.removeTopic(mockTopicId);

      // Assert
      expect(TopicModel.delete).toHaveBeenCalledWith(mockTopicId);
      expect(result).toBe(true);
    });
  });

  describe('removeTopics', () => {
    it('should remove all topics with a given session id', async () => {
      // Setup
      const sessionId = 'session-id';
      (TopicModel.batchDeleteBySessionId as Mock).mockResolvedValue(true);

      // Execute
      const result = await topicService.removeTopics(sessionId);

      // Assert
      expect(TopicModel.batchDeleteBySessionId).toHaveBeenCalledWith(sessionId);
      expect(result).toBe(true);
    });
  });

  describe('batchRemoveTopics', () => {
    it('should batch remove topics', async () => {
      // Setup
      const topicIds = [mockTopicId, 'another-topic-id'];
      (TopicModel.batchDelete as Mock).mockResolvedValue(true);

      // Execute
      const result = await topicService.batchRemoveTopics(topicIds);

      // Assert
      expect(TopicModel.batchDelete).toHaveBeenCalledWith(topicIds);
      expect(result).toBe(true);
    });
  });

  describe('removeAllTopic', () => {
    it('should clear all topics from the table', async () => {
      // Setup
      (TopicModel.clearTable as Mock).mockResolvedValue(true);

      // Execute
      const result = await topicService.removeAllTopic();

      // Assert
      expect(TopicModel.clearTable).toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });

  describe('batchCreateTopics', () => {
    it('should batch create topics', async () => {
      // Setup
      (TopicModel.batchCreate as Mock).mockResolvedValue(mockTopics);

      // Execute
      const result = await topicService.batchCreateTopics(mockTopics);

      // Assert
      expect(TopicModel.batchCreate).toHaveBeenCalledWith(mockTopics);
      expect(result).toBe(mockTopics);
    });
  });

  describe('updateTitle', () => {
    it('should update the title of a topic', async () => {
      // Setup
      const newTitle = 'Updated Topic Title';
      (TopicModel.update as Mock).mockResolvedValue({ ...mockTopic, title: newTitle });

      // Execute
      const result = await topicService.updateTitle(mockTopicId, newTitle);

      // Assert
      expect(TopicModel.update).toHaveBeenCalledWith(mockTopicId, { title: newTitle });
      expect(result).toEqual({ ...mockTopic, title: newTitle });
    });
  });

  describe('getAllTopics', () => {
    it('should retrieve all topics', async () => {
      // Setup
      (TopicModel.queryAll as Mock).mockResolvedValue(mockTopics);

      // Execute
      const result = await topicService.getAllTopics();

      // Assert
      expect(TopicModel.queryAll).toHaveBeenCalled();
      expect(result).toBe(mockTopics);
    });
  });

  describe('searchTopics', () => {
    it('should return topics that match the keyword', async () => {
      // Setup
      const keyword = 'search';
      (TopicModel.queryByKeyword as Mock).mockResolvedValue(mockTopics);

      // Execute
      const result = await topicService.searchTopics(keyword);

      // Assert
      expect(TopicModel.queryByKeyword).toHaveBeenCalledWith(keyword);
      expect(result).toBe(mockTopics);
    });
  });
});
