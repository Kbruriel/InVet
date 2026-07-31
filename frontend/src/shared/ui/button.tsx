import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  isLoading = false,
  disabled,
  className = '',
  ...props 
}) => {
  const baseClasses = "font-medium rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200";
  
  const variantClasses = {
    primary: "bg-[#006065] text-white hover:bg-[#004d51] focus:ring-[#006065]",
    secondary: "bg-[#bcedda] text-[#006065] hover:bg-[#a8dbce] focus:ring-[#bcedda]",
    outline: "border border-[#006065] text-[#006065] hover:bg-[#006065]/[0.05] focus:ring-[#006065]"
  };
  
  const sizeClasses = {
    sm: "text-sm px-4 py-2",
    md: "text-base px-6 py-3",
    lg: "text-lg px-8 py-4"
  };
  
  const disabledClasses = disabled || isLoading ? "opacity-50 cursor-not-allowed" : "";
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses} ${className}`;
  
  return (
    <button 
      className={classes}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center justify-center">
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Procesando...
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;