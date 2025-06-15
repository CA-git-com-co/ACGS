'use client'

import * as React from 'react'
import { Command } from 'cmdk'
import { Search, FileText, Vote, Settings, Plus } from 'lucide-react'
import { useKeyboard } from '@/hooks/useKeyboard'
import { SHORTCUTS } from '@/lib/keyboard'
import { cn } from '@/lib/utils'

interface CommandItem {
  id: string
  label: string
  icon: React.ReactNode
  keywords: string[]
  onSelect: () => void
}

const commands: CommandItem[] = [
  {
    id: 'new-policy',
    label: 'Create New Policy',
    icon: <Plus className="h-4 w-4" />,
    keywords: ['create', 'new', 'policy', 'add'],
    onSelect: () => console.log('Creating new policy...'),
  },
  {
    id: 'new-proposal',
    label: 'Create New Proposal',
    icon: <Vote className="h-4 w-4" />,
    keywords: ['create', 'new', 'proposal', 'vote'],
    onSelect: () => console.log('Creating new proposal...'),
  },
  {
    id: 'view-policies',
    label: 'View All Policies',
    icon: <FileText className="h-4 w-4" />,
    keywords: ['view', 'policies', 'list'],
    onSelect: () => console.log('Viewing policies...'),
  },
  {
    id: 'settings',
    label: 'Open Settings',
    icon: <Settings className="h-4 w-4" />,
    keywords: ['settings', 'preferences', 'config'],
    onSelect: () => console.log('Opening settings...'),
  },
]

export function CommandBar() {
  const [open, setOpen] = React.useState(false)

  useKeyboard(
    SHORTCUTS.COMMAND_PALETTE,
    () => setOpen((open) => !open),
    [setOpen]
  )

  useKeyboard(
    SHORTCUTS.ESCAPE,
    () => setOpen(false),
    [setOpen]
  )

  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [open])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs animate-fade-in"
      onClick={() => setOpen(false)}
    >
      <div className="fixed left-1/2 top-1/2 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 p-4">
        <Command
          className={cn(
            'overflow-hidden rounded-lg border bg-base-white shadow-command animate-scale-in',
            'dark:bg-gray-800 dark:border-gray-700'
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center border-b border-gray-200 dark:border-gray-700 px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 text-gray-400" />
            <Command.Input
              placeholder="Type a command or search..."
              className="flex h-11 w-full rounded-md bg-transparent py-3 text-body outline-none placeholder:text-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
            />
            <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-gray-200 bg-gray-100 px-1.5 text-[10px] font-medium text-gray-600 dark:border-gray-700 dark:bg-gray-700 dark:text-gray-400">
              ESC
            </kbd>
          </div>
          <Command.List className="max-h-[300px] overflow-y-auto overflow-x-hidden">
            <Command.Empty className="py-6 text-center text-body text-gray-500">
              No results found.
            </Command.Empty>
            <Command.Group heading="Actions" className="p-2">
              {commands.map((command) => (
                <Command.Item
                  key={command.id}
                  value={command.label}
                  keywords={command.keywords}
                  onSelect={() => {
                    command.onSelect()
                    setOpen(false)
                  }}
                  className={cn(
                    'relative flex cursor-default select-none items-center rounded-md px-2 py-2 text-body outline-none',
                    'data-[selected=true]:bg-accent-primary data-[selected=true]:text-base-white',
                    'hover:bg-accent-primary hover:text-base-white'
                  )}
                >
                  <div className="mr-2">{command.icon}</div>
                  <span>{command.label}</span>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  )
}