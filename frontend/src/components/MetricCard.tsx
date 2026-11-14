import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  variant?: 'amber' | 'cyan' | 'emerald' | 'orange' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  variant = 'amber',
}) => {
  const variantStyles = {
    amber: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400',
      badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    },
    cyan: {
      border: 'border-cyan-500/20 hover:border-cyan-500/40',
      iconBg: 'bg-cyan-500/10 text-cyan-400',
      badge: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
    },
    emerald: {
      border: 'border-emerald-500/20 hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400',
      badge: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    },
    orange: {
      border: 'border-orange-500/20 hover:border-orange-500/40',
      iconBg: 'bg-orange-500/10 text-orange-400',
      badge: 'bg-orange-500/10 text-orange-300 border-orange-500/30',
    },
    purple: {
      border: 'border-purple-500/20 hover:border-purple-500/40',
      iconBg: 'bg-purple-500/10 text-purple-400',
      badge: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
    },
  }[variant];

  return (
    <div
      className={`p-5 rounded-xl bg-slate-900/80 border ${variantStyles.border} transition-all duration-200 shadow-sm relative overflow-hidden`}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {title}
          </p>
          <h3 className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
            {value}
          </h3>
          {subtitle && (
            <p className="text-xs text-slate-400 pt-0.5">{subtitle}</p>
          )}
        </div>
        <div className={`p-2.5 rounded-xl ${variantStyles.iconBg}`}>
          <Icon className="w-5 h-5 stroke-[2]" />
        </div>
      </div>
      {badge && (
        <div className="mt-3.5 pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <span
            className={`text-[11px] px-2 py-0.5 rounded-md font-mono border ${variantStyles.badge}`}
          >
            {badge}
          </span>
        </div>
      )}
    </div>
  );
};
