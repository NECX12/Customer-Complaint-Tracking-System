import type { ComplaintPriority } from '../types';

const priorityStyles: Record<ComplaintPriority, { bg: string; text: string }> = {
  LOW:      { bg: 'bg-gray-500/15',    text: 'text-gray-400' },
  MEDIUM:   { bg: 'bg-blue-500/15',    text: 'text-blue-400' },
  HIGH:     { bg: 'bg-orange-500/15',   text: 'text-orange-400' },
  CRITICAL: { bg: 'bg-red-500/15',      text: 'text-red-400' },
};

const priorityIcons: Record<ComplaintPriority, string> = {
  LOW: '↓',
  MEDIUM: '→',
  HIGH: '↑',
  CRITICAL: '⚡',
};

interface Props {
  priority: ComplaintPriority;
}

export default function PriorityBadge({ priority }: Props) {
  const style = priorityStyles[priority] || priorityStyles.MEDIUM;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold
        rounded-full ${style.bg} ${style.text}`}
    >
      {priorityIcons[priority]} {priority}
    </span>
  );
}
