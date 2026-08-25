"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { logout } from "@/lib/api";
import { cn } from "@/lib/utils";

export function AppShell({
  login,
  children,
  fill = false,
}: {
  login: string;
  children: ReactNode;
  fill?: boolean;
}) {
  const pathname = usePathname();
  const router = useRouter();

  async function onLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <div className={cn("flex flex-col", fill ? "h-dvh overflow-hidden" : "min-h-full")}>
      <header className="shrink-0 border-b border-border bg-card">
        <div className="mx-auto flex w-full max-w-[1600px] items-center gap-6 px-6 py-3">
          <Link href="/desk" className="font-serif text-xl">
            Рефлекс
          </Link>
          <nav className="flex items-center gap-1">
            <NavLink href="/desk" active={pathname === "/desk"}>
              Стол
            </NavLink>
            <NavLink href="/journal" active={pathname.startsWith("/journal")}>
              Журнал
            </NavLink>
          </nav>
          <Button size="sm" onClick={() => router.push("/appeals/new")}>
            Создать обращение
          </Button>
          <div className="ml-auto flex items-center gap-3">
            <span className="text-sm text-muted-foreground">{login}</span>
            <ThemeToggle />
            <Button variant="outline" size="sm" onClick={() => void onLogout()}>
              Выход
            </Button>
          </div>
        </div>
      </header>
      <main
        className={cn(
          "mx-auto flex w-full max-w-[1600px] flex-1 flex-col px-6",
          fill ? "min-h-0 overflow-hidden py-4" : "py-8",
        )}
      >
        {children}
      </main>
    </div>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: ReactNode;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "rounded-md px-3 py-1.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        active ? "bg-muted text-foreground" : "text-muted-foreground hover:text-foreground",
      )}
    >
      {children}
    </Link>
  );
}
