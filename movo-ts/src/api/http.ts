export function makeAbortable<T extends any[], R>(
  fn: (...args: [...T, AbortSignal?]) => Promise<R>
) {
  let controller: AbortController | null = null;
  return (...args: T) => {
    if (controller) controller.abort();
    controller = new AbortController();
    const signal = controller.signal;
    return fn(...args, signal).finally(() => {
      controller = null;
    });
  };
}


