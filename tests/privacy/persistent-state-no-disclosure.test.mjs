import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

async function source(relativePath) {
  return readFile(path.join(repositoryRoot, relativePath), 'utf8')
}

test('persistent state is default-deny with explicit aggregate authorization', async () => {
  const manifestText = await source(
    'demos/cancer-collaboration/persistent-state-job.json'
  )
  const manifest = JSON.parse(manifestText)
  const reveals = new Map(
    manifest.statePolicy.authorizedReveals.map((entry) => [entry.name, entry.recipients])
  )

  assert.equal(manifest.statePolicy.defaultReveal, 'deny')
  assert.equal(manifest.statePolicy.plaintextMaterialization, 'forbidden')
  assert.equal(manifest.statePolicy.matchedIdentifierReveal, 'forbidden')
  assert.equal(
    manifest.statePolicy.futureIdentifierDisclosure.requiresExplicitOptIn,
    true
  )
  assert.deepEqual(reveals.get('intersection-cardinality'), ['lab-a', 'lab-b', 'ui'])
  assert.deepEqual(reveals.get('matched-feature-sum'), ['lab-a', 'lab-b'])
  assert.equal(reveals.has('matched-identifiers'), false)
  assert.doesNotMatch(manifestText, /P00[1-7]/u)
})

test('every runtime reconstruction is guarded by StatePolicy', async () => {
  const runtime = await source('engines/mpc/persistent_room_state.py')
  const revealCalls = runtime.match(/sf\.reveal\s*\(([^)]*)\)/gu) ?? []

  assert.deepEqual(revealCalls, [
    'sf.reveal(participant_values)',
    'sf.reveal(encrypted_metadata)'
  ])
  assert.match(
    runtime,
    /require_authorized_reveal\(policy, reveal_name, recipients\)[\s\S]*sf\.reveal\(participant_values\)/u
  )
  assert.match(
    runtime,
    /require_authorized_reveal\(policy, "ciphertext-metadata", PARTIES\)[\s\S]*sf\.reveal\(encrypted_metadata\)/u
  )
  assert.doesNotMatch(runtime, /sf\.reveal\s*\(handoff/u)
  assert.doesNotMatch(runtime, /matched[_-]?identifiers?\s*=/iu)
})

test('persisted shares use authenticated encryption and context-bound AAD', async () => {
  const storage = await source('engines/mpc/room_state.py')

  assert.match(storage, /AESGCM\(_read_key\(self\._key_path\)\)\.encrypt/u)
  assert.match(storage, /AESGCM\(_read_key\(self\._key_path\)\)\.decrypt/u)
  for (const binding of [
    'artifactId',
    'cryptoContextId',
    'party',
    'roomId',
    'stateId'
  ]) {
    assert.match(storage, new RegExp(`"${binding}"`, 'u'))
  }
  assert.match(storage, /AESGCM\.generate_key\(bit_length=256\)/u)
})

test('analytics restart has no participant input mount', async () => {
  const analyticsCompose = await source('compose.persistent-state.yml')
  const persistOverride = await source('compose.persistent-state.persist.yml')

  assert.doesNotMatch(analyticsCompose, /private-join\.csv/u)
  assert.doesNotMatch(analyticsCompose, /\/data\/local\.csv/u)
  assert.match(persistOverride, /lab-a\/private-join\.csv:\/data\/local\.csv:ro/u)
  assert.match(persistOverride, /lab-b\/private-join\.csv:\/data\/local\.csv:ro/u)
})
