import { produce } from 'immer';
import pMap from 'p-map';
import { StateCreator } from 'zustand/vanilla';

import { fileService } from '@/services/file';
import { imageGenerationService } from '@/services/imageGeneration';
import { chatSelectors } from '@/store/chat/selectors';
import { ChatStore } from '@/store/chat/store';
import { DallEImageItem } from '@/types/tool/dalle';
import { setNamespace } from '@/utils/storeDebug';

const n = setNamespace('tool');

/**
 * builtin tool action
 */
export interface ChatToolAction {
  generateImageFromPrompts: (items: DallEImageItem[], id: string) => Promise<void>;
  text2image: (id: string, data: DallEImageItem[]) => Promise<void>;
  toggleDallEImageLoading: (key: string, value: boolean) => void;
  updateImageItem: (id: string, updater: (data: DallEImageItem[]) => void) => Promise<void>;
}

export const chatToolSlice: StateCreator<
  ChatStore,
  [['zustand/devtools', never]],
  [],
  ChatToolAction
> = (set, get) => ({
  generateImageFromPrompts: async (items, messageId) => {
    const { toggleDallEImageLoading, updateImageItem } = get();
    // eslint-disable-next-line unicorn/consistent-function-scoping
    const getMessageById = (id: string) => chatSelectors.getMessageById(id)(get());

    const message = getMessageById(messageId);
    if (!message) return;

    const parent = getMessageById(message!.parentId!);
    const originPrompt = parent?.content;

    await pMap(items, async (params, index) => {
      toggleDallEImageLoading(messageId + params.prompt, true);
      const url = await imageGenerationService.generateImage(params);

      await updateImageItem(messageId, (draft) => {
        draft[index].previewUrl = url;
      });

      toggleDallEImageLoading(messageId + params.prompt, false);

      fileService
        .uploadImageByUrl(url, {
          metadata: { ...params, originPrompt: originPrompt },
          name: `${originPrompt || params.prompt}_${index}.png`,
        })
        .then(({ id }) => {
          updateImageItem(messageId, (draft) => {
            draft[index].imageId = id;
            draft[index].previewUrl = undefined;
          });
        });
    });
  },
  text2image: async (id, data) => {
    // const isAutoGen = settingsSelectors.isDalleAutoGenerating(useGlobalStore.getState());
    // if (!isAutoGen) return;

    await get().generateImageFromPrompts(data, id);
  },
  toggleDallEImageLoading: (key, value) => {
    set(
      { dalleImageLoading: { ...get().dalleImageLoading, [key]: value } },
      false,
      n('toggleDallEImageLoading'),
    );
  },
  updateImageItem: async (id, updater) => {
    const message = chatSelectors.getMessageById(id)(get());
    if (!message) return;

    const data: DallEImageItem[] = JSON.parse(message.content);

    const nextContent = produce(data, updater);
    await get().internalUpdateMessageContent(id, JSON.stringify(nextContent));
  },
});
