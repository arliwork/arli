const II_URL = process.env.NEXT_PUBLIC_II_URL || "https://identity.ic0.app";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function loginWithII(): Promise<{ principal: string; token: string }> {
  // Dynamic import ensures this only runs in browser (where crypto.subtle exists)
  const { AuthClient } = await import("@dfinity/auth-client");
  const authClient = await AuthClient.create();

  return new Promise((resolve, reject) => {
    authClient.login({
      identityProvider: II_URL,
      onSuccess: async () => {
        const identity = authClient.getIdentity();
        const principal = identity.getPrincipal().toText();
        try {
          const res = await fetch(`${API_URL}/auth/ii/init`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ principal }),
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "II auth failed");
          resolve({ principal, token: data.access_token });
        } catch (err: any) {
          reject(err);
        }
      },
      onError: (error) => reject(error),
    });
  });
}

export async function logoutII(): Promise<void> {
  const { AuthClient } = await import("@dfinity/auth-client");
  const authClient = await AuthClient.create();
  await authClient.logout();
}
