import type { HTMLAttributes, ReactNode } from "react";

export default function SoftCard({
  children,
  className = "",
  ...rest
}: { children: ReactNode; className?: string } & HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`soft-card${className ? ` ${className}` : ""}`} {...rest}>
      {children}
    </div>
  );
}
