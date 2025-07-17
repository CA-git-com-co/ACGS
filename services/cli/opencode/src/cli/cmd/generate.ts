// Constitutional Hash: cdd01ef066bc6cf2

import { Server } from "../../server/server"
import fs from "fs/promises"
import path from "path"
import type { CommandModule } from "yargs"
import { withACGSCompliance } from "../../acgs/middleware"

export const GenerateCommand = {
  command: "generate",
  handler: withACGSCompliance(async () => {
    const specs = await Server.openapi()
    const dir = "gen"
    await fs.rmdir(dir, { recursive: true }).catch(() => {})
    await fs.mkdir(dir, { recursive: true })
    await Bun.write(
      path.join(dir, "openapi.json"),
      JSON.stringify(specs, null, 2),
    )
  }, "generate_command"),
} satisfies CommandModule
