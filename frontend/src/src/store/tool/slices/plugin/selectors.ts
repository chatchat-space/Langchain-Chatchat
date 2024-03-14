import { LobeChatPluginManifest } from '@lobehub/chat-plugin-sdk';
import { uniq } from 'lodash-es';

import { InstallPluginMeta, LobeToolCustomPlugin } from '@/types/tool/plugin';

import type { ToolStoreState } from '../../initialState';

const installedPlugins = (s: ToolStoreState) => s.installedPlugins;

const isPluginInstalled = (id: string) => (s: ToolStoreState) =>
  installedPlugins(s).some((i) => i.identifier === id);

const getInstalledPluginById = (id: string) => (s: ToolStoreState) =>
  installedPlugins(s).find((p) => p.identifier === id);

const getPluginMetaById = (id: string) => (s: ToolStoreState) => {
  // first try to find meta from store
  const storeMeta = s.pluginStoreList.find((i) => i.identifier === id)?.meta;
  if (storeMeta) return storeMeta;

  // then use installed meta
  return getInstalledPluginById(id)(s)?.manifest?.meta;
};

const getCustomPluginById = (id: string) => (s: ToolStoreState) =>
  installedPlugins(s).find((i) => i.identifier === id && i.type === 'customPlugin') as
    | LobeToolCustomPlugin
    | undefined;

const getPluginManifestById = (id: string) => (s: ToolStoreState) =>
  getInstalledPluginById(id)(s)?.manifest;

const getPluginSettingsById = (id: string) => (s: ToolStoreState) =>
  getInstalledPluginById(id)(s)?.settings || {};

const storeAndInstallPluginsIdList = (s: ToolStoreState) =>
  uniq(
    [
      s.installedPlugins.map((i) => i.identifier),
      s.pluginStoreList.map((i) => i.identifier),
    ].flat(),
  );

const installedPluginManifestList = (s: ToolStoreState) =>
  installedPlugins(s)
    .map((i) => i.manifest as LobeChatPluginManifest)
    .filter((i) => !!i);

const installedPluginMetaList = (s: ToolStoreState) =>
  installedPlugins(s).map<InstallPluginMeta>((p) => ({
    author: p.manifest?.author,
    createdAt: p.manifest?.createdAt || (p.manifest as any)?.createAt,
    homepage: p.manifest?.homepage,
    identifier: p.identifier,
    meta: getPluginMetaById(p.identifier)(s),
    type: p.type,
  }));
const installedCustomPluginMetaList = (s: ToolStoreState) =>
  installedPluginMetaList(s).filter((p) => p.type === 'customPlugin');

const isPluginHasUI = (id: string) => (s: ToolStoreState) => {
  const plugin = getPluginManifestById(id)(s);

  return !!plugin?.ui;
};

export const pluginSelectors = {
  getCustomPluginById,
  getInstalledPluginById,
  getPluginManifestById,
  getPluginMetaById,
  getPluginSettingsById,
  installedCustomPluginMetaList,
  installedPluginManifestList,
  installedPluginMetaList,
  installedPlugins,
  isPluginHasUI,
  isPluginInstalled,
  storeAndInstallPluginsIdList,
};
