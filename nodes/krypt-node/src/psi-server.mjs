import http from 'node:http'
import process from 'node:process'
import PSI from '@openmined/psi.js'

import { loadPatientIds } from './dataset.mjs'
import {
  base64ToBinary,
  binaryToBase64,
  readJsonBody,
  writeJson
} from './wire.mjs'

const inputPath = process.env.KRYPTROOM_INPUT_PATH
const host = process.env.KRYPTROOM_HOST ?? '127.0.0.1'
const port = Number.parseInt(process.env.KRYPTROOM_PORT ?? '5300', 10)

if (!inputPath) {
  throw new Error('KRYPTROOM_INPUT_PATH is required')
}

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('KRYPTROOM_PORT must be a valid TCP port')
}

const patientIds = await loadPatientIds(inputPath)
const psi = await PSI()

// Cardinality-only is a policy boundary. Never enable revealIntersection here.
const revealIntersection = false
const serverParty = psi.server.createWithNewKey(revealIntersection)

const server = http.createServer(async (request, response) => {
  try {
    if (request.method === 'GET' && request.url === '/health') {
      writeJson(response, 200, { status: 'ready', role: 'psi-server' })
      return
    }

    if (request.method !== 'POST' || request.url !== '/v1/psi/cardinality') {
      writeJson(response, 404, { error: 'not_found' })
      return
    }

    const body = await readJsonBody(request)
    const clientElementCount = body.clientElementCount
    if (!Number.isInteger(clientElementCount) || clientElementCount < 1) {
      throw new Error('clientElementCount must be a positive integer')
    }

    const clientRequest = psi.request.deserializeBinary(
      base64ToBinary(body.request)
    )

    // Raw uses exact encrypted values and therefore has no false positives.
    // The false-positive-rate argument is ignored by this data structure.
    const setup = serverParty.createSetupMessage(
      0.001,
      clientElementCount,
      patientIds,
      psi.dataStructure.Raw
    )
    const protocolResponse = serverParty.processRequest(clientRequest)

    writeJson(response, 200, {
      setup: binaryToBase64(setup.serializeBinary()),
      response: binaryToBase64(protocolResponse.serializeBinary()),
      policy: 'cardinality-only'
    })
  } catch {
    // Do not serialize request bodies, patient IDs, or cryptographic messages.
    writeJson(response, 400, {
      error: 'invalid_protocol_request'
    })
  }
})

server.listen(port, host, () => {
  console.log(
    JSON.stringify({
      event: 'kryptnode_ready',
      role: 'psi-server',
      host,
      port,
      revealIntersection
    })
  )
})

function shutdown() {
  server.close(() => process.exit(0))
}

process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)

