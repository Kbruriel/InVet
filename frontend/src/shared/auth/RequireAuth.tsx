'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';

import { isAuthenticated } from './session';
import { LoadingSpinner } from '@/shared/ui/components';

interface RequireAuthProps {
  children: ReactNode;
  redirectTo?: string;
  loadingLabel?: string;
}

export function RequireAuth({
  children,
  redirectTo = '/login',
  loadingLabel = 'Verificando sesión...',
}: RequireAuthProps) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace(redirectTo);
      return;
    }

    setAuthorized(true);
  }, [redirectTo, router]);

  if (!authorized) {
    return (
      <div className="py-16">
        <LoadingSpinner label={loadingLabel} />
      </div>
    );
  }

  return <>{children}</>;
}
