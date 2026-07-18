"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // Password rules check
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[\W_]/.test(password);
  const isPasswordValid = hasMinLength && hasUppercase && hasNumber && hasSpecial;

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");

    if (!isPasswordValid) {
      setErrorMsg("Please satisfy all password complexity rules.");
      return;
    }

    setLoading(true);

    try {
      // Sign up directly with Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) {
        throw error;
      }

      if (data?.user) {
        setSuccessMsg(
          data.session 
            ? "Registration successful! Redirecting..." 
            : "Registration successful! Please check your email for the confirmation link."
        );
        
        // If auto-signed in (session is present), redirect to dashboard
        if (data.session) {
          setTimeout(() => {
            router.push("/dashboard");
          }, 1500);
        }
      }
    } catch (err: any) {
      console.error("Signup error:", err);
      setErrorMsg(err.message || "An unexpected error occurred during registration.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#030712] text-gray-100 flex flex-col justify-center items-center px-6 overflow-hidden">
      {/* Decorative Blur Backgrounds */}
      <div className="glow-blur-green top-[10%] left-[5%]" />
      <div className="glow-blur-indigo bottom-[20%] right-[10%]" />

      <div className="relative z-10 w-full max-w-md glass-panel p-8 md:p-10 rounded-3xl shadow-2xl">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg text-sm">
              W
            </div>
            <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Wealth Genie
            </span>
          </Link>
          <h1 className="text-2xl font-bold text-white tracking-tight">Create your account</h1>
          <p className="text-sm text-gray-400 mt-1">Get started with your AI Personal CFO</p>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 error-message" id="register-error">
            <span>❌</span> {errorMsg}
          </div>
        )}

        {successMsg && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex items-center gap-2" id="register-success">
            <span>✅</span> {successMsg}
          </div>
        )}

        <form onSubmit={handleRegister} className="flex flex-col gap-6" id="register-form">
          <div className="flex flex-col gap-2">
            <label htmlFor="email" className="text-sm font-semibold text-gray-300">
              Email address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="name@example.com"
              autoComplete="username"
              className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="password" className="text-sm font-semibold text-gray-300">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                autoComplete="new-password"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "👁️‍🗨️"}
              </button>
            </div>
            
            {/* Password Rules Checklist */}
            <div className="mt-3 p-4 rounded-xl bg-white/5 border border-white/5 text-xs text-gray-400 flex flex-col gap-2">
              <span className="font-semibold text-gray-300">Password requirements:</span>
              <ul className="grid grid-cols-2 gap-2">
                <li className={`flex items-center gap-1.5 ${hasMinLength ? 'text-emerald-400 font-semibold' : ''}`}>
                  {hasMinLength ? "✓" : "○"} 8+ characters
                </li>
                <li className={`flex items-center gap-1.5 ${hasUppercase ? 'text-emerald-400 font-semibold' : ''}`}>
                  {hasUppercase ? "✓" : "○"} 1 uppercase
                </li>
                <li className={`flex items-center gap-1.5 ${hasNumber ? 'text-emerald-400 font-semibold' : ''}`}>
                  {hasNumber ? "✓" : "○"} 1 number
                </li>
                <li className={`flex items-center gap-1.5 ${hasSpecial ? 'text-emerald-400 font-semibold' : ''}`}>
                  {hasSpecial ? "✓" : "○"} 1 special char
                </li>
              </ul>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-500/50 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/20 transition-all duration-200 flex justify-center items-center gap-2"
          >
            {loading ? "Creating Account..." : "Create Account"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-400 mt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-emerald-400 hover:text-emerald-300 font-semibold hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
