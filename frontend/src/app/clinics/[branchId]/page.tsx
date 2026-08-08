import { BranchProfile } from '@/features/public-clinic-profile/BranchProfile';

type Props = {
  params: Promise<{ branchId: string }>;
};

export default async function PublicBranchPage({ params }: Props) {
  const resolved = await params;
  const branchId = Number(resolved.branchId);

  return (
    <main>
      <BranchProfile branchId={branchId} />
    </main>
  );
}
