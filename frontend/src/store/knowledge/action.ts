
import useSWR, { SWRResponse } from 'swr';
import type { StateCreator } from 'zustand/vanilla';

import { knowledgeService } from '@/services/knowledge';

import { globalHelpers } from '@/store/global/helpers';
import {
  KnowledgeFormFields, KnowledgeList, Reseponse, KnowledgeFilesList,
  KnowledgeDelDocsParams, KnowledgeDelDocsRes,
  KnowledgeRebuildVectorParams, KnowledgeRebuildVectorRes

} from '@/types/knowledge';
import type { FetchSSEOptions } from '@/utils/fetch';

import type { Store } from './store';

export interface StoreAction {
  listData: KnowledgeList;
  useFetchKnowledgeList: () => SWRResponse<Reseponse<KnowledgeList>>;
  useFetchKnowledgeAdd: (arg: KnowledgeFormFields) => Promise<Reseponse<KnowledgeFormFields>>;
  useFetchKnowledgeDel: (name: string) => Promise<Reseponse<{}>>;

  // files
  filesData: KnowledgeFilesList;
  useFetchKnowledgeFilesList: (name: string) => SWRResponse<Reseponse<KnowledgeFilesList>>;
  useFetchKnowledgeUploadDocs: (arg: FormData) => Promise<Reseponse<{}>>;
  useFetchKnowledgeDownloadDocs: (kbName: string, docName: string) => Promise<Reseponse<{}>>;
  useFetcDelInknowledgeDB: (arg: KnowledgeDelDocsParams) => Promise<Reseponse<KnowledgeDelDocsRes>>;
  useFetcRebuildVectorDB: (arg: KnowledgeRebuildVectorParams, options: { 
    onFinish: FetchSSEOptions["onFinish"]; 
    onMessageHandle: FetchSSEOptions["onMessageHandle"] 
  }) => void;

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
  useFetchKnowledgeDel: async (name) => {
    return await knowledgeService.del(name)
  },


  filesData: [],
  useFetchKnowledgeFilesList: (knowledge_base_name) => {
    return useSWR<Reseponse<KnowledgeFilesList>>(
      globalHelpers.getCurrentLanguage(),
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
  useFetcRebuildVectorDB: (params, options) => {
    return knowledgeService.rebuildVectorDB(params, options);
  }

});
