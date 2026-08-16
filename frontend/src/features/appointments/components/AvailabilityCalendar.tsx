'use client';

/**
 * AvailabilityCalendar — Mini-calendario de slots disponibles por fecha/veterinario (FE-008).
 */

'use client';

import React, { useState, useEffect } from 'react';
import { getAvailability } from '../api';
import type { AvailabilitySlot } from '../types';

interface AvailabilityCalendarProps {
  clinicId: number;
  onSelectSlot?: (slot: AvailabilitySlot) => void;
  initialDate?: string;
}

export function AvailabilityCalendar({ clinicId, onSelectSlot, initialDate }: AvailabilityCalendarProps) {
  const [selectedDate, setSelectedDate] = useState<string>(initialDate || new Date().toISOString().split('T')[0]);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function fetchSlots() {
      setLoading(true);
      try {
        const data = await getAvailability({
          date: selectedDate,
          clinic_id: clinicId,
        });
        if (!cancelled) setSlots(data.slots || []);
      } catch {
        // Silently fail - show empty state
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchSlots();
    return () => { cancelled = true; };
  }, [selectedDate, clinicId]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-MX', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Slots disponibles</h3>

      {/* Selector de fecha */}
      <input
        type="date"
        value={selectedDate}
        onChange={(e) => setSelectedDate(e.target.value)}
        min={new Date().toISOString().split('T')[0]}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
      />

      <p className="text-sm text-gray-600 capitalize mb-3">{formatDate(selectedDate)}</p>

      {/* Grid de slots */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      ) : slots.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">No hay slots disponibles para esta fecha.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 max-h-64 overflow-y-auto">
          {slots.map((slot, idx) => (
            <button
              key={idx}
              onClick={() => onSelectSlot?.(slot)}
              disabled={!slot.available}
              className={`p-2 rounded-lg text-xs font-medium transition-colors ${
                slot.available
                  ? 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 cursor-pointer'
                  : 'bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed'
              }`}
              aria-label={`${formatTime(slot.start)} - ${slot.available ? 'Disponible' : 'Ocupado'}`}
            >
              {formatTime(slot.start)}
              <p className={`mt-1 ${slot.available ? 'text-green-600' : 'text-gray-400'}`}>
                {slot.available ? 'Libre' : 'Ocupado'}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
