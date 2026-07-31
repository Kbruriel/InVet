import React, { useState } from 'react';
import Input from '@/shared/ui/Input';
import Button from '@/shared/ui/button';
import Form from '@/shared/ui/Form';
import { register } from '@/shared/api/auth';
import { useRouter } from 'next/navigation';

interface FormData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  firstName?: string;
  lastName?: string;
}

const RegisterForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
  });
  
  const [errors, setErrors] = useState<FormErrors>({});  
  const [isLoading, setIsLoading] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);
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
    
    if (!formData.firstName) {
      newErrors.firstName = 'El nombre es requerido';
    }
    
    if (!formData.lastName) {
      newErrors.lastName = 'El apellido es requerido';
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
    setRegisterError(null);
    
    try {
      const response = await register({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName
      });
      
      // Guardar tokens en localStorage
      localStorage.setItem('accessToken', response.access_token);
      localStorage.setItem('tokenType', response.token_type);
      
      // Redirigir a la página principal o dashboard
      router.push('/');
    } catch (error) {
      console.error('Registration error:', error);
      setRegisterError('Error al registrarse. Por favor, inténtalo nuevamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Nombre"
            type="text"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            error={errors.firstName}
          />
          
          <Input
            label="Apellido"
            type="text"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            error={errors.lastName}
          />
        </div>
        
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
        
        {registerError && (
          <div className="text-red-600 text-sm text-center">
            {registerError}
          </div>
        )}
        
        <Button 
          type="submit" 
          variant="primary" 
          size="md" 
          isLoading={isLoading}
          className="w-full"
        >
          Registrarse
        </Button>
      </div>
    </Form>
  );
};

export default RegisterForm;