import type { ComplaintStatus } from '../types';

const statusStyles: Record<ComplaintStatus, { bg: string; text: string; dot: string }> = {
  SUBMITTED:   { bg: 'bg-amber-500/15',  text: 'text-amber-400',  dot: 'bg-amber-400' },
  ASSIGNED:    { bg: 'bg-blue-500/15',    text: 'text-blue-400',   dot: 'bg-blue-400' },
  IN_PROGRESS: { bg: 'bg-purple-500/15',  text: 'text-purple-400', dot: 'bg-purple-400' },
  RESOLVED:    { bg: 'bg-emerald-500/15', text: 'text-emerald-400',dot: 'bg-emerald-400' },
  CLOSED:      { bg: 'bg-gray-500/15',    text: 'text-gray-400',   dot: 'bg-gray-500' },
};

interface Props {
  status: ComplaintStatus;
  size?: 'sm' | 'md';
}

export default function StatusBadge({ status, size = 'sm' }: Props) {
  const style = statusStyles[status] || statusStyles.SUBMITTED;
  const label = status.replace('_', ' ');

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full
        ${style.bg} ${style.text}
        ${size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-sm'}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
      {label}
    </span>
  );
}
