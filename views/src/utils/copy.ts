export function copyToClip(text: string) {
  return new Promise((resolve, reject) => {
    try {
      const input: HTMLTextAreaElement = document.createElement('textarea')
      input.setAttribute('readonly', 'readonly')
      input.value = text
      document.body.appendChild(input)
      input.select()
      if (document.execCommand('copy'))
        document.execCommand('copy')
      document.body.removeChild(input)
      resolve(text)
    }
    catch (error) {
      reject(error)
    }
  })
}
