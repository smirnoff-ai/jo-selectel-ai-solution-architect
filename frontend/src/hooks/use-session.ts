"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, fetchMe } from "@/lib/api";

export function useSession() {
  const router = useRouter();
  const [login, setLogin] = useState<string | null>(null);

  useEffect(() => {
    void fetchMe()
      .then((me) => setLogin(me.login))
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 401) {
          router.replace("/login");
          return;
        }
        router.replace("/login");
      });
  }, [router]);

  return login;
}
