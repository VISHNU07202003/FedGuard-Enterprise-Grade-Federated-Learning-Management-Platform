import { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, Activity, Users, Network, FlaskConical, Box, ShieldCheck, Bot, Settings, LogOut, Menu, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/features/auth/AuthContext';

const groups = [
  { label: 'Federation', items: [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/training', label: 'Training runs', icon: Activity },
    { to: '/clients', label: 'Edge clients', icon: Users },
    { to: '/topology', label: 'Network topology', icon: Network },
  ] },
  { label: 'Intelligence & operations', items: [
    { to: '/experiments', label: 'Experiments', icon: FlaskConical },
    { to: '/models', label: 'Model registry', icon: Box },
    { to: '/security', label: 'Security', icon: ShieldCheck },
    { to: '/observability', label: 'Observability', icon: Activity },
    { to: '/copilot', label: 'AI Copilot', icon: Bot },
    { to: '/settings', label: 'Settings', icon: Settings },
  ] },
];

export function MainLayout() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const { pathname } = useLocation();
  const current = groups.flatMap(group => group.items).find(item => item.to === pathname)?.label || 'Training details';
  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">Skip to content</a>
      <aside className="app-sidebar">
        <div className="flex items-center justify-between p-5">
          <NavLink to="/" className="flex items-center gap-3" aria-label="FedGuard overview">
            <span className="rounded-xl border border-primary/30 bg-primary/10 p-2 text-primary"><ShieldCheck size={24} /></span>
            <span><span className="block text-lg font-semibold tracking-tight">FedGuard</span><span className="eyebrow">Federated intelligence</span></span>
          </NavLink>
          <button className="icon-button lg:hidden" aria-label="Toggle navigation" aria-expanded={menuOpen} aria-controls="platform-navigation" onClick={() => setMenuOpen(!menuOpen)}><Menu size={20} /></button>
        </div>
        <nav id="platform-navigation" aria-label="Platform" className={cn('sidebar-navigation', menuOpen ? 'block' : 'hidden lg:block')} onKeyDown={event => { if (event.key === 'Escape') setMenuOpen(false); }}>
          {groups.map(group => <div key={group.label} className="mb-6">
            <p className="eyebrow px-3 mb-2">{group.label}</p>
            {group.items.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} onClick={() => setMenuOpen(false)} className={({ isActive }) => cn('nav-item', isActive && 'nav-item-active')}><Icon size={18} aria-hidden="true" />{label}</NavLink>)}
          </div>)}
        </nav>
        <div className="mt-auto hidden lg:block border-t border-border p-5 text-xs leading-relaxed text-muted-foreground">Distributed Intelligence.<br /><span className="text-foreground">Private by Design.</span></div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="app-topbar">
          <div className="flex min-w-0 items-center gap-2 text-sm"><span className="hidden sm:inline text-muted-foreground">Workspace</span><ChevronRight size={14} className="hidden sm:block text-muted-foreground" /><span className="truncate">{current}</span></div>
          {user && <div className="flex min-w-0 items-center gap-3">
            <div className="min-w-0 text-right"><p className="max-w-44 truncate text-sm">{user.full_name || user.email}</p><p className="eyebrow">{user.role}</p></div>
            <button onClick={logout} className="icon-button" aria-label="Sign out" title="Sign out"><LogOut size={18} /></button>
          </div>}
        </header>
        <main id="main-content" tabIndex={-1} className="app-content"><Outlet /></main>
      </div>
    </div>
  );
}
