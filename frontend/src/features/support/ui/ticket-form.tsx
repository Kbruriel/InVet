'use client';

import { useState } from 'react';
import { CreateSupportTicketRequest, supportApi, SupportCategory } from '@/shared/api/support';
import { Button } from '@/shared/ui/components/Button';

interface TicketFormProps {
  categories: SupportCategory[];
  onSubmitSuccess?: () => void;
}

export function TicketForm({ categories, onSubmitSuccess }: TicketFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<number | ''>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const requestData: CreateSupportTicketRequest = {
        title: title.trim(),
        ...(description.trim() ? { description: description.trim() } : {}),
        ...(categoryId !== '' ? { category_id: categoryId } : {}),
      };

      await supportApi.createTicket(requestData);
      setTitle('');
      setDescription('');
      setCategoryId('');
      onSubmitSuccess?.();
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
          onChange={(event) => setTitle(event.target.value)}
          required
          minLength={5}
          maxLength={200}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
          aria-required="true"
        />
        <p className="mt-1 text-sm text-gray-500">Entre 5 y 200 caracteres</p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Descripción
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          maxLength={2000}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
        />
        <p className="mt-1 text-sm text-gray-500">Máximo 2000 caracteres</p>
      </div>

      <div>
        <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
          Categoría
        </label>
        <select
          id="category"
          value={categoryId}
          onChange={(event) => setCategoryId(event.target.value ? Number(event.target.value) : '')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
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
        <div className="rounded-md bg-red-50 p-4" role="alert">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="flex justify-end">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Creando...' : 'Crear ticket'}
        </Button>
      </div>
    </form>
  );
}
