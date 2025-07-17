// Constitutional Hash: cdd01ef066bc6cf2

import type { CommandModule } from "yargs"

export function cmd<T, U>(input: CommandModule<T, U>) {
  return input
}
