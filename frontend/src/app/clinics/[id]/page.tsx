import { BranchProfile } from '@/features/public-clinic-profile/BranchProfile'
import { fetchBranchPublic } from '@/shared/api/branch-client'
import { Loading, ErrorBanner, EmptyState } from '@/shared/ui'

interface Params {
  params: Promise<{ id: string }>
}

export default async function ClinicBranchPage({ params }: Params) {
  const { id } = await params
  const branchId = parseInt(id, 10)

  if (isNaN(branchId)) {
    return <ErrorBanner title="Datos inválidos" message="El ID de sucursal no es válido." />
  }

  try {
    const branch = await fetchBranchPublic(branchId)
    if (!branch) {
      return <EmptyState title="Sucursal no encontrada" message="No existe una sucursal con este ID." />
    }
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <BranchProfile branch={branch} />
      </div>
    )
  } catch (_err) {
    return <ErrorBanner title="Error al cargar" message="No se pudieron cargar los datos de la sucursal. Intente de nuevo más tarde." retryAction={() => window.location.reload()} />
  }
}
