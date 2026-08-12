import type { StatusHistoryResponse } from '../types';

interface Props {
  history: StatusHistoryResponse[];
}

export default function Timeline({ history }: Props) {
  if (!history.length) {
    return <p className="text-gray-500 text-sm py-4">No history available.</p>;
  }

  return (
    <div className="relative pl-6">
      {/* Vertical line */}
      <div className="absolute left-[9px] top-2 bottom-2 w-px bg-gradient-to-b from-blue-500/40 via-gray-700/40 to-transparent" />

      <div className="space-y-6">
        {history.map((entry, i) => (
          <div key={entry.id} className="relative animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
            {/* Dot */}
            <div className={`absolute -left-6 top-1 w-[18px] h-[18px] rounded-full border-2
              ${i === history.length - 1
                ? 'border-blue-500 bg-blue-500/20'
                : 'border-gray-600 bg-gray-800'
              }`}
            >
              <div className={`absolute inset-[3px] rounded-full ${i === history.length - 1 ? 'bg-blue-500' : 'bg-gray-600'}`} />
            </div>

            {/* Content */}
            <div className="glass-card p-4">
              <div className="flex items-center justify-between gap-4 mb-1">
                <div className="flex items-center gap-2 text-sm">
                  {entry.old_status ? (
                    <>
                      <span className="text-gray-500">{entry.old_status.replace('_', ' ')}</span>
                      <span className="text-gray-600">→</span>
                      <span className="text-blue-400 font-semibold">{entry.new_status.replace('_', ' ')}</span>
                    </>
                  ) : (
                    <span className="text-emerald-400 font-semibold">{entry.new_status.replace('_', ' ')}</span>
                  )}
                </div>
                <time className="text-xs text-gray-500 whitespace-nowrap">
                  {new Date(entry.created_at).toLocaleString()}
                </time>
              </div>

              <p className="text-xs text-gray-500 mb-1">
                by <span className="text-gray-300 font-medium">{entry.changed_by.name}</span>
                <span className="text-gray-600"> ({entry.changed_by.role})</span>
              </p>

              {entry.comment && (
                <p className="text-sm text-gray-400 mt-2 italic border-l-2 border-gray-700 pl-3">
                  {entry.comment}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
