'use client';

import Link from 'next/link';
import { memo } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import PageTitle from '@/components/PageTitle';
import { MORE_MODEL_PROVIDER_REQUEST_URL } from '@/const/url';

import Footer from '../features/Footer';
import Anthropic from './Anthropic';
import Bedrock from './Bedrock';
import Google from './Google';
import Mistral from './Mistral';
import Moonshot from './Moonshot';
import Ollama from './Ollama';
import OpenAI from './OpenAI';
import Perplexity from './Perplexity';
import Zhipu from './Zhipu';

export default memo<{ showOllama: boolean }>(({ showOllama }) => {
  const { t } = useTranslation('setting');

  return (
    <>
      <PageTitle title={t('tab.llm')} />
      <OpenAI />
      {/*<AzureOpenAI />*/}
      <Zhipu />
      <Moonshot />
      <Google />
      <Bedrock />
      <Perplexity />
      <Anthropic />
      <Mistral />
      {showOllama && <Ollama />}
      <Footer>
        <Trans i18nKey="llm.waitingForMore" ns={'setting'}>
          更多模型正在
          <Link aria-label={'todo'} href={MORE_MODEL_PROVIDER_REQUEST_URL} target="_blank">
            计划接入
          </Link>
          中 ，敬请期待 ✨
        </Trans>
      </Footer>
    </>
  );
});
