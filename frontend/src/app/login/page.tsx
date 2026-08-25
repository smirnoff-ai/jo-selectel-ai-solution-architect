"use client";

import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [empty, setEmpty] = useState(false);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const loginValue = String(form.get("login") ?? "").trim();
    const password = String(form.get("password") ?? "");
    if (loginValue.length === 0 || password.length === 0) {
      setEmpty(true);
      return;
    }
    if (pending) {
      return;
    }
    setPending(true);
    setError(null);
    setEmpty(false);
    try {
      await login({ login: loginValue, password });
      router.push("/desk");
    } catch {
      setError("Неверный логин или пароль");
      setPending(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-full w-full max-w-sm flex-col justify-center px-6 py-16">
      <h1 className="font-serif text-3xl">Рефлекс</h1>
      <p className="mt-2 text-sm text-muted-foreground">Вход диспетчера</p>
      <form className="mt-8" method="post" onSubmit={(event) => void onSubmit(event)}>
        <FieldGroup>
          <Field data-invalid={empty}>
            <FieldLabel htmlFor="login">Логин</FieldLabel>
            <Input id="login" name="login" autoComplete="username" />
          </Field>
          <Field data-invalid={empty}>
            <FieldLabel htmlFor="password">Пароль</FieldLabel>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
            />
            {empty ? <FieldError>заполните логин и пароль</FieldError> : null}
          </Field>
        </FieldGroup>
        {error ? <p className="mt-4 text-sm text-destructive">{error}</p> : null}
        <Button type="submit" className="mt-6 w-full" disabled={pending}>
          Войти
        </Button>
      </form>
    </main>
  );
}
