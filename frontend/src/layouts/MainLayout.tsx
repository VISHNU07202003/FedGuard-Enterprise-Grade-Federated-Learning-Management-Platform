import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  Users, 
  Network, 
  FlaskConical, 
  Box, 
  ShieldCheck, 
  Bot, 
  Settings,
  LogOut
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/features/auth/AuthContext';

interface SidebarItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  end?: boolean;
}

function SidebarItem({ to, icon, label, end }: SidebarItemProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => cn(
        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
        isActive 
          ? "bg-white shadow-sm text-primary" 
          : "text-muted-foreground hover:bg-slate-100 hover:text-foreground"
      )}
    >
      {({ isActive }) => (
        <>
          {React.cloneElement(icon as React.ReactElement, { 
            className: cn("w-5 h-5 transition-colors", isActive ? "text-primary" : "text-muted-foreground") 
          })}
          {label}
        </>
      )}
    </NavLink>
  );
}

export function MainLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen bg-background text-foreground font-sans">
      
      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-border bg-background/50 backdrop-blur-xl shrink-0">
        <div className="p-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-sm">
              <ShieldCheck className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight leading-none text-foreground">FedGuard</h1>
              <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider mt-1">Platform</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
          <SidebarItem to="/" icon={<LayoutDashboard />} label="Dashboard" end />
          <SidebarItem to="/training" icon={<Activity />} label="Training Runs" />
          <SidebarItem to="/clients" icon={<Users />} label="Clients" />
          <SidebarItem to="/topology" icon={<Network />} label="Topology" />
          <SidebarItem to="/experiments" icon={<FlaskConical />} label="Experiments" />
          <SidebarItem to="/models" icon={<Box />} label="Model Registry" />
          <SidebarItem to="/security" icon={<ShieldCheck />} label="Security" />
          <SidebarItem to="/observability" icon={<Activity />} label="Observability" />
          <SidebarItem to="/copilot" icon={<Bot />} label="Copilot" />
        </nav>

        <div className="p-4 border-t border-border">
          <SidebarItem to="/settings" icon={<Settings />} label="Settings" />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        {/* Topbar */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-border/50 bg-card/50 backdrop-blur-md shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold tracking-tight">FedGuard</h2>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="success" className="gap-1.5 shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              System Active
            </Badge>
            
            <div className="h-6 w-px bg-border/60 mx-2"></div>
            
            {user && (
              <div className="flex items-center gap-3">
                <div className="flex flex-col text-right">
                  <span className="text-sm font-medium">{user.full_name || user.email}</span>
                  <span className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider">{user.role}</span>
                </div>
                <button 
                  onClick={logout}
                  className="p-2 rounded-full hover:bg-slate-100 transition-colors text-muted-foreground hover:text-red-500"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Page Content with soft fade transition */}
        <div className="flex-1 overflow-y-auto bg-slate-50">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
