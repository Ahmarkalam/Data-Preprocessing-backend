import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Zap, Shield, FileText, BarChart, Database, KeyRound } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white font-sans text-slate-900">
      <nav className="sticky top-0 z-50 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Database className="h-7 w-7 text-slate-900" />
              <span className="text-xl font-bold text-slate-900">DataPrep AI</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">How it Works</a>
              <a href="#pricing" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Pricing</a>
            </div>
            <div className="flex items-center gap-3">
              <Link to="/login" className="text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors">
                Sign In
              </Link>
              <Link to="/try" className="px-4 py-2 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition-colors">
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <section className="relative pt-16 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-4">
            Clean data. Clear results.
          </h1>
          <p className="mt-2 text-lg text-slate-600 max-w-2xl mx-auto mb-8">
            A fast, reliable preprocessing platform to clean, validate, and analyze datasets with one click.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <Link to="/try" className="px-6 py-3 rounded-lg bg-slate-900 text-white font-semibold hover:bg-slate-800 transition-colors w-full sm:w-auto flex items-center justify-center gap-2">
              Start Free Trial <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="px-6 py-3 rounded-lg border border-slate-200 text-slate-700 font-semibold hover:bg-slate-50 transition-colors w-full sm:w-auto flex items-center justify-center gap-2">
              <KeyRound size={18} /> Get API Key
            </Link>
          </div>
          <div className="mt-12 mx-auto max-w-5xl">
            <div className="relative bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden">
              <div className="bg-slate-50 border-b border-slate-200 px-4 py-2 flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
              </div>
              <div className="grid md:grid-cols-3 gap-0">
                <div className="p-6 bg-slate-50 border-r border-slate-200 space-y-4">
                  <div className="p-4 bg-white border border-slate-200 rounded-xl">
                    <div className="text-xs font-semibold text-slate-500 mb-1">Quality Score</div>
                    <div className="text-2xl font-extrabold text-slate-900">92</div>
                    <div className="text-xs text-emerald-600 mt-1">+4 since last run</div>
                  </div>
                  <div className="p-4 bg-white border border-slate-200 rounded-xl">
                    <div className="text-xs font-semibold text-slate-500 mb-1">Rows Processed</div>
                    <div className="text-2xl font-extrabold text-slate-900">24,108</div>
                    <div className="text-xs text-slate-500 mt-1">CSV • 18 columns</div>
                  </div>
                  <div className="p-4 bg-white border border-slate-200 rounded-xl">
                    <div className="text-xs font-semibold text-slate-500 mb-1">Actions Applied</div>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs px-2 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">Deduplicate</span>
                      <span className="text-xs px-2 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">Handle Missing</span>
                      <span className="text-xs px-2 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">Normalize</span>
                    </div>
                  </div>
                </div>
                <div className="md:col-span-2 p-6 bg-white">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-sm font-semibold text-slate-700">Preview</div>
                    <div className="text-xs text-slate-500">cleaned_sample.csv</div>
                  </div>
                  <div className="border border-slate-200 rounded-xl overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-left text-xs">
                        <thead className="bg-slate-50 border-b border-slate-200">
                          <tr>
                            {['id','name','email','country','age','joined_at','is_active'].map(h=>(
                              <th key={h} className="px-3 py-2 font-semibold text-slate-600 border-r border-slate-200">{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {[
                            ['1','Alice','alice@example.com','US','29','2025-12-01','true'],
                            ['2','Bob','bob@example.com','UK','31','2025-11-12','true'],
                            ['3','Carol','carol@example.com','IN','27','2025-10-03','false'],
                            ['4','Dan','dan@example.com','DE','45','2025-09-21','true'],
                            ['5','Eve','eve@example.com','FR','36','2025-08-18','true']
                          ].map((row,i)=>(
                            <tr key={i} className="hover:bg-slate-50">
                              {row.map((cell,j)=>(
                                <td key={j} className="px-3 py-2 border-t border-r border-slate-100">{cell}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center gap-2">
                    <Link to="/try" className="px-3 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors flex items-center gap-2">
                      Try This Preview <ArrowRight size={14} />
                    </Link>
                    <Link to="/login" className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors">
                      Get API Key
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-10 flex justify-center">
            <div className="flex items-center gap-8 opacity-80">
              <div className="h-8 w-24 bg-slate-200 rounded"></div>
              <div className="h-8 w-24 bg-slate-200 rounded"></div>
              <div className="h-8 w-24 bg-slate-200 rounded"></div>
              <div className="h-8 w-24 bg-slate-200 rounded"></div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900">Everything you need to prep data</h2>
            <p className="mt-4 text-lg text-slate-600">Built for speed, accuracy, and simplicity.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Zap className="w-6 h-6 text-amber-500" />,
                title: "Instant Preprocessing",
                desc: "Clean messy CSVs automatically. Handle missing values, outliers, and duplicates in one click."
              },
              {
                icon: <BarChart className="w-6 h-6 text-blue-500" />,
                title: "Deep Analysis",
                desc: "Get instant distribution stats, correlation matrices, and quality scores for your datasets."
              },
              {
                icon: <Shield className="w-6 h-6 text-green-500" />,
                title: "Secure & Private",
                desc: "Your data is encrypted and automatically deleted after processing. Enterprise-grade security standard."
              },
              {
                icon: <FileText className="w-6 h-6 text-indigo-500" />,
                title: "Smart Reports",
                desc: "Download detailed PDF quality reports to share with stakeholders or attach to your documentation."
              },
              {
                icon: <Database className="w-6 h-6 text-violet-500" />,
                title: "Format Agnostic",
                desc: "Support for CSV, Excel, JSON, and Parquet. Export to any format you need for your ML pipeline."
              },
              {
                icon: <CheckCircle className="w-6 h-6 text-teal-500" />,
                title: "Job Versioning",
                desc: "Track every change. Revert to previous versions or compare before/after states instantly."
              }
            ].map((feature, i) => (
              <div key={i} className="p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 rounded-lg bg-white flex items-center justify-center shadow-sm mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900">How it works</h2>
            <p className="mt-4 text-lg text-slate-600">From upload to clean output in minutes.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Upload", desc: "Upload CSV, Excel, JSON or Parquet securely." },
              { step: "2", title: "Configure", desc: "Choose preprocessing options or use smart defaults." },
              { step: "3", title: "Download", desc: "View results, preview changes, and export processed files." }
            ].map((s, i) => (
              <div key={i} className="p-6 bg-white border border-slate-200 rounded-2xl text-center">
                <div className="mx-auto w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold mb-3">{s.step}</div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{s.title}</h3>
                <p className="text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900">Simple, transparent pricing</h2>
            <p className="mt-4 text-lg text-slate-600">Start for free, upgrade as you grow.</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 relative overflow-hidden">
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Free Trial</h3>
              <div className="text-4xl font-extrabold text-slate-900 mb-6">$0</div>
              <p className="text-slate-600 mb-8">Perfect for testing and small ad-hoc tasks.</p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-green-500" /> No API Key required
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-green-500" /> 5MB File Limit
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-green-500" /> 24-hour Data Retention
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-green-500" /> Basic Preprocessing
                </li>
              </ul>
              <Link to="/try" className="btn-primary w-full block text-center py-3 rounded-lg">Start Free Trial</Link>
            </div>
            
            <div className="bg-white rounded-2xl shadow-xl border-2 border-slate-900 p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-slate-900 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">POPULAR</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Developer API</h3>
              <div className="text-4xl font-extrabold text-slate-900 mb-6">Free <span className="text-lg font-normal text-slate-500">/ forever</span></div>
              <p className="text-slate-600 mb-8">For developers building data pipelines.</p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-indigo-600" /> 1GB Monthly Quota
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-indigo-600" /> 50MB File Limit
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-indigo-600" /> Full API Access
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-indigo-600" /> Persistent History
                </li>
                <li className="flex items-center gap-3 text-slate-700">
                  <CheckCircle size={20} className="text-indigo-600" /> Advanced Quality Reports
                </li>
              </ul>
              <Link to="/login?mode=register" className="block w-full text-center py-3 rounded-lg bg-slate-900 text-white font-bold hover:bg-slate-800 transition-colors">
                Get API Key
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-8 rounded-2xl bg-white border border-slate-200 flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h3 className="text-2xl font-bold text-slate-900">Ready to clean your data?</h3>
              <p className="text-slate-600 mt-1">Start a free trial or get a forever‑free API key.</p>
            </div>
            <div className="flex gap-3">
              <Link to="/try" className="px-5 py-3 rounded-lg bg-slate-900 text-white font-semibold hover:bg-slate-800 transition-colors">
                Start Free Trial
              </Link>
              <Link to="/login?mode=register" className="px-5 py-3 rounded-lg border border-slate-200 text-slate-700 font-semibold hover:bg-slate-50 transition-colors">
                Get API Key
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-slate-900 text-slate-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <Database className="h-6 w-6 text-white" />
              <span className="text-lg font-bold text-white">DataPrep AI</span>
            </div>
            <div className="text-sm">
              &copy; {new Date().getFullYear()} DataPrep AI Inc. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
