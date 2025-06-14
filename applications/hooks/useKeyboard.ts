'use client'

import { useEffect } from 'react'
import { matchesShortcut, KeyboardShortcut } from '@/lib/keyboard'

export function useKeyboard(
  shortcut: KeyboardShortcut,
  callback: (event: KeyboardEvent) => void,
  dependencies: any[] = []
) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (matchesShortcut(event, shortcut)) {
        event.preventDefault()
        callback(event)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [shortcut, callback, ...dependencies])
}