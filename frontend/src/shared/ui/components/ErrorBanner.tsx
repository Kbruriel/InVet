'use client'

interface Props {
  title?: string
  message?: string
  retryAction?: () => void
}

export function ErrorBanner({ title = 'Error', message, retryAction }: Props) {
  return (
    <div role="alert" aria-live="assertive" className="p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg mb-6">
      <h3 className="text-red-800 font-medium">{title}</h3>
      <p className="text-red-700 text-sm mt-1">{message || 'Ha ocurrido un error inesperado.'}</p>
      {retryAction && (
        <button
          aria-label="Reintentar"
          onClick={retryAction}
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors cursor-pointer"
        >
          Reintentar
        </button>
      )}
    </div>
  )
}

export default ErrorBanner
