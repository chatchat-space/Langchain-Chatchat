import { memo, useMemo } from 'react';
import { Md5 } from 'ts-md5';

import { useGlobalStore } from '@/store/global';
import { settingsSelectors } from '@/store/global/selectors';
import { useSessionStore } from '@/store/session';
import { agentSelectors } from '@/store/session/selectors';

import FilePlayer from './FilePlayer';
import InitPlayer, { TTSProps } from './InitPlayer';

const TTS = memo<TTSProps>(
  (props) => {
    const { file, voice, content, contentMd5 } = props;
    const lang = useGlobalStore(settingsSelectors.currentLanguage);
    const currentVoice = useSessionStore(agentSelectors.currentAgentTTSVoice(lang));

    const md5 = useMemo(() => Md5.hashStr(content).toString(), [content]);

    const isContentEqual = contentMd5 === md5;
    const isVoiceEqual = currentVoice === voice;
    const isEqual = isVoiceEqual && isContentEqual;

    const PlayerRender = file && isEqual ? FilePlayer : InitPlayer;

    return <PlayerRender {...props} contentMd5={md5} />;
  },
  (prevProps, nextProps) => {
    return prevProps.id === nextProps.id && prevProps.content === nextProps.content;
  },
);
export default TTS;
