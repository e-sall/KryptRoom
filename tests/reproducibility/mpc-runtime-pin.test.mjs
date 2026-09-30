import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

const repositoryRoot = path.resolve(import.meta.dirname, '../..')

test('SecretFlow container is pinned by version and immutable digest', async () => {
  const compose = await readFile(
    path.join(repositoryRoot, 'compose.private-join.yml'),
    'utf8'
  )

  assert.match(
    compose,
    /secretflow\/secretflow-ubuntu:1\.14\.0b0@sha256:bdd43242c28466bdc0afddb99d7b50237a94748b5ca7467f8aea73667a38383b/u
  )
  assert.doesNotMatch(compose, /secretflow[^\n]*:latest/u)
})
