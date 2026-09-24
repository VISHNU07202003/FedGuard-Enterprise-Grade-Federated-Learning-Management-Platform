
import { motion } from 'framer-motion';

export function PlaceholderPage({ title, description }: { title: string, description: string }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-8 max-w-7xl mx-auto space-y-8"
    >
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">{title}</h1>
        <p className="text-muted-foreground mt-1">{description}</p>
      </header>

      <div className="bg-white rounded-xl border border-border shadow-sm p-12 text-center">
        <h3 className="text-lg font-medium text-foreground">Coming Soon</h3>
        <p className="text-muted-foreground mt-2">This module is planned for a subsequent development phase.</p>
      </div>
    </motion.div>
  );
}
