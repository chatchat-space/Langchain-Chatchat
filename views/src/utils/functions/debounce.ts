type CallbackFunc<T extends unknown[]> = (...args: T) => void

export function debounce<T extends unknown[]>(
  func: CallbackFunc<T>,
  wait: number,
): (...args: T) => void {
  let timeoutId: ReturnType<typeof setTimeout> | undefined

  return (...args: T) => {
    const later = () => {
      clearTimeout(timeoutId)
      func(...args)
    }

    clearTimeout(timeoutId)
    timeoutId = setTimeout(later, wait)
  }
}
