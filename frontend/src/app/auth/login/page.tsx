import React from 'react';
import AuthLayout from '@/shared/layout/AuthLayout';
import LoginForm from '@/features/auth/components/LoginForm';
import Link from 'next/link';

const LoginPage: React.FC = () => {
  return (
    <AuthLayout>
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-[#006065] mb-2">Iniciar sesión</h1>
          <p className="text-gray-600">Ingresa a tu cuenta de InVet</p>
        </div>
        
        <LoginForm />
        
        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            ¿No tienes cuenta?{' '}
            <Link href="/auth/register" className="text-[#006065] font-medium hover:underline">
              Regístrate aquí
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;