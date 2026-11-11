
"use client";

import { useState } from "react";
import { supabase } from "../../lib/supabase";

export default function AuthScreen({
  onAuthSuccess,
}: {
  onAuthSuccess: () => void;
}) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = isLogin
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });

      if (result.error) {
        throw result.error;
      }

      if (!result.data.session) {
        setError("Registration successful. Please check your email to confirm your account.");
        return;
      }

      onAuthSuccess();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Authentication failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#090909] px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-[#141414] p-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-amber-400">LearnVault</h1>
          <p className="mt-2 text-sm text-slate-400">
            Your personal AI learning space
          </p>
        </div>

        <h2 className="mb-2 text-xl font-semibold">
          {isLogin ? "Welcome back" : "Create your account"}
        </h2>

        <p className="mb-6 text-sm text-slate-400">
          {isLogin
            ? "Log in to continue learning."
            : "Register to start learning with LearnVault."}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-white/10 bg-[#090909] px-4 py-3 text-sm outline-none focus:border-amber-400"
          />

          <input
            type="password"
            placeholder="Password (minimum 8 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
            className="w-full rounded-lg border border-white/10 bg-[#090909] px-4 py-3 text-sm outline-none focus:border-amber-400"
          />

          {error && (
            <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-400">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-amber-400 py-3 font-semibold text-black hover:bg-amber-300 disabled:opacity-50"
          >
            {loading
              ? "Please wait..."
              : isLogin
                ? "Log In"
                : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          {isLogin ? "Don't have an account?" : "Already have an account?"}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError("");
            }}
            className="ml-2 font-medium text-amber-400"
          >
            {isLogin ? "Register" : "Log In"}
          </button>
        </p>
      </div>
    </main>
  );
}
