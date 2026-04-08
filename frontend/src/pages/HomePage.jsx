import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { useAuth } from '../hooks/useAuth';
import { ROUTES } from '../utils/constants';

export function HomePage() {
  const [email, setEmail] = useState('');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();


  const handleGetStarted = (e) => {
    if (e) e.preventDefault();
    if (email) {
      navigate(ROUTES.SIGNUP, { state: { email } });
    } else {
      navigate(ROUTES.SIGNUP);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-zinc-50 to-amber-50/40 flex flex-col selection:bg-amber-100 selection:text-slate-900">
      <Header />

      {/* Background accents */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-25%] left-[-15%] w-[70%] h-[70%] bg-gradient-to-br from-slate-300/30 to-slate-100/30 rounded-full blur-[130px]" />
        <div className="absolute bottom-[-20%] right-[-15%] w-[70%] h-[70%] bg-gradient-to-tr from-amber-200/35 to-orange-100/35 rounded-full blur-[140px]" />
      </div>

      <main className="flex-1 flex flex-col items-center px-6 relative z-10">
        <section className="max-w-6xl mx-auto pt-16 pb-20 w-full">
          <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 rounded-full mb-6">
                <span className="w-2 h-2 bg-amber-400 rounded-full" />
                <span className="text-xs font-semibold uppercase tracking-wider text-amber-300">AI Workspace</span>
              </div>
              <h1 className="text-4xl md:text-6xl font-bold leading-tight text-slate-900 max-w-3xl">
                Ask Better Questions.
                <span className="block text-amber-700">Get Verifiable Answers.</span>
              </h1>
              <p className="mt-6 text-lg text-slate-700 max-w-2xl leading-relaxed">
                Upload documents, connect your database, and chat in plain language.
                MINI turns complex data into clear decisions with traceable results.
              </p>

              <div className="mt-8 grid sm:grid-cols-3 gap-3 text-sm">
                <div className="p-4 rounded-xl bg-white/80 border border-slate-200 text-slate-700">
                  PDF, DOCX, TXT
                </div>
                <div className="p-4 rounded-xl bg-white/80 border border-slate-200 text-slate-700">
                  Natural language SQL
                </div>
                <div className="p-4 rounded-xl bg-white/80 border border-slate-200 text-slate-700">
                  Source-backed output
                </div>
              </div>
            </div>

            <div className="p-6 md:p-8 rounded-3xl bg-white/90 border border-slate-200 shadow-xl shadow-slate-300/30">
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Start in under a minute</h2>
              <p className="text-slate-600 mb-6">Use your email to create a workspace and begin chatting with your data.</p>

            {!isAuthenticated ? (
              <form onSubmit={handleGetStarted} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="email" className="block text-sm font-medium text-slate-700">Work email</label>
                  <div className="relative p-1 bg-white border border-slate-300 rounded-xl focus-within:border-amber-600 focus-within:ring-4 focus-within:ring-amber-500/10 transition-all">
                    <input
                      id="email"
                      type="email"
                      placeholder="name@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-4 py-3 bg-transparent border-none focus:ring-0 focus:outline-none text-slate-900 text-base placeholder-slate-400 rounded-lg"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full px-6 py-3.5 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-colors"
                >
                  Create Free Workspace
                </button>

                <div className="pt-2 text-xs text-slate-500 flex items-center justify-between">
                  <span>No credit card</span>
                  <span>2-minute setup</span>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <button
                  onClick={() => navigate(ROUTES.CHAT)}
                  className="w-full px-6 py-3.5 bg-amber-700 text-white font-semibold rounded-xl hover:bg-amber-800 transition-colors"
                >
                  Open Dashboard
                </button>
                <p className="text-sm text-slate-600">You are already signed in. Continue where you left off.</p>
              </div>
            )}
            </div>
          </div>
        </section>

        <section className="w-full max-w-6xl mx-auto pb-20">
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-semibold text-slate-900 mb-3">Clarity from ingestion to insight</h2>
            <p className="text-slate-600">A single workflow for document intelligence and database analytics.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 bg-white/90 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-xl font-semibold text-slate-900 mb-2">1. Connect your data</h3>
              <p className="text-slate-600 leading-relaxed">
                Add files or point to your database. MINI prepares and indexes data for retrieval.
              </p>
              <p className="mt-4 text-xs uppercase tracking-wide text-slate-500">PDF, DOCX, TXT, SQL sources</p>
            </div>

            <div className="p-6 bg-white/90 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-xl font-semibold text-slate-900 mb-2">2. Ask naturally</h3>
              <p className="text-slate-600 leading-relaxed">
                Ask in plain English. The system converts your intent into search, SQL, or multi-step reasoning.
              </p>
              <p className="mt-4 text-xs uppercase tracking-wide text-slate-500">No prompt engineering needed</p>
            </div>

            <div className="p-6 bg-white/90 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-xl font-semibold text-slate-900 mb-2">3. Decide with confidence</h3>
              <p className="text-slate-600 leading-relaxed">
                Responses include evidence and context so your team can validate and move quickly.
              </p>
              <p className="mt-4 text-xs uppercase tracking-wide text-slate-500">Traceable and reviewable outputs</p>
            </div>
          </div>

          <div className="mt-8 p-6 bg-slate-900 text-slate-100 rounded-2xl border border-slate-800">
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-slate-400 uppercase tracking-wide mb-1">Use case</p>
                <p>Internal research, customer support intelligence, and BI acceleration.</p>
              </div>
            </div>
            <div className="mt-4 grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-slate-400 uppercase tracking-wide mb-1">Models</p>
                <p>Balanced options for deep reasoning and fast conversational responses.</p>
              </div>
              <div>
                <p className="text-slate-400 uppercase tracking-wide mb-1">Output</p>
                <p>SQL, summaries, and chart-ready insights from one unified chat interface.</p>
              </div>
              <div>
                <p className="text-slate-400 uppercase tracking-wide mb-1">Trust</p>
                <p>Evidence-aware answers designed for operational and technical teams.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
