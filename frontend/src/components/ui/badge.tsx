import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline";
}

export function Badge({ className, variant = "default", children, ...props }: BadgeProps) {
  const variantStyles = {
    default: "bg-surface text-primary border-border",
    success: "bg-green-mint text-green-dark border-green/20",
    warning: "bg-amber-50 text-warning border-warning/20",
    danger: "bg-red-50 text-danger border-danger/20",
    info: "bg-blue-light text-blue-dark border-blue/20",
    outline: "bg-transparent text-primary border-border",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

