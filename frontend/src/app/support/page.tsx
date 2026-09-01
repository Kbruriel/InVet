'use client';

import { useState, useEffect } from 'react';
import { supportApi, SupportCategory } from '@/shared/api/support';
import { TicketForm } from '@/features/support/ui/ticket-form';
import { TicketListFiltered } from '@/features/support/ui/ticket-list-filtered';
import { Button } from '@/shared/ui/button';

export default function SupportPage() {
  const [categories, setCategories] = useState<SupportCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await supportApi.getCategories();
      setCategories(response);
    } catch (err) {
      setError('Error al cargar las categorías. Por favor, inténtelo de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    // Reload the ticket list when a new ticket is created
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <div className="rounded-md bg-red-50 p-4 mb-6">
          <p className="text-sm text-red-700">{error}</p>
          <Button 
            onClick={loadCategories} 
            variant="outline" 
            className="mt-2"
          >
            Reintentar
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Soporte</h1>
        <p className="text-gray-600">Crea tickets de soporte y consulta tu historial</p>
      </div>

      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Crear nuevo ticket</h2>
          <Button 
            onClick={() => setShowForm(!showForm)}
            className="bg-teal-600 hover:bg-teal-700 focus:ring-teal-500"
          >
            {showForm ? 'Ocultar formulario' : 'Mostrar formulario'}
          </Button>
        </div>

        {showForm && (
          <div className="border border-gray-200 rounded-lg p-6 mb-8 shadow-sm">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Nuevo ticket</h3>
            <TicketForm categories={categories} onSubmitSuccess={handleFormSuccess} />
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Mis tickets</h2>
        <div className="border border-gray-200 rounded-lg p-6 shadow-sm">
          <TicketListFiltered onTicketClick={(ticketId) => window.location.href = `/support/${ticketId}`} />
        </div>
      </div>
    </div>
  );
}