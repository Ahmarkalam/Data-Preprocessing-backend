import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { KeyRound, ArrowRight, Loader2, Mail, CheckCircle } from 'lucide-react';
import apiClient from '../api/client';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [previewLink, setPreviewLink] = useState('');
  const [previewApiKey, setPreviewApiKey] = useState('');

  const handleRequestAccess = async (e) => {
    e.preventDefault();
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!email || !emailRegex.test(email)) {
      setError('Please enter a valid email address.');
      return;
    }
    setLoading(true);
    setError('');

    try {
      const { data } = await apiClient.post(`/auth/request-access?email=${encodeURIComponent(email)}`);
      const link = data?.preview?.link;
      const apiKey = data?.preview?.api_key;
      if (link) setPreviewLink(link);
      if (apiKey) setPreviewApiKey(apiKey);
      setSent(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send access link.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
        
        {/* Header */}
        <div className="p-8 pb-0">
           <Link to="/" className="inline-flex items-center gap-2 text-indigo-600 font-bold mb-6 hover:opacity-80">
             <ArrowRight className="rotate-180" size={16} /> Back to Home
           </Link>
           <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-200">
             <KeyRound className="text-white" size={24} />
           </div>
           <h1 className="text-2xl font-bold text-slate-900 mb-2">
             Access Your Dashboard
           </h1>
           <p className="text-slate-500 mb-6">
             Enter your email to receive a secure access link.
           </p>
        </div>

        <div className="p-8 pt-0">
          {!sent ? (
            <form onSubmit={handleRequestAccess} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                    placeholder="you@company.com"
                    required
                  />
                </div>
              </div>
              {error && (
                <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                  {error}
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary py-3 rounded-lg bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-all flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="animate-spin" /> : "Send me access link"}
              </button>
              <div className="text-center mt-3 text-sm text-slate-500">
                Or <button type="button" onClick={() => navigate('/try')} className="text-indigo-600 hover:underline">start a free trial</button>
              </div>
            </form>
          ) : (
            <div className="bg-green-50 border border-green-100 rounded-xl p-6 text-center space-y-3">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto text-green-600">
                <CheckCircle size={24} />
              </div>
              <h3 className="text-lg font-bold text-green-800">Check your email</h3>
              <p className="text-sm text-green-700">We sent you an access link to continue.</p>
              {previewLink && (
                <div className="mt-2 p-3 bg-white rounded-lg border border-green-200 text-left">
                  <p className="text-xs text-slate-600 mb-2">
                    If the email doesn’t arrive, you can use the instant access link below:
                  </p>
                  <div className="flex items-center gap-2">
                    <a
                      href={previewLink}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
                    >
                      Open Access Link
                    </a>
                    {previewApiKey && (
                      <button
                        type="button"
                        onClick={() => navigator.clipboard.writeText(previewApiKey)}
                        className="px-3 py-2 bg-white border border-green-300 text-green-700 text-sm rounded-md hover:bg-green-50 transition-colors"
                      >
                        Copy API Key
                      </button>
                    )}
                  </div>
                </div>
              )}
              <div className="text-center mt-1 text-sm text-slate-500">
                Or <button type="button" onClick={() => navigate('/try')} className="text-indigo-600 hover:underline">start a free trial</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Login;
