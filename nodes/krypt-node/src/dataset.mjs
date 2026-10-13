import { readFile } from 'node:fs/promises'

const ID_HEADER = 'patient_id'
const SAFE_ID = /^[A-Za-z0-9_-]{1,128}$/u

export async function loadPatientIds(path) {
  const source = await readFile(path, 'utf8')
  const lines = source
    .replace(/^\uFEFF/u, '')
    .split(/\r?\n/u)
    .filter((line) => line.length > 0)

  if (lines.shift()?.trim() !== ID_HEADER) {
    throw new Error(`Dataset must start with the ${ID_HEADER} header`)
  }

  if (lines.length === 0) {
    throw new Error('Dataset must contain at least one patient identifier')
  }

  const ids = lines.map((line) => line.trim())
  if (ids.some((id) => !SAFE_ID.test(id))) {
    throw new Error('Dataset contains an invalid patient identifier')
  }

  if (new Set(ids).size !== ids.length) {
    throw new Error('Dataset contains duplicate patient identifiers')
  }

  return ids
}

