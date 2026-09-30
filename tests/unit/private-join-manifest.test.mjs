import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

async function json(relativePath) {
  return JSON.parse(await readFile(path.join(repositoryRoot, relativePath), 'utf8'))
}

test('private join manifest pins a two-party SPU backend', async () => {
  const manifest = await json('demos/cancer-collaboration/private-join-job.json')

  assert.deepEqual(manifest.backend, {
    name: 'SecretFlow SPU',
    version: '1.14.0b0',
    protocol: 'CHEETAH',
    field: 'FM128',
    securityModel: 'semi-honest'
  })
  assert.deepEqual(
    manifest.participants.map(({ id, role }) => ({ id, role })),
    [
      { id: 'lab-a', role: 'left' },
      { id: 'lab-b', role: 'right' }
    ]
  )
  assert.ok(manifest.participants.every(({ input }) => input.startsWith('local://')))
})

test('private join shape is public, fixed, and bounded', async () => {
  const manifest = await json('demos/cancer-collaboration/private-join-job.json')

  assert.equal(manifest.join.key, 'patient_id')
  assert.equal(manifest.join.identifierEncoding, 'fixed-width-utf8')
  assert.equal(manifest.join.maxIdentifierBytes, 128)
  assert.equal(manifest.join.maxRowsPerParticipant, 4)
})

test('private join schema requires privacy-critical fields', async () => {
  const schema = await json('packages/manifests/private-join-job.schema.json')

  assert.equal(schema.properties.operation.const, 'private-join-handoff')
  assert.equal(schema.properties.backend.properties.protocol.const, 'CHEETAH')
  assert.equal(schema.properties.mpcHandoff.properties.visibility.const, 'secret-shared')
  assert.equal(schema.properties.mpcHandoff.properties.includesIdentifiers.const, false)
  assert.equal(schema.properties.controlPlaneDataAccess.const, 'none')
})
