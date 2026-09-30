import { spawn } from 'node:child_process'
import { setTimeout as delay } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const demoDirectory = path.dirname(fileURLToPath(import.meta.url))
const repositoryRoot = path.resolve(demoDirectory, '../..')
const serverScript = path.join(
  repositoryRoot,
  'nodes/krypt-node/src/psi-server.mjs'
)
const clientScript = path.join(
  repositoryRoot,
  'nodes/krypt-node/src/psi-client.mjs'
)
const labAData = path.join(demoDirectory, 'lab-a/patients.csv')
const labBData = path.join(demoDirectory, 'lab-b/patients.csv')

const server = spawn(process.execPath, [serverScript], {
  cwd: repositoryRoot,
  env: {
    ...process.env,
    KRYPTROOM_INPUT_PATH: labAData,
    KRYPTROOM_HOST: '127.0.0.1',
    KRYPTROOM_PORT: '5300'
  },
  stdio: ['ignore', 'pipe', 'pipe']
})
const serverExit = new Promise((resolve) => server.once('close', resolve))

let serverOutput = ''
server.stdout.on('data', (chunk) => {
  serverOutput += chunk.toString('utf8')
})
server.stderr.on('data', (chunk) => {
  serverOutput += chunk.toString('utf8')
})

try {
  const deadline = Date.now() + 10_000
  while (Date.now() < deadline) {
    try {
      const health = await fetch('http://127.0.0.1:5300/health')
      if (health.ok) break
    } catch {
      await delay(100)
    }
  }

  const client = spawn(process.execPath, [clientScript], {
    cwd: repositoryRoot,
    env: {
      ...process.env,
      KRYPTROOM_INPUT_PATH: labBData,
      KRYPTROOM_PSI_ENDPOINT: 'http://127.0.0.1:5300/v1/psi/cardinality'
    },
    stdio: ['ignore', 'pipe', 'pipe']
  })
  const clientExit = new Promise((resolve) => client.once('close', resolve))

  let clientOutput = ''
  for await (const chunk of client.stdout) clientOutput += chunk.toString('utf8')
  for await (const chunk of client.stderr) clientOutput += chunk.toString('utf8')
  const clientExitCode = await clientExit

  if (clientExitCode !== 0) {
    throw new Error(`Lab B KryptNode failed:\n${clientOutput}`)
  }

  const resultLine = clientOutput
    .trim()
    .split(/\r?\n/u)
    .findLast((line) => line.startsWith('{'))
  const result = JSON.parse(resultLine)

  if (result.intersectionCardinality !== 2) {
    throw new Error('Unexpected PSI cardinality')
  }

  if (/P00[1-7]/u.test(`${serverOutput}\n${clientOutput}`)) {
    throw new Error('A KryptNode output disclosed a patient identifier')
  }

  console.log(JSON.stringify(result, null, 2))
} finally {
  server.kill('SIGTERM')
  await Promise.race([
    serverExit,
    delay(2_000)
  ])
}

