import assert from 'node:assert/strict'
import { mkdtemp, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'

import { loadPatientIds } from '../../nodes/krypt-node/src/dataset.mjs'

async function fixture(content) {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'kryptroom-'))
  const file = path.join(directory, 'patients.csv')
  await writeFile(file, content, 'utf8')
  return file
}

test('loads unique patient identifiers', async () => {
  const file = await fixture('patient_id\nP001\nP002\n')
  assert.deepEqual(await loadPatientIds(file), ['P001', 'P002'])
})

test('rejects duplicate identifiers', async () => {
  const file = await fixture('patient_id\nP001\nP001\n')
  await assert.rejects(loadPatientIds(file), /duplicate/u)
})

test('rejects an unexpected schema', async () => {
  const file = await fixture('id\nP001\n')
  await assert.rejects(loadPatientIds(file), /patient_id/u)
})

