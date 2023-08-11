//
//  tts-ws.ts
//  科大讯飞语音合成
//
//  Created by panhong on 2023/07/20.
//
import { downloadPCM, downloadWAV } from './download.js';
import CryptoES from "crypto-es"; // 科大讯飞
import Enc from 'enc';
const transWorker = new Worker(
	new URL("../kedatts/transcode.worker.js", import.meta.url)
);
import VConsole from 'vconsole';
import { Base64 } from 'js-base64';

/**
 * 获取websocket url
 * APPID，APISecret，APIKey在控制台-我的应用-语音合成（流式版）页面获取，正式使用需要后端配置返回避免泄露
 */
const APPID = "";
const API_SECRET = "";
const API_KEY = "";

function getWebsocketUrl(): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    var apiKey = API_KEY;
    var apiSecret = API_SECRET;
    var url = 'wss://tts-api.xfyun.cn/v2/tts';
    var host = location.host;
    var date = new Date().toGMTString();
    var algorithm = 'hmac-sha256';
    var headers = 'host date request-line';
    var signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v2/tts HTTP/1.1`;
    var signatureSha = CryptoES.HmacSHA256(signatureOrigin, apiSecret);
    var signature = CryptoES.enc.Base64.stringify(signatureSha);
    var authorizationOrigin = `api_key="${apiKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`;
    var authorization = btoa(authorizationOrigin);
    url = `${url}?authorization=${authorization}&date=${date}&host=${host}`;
    resolve(url);
  });
}


class TTSRecorder {
  private speed: number;
  private voice: number;
  private pitch: number;
  private voiceName: string;
  private text: string;
  private tte: string;
  private defaultText: string;
  private appId: string;
  private audioData: number[];
  private rawAudioData: number[];
  private audioDataOffset: number;
  private status: string;
  private ttsWS: WebSocket;
  private playTimeout: ReturnType<typeof setTimeout> | null;
  private audioContext: AudioContext | null;
  private bufferSource: AudioBufferSourceNode | null;

  constructor({
    speed = 50,
    voice = 50,
    pitch = 50,
    voiceName = 'xiaoyan',
    appId = APPID,
    text = '',
    tte = 'UTF8',
    defaultText = '请输入您要合成的文本',
  }: {
    speed?: number;
    voice?: number;
    pitch?: number;
    voiceName?: string;
    appId?: string;
    text?: string;
    tte?: string;
    defaultText?: string;
  } = {}) {
    this.speed = speed;
    this.voice = voice;
    this.pitch = pitch;
    this.voiceName = voiceName;
    this.text = text;
    this.tte = tte;
    this.defaultText = defaultText;
    this.appId = appId;
    this.audioData = [];
    this.rawAudioData = [];
    this.audioDataOffset = 0;
    this.status = 'init';
    this.ttsWS = null;
    this.playTimeout = null;
    this.audioContext = null;
    this.bufferSource = null;
    transWorker.onmessage = (e: MessageEvent) => {
			// if(e.data != undefined && e.data.length > 0) {
				this.audioData.push(...e.data.data);
				this.rawAudioData.push(...e.data.rawAudioData);
			// }
    };
  }

  // 修改录音听写状态
  private setStatus(status: string) {
    if (this.onWillStatusChange) {
      this.onWillStatusChange(this.status, status);
    }
    this.status = status;
  }

  // 设置合成相关参数
  public setParams({ speed, voice, pitch, text, voiceName, tte }: {
    speed?: number;
    voice?: number;
    pitch?: number;
    text?: string;
    voiceName?: string;
    tte?: string;
  }) {
    speed !== undefined && (this.speed = speed);
    voice !== undefined && (this.voice = voice);
    pitch !== undefined && (this.pitch = pitch);
    text && (this.text = text);
    tte && (this.tte = tte);
    voiceName && (this.voiceName = voiceName);
    this.resetAudio();
  }

  // 连接websocket
  private connectWebSocket() {
    this.setStatus('ttsing');
    return getWebsocketUrl().then(url => {
      let ttsWS: WebSocket;
      if ('WebSocket' in window) {
        ttsWS = new WebSocket(url);
      } else if ('MozWebSocket' in window) {
        ttsWS = new MozWebSocket(url);
      } else {
        alert('浏览器不支持WebSocket');
        return;
      }
      this.ttsWS = ttsWS;
      ttsWS.onopen = e => {
        this.webSocketSend();
        this.playTimeout = setTimeout(() => {
          this.audioPlay();
        }, 1000);
      };
      ttsWS.onmessage = e => {
        this.result(e.data);
      };
      ttsWS.onerror = e => {
        clearTimeout(this.playTimeout);
        this.setStatus('errorTTS');
        alert('WebSocket报错，请f12查看详情');
        console.error(`详情查看：${encodeURI(url.replace('wss:', 'https:'))}`);
      };
      ttsWS.onclose = e => {
        console.log(e);
      };
    });
  }

  // 处理音频数据
  private transToAudioData(audioData: number[]) {
    // Implement your logic here
  }

  // websocket发送数据
	// bgs有背景音 0:无背景音（默认值） 1:有背景音
	// auf 音频采样率，可选值：
	// audio/L16;rate=8000：合成8K 的音频
	// audio/L16;rate=16000：合成16K 的音频
	// auf不传值：合成16K 的音频
	// aue：音频编码，可选值：
	// raw：未压缩的pcm
	// lame：mp3 (当aue=lame时需传参sfl=1)
	// speex-org-wb;7： 标准开源speex（for speex_wideband，即16k）数字代表指定压缩等级（默认等级为8）
	// speex-org-nb;7： 标准开源speex（for speex_narrowband，即8k）数字代表指定压缩等级（默认等级为8）
	// speex;7：压缩格式，压缩等级1~10，默认为7（8k讯飞定制speex）
	// speex-wb;7：压缩格式，压缩等级1~10，默认为7（16k讯飞定制speex）
  private webSocketSend() {
    var params = {
      common: {
        app_id: this.appId, // APPID
      },
      business: {
        aue: 'raw',
        auf: 'audio/L16;rate=16000',
        vcn: this.voiceName,
        speed: this.speed,
        volume: this.voice,
        pitch: this.pitch,
        bgs: 0,
        tte: this.tte,
      },
      data: {
        status: 2,
        text: this.encodeText(
          this.text || this.defaultText,
          this.tte === 'unicode' ? 'base64&utf16le' : ''
        ),
      },
    };
    this.ttsWS.send(JSON.stringify(params));
  }

  private encodeText(text: string, encoding: string): ArrayBuffer | string {
    switch (encoding) {
      case 'utf16le': {
        let buf = new ArrayBuffer(text.length * 4);
        let bufView = new Uint16Array(buf);
        for (let i = 0, strlen = text.length; i < strlen; i++) {
          bufView[i] = text.charCodeAt(i);
        }
        return buf;
      }
      case 'buffer2Base64': {
        let binary = '';
        let bytes = new Uint8Array(text);
        let len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
      }
      case 'base64&utf16le': {
        return this.encodeText(
          this.encodeText(text, 'utf16le') as string,
          'buffer2Base64'
        );
      }
      default: {
        return Base64.encode(text);
      }
    }
  }

  // websocket接收数据的处理
  private result(resultData: string) {
    let jsonData = JSON.parse(resultData);
    // 合成失败
    if (jsonData.code !== 0) {
      alert(`合成失败: ${jsonData.code}:${jsonData.message}`);
      console.error(`${jsonData.code}:${jsonData.message}`);
      this.resetAudio();
      return;
    }
    transWorker.postMessage(jsonData.data.audio);

    if (jsonData.code === 0 && jsonData.data.status === 2) {
      this.ttsWS.close();
    }
  }

  // 重置音频数据
  private resetAudio() {
    this.audioStop();
    this.setStatus('init');
    this.audioDataOffset = 0;
    this.audioData = [];
    this.rawAudioData = [];
    this.ttsWS && this.ttsWS.close();
    clearTimeout(this.playTimeout);
  }

  // 音频初始化
  private audioInit() {
    let AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      this.audioContext = new AudioContext();
      this.audioContext.resume();
      this.audioDataOffset = 0;
    }
  }

  // 音频播放
  private audioPlay() {
    this.setStatus('play');
    let audioData = this.audioData.slice(this.audioDataOffset);
    this.audioDataOffset += audioData.length;
    let audioBuffer = this.audioContext.createBuffer(1, audioData.length, 22050);
    let nowBuffering = audioBuffer.getChannelData(0);
    if (audioBuffer.copyToChannel) {
      audioBuffer.copyToChannel(
        new Float32Array(audioData),
        0,
        0
      );
    } else {
      for (let i = 0; i < audioData.length; i++) {
        nowBuffering[i] = audioData[i];
      }
    }
    let bufferSource = this.bufferSource = this.audioContext.createBufferSource();
    bufferSource.buffer = audioBuffer;
    bufferSource.connect(this.audioContext.destination);
    bufferSource.start();
    bufferSource.onended = event => {
      if (this.status !== 'play') {
        return;
      }
      if (this.audioDataOffset < this.audioData.length) {
        this.audioPlay();
      } else {
        this.audioStop();
      }
    };
  }

  // 音频播放结束
  private audioStop() {
    this.setStatus('endPlay');
    clearTimeout(this.playTimeout);
    this.audioDataOffset = 0;
    if (this.bufferSource) {
      try {
        this.bufferSource.stop();
      } catch (e) {
        console.log(e);
      }
    }
  }

  public start() {
    if (this.audioData.length) {
      this.audioPlay();
    } else {
      if (!this.audioContext) {
        this.audioInit();
      }
      if (!this.audioContext) {
        alert('该浏览器不支持webAudioApi相关接口');
        return;
      }
      this.connectWebSocket();
    }
  }

  public stop() {
    this.audioStop();
  }
}

export default TTSRecorder;
