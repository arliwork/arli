"use client";

import { useState, useEffect } from "react";

export function useAuthSafe() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const savedToken = typeof window !== "undefined" ? localStorage.getItem("arli_token") : null;
    setToken(savedToken);
    setIsLoaded(true);
  }, []);

  const getToken = async () => token;

  return { isLoaded, userId, token, getToken, isSignedIn: !!token };
}
