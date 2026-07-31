import React from 'react';
import AuthLayout from '@/shared/layout/AuthLayout';
import RegisterForm from '@/features/auth/components/RegisterForm';
import Link from 'next/link';

const RegisterPage: React.FC = () => {
  return (
    <AuthLayout>
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-[#006065] mb-2">Crear cuenta</h1>
          <p className="text-gray-600">Regístrate en InVet</p>
        </div>
        
        <RegisterForm />
        
        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            ¿Ya tienes cuenta?{' '}
            <Link href="/auth/login" className="text-[#006065] font-medium hover:underline">
              Inicia sesión aquí
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
};

export default RegisterPage;