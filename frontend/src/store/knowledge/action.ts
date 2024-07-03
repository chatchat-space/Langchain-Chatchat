
import useSWR, { SWRResponse } from 'swr';
import type { StateCreator } from 'zustand/vanilla';
import { knowledgeService } from '@/services/knowledge';
import { globalHelpers } from '@/store/global/helpers';

import type {
  KnowledgeFormFields, KnowledgeList, Reseponse, KnowledgeFilesList,
  KnowledgeDelDocsParams, KnowledgeDelDocsRes,
  KnowledgeRebuildVectorParams, KnowledgeUplodDocsParams, KnowledgeUplodDocsRes,
  ReAddVectorDBParams, ReAddVectorDBRes,
  KnowledgeSearchDocsParams, KnowledgeSearchDocsList, KnowledgeSearchDocsListItem, KnowledgeUpdateDocsParams
} from '@/types/knowledge';
import type { FetchSSEOptions } from '@/utils/fetch';

import type { Store } from './store';

export interface StoreAction {

  // 当前编辑的知识库
  editKnowledgeInfo: null | KnowledgeFormFields;
  setEditKnowledge: (data: KnowledgeFormFields) => void;

  // 知识库数据列表
  listData: KnowledgeList;
  useFetchKnowledgeList: () => SWRResponse<Reseponse<KnowledgeList>>;
  useFetchKnowledgeAdd: (arg: KnowledgeFormFields) => Promise<Reseponse<KnowledgeFormFields>>;
  useFetchKnowledgeUpdate: (arg: Partial<KnowledgeFormFields>) => Promise<Reseponse<KnowledgeFormFields>>;
  useFetchKnowledgeDel: (name: string) => Promise<Reseponse<{}>>;

  // files
  filesData: KnowledgeFilesList;
  useFetchKnowledgeFilesList: (name: string) => SWRResponse<Reseponse<KnowledgeFilesList>>;
  useFetchKnowledgeUploadDocs: (arg: FormData) => Promise<Reseponse<{}>>;
  // useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => Promise<Reseponse<{}>>;
  useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => Promise<void>;
  useFetcDelInknowledgeDB: (arg: KnowledgeDelDocsParams) => Promise<Reseponse<KnowledgeDelDocsRes>>;
  useFetcDelInVectorDB: (arg: KnowledgeDelDocsParams) => Promise<Reseponse<KnowledgeDelDocsRes>>;
  useFetcRebuildVectorDB: (arg: KnowledgeRebuildVectorParams, options: {
    onFinish: FetchSSEOptions["onFinish"];
    onMessageHandle: FetchSSEOptions["onMessageHandle"]
  }) => void;
  useFetcReAddVectorDB: (arg: ReAddVectorDBParams) => Promise<Reseponse<ReAddVectorDBRes>>; 

  fileSearchData: KnowledgeSearchDocsList;
  // useFetchSearchDocs:  (arg: KnowledgeSearchDocsParams) => SWRResponse<Reseponse<KnowledgeSearchDocsList>>;
  useFetchSearchDocs:  (arg: KnowledgeSearchDocsParams) => SWRResponse<KnowledgeSearchDocsList>;
  useFetcUpdateDocs:  (arg: KnowledgeUpdateDocsParams) => Promise<Reseponse<{}>>; 
  editContentInfo: null | KnowledgeSearchDocsListItem;
  setEditContentInfo: (data: KnowledgeSearchDocsListItem) => void;
}

export const createKnowledgeAction: StateCreator<
  Store,
  [['zustand/devtools', never]],
  [],
  StoreAction
> = (set, get) => ({
  listData: [],
  useFetchKnowledgeList: () => {
    return useSWR<Reseponse<KnowledgeList>>(
      globalHelpers.getCurrentLanguage(),
      knowledgeService.getList,
      {
        onSuccess: (res) => {
          set({ listData: res.data })
        },
      },
    )
  },
  useFetchKnowledgeAdd: async (formValues) => {
    return await knowledgeService.add(formValues)
  },
  useFetchKnowledgeUpdate: async (formValues) => {
    return await knowledgeService.update(formValues)
  },
  useFetchKnowledgeDel: async (name) => {
    return await knowledgeService.del(name)
  },
  filesData: [],
  useFetchKnowledgeFilesList: (knowledge_base_name) => {
    return useSWR<Reseponse<KnowledgeFilesList>>(
      [globalHelpers.getCurrentLanguage(), knowledge_base_name],
      knowledgeService.getFilesList(knowledge_base_name),
      {
        onSuccess: (res) => {
          set({ filesData: res.data })
        },
      },
    )
  },
  useFetchKnowledgeUploadDocs: (formData) => {
    return knowledgeService.uploadDocs(formData);
  },
  useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => {
    return knowledgeService.downloadDocs(kbName, docName);
  },
  useFetcDelInknowledgeDB: (params) => {
    return knowledgeService.delInknowledgeDB(params);
  },
  useFetcDelInVectorDB: async (name) => {
    return await knowledgeService.delVectorDocs(name)
  },
  useFetcRebuildVectorDB: (params, options) => {
    return knowledgeService.rebuildVectorDB(params, options);
  },
  useFetcReAddVectorDB: (params) => {
    return knowledgeService.reAddVectorDB(params);
  },


  editKnowledgeInfo: null,
  setEditKnowledge: (data) => {
    set({ editKnowledgeInfo: data })
  },
  
  
  fileSearchData: [],
  useFetchSearchDocs: (params) => {
    // return useSWR<Reseponse<KnowledgeSearchDocsList>>(
    return useSWR<KnowledgeSearchDocsList>(
      globalHelpers.getCurrentLanguage(),
      ()=> knowledgeService.searchDocs(params),
      {
        onSuccess: (res) => {
          // set({ fileSearchData: res.data })
          set({ fileSearchData: res })
        },
      },
    )
  },
  useFetcUpdateDocs: (params) => {
    return knowledgeService.updateDocs(params);
  }, 
  editContentInfo: null,
  setEditContentInfo: (data) => {
    set({ editContentInfo: data })
  },

});
