import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Alert({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-md border border-border bg-muted px-3 py-2 text-sm text-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function AlertError({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-md border border-destructive/40 bg-card px-3 py-2 text-sm text-destructive",
        className,
      )}
      {...props}
    />
  );
}
