'use client';

import { useState } from 'react';
import { supportApi, CreateSupportTicketRequest, SupportCategory } from '@/shared/api/support';
import { Button } from '@/shared/ui/button';

interface TicketFormProps {
  categories: SupportCategory[];
  onSubmitSuccess?: () => void;
}

export function TicketForm({ categories, onSubmitSuccess }: TicketFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const requestData: CreateSupportTicketRequest = {
        title,
        description,
        ...(categoryId && { category_id: categoryId })
      };

      await supportApi.createTicket(requestData);
      onSubmitSuccess?.();
      
      // Reset form after successful submission
      setTitle('');
      setDescription('');
      setCategoryId(null);
    } catch (err) {
      setError('Error al crear el ticket. Por favor, inténtelo de nuevo.');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Título *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
          aria-required="true"
        />
        <p className="mt-1 text-sm text-gray-500">
          Máximo 200 caracteres
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Descripción
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={2000}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
        />
        <p className="mt-1 text-sm text-gray-500">
          Máximo 2000 caracteres
        </p>
      </div>

      <div>
        <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
          Categoría
        </label>
        <select
          id="category"
          value={categoryId || ''}
          onChange={(e) => setCategoryId(e.target.value || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
        >
          <option value="">Seleccione una categoría</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="flex justify-end">
        <Button
          type="submit"
          disabled={isSubmitting}
          className="bg-teal-600 hover:bg-teal-700 focus:ring-teal-500"
        >
          {isSubmitting ? 'Creando...' : 'Crear Ticket'}
        </Button>
      </div>
    </form>
  );
}