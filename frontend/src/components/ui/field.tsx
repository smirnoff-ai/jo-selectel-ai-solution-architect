import type { HTMLAttributes, LabelHTMLAttributes, ReactNode } from "react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

export function FieldGroup({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col gap-4", className)} {...props} />;
}

export function Field({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement> & { "data-invalid"?: boolean }) {
  return <div className={cn("flex flex-col gap-1.5", className)} {...props} />;
}

export function FieldLabel({
  className,
  ...props
}: LabelHTMLAttributes<HTMLLabelElement>) {
  return <Label className={className} {...props} />;
}

export function FieldDescription({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <p className={cn("text-sm text-muted-foreground", className)}>{children}</p>;
}

export function FieldError({ children }: { children: ReactNode }) {
  return <p className="text-sm text-destructive">{children}</p>;
}
