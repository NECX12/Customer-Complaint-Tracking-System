import { useState } from 'react';
import client from '../api/client';
import type { AiSuggestionResponse, AiSuggestionItem } from '../types';

interface AiSuggestionPanelProps {
  complaintId: string;
}

export default function AiSuggestionPanel({ complaintId }: AiSuggestionPanelProps) {
  const [data, setData] = useState<AiSuggestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const fetchSuggestions = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await client.get<AiSuggestionResponse>(`/ai/suggestions/${complaintId}`);
      // Surface backend-reported errors (e.g. knowledge base not indexed)
      // even when the HTTP status is 200.
      if (res.data.error) {
        setError(res.data.error);
        setData(null);
      } else {
        setData(res.data);
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to fetch AI suggestions');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.75) return 'text-emerald-400';
    if (score >= 0.5) return 'text-amber-400';
    return 'text-gray-500';
  };

  const getScoreBarWidth = (score: number) => `${Math.round(score * 100)}%`;

  const getSourceBadge = (sourceType: string) => {
    if (sourceType === 'knowledge_base') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/25">
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          Knowledge Base
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-purple-500/15 text-purple-400 border border-purple-500/25">
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Past Complaint
      </span>
    );
  };

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500/20 to-cyan-500/20 border border-violet-500/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div className="text-left">
            <h3 className="text-sm font-semibold text-gray-200">AI Resolution Suggestions</h3>
            <p className="text-[11px] text-gray-500 mt-0.5">Powered by RAG knowledge base</p>
          </div>
        </div>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Body */}
      {isOpen && (
        <div className="px-5 pb-5 animate-fade-in">
          {/* Not loaded yet — show fetch button */}
          {!data && !loading && !error && (
            <button
              onClick={fetchSuggestions}
              className="w-full py-3 px-4 rounded-xl border border-dashed border-violet-500/30 
                         text-violet-400 text-sm font-medium hover:bg-violet-500/5 hover:border-violet-500/50 
                         transition-all duration-200 flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Search Knowledge Base for Suggestions
            </button>
          )}

          {/* Loading state */}
          {loading && (
            <div className="flex flex-col items-center py-8 gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-full border-2 border-violet-500/20 border-t-violet-400 animate-spin" />
                <div className="absolute inset-0 w-10 h-10 rounded-full border-2 border-transparent border-b-cyan-400/50 animate-spin" style={{ animationDuration: '1.5s', animationDirection: 'reverse' }} />
              </div>
              <p className="text-xs text-gray-500 animate-pulse">Searching knowledge base...</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <p>{error}</p>
              <button
                onClick={fetchSuggestions}
                className="mt-2 text-xs underline hover:text-red-300 transition-colors"
              >
                Try again
              </button>
            </div>
          )}

          {/* Results */}
          {data && !loading && (
            <div className="space-y-3">
              {/* Summary bar */}
              <div className="flex items-center justify-between text-[11px] text-gray-500 pb-2 border-b border-gray-800/50">
                <span>
                  {data.total_results} result{data.total_results !== 1 ? 's' : ''} found
                </span>
                <button
                  onClick={fetchSuggestions}
                  className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </button>
              </div>

              {data.suggestions.length === 0 ? (
                <div className="text-center py-6 text-gray-500 text-sm">
                  <p>No relevant suggestions found in the knowledge base.</p>
                  <p className="text-xs mt-1">The knowledge base may need to be indexed.</p>
                </div>
              ) : (
                data.suggestions.map((suggestion) => (
                  <SuggestionCard
                    key={suggestion.id}
                    suggestion={suggestion}
                    isExpanded={expandedIds.has(suggestion.id)}
                    onToggle={() => toggleExpand(suggestion.id)}
                    getScoreColor={getScoreColor}
                    getScoreBarWidth={getScoreBarWidth}
                    getSourceBadge={getSourceBadge}
                  />
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Suggestion Card Sub-Component ──────────────────────────────── */

function SuggestionCard({
  suggestion,
  isExpanded,
  onToggle,
  getScoreColor,
  getScoreBarWidth,
  getSourceBadge,
}: {
  suggestion: AiSuggestionItem;
  isExpanded: boolean;
  onToggle: () => void;
  getScoreColor: (score: number) => string;
  getScoreBarWidth: (score: number) => string;
  getSourceBadge: (sourceType: string) => JSX.Element;
}) {
  // Get first 2 lines as preview
  const lines = suggestion.content.split('\n').filter((l) => l.trim());
  const preview = lines.slice(0, 2).join(' ').slice(0, 150);

  return (
    <div
      className="rounded-xl border border-gray-800/60 bg-gray-900/40 hover:bg-gray-900/60 
                 transition-all duration-200 overflow-hidden"
    >
      {/* Card header — clickable */}
      <button
        onClick={onToggle}
        className="w-full text-left px-4 py-3 flex items-start gap-3"
      >
        <div className="flex-1 min-w-0">
          {/* Badges row */}
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            {getSourceBadge(suggestion.source_type)}
            <span className="text-[10px] text-gray-600 px-1.5 py-0.5 rounded bg-gray-800/60">
              {suggestion.category}
            </span>
          </div>
          {/* Preview text */}
          <p className="text-xs text-gray-400 leading-relaxed line-clamp-2">
            {preview}{!isExpanded && preview.length >= 150 ? '...' : ''}
          </p>
        </div>

        {/* Score + expand indicator */}
        <div className="flex flex-col items-end gap-1.5 shrink-0 pt-0.5">
          <span className={`text-xs font-bold tabular-nums ${getScoreColor(suggestion.similarity_score)}`}>
            {Math.round(suggestion.similarity_score * 100)}%
          </span>
          <svg
            className={`w-3.5 h-3.5 text-gray-600 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-4 pb-4 animate-fade-in">
          {/* Score bar */}
          <div className="mb-3">
            <div className="flex items-center justify-between text-[10px] mb-1">
              <span className="text-gray-500">Relevance</span>
              <span className={getScoreColor(suggestion.similarity_score)}>
                {Math.round(suggestion.similarity_score * 100)}% match
              </span>
            </div>
            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-violet-500 to-cyan-500"
                style={{ width: getScoreBarWidth(suggestion.similarity_score) }}
              />
            </div>
          </div>

          {/* Full content */}
          <div className="text-xs text-gray-400 leading-relaxed whitespace-pre-wrap bg-gray-950/50 rounded-lg p-3 border border-gray-800/40 max-h-64 overflow-y-auto">
            {suggestion.content}
          </div>

          {/* Source info */}
          <div className="mt-2 flex items-center gap-1.5 text-[10px] text-gray-600">
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span className="truncate">{suggestion.source}</span>
          </div>
        </div>
      )}
    </div>
  );
}
