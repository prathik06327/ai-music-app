import type { ReactNode } from "react";

type PageContainerProps = {
  children: ReactNode;
  className?: string;
};

export default function PageContainer({ children, className = "" }: PageContainerProps) {
  return (
    <main className={`relative z-10 mx-auto w-full max-w-[1200px] px-4 py-6 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </main>
  );
}