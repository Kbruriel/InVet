'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { BranchProfile } from '@/features/public-clinic-profile/BranchProfile'
import { fetchBranchProtected } from '@/shared/api/branch-client-protected'
import type { BranchProtectedProfile } from '@/shared/api/types'
import { ErrorBanner } from '@/shared/ui/ErrorBanner'
import { Loading } from '@/shared/ui/Loading'

interface ProtectedClinicBranchClientProps {
  clinicId: number
  branchId: number
}

export function ProtectedClinicBranchClient({
  clinicId,
  branchId,
}: ProtectedClinicBranchClientProps) {
  const router = useRouter()
  const [branch, setBranch] = useState<BranchProtectedProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const data = await fetchBranchProtected(clinicId, branchId)
        if (!cancelled) {
          setBranch(data)
        }
      } catch (err) {
        const status =
          typeof err === 'object' && err && 'status' in err
            ? (err as { status?: number }).status
            : undefined

        if (status === 401) {
          router.push(`/login?redirect=/clinics/${clinicId}/branches/${branchId}`)
          return
        }

        if (status === 403) {
          setError('No tienes permiso para acceder a esta sucursal.')
          return
        }

        if (!cancelled) {
          setError('Error de red. Intente de nuevo.')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [clinicId, branchId, router])

  if (isLoading) return <Loading text="Cargando perfil protegido..." />

  if (error) return <ErrorBanner title="Acceso denegado" message={error} />

  if (!branch) {
    return <div className="text-gray-500">No se encontraron datos para esta sucursal.</div>
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <BranchProfile branch={branch} />
    </div>
  )
}
