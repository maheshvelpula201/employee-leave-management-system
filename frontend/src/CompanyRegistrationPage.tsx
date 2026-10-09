
import { useState, type FormEvent } from "react";
import { apiRequest } from "./lib/api";
import "./CompanyRegistrationPage.css";

type CompanyRegistrationPageProps = {
  onBack: () => void;
};

type RegistrationResponse = {
  message: string;
  company: {
    company_id: number;
    company_name: string;
    company_email: string;
    company_code: string;
    status: string;
    is_active: boolean;
  };
  admin: {
    user_id: number;
    name: string;
    email: string;
    role: string;
    company_id: number;
    is_active: boolean;
  };
};

type RegistrationForm = {
  company_name: string;
  company_email: string;
  company_phone: string;
  address: string;
  city: string;
  state: string;
  country: string;
  website: string;
  description: string;
  admin_name: string;
  admin_email: string;
  admin_password: string;
  confirm_password: string;
};

const initialForm: RegistrationForm = {
  company_name: "",
  company_email: "",
  company_phone: "",
  address: "",
  city: "",
  state: "",
  country: "India",
  website: "",
  description: "",
  admin_name: "",
  admin_email: "",
  admin_password: "",
  confirm_password: "",
};

export default function CompanyRegistrationPage({
  onBack,
}: CompanyRegistrationPageProps) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<RegistrationForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<RegistrationResponse | null>(null);

  function updateField(field: keyof RegistrationForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function handleCompanyDetails(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setStep(2);
  }

  async function handleRegistration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (form.admin_password !== form.confirm_password) {
      setError("The passwords do not match.");
      return;
    }

    if (form.admin_password.length < 8) {
      setError("Your password must contain at least 8 characters.");
      return;
    }

    setLoading(true);

    try {
      const response = await apiRequest<RegistrationResponse>(
        "/registration/",
        {
          method: "POST",
          body: {
            company_name: form.company_name.trim(),
            company_email: form.company_email.trim(),
            company_phone: form.company_phone.trim() || null,
            address: form.address.trim() || null,
            city: form.city.trim() || null,
            state: form.state.trim() || null,
            country: form.country.trim() || null,
            website: form.website.trim() || null,
            description: form.description.trim() || null,
            admin_name: form.admin_name.trim(),
            admin_email: form.admin_email.trim(),
            admin_password: form.admin_password,
          },
        },
      );

      setSuccess(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Registration failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <main className="registration-page">
        <section className="registration-card registration-success">
          <div className="registration-success-icon">✓</div>

          <p className="registration-eyebrow">REGISTRATION SUBMITTED</p>
          <h1>Your company is registered!</h1>
          <p className="registration-description">
            Your request has been submitted successfully. An administrator
            must approve your company before you can sign in.
          </p>

          <div className="registration-summary">
            <div>
              <span>Company</span>
              <strong>{success.company.company_name}</strong>
            </div>
            <div>
              <span>Company code</span>
              <strong>{success.company.company_code}</strong>
            </div>
            <div>
              <span>Admin email</span>
              <strong>{success.admin.email}</strong>
            </div>
            <div>
              <span>Status</span>
              <strong>{success.company.status}</strong>
            </div>
          </div>

          <button
            type="button"
            className="registration-primary-button"
            onClick={onBack}
          >
            Return to sign in
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="registration-page">
      <section className="registration-card">
        <button
          type="button"
          className="registration-back-link"
          onClick={onBack}
        >
          ← Back to sign in
        </button>

        <div className="registration-brand">
          <div className="registration-brand-icon">N</div>
          <div>
            <h1>Northstar</h1>
            <p>HR Management Platform</p>
          </div>
        </div>

        <div className="registration-heading">
          <p className="registration-eyebrow">
            CREATE YOUR WORKSPACE
          </p>
          <h2>
            {step === 1
              ? "Tell us about your company"
              : "Create your admin account"}
          </h2>
          <p>
            {step === 1
              ? "Start by entering your company information."
              : "These credentials will be used to access your workspace after approval."}
          </p>
        </div>

        <div className="registration-progress">
          <div className={step === 1 ? "progress-step active" : "progress-step complete"}>
            <span>1</span>
            Company details
          </div>
          <div className="progress-line" />
          <div className={step === 2 ? "progress-step active" : "progress-step"}>
            <span>2</span>
            Admin account
          </div>
        </div>

        {step === 1 && (
          <form
            className="registration-form"
            onSubmit={handleCompanyDetails}
          >
            <label htmlFor="company_name">Company name *</label>
            <input
              id="company_name"
              value={form.company_name}
              onChange={(event) =>
                updateField("company_name", event.target.value)
              }
              placeholder="Your company name"
              minLength={2}
              maxLength={200}
              required
            />

            <label htmlFor="company_email">Company email *</label>
            <input
              id="company_email"
              type="email"
              value={form.company_email}
              onChange={(event) =>
                updateField("company_email", event.target.value)
              }
              placeholder="contact@company.com"
              required
            />

            <label htmlFor="company_phone">Phone number</label>
            <input
              id="company_phone"
              type="tel"
              value={form.company_phone}
              onChange={(event) =>
                updateField("company_phone", event.target.value)
              }
              placeholder="Company phone number"
            />

            <label htmlFor="address">Street address</label>
            <input
              id="address"
              value={form.address}
              onChange={(event) =>
                updateField("address", event.target.value)
              }
              placeholder="Building, street or area"
            />

            <div className="registration-field-row">
              <div>
                <label htmlFor="city">City</label>
                <input
                  id="city"
                  value={form.city}
                  onChange={(event) =>
                    updateField("city", event.target.value)
                  }
                  placeholder="City"
                />
              </div>
              <div>
                <label htmlFor="state">State</label>
                <input
                  id="state"
                  value={form.state}
                  onChange={(event) =>
                    updateField("state", event.target.value)
                  }
                  placeholder="State"
                />
              </div>
            </div>

            <label htmlFor="country">Country</label>
            <input
              id="country"
              value={form.country}
              onChange={(event) =>
                updateField("country", event.target.value)
              }
              placeholder="Country"
            />

            <label htmlFor="website">Company website</label>
            <input
              id="website"
              type="url"
              value={form.website}
              onChange={(event) =>
                updateField("website", event.target.value)
              }
              placeholder="https://company.com"
            />

            <label htmlFor="description">Company description</label>
            <textarea
              id="description"
              value={form.description}
              onChange={(event) =>
                updateField("description", event.target.value)
              }
              placeholder="Briefly describe your company"
              rows={3}
            />

            <button
              type="submit"
              className="registration-primary-button"
            >
              Continue to admin account →
            </button>
          </form>
        )}

        {step === 2 && (
          <form
            className="registration-form"
            onSubmit={handleRegistration}
          >
            <label htmlFor="admin_name">Admin full name *</label>
            <input
              id="admin_name"
              value={form.admin_name}
              onChange={(event) =>
                updateField("admin_name", event.target.value)
              }
              placeholder="Your full name"
              minLength={2}
              maxLength={200}
              autoComplete="name"
              required
            />

            <label htmlFor="admin_email">Admin email *</label>
            <input
              id="admin_email"
              type="email"
              value={form.admin_email}
              onChange={(event) =>
                updateField("admin_email", event.target.value)
              }
              placeholder="you@company.com"
              autoComplete="email"
              required
            />

            <label htmlFor="admin_password">Password *</label>
            <input
              id="admin_password"
              type="password"
              value={form.admin_password}
              onChange={(event) =>
                updateField("admin_password", event.target.value)
              }
              placeholder="At least 8 characters"
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              required
            />

            <label htmlFor="confirm_password">Confirm password *</label>
            <input
              id="confirm_password"
              type="password"
              value={form.confirm_password}
              onChange={(event) =>
                updateField("confirm_password", event.target.value)
              }
              placeholder="Enter the password again"
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              required
            />

            {error && (
              <p className="registration-error" role="alert">
                {error}
              </p>
            )}

            <div className="registration-actions">
              <button
                type="button"
                className="registration-secondary-button"
                onClick={() => {
                  setError("");
                  setStep(1);
                }}
                disabled={loading}
              >
                ← Back
              </button>

              <button
                type="submit"
                className="registration-primary-button"
                disabled={loading}
              >
                {loading ? "Submitting..." : "Submit registration"}
              </button>
            </div>

            <p className="registration-note">
              Your company must be approved before you can sign in.
            </p>
          </form>
        )}

        {step === 1 && error && (
          <p className="registration-error" role="alert">
            {error}
          </p>
        )}

        <p className="registration-footer">
          Secure registration for your company workspace
        </p>
      </section>
    </main>
  );
}
