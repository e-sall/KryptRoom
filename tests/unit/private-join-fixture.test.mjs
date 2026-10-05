import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

async function rows(relativePath) {
  const [header, ...lines] = (
    await readFile(path.join(repositoryRoot, relativePath), 'utf8')
  )
    .trim()
    .split(/\r?\n/u)
  const columns = header.split(',')
  return lines.map((line) =>
    Object.fromEntries(columns.map((column, index) => [column, line.split(',')[index]]))
  )
}

test('synthetic private-join fixture has cardinality two', async () => {
  // This cleartext comparison is test-fixture validation only. It is not used
  // by either KryptNode runtime or by a Control Plane component.
  const [labA, labB] = await Promise.all([
    rows('demos/cancer-collaboration/lab-a/private-join.csv'),
    rows('demos/cancer-collaboration/lab-b/private-join.csv')
  ])
  const labBIdentifiers = new Set(labB.map(({ patient_id: id }) => id))
  const cardinality = labA.filter(({ patient_id: id }) => labBIdentifiers.has(id)).length

  assert.equal(cardinality, 2)
})
