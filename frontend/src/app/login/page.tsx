// "use client";
// import { useState } from "react";
// import { useRouter } from "next/navigation";
// import { login } from "@/lib/api";

// export default function LoginPage() {
//     const router = useRouter();
//     const [email, setEmail] = useState("");
//     const [password, setPassword] = useState("");
//     const [error, setError] = useState("");

//     async function handleSubmit(e: React.FormEvent) {
//     e.preventDefault();
//     setError("");
//     try 
//     {
//         const token = await login(email, password);
//         localStorage.setItem("token", token);   // keep it across refreshes
//         router.push("/");                       // go to the chat
//     } 
//     catch (err) 
//     {
//         setError((err as Error).message);
//     }
//     }

//     return (
//     <main className="mx-auto max-w-sm p-8">
//         <h1 className="text-2xl font-bold">Sign in</h1>
//         <form onSubmit={handleSubmit} className="mt-4 space-y-3">
//         <input className="w-full rounded border px-3 py-2" placeholder="Email"
//                 value={email} onChange={(e) => setEmail(e.target.value)} />
//         <input className="w-full rounded border px-3 py-2" placeholder="Password" type="password"
//                 value={password} onChange={(e) => setPassword(e.target.value)} />
//         <button type="submit" className="w-full rounded bg-blue-600 px-4 py-2 text-white">
//             Sign in
//         </button>
//         {error && <p className="text-red-600">{error}</p>}
//         </form>
//     </main>
//     );
// }


"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const token = await login(email, password);

      localStorage.setItem("token", token);
      router.push("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold text-white">
            K
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-gray-900">
            Welcome back
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Sign in to your Knowledge Assistant
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-gray-700"
            >
              Email address
            </label>

            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-gray-700"
            >
              Password
            </label>

            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && (
            <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-gray-400">
          Knowledge Assistant
        </p>
      </div>
    </main>
  );
}
