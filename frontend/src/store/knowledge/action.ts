
import useSWR, { SWRResponse } from 'swr';
import type { StateCreator } from 'zustand/vanilla';

import { knowledgeService } from '@/services/knowledge';

import { globalHelpers } from '@/store/global/helpers';
import { KnowledgeFormFields, KnowledgeList, Reseponse } from '@/types/knowledge';

import type { Store } from './store';

export interface StoreAction {
  listData: KnowledgeList;
  useFetchKnowledgeList: () => SWRResponse<Reseponse<KnowledgeList>>;
  useFetchKnowledgeAdd: (arg: KnowledgeFormFields) => Promise<Reseponse<KnowledgeFormFields>>;
  useFetchKnowledgeDel: (name: string)=> Promise<Reseponse<{}>>;
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
});
