import { ProtectedClinicBranchClient } from '@/features/public-clinic-profile/ProtectedClinicBranchClient'

interface Params {
  params: Promise<{ clinicId: string; branchId: string }>
}

export default async function ProtectedClinicBranchPage({ params }: Params) {
  const { clinicId, branchId } = await params

  return (
    <ProtectedClinicBranchClient
      clinicId={parseInt(clinicId, 10)}
      branchId={parseInt(branchId, 10)}
    />
  )
}
