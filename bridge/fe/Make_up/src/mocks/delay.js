export function delay(value, ms = 300) {
  return new Promise(resolve => setTimeout(() => resolve(value), ms))
}
