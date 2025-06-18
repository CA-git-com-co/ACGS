export type KeyboardShortcut = {
  key: string
  ctrlKey?: boolean
  metaKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
}

export function matchesShortcut(
  event: KeyboardEvent,
  shortcut: KeyboardShortcut
): boolean {
  return (
    event.key.toLowerCase() === shortcut.key.toLowerCase() &&
    event.ctrlKey === (shortcut.ctrlKey ?? false) &&
    event.metaKey === (shortcut.metaKey ?? false) &&
    event.shiftKey === (shortcut.shiftKey ?? false) &&
    event.altKey === (shortcut.altKey ?? false)
  )
}

export const SHORTCUTS = {
  COMMAND_PALETTE: { key: 'k', metaKey: true, ctrlKey: true },
  ESCAPE: { key: 'Escape' },
} as const