import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { setTimeout as delay } from 'node:timers/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')
const serverScript = path.join(
  repositoryRoot,
  'nodes/krypt-node/src/psi-server.mjs'
)
const clientScript = path.join(
  repositoryRoot,
  'nodes/krypt-node/src/psi-client.mjs'
)
const labAData = path.join(
  repositoryRoot,
  'demos/cancer-collaboration/lab-a/patients.csv'
)
const labBData = path.join(
  repositoryRoot,
  'demos/cancer-collaboration/lab-b/patients.csv'
)

function collect(child) {
  let output = ''
  child.stdout.on('data', (chunk) => { output += chunk.toString('utf8') })
  child.stderr.on('data', (chunk) => { output += chunk.toString('utf8') })
  return () => output
}

test('two KryptNodes compute only the exact intersection cardinality', {
  timeout: 30_000
}, async (context) => {
  const port = 15300
  const server = spawn(process.execPath, [serverScript], {
    cwd: repositoryRoot,
    env: {
      ...process.env,
      KRYPTROOM_INPUT_PATH: labAData,
      KRYPTROOM_PORT: String(port)
    },
    stdio: ['ignore', 'pipe', 'pipe']
  })
  const serverOutput = collect(server)
  context.after(() => server.kill('SIGTERM'))

  const deadline = Date.now() + 10_000
  let ready = false
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/health`)
      ready = response.ok
      if (ready) break
    } catch {
      await delay(100)
    }
  }
  assert.equal(ready, true, `server did not start: ${serverOutput()}`)

  const client = spawn(process.execPath, [clientScript], {
    cwd: repositoryRoot,
    env: {
      ...process.env,
      KRYPTROOM_INPUT_PATH: labBData,
      KRYPTROOM_PSI_ENDPOINT:
        `http://127.0.0.1:${port}/v1/psi/cardinality`
    },
    stdio: ['ignore', 'pipe', 'pipe']
  })
  const clientOutput = collect(client)
  const exitCode = await new Promise((resolve) => client.once('close', resolve))

  assert.equal(exitCode, 0, clientOutput())
  const result = JSON.parse(clientOutput().trim().split(/\r?\n/u).at(-1))
  assert.equal(result.intersectionCardinality, 2)
  assert.equal(result.matchedIdentifiersRevealed, false)
  assert.doesNotMatch(`${serverOutput()}\n${clientOutput()}`, /P00[1-7]/u)
})

