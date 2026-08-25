"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

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
    <Button type="button" variant="outline" size="sm" onClick={toggle}>
      {dark ? "Светлая" : "Тёмная"}
    </Button>
  );
}
