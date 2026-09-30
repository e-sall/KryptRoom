import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

test('the cryptographic dependency uses an exact version', async () => {
  const packageJson = JSON.parse(
    await readFile(path.join(repositoryRoot, 'package.json'), 'utf8')
  )
  assert.equal(packageJson.dependencies['@openmined/psi.js'], '2.0.6')
})

