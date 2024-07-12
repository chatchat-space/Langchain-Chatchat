import { subscribeWithSelector, devtools, persist } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';
import { createWithEqualityFn } from 'zustand/traditional';
import type { StateCreator } from 'zustand/vanilla'; 
 
import { isDev } from '@/utils/env';

import { type StoreAction, createKnowledgeAction } from './action'; 
export type Store = StoreAction;
 
const createStore: StateCreator<Store, [['zustand/devtools', never]]> = (...parameters) => ({ 
  ...createKnowledgeAction(...parameters),
});
 
export const useKnowledgeStore = createWithEqualityFn<Store>()(
  subscribeWithSelector(
    devtools(createStore, {
      name: 'ChatChat_Chat' + (isDev ? '_DEV' : ''),
    }),
  ),
  shallow,
);
