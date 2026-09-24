import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MotionCard } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MotionButton } from '@/components/ui/button';
import { Search, Filter, Server, MapPin, Cpu, Smartphone, Zap, BatteryFull, BatteryMedium, BatteryWarning } from 'lucide-react';


import axios from 'axios';

export function Clients() {
  const [clients, setClients] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      try {
        const response = await axios.get('/api/v1/clients');
        setClients(response.data);
      } catch (e) {
        console.error(e);
      }
    }
    load();
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-8 max-w-7xl mx-auto space-y-8"
    >
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Clients</h1>
          <p className="text-muted-foreground mt-1">Edge devices and organizations in the federation.</p>
        </div>
        <MotionButton>
          Provision Client
        </MotionButton>
      </header>

      <MotionCard className="p-0 overflow-hidden">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row gap-4 items-center justify-between bg-slate-50/50">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search clients..." 
              className="w-full pl-9 pr-4 py-2 bg-white border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
          <MotionButton variant="outline" size="sm" className="w-full sm:w-auto gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </MotionButton>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-muted-foreground font-medium border-b border-border">
              <tr>
                <th className="px-6 py-3">Client</th>
                <th className="px-6 py-3">Device Type</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">CPU / Memory</th>
                <th className="px-6 py-3">Bandwidth</th>
                <th className="px-6 py-3">Battery</th>
                <th className="px-6 py-3">Location</th>
                <th className="px-6 py-3">Data Size</th>
                <th className="px-6 py-3 text-right">Last Ping</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {clients.map((client) => (
                <tr key={client.client_id} className="hover:bg-slate-50/50 transition-colors cursor-pointer">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-md bg-slate-100 flex items-center justify-center text-slate-500">
                        <Server className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="font-medium text-foreground">{client.organization_name || client.client_id}</div>
                        <div className="text-xs text-muted-foreground">{client.client_id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {client.device_type === 'iot' ? <Cpu className="w-4 h-4 text-slate-500" /> :
                       client.device_type === 'mobile' ? <Smartphone className="w-4 h-4 text-slate-500" /> :
                       <Server className="w-4 h-4 text-slate-500" />}
                      <span className="capitalize">{client.device_type || 'unknown'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={
                      client.status === 'online' ? 'success' : 
                      client.status === 'offline' ? 'secondary' : 'default'
                    } className="capitalize">
                      {client.status || 'unknown'}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-foreground capitalize">
                      {client.cpu_class || '-'} {client.memory_mb ? `• ${client.memory_mb} MB` : ''}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-foreground">
                      {client.bandwidth_mbps ? `${client.bandwidth_mbps} Mbps` : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {client.battery_powered ? (
                      <div className="flex items-center gap-1.5" title={client.battery_level < 0.2 ? 'Low Battery' : ''}>
                        {client.battery_level > 0.8 ? <BatteryFull className="w-4 h-4 text-green-500" /> :
                         client.battery_level > 0.3 ? <BatteryMedium className="w-4 h-4 text-amber-500" /> :
                         <BatteryWarning className="w-4 h-4 text-red-500" />}
                        <span className="text-sm">{(client.battery_level * 100).toFixed(0)}%</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <Zap className="w-4 h-4" />
                        <span className="text-sm">AC</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      Global
                    </div>
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{client.sample_count || '-'}</td>
                  <td className="px-6 py-4 text-right text-muted-foreground">
                    {client.last_seen_at ? new Date(client.last_seen_at).toLocaleTimeString() : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </MotionCard>
    </motion.div>
  );
}
