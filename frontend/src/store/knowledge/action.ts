import useSWR, { SWRResponse } from 'swr';
import type { StateCreator } from 'zustand/vanilla';

import { knowledgeService } from '@/services/knowledge';
import { globalHelpers } from '@/store/global/helpers';
import type {
  KnowledgeDelDocsParams,
  KnowledgeDelDocsRes,
  KnowledgeFilesList,
  KnowledgeFormFields,
  KnowledgeList,
  KnowledgeRebuildVectorParams,
  KnowledgeSearchDocsList,
  KnowledgeSearchDocsListItem,
  KnowledgeSearchDocsParams,
  KnowledgeUpdateDocsParams,
  ReAddVectorDBParams,
  ReAddVectorDBRes,
  Reseponse,
} from '@/types/knowledge';
import type { FetchSSEOptions } from '@/utils/fetch';

import type { Store } from './store';

export interface StoreAction {
  editContentInfo: null | KnowledgeSearchDocsListItem;
  // 当前编辑的知识库
  editKnowledgeInfo: null | KnowledgeFormFields;

  fileSearchData: KnowledgeSearchDocsList;
  // files
  filesData: KnowledgeFilesList;
  // 知识库数据列表
  listData: KnowledgeList;
  setEditContentInfo: (data: KnowledgeSearchDocsListItem) => void;
  setEditKnowledge: (data: KnowledgeFormFields) => void;

  useFetcDelInVectorDB: (arg: KnowledgeDelDocsParams) => Promise<Reseponse<KnowledgeDelDocsRes>>;
  useFetcDelInknowledgeDB: (arg: KnowledgeDelDocsParams) => Promise<Reseponse<KnowledgeDelDocsRes>>;
  useFetcReAddVectorDB: (arg: ReAddVectorDBParams) => Promise<Reseponse<ReAddVectorDBRes>>;
  useFetcRebuildVectorDB: (
    arg: KnowledgeRebuildVectorParams,
    options: {
      onFinish: FetchSSEOptions['onFinish'];
      onMessageHandle: FetchSSEOptions['onMessageHandle'];
    },
  ) => void;
  useFetcUpdateDocs: (arg: KnowledgeUpdateDocsParams) => Promise<Reseponse<NonNullable<unknown>>>;
  useFetchKnowledgeAdd: (arg: KnowledgeFormFields) => Promise<Reseponse<KnowledgeFormFields>>;
  useFetchKnowledgeDel: (name: string) => Promise<Reseponse<NonNullable<unknown>>>;
  // useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => Promise<Reseponse<{}>>;
  useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => Promise<void>;

  useFetchKnowledgeFilesList: (name: string) => SWRResponse<Reseponse<KnowledgeFilesList>>;
  useFetchKnowledgeList: () => SWRResponse<Reseponse<KnowledgeList>>;
  useFetchKnowledgeUpdate: (
    arg: Partial<KnowledgeFormFields>,
  ) => Promise<Reseponse<KnowledgeFormFields>>;
  useFetchKnowledgeUploadDocs: (arg: FormData) => Promise<Reseponse<{}>>;
  // useFetchSearchDocs:  (arg: KnowledgeSearchDocsParams) => SWRResponse<Reseponse<KnowledgeSearchDocsList>>;
  useFetchSearchDocs: (arg: KnowledgeSearchDocsParams) => SWRResponse<KnowledgeSearchDocsList>;
}

export const createKnowledgeAction: StateCreator<
  Store,
  [['zustand/devtools', never]],
  [],
  StoreAction
> = (set, get) => ({
  editContentInfo: null,
  editKnowledgeInfo: null,
  fileSearchData: [],
  filesData: [],
  listData: [],
  setEditContentInfo: (data) => {
    set({ editContentInfo: data });
  },
  setEditKnowledge: (data) => {
    set({ editKnowledgeInfo: data });
  },
  useFetcDelInVectorDB: async (name) => {
    return await knowledgeService.delVectorDocs(name);
  },
  useFetcDelInknowledgeDB: (params) => {
    return knowledgeService.delInknowledgeDB(params);
  },
  useFetcReAddVectorDB: (params) => {
    return knowledgeService.reAddVectorDB(params);
  },
  useFetcRebuildVectorDB: (params, options) => {
    return knowledgeService.rebuildVectorDB(params, options);
  },
  useFetcUpdateDocs: (params) => {
    return knowledgeService.updateDocs(params);
  },
  useFetchKnowledgeAdd: async (formValues) => {
    return await knowledgeService.add(formValues);
  },

  useFetchKnowledgeDel: async (name) => {
    return await knowledgeService.del(name);
  },
  useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => {
    return knowledgeService.downloadDocs(kbName, docName);
  },

  useFetchKnowledgeFilesList: (knowledge_base_name) => {
    return useSWR<Reseponse<KnowledgeFilesList>>(
      [globalHelpers.getCurrentLanguage(), knowledge_base_name],
      knowledgeService.getFilesList(knowledge_base_name),
      {
        onSuccess: (res) => {
          set({ filesData: res.data });
        },
      },
    );
  },
  useFetchKnowledgeList: () => {
    return useSWR<Reseponse<KnowledgeList>>(
      globalHelpers.getCurrentLanguage(),
      knowledgeService.getList,
      {
        onSuccess: (res) => {
          set({ listData: res.data });
        },
      },
    );
  },
  useFetchKnowledgeUpdate: async (formValues) => {
    return await knowledgeService.update(formValues);
  },
  useFetchKnowledgeUploadDocs: (formData) => {
    return knowledgeService.uploadDocs(formData);
  },
  useFetchSearchDocs: (params) => {
    // return useSWR<Reseponse<KnowledgeSearchDocsList>>(
    return useSWR<KnowledgeSearchDocsList>(
      globalHelpers.getCurrentLanguage(),
      () => knowledgeService.searchDocs(params),
      {
        onSuccess: (res) => {
          // set({ fileSearchData: res.data })
          set({ fileSearchData: res });
        },
      },
    );
  },
});
