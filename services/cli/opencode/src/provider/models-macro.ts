// Constitutional Hash: cdd01ef066bc6cf2

export async function data() {
  const json = await fetch("https://models.dev/api.json").then((x) => x.text())
  return json
}
