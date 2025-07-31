import React, { ReactNode } from 'react';

interface ButtonProps {
  children?: ReactNode; // Tornando opcional
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  className = '',
  onClick,
  disabled = false,
  type = 'button',
}) => {
  const baseClasses = 'totem-button flex items-center justify-center font-medium transition-all';
  
  const variantClasses = {
    primary: 'totem-button-primary',
    secondary: 'totem-button-secondary',
    outline: 'border-2 border-primary text-primary hover:bg-primary/10',
  };
  
  const sizeClasses = {
    sm: 'py-2 px-4 text-sm',
    md: 'py-3 px-6 text-base',
    lg: 'py-3 px-8 text-lg',
    xl: 'py-4 px-10 text-xl',
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  
  return (
    <button
      type={type}
      className={classes}
      onClick={(e) => {
        console.log('🔍 DEBUG - Button onClick chamado');
        console.log('🔍 DEBUG - Evento:', e);
        console.log('🔍 DEBUG - Target:', e.target);
        if (onClick) {
          onClick();
        }
      }}
      disabled={disabled}
    >
      {icon && iconPosition === 'left' && (
        <span className="mr-2">{icon}</span>
      )}
      {children}
      {icon && iconPosition === 'right' && (
        <span className="ml-2">{icon}</span>
      )}
    </button>
  );
}; 