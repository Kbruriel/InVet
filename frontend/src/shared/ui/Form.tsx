import React from 'react';

interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode;
  onSubmit?: (e: React.FormEvent) => void;
}

const Form: React.FC<FormProps> = ({ children, onSubmit, className = '', ...props }) => {
  return (
    <form 
      className={`space-y-6 ${className}`}
      onSubmit={onSubmit}
      {...props}
    >
      {children}
    </form>
  );
};

export default Form;