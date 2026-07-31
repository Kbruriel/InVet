import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  className?: string;
}

const Input: React.FC<InputProps> = ({ 
  label, 
  error, 
  className = '',
  ...props 
}) => {
  const baseClasses = "w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2 transition-colors duration-200";
  
  const focusClasses = "focus:ring-[#006065] focus:border-[#006065]";
  
  const defaultBorderClass = "border-[#f4ede2]";
  
  const errorBorderClass = "border-red-500";
  
  const classes = `${baseClasses} ${focusClasses} ${defaultBorderClass} ${className}`;
  
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-[#006065] mb-2">
          {label}
        </label>
      )}
      <input 
        className={classes}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default Input;