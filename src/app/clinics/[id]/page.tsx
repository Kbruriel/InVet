'use client';

import { useState, useEffect } from 'react';
import { Clinic } from '@/shared/api/types';
import { apiClient } from '@/shared/api';

interface ClinicDetailPageProps {
  params: {
    id: string;
  };
}

export default function ClinicDetailPage({ params }: ClinicDetailPageProps) {
  const [clinic, setClinic] = useState<Clinic | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClinic = async () => {
      try {
        setLoading(true);
        const clinicData = await apiClient.getClinicById(params.id);
        setClinic(clinicData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        console.error('Error fetching clinic:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchClinic();
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#fff8f0] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6 mb-4"></div>
            <div className="h-12 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[...Array(4)].map((_, index) => (
                <div key={index} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !clinic) {
    return (
      <div className="min-h-screen bg-[#fff8f0] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  {error || 'Clínica no encontrada'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fff8f0] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <a 
            href="/search" 
            className="inline-flex items-center text-teal-600 hover:text-teal-800 mb-6"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293z" clipRule="evenodd" />
            </svg>
            Volver a resultados
          </a>
          <h1 className="text-3xl font-bold text-gray-900">{clinic.name}</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Clinic Info */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Información de la clínica</h2>
              <div className="space-y-3">
                <div className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-teal-600 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700">{clinic.address}</span>
                </div>
                <div className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-teal-600 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                  </svg>
                  <span className="text-gray-700">{clinic.phone}</span>
                </div>
                <div className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-teal-600 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2.003 12.377a1 1 0 01-.691-1.476l.004-.002c.286-.154.566-.3.834-.443.265-.142.515-.279.751-.411.223-.122.43-.237.623-.344.193-.107.371-.208.534-.303.163-.095.312-.184.447-.267.135-.083.256-.159.363-.229.107-.07.202-.133.285-.19.083-.057.154-.113.213-.163.059-.05.106-.095.142-.134.036-.039.062-.074.078-.105.016-.031.024-.058.024-.082 0-.024-.008-.051-.024-.082-.016-.031-.042-.066-.078-.105-.036-.039-.083-.084-.142-.134-.059-.05-.13-.106-.213-.163-.083-.057-.178-.12-.285-.19-.107-.07-.228-.145-.363-.229-.135-.083-.27-.166-.447-.267-.177-.101-.356-.202-.534-.303-.177-.101-.347-.201-.51-.299-.163-.098-.327-.19-.482-.275a1 1 0 00-.449-.185l-.385-.156.385-.156a1 1 0 00.449-.185c.155-.085.32-.177.482-.275.163-.098.333-.197.51-.299.177-.101.357-.202.534-.303.177-.101.331-.206.486-.309.155-.103.3-.201.432-.294.132-.093.253-.176.363-.25.11-.074.209-.141.3-.2.091-.059.18-.112.259-.16.079-.048.15-.09.211-.125.061-.035.113-.065.155-.09.042-.025.075-.044.099-.059.024-.015.04-.022.048-.025.008-.003.014-.004.018-.004.004 0 .009.001.013.004.004.003.01.01.018.025.024.015.057.034.099.059.042.025.094.055.155.09.061.035.132.077.211.125.079.048.15.1.259.16.11.074.231.157.363.25.132.093.267.186.432.294.165.108.32.213.486.309.166.096.336.191.51.299.174.109.338.211.51.309.172.098.338.192.51.282.172.09.336.174.51.25.174.076.338.145.51.208.172.063.336.12.51.17.174.05.338.094.51.131.172.037.336.069.51.093.174.024.338.043.51.056.172.013.336.02.51.02.174 0 .338-.007.51-.02.172-.013.336-.032.51-.056.174-.024.338-.056.51-.093.172-.037.336-.084.51-.131.174-.05.338-.107.51-.17.174-.063.338-.132.51-.208.172-.076.336-.17.51-.282.174-.112.338-.229.51-.358.172-.129.336-.273.51-.431.174-.158.338-.33.51-.516.174-.186.338-.387.51-.602.174-.215.338-.446.51-.692.174-.246.338-.508.51-.784.174-.276.338-.568.51-.874.174-.306.338-.628.51-1.06.174-.432.338-.88.51-1.342.174-.462.338-.938.51-1.426.174-.488.338-.988.51-1.502.174-.514.338-1.038.51-1.572.174-.534.338-1.075.51-1.624.174-.549.338-1.104.51-1.666.174-.562.338-1.128.51-1.698.174-.57.338-1.142.51-1.718.174-.576.338-1.152.51-1.73.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734.174-.578.338-1.156.51-1.734" />
                  </svg>
                  <span className="text-gray-700">{clinic.email}</span>
                </div>
                <div className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-teal-600 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700">{clinic.opening_hours}</span>
                </div>
              </div>
            </div>

            {/* Branches Section */}
            {clinic.branches && clinic.branches.length > 0 && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Sucursales</h2>
                <div className="space-y-4">
                  {clinic.branches.map((branch) => (
                    <div key={branch.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="font-medium text-gray-900">{branch.name}</div>
                      <div className="flex items-start mt-2 text-gray-600">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                        </svg>
                        <span>{branch.address}</span>
                      </div>
                      <div className="flex items-start mt-1 text-gray-600">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                        </svg>
                        <span>{branch.phone}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-md p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Solicita tu cita</h2>
              <p className="text-gray-600 mb-6">¿Quieres agendar una cita en esta clínica?</p>
              
              <button 
                className="w-full bg-teal-600 hover:bg-teal-700 text-white font-medium py-3 px-4 rounded-lg transition duration-300"
              >
                Solicitar cita
              </button>
              
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="font-medium text-gray-900 mb-3">Horario de atención</h3>
                <p className="text-gray-600">{clinic.opening_hours}</p>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="font-medium text-gray-900 mb-3">Comentarios</h3>
                <div className="flex items-center">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81l2.8-2.034a1 1 0 00.364-1.118z" />
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2 text-gray-600">4.8 (125 opiniones)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}