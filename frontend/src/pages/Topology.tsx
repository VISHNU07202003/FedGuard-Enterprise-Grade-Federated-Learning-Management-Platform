import { DataState } from '@/components/ui/data-state';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Server, Cpu, Smartphone } from 'lucide-react';

export function Topology() {
  const [clients, setClients] = useState<any[]>([]);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const token = localStorage.getItem('token');
        const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};
        const response = await fetch(`${API_URL}/api/v1/clients`, { headers });
        if (response.ok) {
          setClients(await response.json());
        } else {
          setFailed(true);
        }
      } catch (e) {
        console.error(e);
        setFailed(true);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [API_URL]);

  const radius = 250;
  const centerX = 400;
  const centerY = 300;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="max-w-7xl mx-auto space-y-8 flex flex-col min-h-[620px]"
    >
      <header className="flex-shrink-0">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Topology</h1>
        <p className="text-muted-foreground mt-1">Network map of federated nodes and aggregation servers.</p>
      </header>

      {loading ? <DataState kind="loading" title="Loading network topology" /> : failed ? <DataState kind="error" title="Network map unavailable" description="Check your connection and refresh to try again." /> : !clients.length ? <DataState title="No clients reported" /> : <MotionCard className="flex-1 flex items-center justify-center bg-muted/50 border-2 relative overflow-hidden">
        <div className="absolute inset-0 opacity-5 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-500 via-transparent to-transparent" />

        <svg role="img" aria-label="Federated client topology; solid lines indicate online clients and dashed lines indicate other states" viewBox="0 0 800 600" className="w-full h-full max-h-[600px] z-10">
          {/* Connection Lines */}
          {clients.map((client, i) => {
            const angle = (i / clients.length) * 2 * Math.PI - Math.PI / 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            return (
              <line
                key={`line-${client.client_id}`}
                x1={centerX} y1={centerY}
                x2={x} y2={y}
                stroke={client.status === 'online' ? '#93c5fd' : '#475569'}
                strokeWidth="2"
                strokeDasharray={client.status === 'online' ? 'none' : '4 4'}
              />
            );
          })}

          {/* Central Server Node */}
          <g transform={`translate(${centerX}, ${centerY})`}>
            <circle r="40" fill="#111a29" stroke="#4f46e5" strokeWidth="3" className="shadow-lg" />
            <foreignObject x="-24" y="-24" width="48" height="48">
              <div className="flex items-center justify-center w-full h-full text-indigo-300">
                <Server size={28} />
              </div>
            </foreignObject>
            <text y="60" textAnchor="middle" className="text-sm font-semibold fill-foreground">Aggregation Server</text>
            <circle r="60" fill="none" stroke="#e0e7ff" strokeWidth="1" strokeDasharray="5 5">

            </circle>
          </g>

          {/* Client Nodes */}
          {clients.map((client, i) => {
            const angle = (i / clients.length) * 2 * Math.PI - Math.PI / 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);

            const isOnline = client.status === 'online';
            const nodeColor = client.device_type === 'mobile' ? '#10b981' :
                              client.device_type === 'iot' ? '#f59e0b' : '#3b82f6';

            return (
              <g key={`node-${client.client_id}`} transform={`translate(${x}, ${y})`}>
                <circle r="25" fill="#111a29" stroke={isOnline ? nodeColor : '#94a3b8'} strokeWidth="2" />
                <foreignObject x="-16" y="-16" width="32" height="32">
                  <div className={`flex items-center justify-center w-full h-full ${isOnline ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {client.device_type === 'iot' ? <Cpu size={18} color={isOnline ? nodeColor : '#94a3b8'} /> :
                     client.device_type === 'mobile' ? <Smartphone size={18} color={isOnline ? nodeColor : '#94a3b8'} /> :
                     <Server size={18} color={isOnline ? nodeColor : '#94a3b8'} />}
                  </div>
                </foreignObject>
                <text y="40" textAnchor="middle" className="text-xs font-medium fill-foreground">{client.client_id.substring(0, 8)}</text>
                <text y="54" textAnchor="middle" className="text-[10px] fill-muted-foreground capitalize">{client.device_type || 'Unknown'}</text>
              </g>
            );
          })}
        </svg>
      </MotionCard>}
    </motion.div>
  );
}
