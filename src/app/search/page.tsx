'use client';

import { useState, useEffect } from 'react';
import { SearchBar } from '@/shared/ui/components/SearchBar';
import { CategoryChips } from '@/shared/ui/components/CategoryChips';
import { ClinicCard } from '@/shared/ui/components/ClinicCard';
import { LoadingSkeleton } from '@/shared/ui/components/LoadingSkeleton';
import { ErrorMessage } from '@/shared/ui/components/ErrorMessage';
import { EmptyState } from '@/shared/ui/components/EmptyState';
import { apiClient } from '@/shared/api';
import { Clinic, ClinicSearchResponse } from '@/shared/api/types';

export default function HomePage() {
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCity, setSelectedCity] = useState<string>('');

  // Function to fetch clinics with search and filtering
  const fetchClinics = async (page: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const response: ClinicSearchResponse = await apiClient.getClinics({
        page,
        size: 12,
        search: searchTerm,
        city: selectedCity || undefined
      });

      setClinics(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Error fetching clinics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch clinics when search or filters change
  useEffect(() => {
    fetchClinics();
  }, [searchTerm, selectedCity]);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
  };

  const handleCityChange = (city: string) => {
    setSelectedCity(city);
  };

  return (
    <div className="min-h-screen bg-[#fff8f0]">
      {/* Public Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-teal-700">InVet</span>
            </div>
            <nav className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <a href="/" className="text-gray-700 hover:text-teal-600 px-3 py-2 rounded-md text-sm font-medium">Inicio</a>
                <a href="/clinics" className="text-gray-700 hover:text-teal-600 px-3 py-2 rounded-md text-sm font-medium">Clínicas</a>
                <a href="/about" className="text-gray-700 hover:text-teal-600 px-3 py-2 rounded-md text-sm font-medium">Acerca de</a>
              </div>
            </nav>
            <div className="flex items-center space-x-4">
              <a 
                href="/login" 
                className="text-gray-700 hover:text-teal-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Iniciar sesión
              </a>
              <a 
                href="/register" 
                className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition duration-300"
              >
                Registrarse
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12 bg-gradient-to-r from-teal-50 to-mint-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Encuentra la clínica veterinaria perfecta para tu mascota
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Busca y compara clínicas veterinarias cerca de ti. Encuentra las mejores opciones con servicios 
            especializados en atención a mascotas.
          </p>

          {/* Search Bar */}
          <div className="max-w-4xl mx-auto mb-12">
            <SearchBar
              onSearch={handleSearch}
              placeholder="Buscar clínica por nombre o servicio..."
            />
          </div>

          {/* Category Chips */}
          <div className="mb-12">
            <CategoryChips 
              onCitySelect={handleCityChange}
              selectedCity={selectedCity}
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">¿Cómo funciona?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6 bg-teal-50 rounded-lg">
              <div className="w-16 h-16 bg-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Busca clínicas</h3>
              <p className="text-gray-600">Encuentra clínicas cerca de ti por nombre, servicio o ubicación.</p>
            </div>
            <div className="text-center p-6 bg-mint-50 rounded-lg">
              <div className="w-16 h-16 bg-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Compara opciones</h3>
              <p className="text-gray-600">Revisa servicios, horarios y opiniones de otros usuarios.</p>
            </div>
            <div className="text-center p-6 bg-teal-50 rounded-lg">
              <div className="w-16 h-16 bg-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Solicita tu cita</h3>
              <p className="text-gray-600">Haz la reserva directamente desde la plataforma.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Clinics Results */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              {clinics.length > 0 ? 'Clínicas encontradas' : 'Resultados de búsqueda'}
            </h2>
            <p className="text-gray-600">
              {clinics.length} clínica{clinics.length !== 1 ? 's' : ''} encontrada{clinics.length !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, index) => (
                <LoadingSkeleton key={index} />
              ))}
            </div>
          )}

          {/* Error State */}
          {error && <ErrorMessage message={error} />}

          {/* Empty State */}
          {!loading && clinics.length === 0 && !error && (
            <EmptyState 
              title="No se encontraron clínicas"
              message="Intenta con otros términos de búsqueda o filtros"
            />
          )}

          {/* Clinic Results */}
          {!loading && clinics.length > 0 && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {clinics.map((clinic) => (
                <ClinicCard key={clinic.id} clinic={clinic} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-teal-600 to-mint-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">¿Eres una clínica veterinaria?</h2>
          <p className="text-xl text-teal-100 mb-8 max-w-3xl mx-auto">
            Únete a nuestra plataforma para mostrar tus servicios y llegar a más mascotas.
          </p>
          <a 
            href="/register-clinic" 
            className="bg-white text-teal-600 hover:bg-gray-100 px-8 py-3 rounded-lg text-lg font-semibold transition duration-300 inline-block"
          >
            Regístrate como clínica
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">InVet</h3>
              <p className="text-gray-400">La plataforma definitiva para la atención veterinaria.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Enlaces</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/" className="hover:text-white">Inicio</a></li>
                <li><a href="/clinics" className="hover:text-white">Clínicas</a></li>
                <li><a href="/about" className="hover:text-white">Acerca de</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/terms" className="hover:text-white">Términos</a></li>
                <li><a href="/privacy" className="hover:text-white">Privacidad</a></li>
                <li><a href="/cookies" className="hover:text-white">Cookies</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Contacto</h4>
              <ul className="space-y-2 text-gray-400">
                <li>info@invet.es</li>
                <li>+34 123 456 789</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} InVet. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}