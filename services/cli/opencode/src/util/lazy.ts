// Constitutional Hash: cdd01ef066bc6cf2

export function lazy<T>(fn: () => T) {
  let value: T | undefined
  let loaded = false

  return (): T => {
    if (loaded) return value as T
    loaded = true
    value = fn()
    return value as T
  }
}
