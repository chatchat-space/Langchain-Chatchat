/*
 * @Autor: lycheng
 * @Date: 2019-12-27 15:21:38
 * @Description: 
 */
function writeString(data, offset, str) {
  for (var i = 0; i < str.length; i++) {
    data.setUint8(offset + i, str.charCodeAt(i))
  }
}

/**
 * 加wav头
 * @param {音频arrayBuffer} bytes 
 * @param {采样率} sampleRate 
 * @param {声道数} numChannels 
 * @param {sampleBits} oututSampleBits 
 * @param {小端字节} littleEdian 
 */
function encodeWAV(
  bytes,
  sampleRate,
  numChannels,
  oututSampleBits,
  littleEdian = true
) {
  let sampleBits = oututSampleBits
  let buffer = new ArrayBuffer(44 + bytes.byteLength)
  let data = new DataView(buffer)
  let channelCount = numChannels
  let offset = 0
  // 资源交换文件标识符
  writeString(data, offset, 'RIFF')
  offset += 4
  // 下个地址开始到文件尾总字节数,即文件大小-8
  data.setUint32(offset, 36 + bytes.byteLength, true)
  offset += 4
  // WAV文件标志
  writeString(data, offset, 'WAVE')
  offset += 4
  // 波形格式标志
  writeString(data, offset, 'fmt ')
  offset += 4
  // 过滤字节,一般为 0x10 = 16
  data.setUint32(offset, 16, true)
  offset += 4
  // 格式类别 (PCM形式采样数据)
  data.setUint16(offset, 1, true)
  offset += 2
  // 通道数
  data.setUint16(offset, channelCount, true)
  offset += 2
  // 采样率,每秒样本数,表示每个通道的播放速度
  data.setUint32(offset, sampleRate, true)
  offset += 4
  // 波形数据传输率 (每秒平均字节数) 单声道×每秒数据位数×每样本数据位/8
  data.setUint32(offset, channelCount * sampleRate * (sampleBits / 8), true)
  offset += 4
  // 快数据调整数 采样一次占用字节数 单声道×每样本的数据位数/8
  data.setUint16(offset, channelCount * (sampleBits / 8), true)
  offset += 2
  // 每样本数据位数
  data.setUint16(offset, sampleBits, true)
  offset += 2
  // 数据标识符
  writeString(data, offset, 'data')
  offset += 4
  // 采样数据总数,即数据总大小-44
  data.setUint32(offset, bytes.byteLength, true)
  offset += 4

  // 给wav头增加pcm体
  for (let i = 0; i < bytes.byteLength; ) {
    data.setUint8(offset, bytes.getUint8(i), true)
    offset++
    i++
  }

  return data
}

function downloadWAV(audioData, sampleRate, oututSampleBits) {
  let wavData = encodeWAV(audioData, sampleRate||44100, 1, oututSampleBits||16) 
  let blob = new Blob([wavData], {
    type: 'audio/wav',
  })
  let defaultName = new Date().getTime()
  let node = document.createElement('a')
  node.href = window.URL.createObjectURL(blob)
  node.download = `${defaultName}.wav`
  node.click()
  node.remove()
}

function downloadPCM(audioData) {
  let blob = new Blob([audioData], {
    type: 'audio/pcm',
  })
  let defaultName = new Date().getTime()
  let node = document.createElement('a')
  node.href = window.URL.createObjectURL(blob)
  node.download = `${defaultName}.pcm`
  node.click()
  node.remove()
}
export {
  downloadWAV,
  downloadPCM
}