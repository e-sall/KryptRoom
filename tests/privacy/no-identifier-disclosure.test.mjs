import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

async function source(relativePath) {
  return readFile(path.join(repositoryRoot, relativePath), 'utf8')
}

test('both KryptNode roles enforce cardinality-only mode', async () => {
  const server = await source('nodes/krypt-node/src/psi-server.mjs')
  const client = await source('nodes/krypt-node/src/psi-client.mjs')

  assert.match(server, /const revealIntersection = false/u)
  assert.match(client, /const revealIntersection = false/u)
  assert.doesNotMatch(client, /\.getIntersection\s*\(/u)
  assert.match(client, /\.getIntersectionSize\s*\(/u)
})

test('the exact Raw encrypted container is selected', async () => {
  const server = await source('nodes/krypt-node/src/psi-server.mjs')
  assert.match(server, /psi\.dataStructure\.Raw/u)
  assert.doesNotMatch(server, /psi\.dataStructure\.(?:GCS|BloomFilter)/u)
})

test('the disclosure manifest requires opt-in for any future ID reveal', async () => {
  const manifest = JSON.parse(
    await source('demos/cancer-collaboration/disclosure-policy.json')
  )
  assert.equal(manifest.revealMatchedIdentifiers, false)
  assert.equal(manifest.resultMode, 'cardinality-only')
  assert.equal(manifest.futureIdentifierDisclosure.requiresExplicitOptIn, true)
})

test('the PSI job manifest contains no patient identifiers or remote inputs', async () => {
  const sourceText = await source('demos/cancer-collaboration/psi-job.json')
  const manifest = JSON.parse(sourceText)

  assert.doesNotMatch(sourceText, /P00[1-7]/u)
  assert.equal(manifest.controlPlaneDataAccess, 'none')
  assert.equal(manifest.outputPolicy.revealMatchedIdentifiers, false)
  assert.ok(manifest.participants.every(({ input }) => input.startsWith('local://')))
})

