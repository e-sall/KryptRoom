import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')
const image =
  'secretflow/secretflow-ubuntu:1.14.0b0@sha256:bdd43242c28466bdc0afddb99d7b50237a94748b5ca7467f8aea73667a38383b'

async function source(relativePath) {
  return readFile(path.join(repositoryRoot, relativePath), 'utf8')
}

test('M2.5 reuses the exact verified SecretFlow image and protocol', async () => {
  const [compose, manifest] = await Promise.all([
    source('compose.persistent-state.yml'),
    source('demos/cancer-collaboration/persistent-state-job.json').then(JSON.parse)
  ])

  assert.equal(compose.match(new RegExp(image.replaceAll('.', '\\.'), 'gu'))?.length, 1)
  assert.equal(manifest.cryptoContext.backendVersion, '1.14.0b0')
  assert.equal(manifest.cryptoContext.protocol, 'CHEETAH')
  assert.equal(manifest.cryptoContext.field, 'FM128')
  assert.equal(manifest.cryptoContext.securityModel, 'semi-honest')
})

test('state commitment encoding is deterministic while ciphertext is randomized', async () => {
  const storage = await source('engines/mpc/room_state.py')

  assert.match(storage, /separators=\(",", ":"\)/u)
  assert.match(storage, /sort_keys=True/u)
  assert.match(storage, /hashlib\.sha256/u)
  assert.match(storage, /nonce = os\.urandom\(NONCE_BYTES\)/u)
})
