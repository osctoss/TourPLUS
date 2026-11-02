import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle, Info, AlertTriangle } from "lucide-react";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "info" | "success" | "warning" | "danger";
  title?: string;
}

export function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  const icons = {
    info: <Info className="h-5 w-5 text-blue" />,
    success: <CheckCircle className="h-5 w-5 text-green" />,
    warning: <AlertTriangle className="h-5 w-5 text-warning" />,
    danger: <AlertCircle className="h-5 w-5 text-danger" />,
  };

  const containerStyles = {
    info: "bg-blue-light border-blue/20 text-primary",
    success: "bg-green-mint border-green/20 text-primary",
    warning: "bg-amber-50 border-warning/20 text-primary",
    danger: "bg-red-50 border-danger/20 text-primary",
  };

  return (
    <div
      className={cn(
        "relative w-full rounded-lg border p-4 flex gap-3 text-sm",
        containerStyles[variant],
        className
      )}
      role="alert"
      {...props}
    >
      <div className="shrink-0">{icons[variant]}</div>
      <div className="space-y-1">
        {title && <h5 className="font-semibold leading-none tracking-tight">{title}</h5>}
        <div className="text-sm opacity-90 leading-relaxed">{children}</div>
      </div>
    </div>
  );
}

