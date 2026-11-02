import React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", label, error, helperText, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-semibold uppercase tracking-wider text-muted">
            {label}
          </label>
        )}
        <input
          id={inputId}
          type={type}
          ref={ref}
          className={cn(
            "flex h-10 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm text-body placeholder:text-muted/60 transition-colors focus:border-blue focus:outline-none focus:ring-1 focus:ring-blue disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-danger focus:border-danger focus:ring-danger",
            className
          )}
          {...props}
        />
        {helperText && !error && <p className="text-xs text-muted">{helperText}</p>}
        {error && <p className="text-xs text-danger font-medium">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";

