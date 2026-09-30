const MAX_MESSAGE_BYTES = 2 * 1024 * 1024

export function binaryToBase64(value) {
  return Buffer.from(value).toString('base64')
}

export function base64ToBinary(value) {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error('Expected a non-empty base64 message')
  }

  return Uint8Array.from(Buffer.from(value, 'base64'))
}

export async function readJsonBody(request) {
  const chunks = []
  let size = 0

  for await (const chunk of request) {
    size += chunk.length
    if (size > MAX_MESSAGE_BYTES) {
      throw new Error('Protocol message exceeds the size limit')
    }
    chunks.push(chunk)
  }

  return JSON.parse(Buffer.concat(chunks).toString('utf8'))
}

export function writeJson(response, statusCode, body) {
  const payload = JSON.stringify(body)
  response.writeHead(statusCode, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(payload),
    'cache-control': 'no-store'
  })
  response.end(payload)
}

