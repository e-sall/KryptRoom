import process from 'node:process'
import PSI from '@openmined/psi.js'

import { loadPatientIds } from './dataset.mjs'
import { base64ToBinary, binaryToBase64 } from './wire.mjs'

const inputPath = process.env.KRYPTROOM_INPUT_PATH
const endpoint = process.env.KRYPTROOM_PSI_ENDPOINT ??
  'http://127.0.0.1:5300/v1/psi/cardinality'

if (!inputPath) {
  throw new Error('KRYPTROOM_INPUT_PATH is required')
}

const patientIds = await loadPatientIds(inputPath)
const psi = await PSI()

// Both peers must use false. The library then exposes cardinality but rejects
// attempts to retrieve matched identifiers.
const revealIntersection = false
const clientParty = psi.client.createWithNewKey(revealIntersection)
const clientRequest = clientParty.createRequest(patientIds)

const response = await fetch(endpoint, {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({
    clientElementCount: patientIds.length,
    request: binaryToBase64(clientRequest.serializeBinary())
  })
})

if (!response.ok) {
  throw new Error(`PSI peer rejected the request with HTTP ${response.status}`)
}

const body = await response.json()
if (body.policy !== 'cardinality-only') {
  throw new Error('PSI peer did not confirm the cardinality-only policy')
}

const setup = psi.serverSetup.deserializeBinary(base64ToBinary(body.setup))
const protocolResponse = psi.response.deserializeBinary(
  base64ToBinary(body.response)
)
const intersectionCardinality = clientParty.getIntersectionSize(
  setup,
  protocolResponse
)

console.log(
  JSON.stringify({
    event: 'psi_completed',
    protocol: 'OpenMined PSI ECDH cardinality',
    dataStructure: 'Raw',
    intersectionCardinality,
    matchedIdentifiersRevealed: false
  })
)

