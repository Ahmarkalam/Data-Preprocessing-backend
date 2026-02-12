import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckCircle,
  Zap,
  Shield,
  BarChart,
  Database,
  KeyRound,
  Menu,
  X,
  Sparkles,
  WandSparkles,
  Layers,
  LineChart,
} from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'High-performance processing',
    text: 'Run cleaning, validation, and transformation pipelines quickly on large datasets.',
  },
  {
    icon: Shield,
    title: 'Enterprise-grade data quality',
    text: 'Detect missing values, duplicates, type mismatches, and schema issues automatically.',
  },
  {
    icon: BarChart,
    title: 'Operational insights',
    text: 'Monitor quality trends, job outcomes, and transformation impact in one place.',
  },
  {
    icon: Layers,
    title: 'Reusable workflow templates',
    text: 'Standardize data preparation with templates your team can reuse across projects.',
  },
];

const steps = [
  {
    title: 'Ingest your data',
    text: 'Upload CSV, JSON, or Parquet files securely with progress tracking and validation checks.',
  },
  {
    title: 'Configure processing',
    text: 'Apply recommended presets or customize each preprocessing step based on your requirements.',
  },
  {
    title: 'Review and deliver',
    text: 'Compare results, inspect quality metrics, and export datasets for analytics or production pipelines.',
  },
];

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 overflow-x-hidden">
      <div className="fixed inset-0 -z-10">
        <div className="absolute -top-40 -left-20 h-80 w-80 bg-indigo-500/30 blur-3xl rounded-full" />
        <div className="absolute top-1/3 -right-16 h-72 w-72 bg-cyan-500/20 blur-3xl rounded-full" />
        <div className="absolute bottom-0 left-1/4 h-72 w-72 bg-fuchsia-500/20 blur-3xl rounded-full" />
      </div>

      <nav className="sticky top-0 z-50 bg-slate-950/75 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Database className="h-7 w-7 text-indigo-300" />
              <span className="text-lg sm:text-xl font-bold text-white">DataPrep AI</span>
            </div>

            <div className="hidden md:flex items-center gap-8 text-sm">
              <a href="#features" className="text-slate-300 hover:text-white transition-colors">Capabilities</a>
              <a href="#how-it-works" className="text-slate-300 hover:text-white transition-colors">Workflow</a>
              <a href="#pricing" className="text-slate-300 hover:text-white transition-colors">Plans</a>
            </div>

            <div className="hidden md:flex items-center gap-3">
              <Link to="/login" className="text-sm font-medium text-slate-200 hover:text-white transition-colors">
                Sign In
              </Link>
              <Link to="/try" className="px-4 py-2 rounded-lg bg-indigo-500 text-white text-sm font-semibold hover:bg-indigo-400 transition-colors">
                Start Free Trial
              </Link>
            </div>

            <button
              onClick={() => setIsMenuOpen((prev) => !prev)}
              className="md:hidden p-2 rounded-lg text-slate-200 hover:bg-white/10"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden border-t border-white/10 bg-slate-950/95 backdrop-blur-xl px-4 py-4 space-y-2">
            <a href="#features" className="block py-2 text-slate-300" onClick={() => setIsMenuOpen(false)}>Capabilities</a>
            <a href="#how-it-works" className="block py-2 text-slate-300" onClick={() => setIsMenuOpen(false)}>Workflow</a>
            <a href="#pricing" className="block py-2 text-slate-300" onClick={() => setIsMenuOpen(false)}>Plans</a>
            <div className="pt-2 grid grid-cols-2 gap-2">
              <Link to="/login" className="text-center px-4 py-2 rounded-lg border border-white/20 text-slate-100">Sign In</Link>
              <Link to="/try" className="text-center px-4 py-2 rounded-lg bg-indigo-500 text-white">Free Trial</Link>
            </div>
          </div>
        )}
      </nav>

      <section className="relative pt-14 sm:pt-20 pb-16 sm:pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-indigo-300/30 bg-indigo-400/10 px-3 py-1 text-xs sm:text-sm text-indigo-200 mb-5">
                <Sparkles size={14} /> Trusted data operations platform
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
                Professional data preprocessing for modern teams.
              </h1>
              <p className="mt-5 text-slate-300 text-base sm:text-lg max-w-xl">
                Improve data quality, reduce manual cleanup, and ship reliable datasets with a polished workflow built for day-to-day production use.
              </p>

              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Link to="/try" className="px-6 py-3 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-semibold flex items-center justify-center gap-2">
                  Start Free Trial <ArrowRight size={18} />
                </Link>
                <Link to="/login" className="px-6 py-3 rounded-xl border border-white/20 hover:bg-white/10 text-slate-100 font-semibold flex items-center justify-center gap-2">
                  <KeyRound size={18} /> Create API Access
                </Link>
              </div>
            </div>

            <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/15 shadow-2xl shadow-indigo-900/30">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                  <p className="text-xs uppercase text-slate-400">Quality Score</p>
                  <p className="text-3xl font-bold text-white mt-2">97.2</p>
                  <p className="text-emerald-300 text-sm mt-2">Consistent month over month</p>
                </div>
                <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                  <p className="text-xs uppercase text-slate-400">Jobs Processed</p>
                  <p className="text-3xl font-bold text-white mt-2">1,284</p>
                  <p className="text-cyan-300 text-sm mt-2">Stable and monitored</p>
                </div>
                <div className="sm:col-span-2 rounded-xl bg-gradient-to-br from-indigo-500/30 to-cyan-400/20 border border-indigo-200/20 p-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-indigo-100">Pipeline Health</span>
                    <LineChart className="text-indigo-100" size={18} />
                  </div>
                  <div className="h-2 bg-white/15 rounded-full overflow-hidden">
                    <div className="h-full w-[82%] bg-gradient-to-r from-cyan-300 to-indigo-300 rounded-full" />
                  </div>
                  <p className="text-sm text-slate-200 mt-3">82% of active workflows are fully optimized and policy-compliant.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="py-16 sm:py-20 border-y border-white/10 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-white">Built for reliability and scale.</h2>
            <p className="mt-4 text-slate-300 max-w-2xl mx-auto">A complete toolkit for teams that need clean, dependable datasets without operational overhead.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {features.map(({ icon: Icon, title, text }) => (
              <div key={title} className="glass-panel rounded-2xl p-6 border border-white/10 hover:border-indigo-300/40 transition-colors">
                <div className="w-11 h-11 rounded-xl bg-indigo-500/20 text-indigo-200 flex items-center justify-center mb-4">
                  <Icon size={22} />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
                <p className="text-slate-300">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 text-indigo-200 mb-6">
            <WandSparkles size={18} />
            <span className="text-sm uppercase tracking-widest">Workflow</span>
          </div>
          <div className="grid md:grid-cols-3 gap-5">
            {steps.map((step, idx) => (
              <div key={step.title} className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="w-9 h-9 rounded-full bg-indigo-500 text-white font-bold flex items-center justify-center mb-4">{idx + 1}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-slate-300 text-sm">{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" className="pb-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-7 flex flex-col">
              <h3 className="text-2xl font-bold text-white">Free Trial</h3>
              <p className="text-4xl font-extrabold text-white mt-3">$0</p>
              <p className="text-slate-300 mt-2 mb-6">For evaluation and quick dataset checks.</p>
              <ul className="space-y-3 text-slate-200 mb-8">
                <li className="flex items-center gap-2"><CheckCircle size={18} className="text-emerald-300" /> No API key required</li>
                <li className="flex items-center gap-2"><CheckCircle size={18} className="text-emerald-300" /> 5MB file uploads</li>
                <li className="flex items-center gap-2"><CheckCircle size={18} className="text-emerald-300" /> Core preprocessing tools</li>
              </ul>
              <Link to="/try" className="mt-auto text-center rounded-xl bg-white text-slate-900 px-4 py-3 font-semibold hover:bg-slate-100">Start Trial</Link>
            </div>

            <div className="rounded-2xl border-2 border-indigo-300/70 bg-indigo-500/15 p-7 flex flex-col shadow-xl shadow-indigo-900/30">
              <span className="inline-block text-xs font-bold tracking-wide px-2 py-1 rounded-md bg-indigo-300 text-slate-950 mb-4 w-fit">RECOMMENDED</span>
              <h3 className="text-2xl font-bold text-white">Developer API</h3>
              <p className="text-4xl font-extrabold text-white mt-3">Free</p>
              <p className="text-slate-200 mt-2 mb-6">For recurring workflows and integrations.</p>
              <ul className="space-y-3 text-slate-100 mb-8">
                <li className="flex items-center gap-2"><CheckCircle size={18} className="text-cyan-300" /> 1GB monthly quota</li>
                <li className="flex items-center gap-2"><CheckCircle size={18} className="text-cyan-300" /> 50MB uploads</li>
                <li className="flex items-center gap-2"><CheckCircle size={18} className="text-cyan-300" /> Full reporting and history</li>
              </ul>
              <Link to="/login?mode=register" className="mt-auto text-center rounded-xl bg-indigo-500 text-white px-4 py-3 font-semibold hover:bg-indigo-400">Get API Key</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
