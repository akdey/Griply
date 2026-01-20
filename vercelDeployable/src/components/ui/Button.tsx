import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger';
    isLoading?: boolean;
    icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    variant = 'primary',
    isLoading,
    icon,
    className = '',
    disabled,
    ...props
}) => {
    const baseClass = 'glass-button';
    const variantClass = variant === 'secondary' ? 'secondary' :
        variant === 'danger' ? 'bg-red-500/20 text-red-400 border border-red-500/50' : '';

    return (
        <button
            className={`${baseClass} ${variantClass} ${className} ${disabled || isLoading ? 'opacity-50 cursor-not-allowed' : ''} flex items-center justify-center gap-3`}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : icon}
            <span className="font-black uppercase tracking-widest text-[11px]">{children}</span>
        </button>
    );
};
