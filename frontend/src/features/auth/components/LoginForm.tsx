import React, { useState } from 'react';
import Input from '@/shared/ui/Input';
import Button from '@/shared/ui/button';
import Form from '@/shared/ui/Form';
import { login } from '@/shared/api/auth';
import { useRouter } from 'next/navigation';

interface FormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
}

const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  
  const [errors, setErrors] = useState<FormErrors>({});  
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const router = useRouter();

  const validate = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'El correo electrónico es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El correo electrónico no es válido';
    }
    
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsLoading(true);
    setLoginError(null);
    
    try {
      const response = await login({
        email: formData.email,
        password: formData.password
      });
      
      // Guardar tokens en localStorage
      localStorage.setItem('accessToken', response.access_token);
      localStorage.setItem('tokenType', response.token_type);
      
      // Redirigir a la página principal o dashboard
      router.push('/');
    } catch (error) {
      console.error('Login error:', error);
      setLoginError('Credenciales inválidas. Por favor, inténtalo nuevamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <div className="space-y-4">
        <Input
          label="Correo electrónico"
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
        />
        
        <Input
          label="Contraseña"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          error={errors.password}
        />
        
        {loginError && (
          <div className="text-red-600 text-sm text-center">
            {loginError}
          </div>
        )}
        
        <Button 
          type="submit" 
          variant="primary" 
          size="md" 
          isLoading={isLoading}
          className="w-full"
        >
          Iniciar sesión
        </Button>
      </div>
    </Form>
  );
};

export default LoginForm;