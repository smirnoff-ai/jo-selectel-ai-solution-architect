"use client";

import { useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    if (typeof document === "undefined") {
      return true;
    }
    return document.documentElement.classList.contains("dark");
  });

  function toggle() {
    const next = !dark;
    setDark(next);
    localStorage.setItem("reflex.theme", next ? "dark" : "light");
    document.documentElement.classList.toggle("dark", next);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className="rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
    >
      {dark ? "Светлая" : "Тёмная"}
    </button>
  );
}
