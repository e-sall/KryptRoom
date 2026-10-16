import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

async function source(relativePath) {
  return readFile(path.join(repositoryRoot, relativePath), 'utf8')
}

async function rows(relativePath) {
  const [header, ...lines] = (await source(relativePath)).trim().split(/\r?\n/u)
  const columns = header.split(',')
  return lines.map((line) => {
    const values = line.split(',')
    return Object.fromEntries(columns.map((column, index) => [column, values[index]]))
  })
}

test('M2.5 manifest defines immutable S1 with list-valued parents', async () => {
  const manifest = JSON.parse(
    await source('demos/cancer-collaboration/persistent-state-job.json')
  )

  assert.equal(manifest.operation, 'persist-private-join')
  assert.equal(manifest.stateId, 'S1')
  assert.deepEqual(manifest.transition.parentStateIds, [])
  assert.deepEqual(manifest.transition.outputArtifactIds, [
    'match-mask',
    'lab-a-features',
    'lab-b-features'
  ])
  assert.equal(manifest.cryptoContext.protocol, 'CHEETAH')
  assert.equal(manifest.cryptoContext.field, 'FM128')
  assert.equal(manifest.cryptoContext.artifactCipher, 'AES-256-GCM')
  assert.equal(manifest.cryptoContext.keyScope, 'per-kryptnode-local')
})

test('fixture aggregate for the post-restart MPC check is 68', async () => {
  // Cleartext is used only to establish the expected synthetic test answer.
  const [labA, labB] = await Promise.all([
    rows('demos/cancer-collaboration/lab-a/private-join.csv'),
    rows('demos/cancer-collaboration/lab-b/private-join.csv')
  ])
  const rightById = new Map(
    labB.map((row) => [row.patient_id, Number(row.treatment_response)])
  )
  const aggregate = labA.reduce(
    (sum, row) =>
      rightById.has(row.patient_id)
        ? sum + Number(row.genomic_score) + rightById.get(row.patient_id)
        : sum,
    0
  )

  assert.equal(aggregate, 68)
})

test('RoomState types are immutable and committed before storage', async () => {
  const runtime = await source('engines/mpc/room_state.py')
  const requiredTypes = [
    'RoomState',
    'ArtifactRef',
    'StateTransition',
    'StatePolicy',
    'CryptoContext',
    'StateCommitment'
  ]

  for (const type of requiredTypes) {
    assert.match(runtime, new RegExp(`@dataclass\\(frozen=True\\)\\r?\\nclass ${type}:`, 'u'))
  }
  assert.match(runtime, /os\.O_CREAT \| os\.O_EXCL/u)
  assert.match(runtime, /state\.verify\(\)/u)
  assert.match(runtime, /RoomState commitment verification failed/u)
})

test('RoomState schema closes each public contract', async () => {
  const schema = JSON.parse(await source('packages/manifests/room-state.schema.json'))
  const definitions = schema.$defs

  assert.equal(schema.additionalProperties, false)
  for (const name of [
    'artifactRef',
    'stateTransition',
    'statePolicy',
    'cryptoContext',
    'stateCommitment'
  ]) {
    assert.equal(definitions[name].additionalProperties, false)
  }
  assert.equal(definitions.artifactRef.properties.includesIdentifiers.const, false)
  assert.equal(definitions.statePolicy.properties.defaultReveal.const, 'deny')
})
