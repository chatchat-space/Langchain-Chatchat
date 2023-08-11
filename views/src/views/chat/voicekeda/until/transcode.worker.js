

self.onmessage = function(e){
  transAudioData.transcode(e.data)
}
let transAudioData = {
  transcode(audioData) {
    let output = transAudioData.to16kHz(audioData)
    output = transAudioData.to16BitPCM(output)
    output = Array.from(new Uint8Array(output.buffer))
    self.postMessage(output)
    // return output
  },
  to16kHz(audioData) {
    var data = new Float32Array(audioData)
    var fitCount = Math.round(data.length * (16000 / 44100))
    var newData = new Float32Array(fitCount)
    var springFactor = (data.length - 1) / (fitCount - 1)
    newData[0] = data[0]
    for (let i = 1; i < fitCount - 1; i++) {
      var tmp = i * springFactor
      var before = Math.floor(tmp).toFixed()
      var after = Math.ceil(tmp).toFixed()
      var atPoint = tmp - before
      newData[i] = data[before] + (data[after] - data[before]) * atPoint
    }
    newData[fitCount - 1] = data[data.length - 1]
    return newData
  },
  to16BitPCM(input) {
    var dataLength = input.length * (16 / 8)
    var dataBuffer = new ArrayBuffer(dataLength)
    var dataView = new DataView(dataBuffer)
    var offset = 0
    for (var i = 0; i < input.length; i++, offset += 2) {
      var s = Math.max(-1, Math.min(1, input[i]))
      dataView.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
    }
    return dataView
  },
}
