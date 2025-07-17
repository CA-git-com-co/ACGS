// Constitutional Hash: cdd01ef066bc6cf2

export namespace Flag {
  export const OPENCODE_AUTO_SHARE = truthy("OPENCODE_AUTO_SHARE")
  export const OPENCODE_DISABLE_WATCHER = truthy("OPENCODE_DISABLE_WATCHER")

  function truthy(key: string) {
    const value = process.env[key]?.toLowerCase()
    return value === "true" || value === "1"
  }
}
