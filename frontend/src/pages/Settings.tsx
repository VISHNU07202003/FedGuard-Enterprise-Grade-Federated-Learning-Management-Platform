import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { MotionButton } from '@/components/ui/button';
import { useAuth } from '@/features/auth/AuthContext';
import { User, Shield, Bell, Database, Key, Check } from 'lucide-react';

export function Settings() {
  const { user } = useAuth();

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-8 max-w-5xl mx-auto space-y-8"
    >
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your platform configuration and profile.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg bg-indigo-50 text-indigo-700">
            <User className="h-4 w-4" />
            Profile
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors">
            <Shield className="h-4 w-4" />
            Security
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors">
            <Bell className="h-4 w-4" />
            Notifications
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors">
            <Database className="h-4 w-4" />
            AWS & Storage
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors">
            <Key className="h-4 w-4" />
            API Keys
          </button>
        </div>

        <div className="col-span-1 md:col-span-3 space-y-6">
          <MotionCard className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">Profile Information</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700">Full Name</label>
                  <input type="text" defaultValue={user?.full_name || 'Administrator'} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700">Email Address</label>
                  <input type="email" defaultValue={user?.email || 'admin@fedguard.dev'} className="w-full px-3 py-2 border border-slate-200 bg-slate-50 rounded-lg text-sm text-slate-500 cursor-not-allowed" disabled />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Role</label>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-800 capitalize border border-slate-200">
                    {user?.role || 'admin'}
                  </span>
                  <span className="text-xs text-slate-500">You have full platform access.</span>
                </div>
              </div>
              <div className="pt-4 flex justify-end">
                <MotionButton className="gap-2">
                  <Check className="h-4 w-4" />
                  Save Changes
                </MotionButton>
              </div>
            </div>
          </MotionCard>

          <MotionCard className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-1">Local Configuration</h2>
            <p className="text-sm text-slate-500 mb-4">Your platform is currently running in local development mode.</p>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg bg-slate-50">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-900">Environment Provider</p>
                  <p className="text-xs text-slate-500">Configuration is loaded from .env (Parameter Store disabled)</p>
                </div>
                <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-2 py-1 rounded text-xs font-medium border border-emerald-100">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                  Local (.env)
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg bg-slate-50">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-900">LLM Proxy Connected</p>
                  <p className="text-xs text-slate-500">Connected to UF NaviGator (api.ai.it.ufl.edu)</p>
                </div>
                <div className="flex items-center gap-2 text-indigo-600 bg-indigo-50 px-2 py-1 rounded text-xs font-medium border border-indigo-100">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                  LiteLLM Active
                </div>
              </div>
            </div>
          </MotionCard>
        </div>
      </div>
    </motion.div>
  );
}
