export function asArray<T = any>(v: unknown): T[] {
  if (Array.isArray(v)) return v as T[];
  // Common API shapes: {items: []}, {data: []}
  // @ts-ignore
  if (v && Array.isArray((v as any)?.items)) return (v as any).items as T[];
  // @ts-ignore
  if (v && Array.isArray((v as any)?.data)) return (v as any).data as T[];
  return [];
}


