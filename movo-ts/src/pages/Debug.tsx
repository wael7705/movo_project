import { useState } from 'react'

async function jget(url: string, init?: RequestInit){
  const res = await fetch(url, { headers: { 'Accept': 'application/json' }, ...init })
  const text = await res.text()
  try { return JSON.parse(text) } catch { return { text } }
}

export default function DebugPage(){
  const [out, setOut] = useState<any>(null)

  const run = async (fn: ()=>Promise<any>) => {
    try { setOut(await fn()) } catch (e: any) { setOut({ error: String(e?.message || e) }) }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Debug / API Checks</h1>
      <div className="flex gap-2 flex-wrap">
        <button className="px-3 py-2 bg-violet-600 text-white rounded" onClick={()=>run(()=>jget('/api/v1/orders/counts'))}>Ping Counts</button>
        <button className="px-3 py-2 bg-violet-600 text-white rounded" onClick={()=>run(()=>jget('/api/v1/orders?order_status=pending'))}>List Pending</button>
        <button className="px-3 py-2 bg-violet-600 text-white rounded" onClick={()=>run(()=>jget('/api/v1/orders/demo', { method:'POST' }))}>Create Demo</button>
        <button className="px-3 py-2 bg-violet-600 text-white rounded" onClick={()=>run(()=>jget('/__selfcheck'))}>Backend Selfcheck</button>
        <a className="px-3 py-2 bg-gray-200 rounded" href="/t/pending" target="_blank" rel="noreferrer">Open /t/pending</a>
        <a className="px-3 py-2 bg-gray-200 rounded" href="/t/processing" target="_blank" rel="noreferrer">Open /t/processing</a>
      </div>
      <pre className="bg-black text-green-300 p-3 rounded overflow-auto text-xs max-h-[70vh]">
        {out ? JSON.stringify(out, null, 2) : 'No output yet'}
      </pre>
    </div>
  )
}


