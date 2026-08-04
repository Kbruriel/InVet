'use client'

export function Loading({ text = 'Cargando...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3" role="status" aria-live="polite">
      <div aria-hidden="true" className="w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin"></div>
      <span className="text-gray-600 text-sm">{text}</span>
    </div>
  )
}

export default Loading
