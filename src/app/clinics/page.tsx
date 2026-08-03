'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/shared/api';
import { ClinicCard } from '@/shared/ui/components/ClinicCard';
import { LoadingSkeleton } from '@/shared/ui/components/LoadingSkeleton';
import { ErrorMessage } from '@/shared/ui/components/ErrorMessage';
import { EmptyState } from '@/shared/ui/components/EmptyState';

export default function ClinicsPage() {
  const [clinics, setClinics] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClinics = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getClinics({ page: 1, size: 20 });
        setClinics(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        console.error('Error fetching clinics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchClinics();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#fff8f0] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <LoadingSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#fff8f0] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorMessage message={error} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fff8f0] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Clínicas Veterinarias</h1>
        
        {clinics.length === 0 ? (
          <EmptyState 
            title="No se encontraron clínicas"
            message="Intenta con otros términos de búsqueda o filtros" 
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {clinics.map((clinic) => (
              <ClinicCard key={clinic.id} clinic={clinic} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}