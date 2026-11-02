import React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "green";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading, children, disabled, ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";

    const variantStyles = {
      primary: "bg-primary text-white hover:bg-primary-hover focus:ring-primary",
      secondary: "bg-surface text-primary hover:bg-border/60 focus:ring-primary",
      outline: "border border-border bg-white text-primary hover:bg-surface focus:ring-primary",
      ghost: "text-primary hover:bg-surface focus:ring-primary",
      green: "bg-green text-white hover:bg-green-dark focus:ring-green",
    };

    const sizeStyles = {
      sm: "text-xs px-3 py-1.5 h-8",
      md: "text-sm px-4 py-2.5 h-10",
      lg: "text-base px-6 py-3 h-12",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

