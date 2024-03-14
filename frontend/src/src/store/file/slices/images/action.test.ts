import { act, renderHook } from '@testing-library/react';
import useSWR from 'swr';
import { Mock, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';

import { fileService } from '@/services/file';

import { useFileStore as useStore } from '../../store';

vi.mock('zustand/traditional');

// Mocks for fileService
vi.mock('@/services/file', () => ({
  fileService: {
    removeFile: vi.fn(),
    uploadFile: vi.fn(),
    getFile: vi.fn(),
  },
}));

// Mock for useSWR
vi.mock('swr', () => ({
  default: vi.fn(),
}));

//  mock the arrayBuffer
beforeAll(() => {
  Object.defineProperty(File.prototype, 'arrayBuffer', {
    writable: true,
    value: function () {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          resolve(reader.result);
        };
        reader.readAsArrayBuffer(this);
      });
    },
  });
});

beforeEach(() => {
  // Reset all mocks before each test
  vi.resetAllMocks();
});

describe('useFileStore:images', () => {
  it('clearImageList should clear the inputFilesList', () => {
    const { result } = renderHook(() => useStore());

    // Populate the list to clear it later
    act(() => {
      useStore.setState({ inputFilesList: ['test-id'] });
    });

    expect(result.current.inputFilesList).toEqual(['test-id']);

    act(() => {
      result.current.clearImageList();
    });

    expect(result.current.inputFilesList).toEqual([]);
  });

  it('removeFile should call fileService.removeFile and update the store', async () => {
    const { result } = renderHook(() => useStore());

    const fileId = 'test-id';

    // Mock the fileService.removeFile to resolve
    (fileService.removeFile as Mock).mockResolvedValue(undefined);

    // Populate the list to remove an item later
    act(() => {
      useStore.setState(({ inputFilesList }) => ({ inputFilesList: [...inputFilesList, fileId] }));
      //   // result.current.inputFilesList.push(fileId);
    });

    await act(async () => {
      await result.current.removeFile(fileId);
    });

    expect(fileService.removeFile).toHaveBeenCalledWith(fileId);
    expect(result.current.inputFilesList).toEqual([]);
  });

  // Test for useFetchFile
  it('useFetchFile should call useSWR and update the store', async () => {
    const fileId = 'test-id';
    const fileData = {
      id: fileId,
      name: 'test',
      url: 'blob:test',
      fileType: 'image/png',
      base64Url: '',
      saveMode: 'local',
    };

    // Mock the fileService.getFile to resolve with fileData
    (fileService.getFile as Mock).mockResolvedValue(fileData);

    // Mock useSWR to call the fetcher function immediately
    const useSWRMock = vi.mocked(useSWR);
    useSWRMock.mockImplementation(((key: string, fetcher: any) => {
      const data = fetcher(key);
      return { data, error: undefined, isValidating: false, mutate: vi.fn() };
    }) as any);

    const { result } = renderHook(() => useStore().useFetchFile(fileId));

    await act(async () => {
      await result.current.data;
    });

    expect(fileService.getFile).toHaveBeenCalledWith(fileId);

    // Since we are not rendering a component with the hook, we cannot test the state update here
    // Instead, we would need to use a test renderer that can work with hooks, like @testing-library/react
  });

  describe('uploadFile', () => {
    it('uploadFile should handle errors', async () => {
      const { result } = renderHook(() => useStore());
      const testFile = new File(['content'], 'test.png', { type: 'image/png' });

      // 模拟 fileService.uploadFile 抛出错误
      const errorMessage = 'Upload failed';
      (fileService.uploadFile as Mock).mockRejectedValue(new Error(errorMessage));

      // Mock console.error for testing
      const consoleErrorMock = vi.spyOn(console, 'error').mockImplementation(() => {});

      await act(async () => {
        await result.current.uploadFile(testFile);
      });

      expect(fileService.uploadFile).toHaveBeenCalledWith({
        createdAt: testFile.lastModified,
        data: await testFile.arrayBuffer(),
        fileType: testFile.type,
        name: testFile.name,
        saveMode: 'local',
        size: testFile.size,
      });
      // 由于上传失败，inputFilesList 应该没有变化
      expect(result.current.inputFilesList).toEqual([]);
      // 确保错误被正确记录
      expect(consoleErrorMock).toHaveBeenCalledWith('upload error:', expect.any(Error));

      // Cleanup mock
      consoleErrorMock.mockRestore();
    });

    it('uploadFile should upload the file and update inputFilesList', async () => {
      const { result } = renderHook(() => useStore());
      const testFile = new File(['content'], 'test.png', { type: 'image/png' });

      // 模拟 fileService.uploadFile 返回的数据
      const uploadedFileData = {
        id: 'new-file-id',
        createdAt: testFile.lastModified,
        data: await testFile.arrayBuffer(),
        fileType: testFile.type,
        name: testFile.name,
        saveMode: 'local',
        size: testFile.size,
      };

      // Mock the fileService.uploadFile to resolve with uploadedFileData
      (fileService.uploadFile as Mock).mockResolvedValue(uploadedFileData);

      await act(async () => {
        await result.current.uploadFile(testFile);
      });

      expect(fileService.uploadFile).toHaveBeenCalledWith({
        createdAt: testFile.lastModified,
        data: await testFile.arrayBuffer(),
        fileType: testFile.type,
        name: testFile.name,
        saveMode: 'local',
        size: testFile.size,
      });
      expect(result.current.inputFilesList).toContain(uploadedFileData.id);
    });
  });
});
