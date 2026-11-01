export const name = 'learning-marker'

export function apply(runtime) {
  console.info('[learning-marker] active')
  runtime.effect(() => {
    let released = false
    return () => {
      if (released) return
      released = true
      console.info('[learning-marker] disposed')
    }
  })
}
