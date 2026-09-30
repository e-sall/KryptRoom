import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

async function source(relativePath) {
  return readFile(path.join(repositoryRoot, relativePath), 'utf8')
}

test('private join policy keeps identifiers and the handoff secret', async () => {
  const manifestText = await source(
    'demos/cancer-collaboration/private-join-job.json'
  )
  const manifest = JSON.parse(manifestText)

  assert.equal(manifest.outputPolicy.resultMode, 'cardinality-only')
  assert.equal(manifest.outputPolicy.revealMatchedIdentifiers, false)
  assert.equal(
    manifest.outputPolicy.futureIdentifierDisclosure.requiresExplicitOptIn,
    true
  )
  assert.equal(manifest.mpcHandoff.visibility, 'secret-shared')
  assert.equal(manifest.mpcHandoff.includesIdentifiers, false)
  assert.equal(manifest.controlPlaneDataAccess, 'none')
  assert.doesNotMatch(manifestText, /P00[1-7]/u)
})

test('runtime reconstructs only the cardinality object', async () => {
  const runtime = await source('engines/mpc/private_join.py')
  const revealCalls = runtime.match(/sf\.reveal\s*\(([^)]*)\)/gu) ?? []

  assert.deepEqual(revealCalls, ['sf.reveal(cardinality_for_local_party)'])
  assert.doesNotMatch(runtime, /\.psi(?:_df|_csv|_join_df|_join_csv)?\s*\(/u)
  assert.match(runtime, /user_specified_num_returns=3/u)
  assert.match(runtime, /secret_cardinality = secure_device\(intersection_cardinality\)/u)
  assert.doesNotMatch(runtime, /flax|optimizer|gradient|train(?:ing)?\s*\(/iu)
})

test('each container mounts only its participant local dataset', async () => {
  const compose = await source('compose.private-join.yml')
  const labA = compose.slice(compose.indexOf('  lab-a:'), compose.indexOf('  lab-b:'))
  const labB = compose.slice(compose.indexOf('  lab-b:'), compose.indexOf('\nnetworks:'))

  assert.match(labA, /lab-a\/private-join\.csv:\/data\/local\.csv:ro/u)
  assert.doesNotMatch(labA, /lab-b\/private-join\.csv/u)
  assert.match(labB, /lab-b\/private-join\.csv:\/data\/local\.csv:ro/u)
  assert.doesNotMatch(labB, /lab-a\/private-join\.csv/u)
  assert.doesNotMatch(compose, /:\/workspace(?::|\s)/u)
})
