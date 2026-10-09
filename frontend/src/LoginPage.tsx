import { useState, type FormEvent } from "react";
import { login } from "./lib/auth";
import "./LoginPage.css";

type LoginPageProps = {
  onLoginSuccess: () => void;
  onCreateCompany: () => void;
};

export default function LoginPage({
  onLoginSuccess,
  onCreateCompany,
}: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login({
        role: "COMPANY_ADMIN",
        email: email.trim(),
        password,
      });

      onLoginSuccess();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">
          <div className="login-brand-icon">N</div>
          <div>
            <h1>Northstar</h1>
            <p>HR Management Platform</p>
          </div>
        </div>

        <div className="login-heading">
          <p className="login-eyebrow">WELCOME BACK</p>
          <h2>Sign in to your workspace</h2>
          <p>Enter your company admin credentials to continue.</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@company.com"
            autoComplete="username"
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            autoComplete="current-password"
            required
          />

          {error && (
            <p className="login-error" role="alert">
              {error}
            </p>
          )}

          <button
            className="login-submit"
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="login-register">
          <p>New to Northstar?</p>
          <button
            type="button"
            className="login-register-button"
            onClick={onCreateCompany}
          >
            Create a company account
          </button>
        </div>

        <p className="login-footer">
          Secure access to your company workspace
        </p>
      </section>
    </main>
  );
}

