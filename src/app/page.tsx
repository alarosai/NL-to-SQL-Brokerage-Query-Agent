"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Database, Code2, AlertCircle, Table as TableIcon } from 'lucide-react';
import Link from 'next/link';

const SUGGESTIONS = [
  "Find the ticker with the highest average position size",
  "What is the average order size for AAPL?",
  "Which tickers have the highest average order size?",
  "Show positions where unrealized loss exceeds 10%"
];

type QueryResponse = {
  status: 'success' | 'rejected' | 'error';
  sql?: string;
  results?: any[];
  summary?: string;
  reason?: string;
  error?: string;
};

export default function Home() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);

  const handleSubmit = async (e?: React.FormEvent, textOverride?: string) => {
    e?.preventDefault();
    const submitText = textOverride || query;
    if (!submitText.trim()) return;

    setIsLoading(true);
    setResponse(null);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: submitText }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err: any) {
      setResponse({ status: 'error', error: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto flex flex-col items-center">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="text-center mb-12 mt-8"
      >
        <div className="inline-flex items-center justify-center p-3 mb-6 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
          <Database className="w-8 h-8 text-indigo-400" />
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight mb-4">
          Brokerage Query <span className="text-gradient">Agent</span>
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
          Ask complex questions about accounts, orders, prices, and positions in plain English. Powered by Google Gemini and local SQLite data.
        </p>

        <div className="flex justify-center flex-row">
          <Link 
            href="/erd"
            className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 text-sm font-medium text-gray-300 hover:text-white transition-all shadow-lg backdrop-blur-md"
          >
            <Database className="w-4 h-4 text-indigo-400" />
            View ERD Schema Diagram
          </Link>
        </div>
      </motion.div>

      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="w-full max-w-3xl mb-8"
      >
        <form onSubmit={handleSubmit} className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500" />
          <div className="relative flex items-center bg-[#0a0a0c] border border-white/10 rounded-2xl overflow-hidden shadow-2xl focus-within:ring-2 focus-within:ring-indigo-500/50 transition-all">
            <input
              type="text"
              className="flex-1 bg-transparent px-6 py-5 text-lg outline-none placeholder-gray-500 text-gray-100"
              placeholder="e.g. Find the ticker with the highest average position size..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="p-4 mr-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors text-white flex items-center justify-center"
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Send className="w-6 h-6" />
              )}
            </button>
          </div>
        </form>

        {/* Suggestion Pills */}
        <div className="flex flex-wrap gap-2 mt-6 justify-center">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => { setQuery(s); handleSubmit(undefined, s); }}
              className="text-xs font-medium px-4 py-2 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Results Section */}
      <div className="w-full max-w-4xl mt-4">
        <AnimatePresence mode="wait">
          {response && (
            <motion.div
              key="response"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.4 }}
              className="glass rounded-3xl overflow-hidden shadow-2xl"
            >
              {response.status === 'rejected' && (
                <div className="p-8 border-l-4 border-red-500 bg-red-500/5">
                  <div className="flex items-start gap-4">
                    <AlertCircle className="w-6 h-6 text-red-500 shrink-0 mt-1" />
                    <div>
                      <h3 className="text-xl font-semibold text-red-400 mb-2">Query Rejected</h3>
                      <p className="text-gray-300">{response.reason}</p>
                    </div>
                  </div>
                </div>
              )}

              {response.status === 'error' && (
                <div className="p-8 border-l-4 border-orange-500 bg-orange-500/5">
                  <div className="flex items-start gap-4">
                    <AlertCircle className="w-6 h-6 text-orange-500 shrink-0 mt-1" />
                    <div>
                      <h3 className="text-xl font-semibold text-orange-400 mb-2">Execution Error</h3>
                      <p className="text-gray-300">{response.error}</p>
                      {response.sql && (
                        <div className="mt-4 p-4 bg-black/50 rounded-lg font-mono text-sm text-gray-400 overflow-x-auto">
                          {response.sql}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {response.status === 'success' && (
                <div className="flex flex-col">
                  {/* Summary Header */}
                  <div className="p-8 bg-white/[0.02] border-b border-white/5">
                    <h3 className="text-[1.35rem] leading-relaxed text-indigo-100 font-medium">
                      {response.summary}
                    </h3>
                  </div>

                  {/* SQL Toggle */}
                  {/* Generated SQL */}
                  <div className="border-b border-white/5 bg-black/40">
                    <div className="px-8 py-3 flex items-center gap-2 text-sm text-gray-400 border-b border-white/5">
                      <Code2 className="w-4 h-4" /> Generated SQL
                    </div>
                    <div className="p-6 font-mono text-sm text-green-400 overflow-x-auto">
                      <pre>{response.sql}</pre>
                    </div>
                  </div>

                  {/* Data Table */}
                  {response.results && response.results.length > 0 && (
                    <div className="w-full overflow-x-auto">
                      <div className="p-4 border-b border-white/5 flex items-center gap-2 text-sm text-gray-400 bg-black/20">
                        <TableIcon className="w-4 h-4" />
                        {response.results.length} rows returned
                      </div>
                      <table className="w-full text-sm text-left">
                        <thead className="text-xs uppercase bg-black/30 text-gray-400">
                          <tr>
                            {Object.keys(response.results[0]).map((key) => (
                              <th key={key} className="px-6 py-4 font-medium tracking-wider">{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {response.results.map((row, i) => (
                            <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                              {Object.values(row).map((val: any, j) => (
                                <td key={j} className="px-6 py-4 whitespace-nowrap text-gray-300">
                                  {val === null ? <span className="text-gray-600">NULL</span> : String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {response.results?.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                      No results found.
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <footer className="w-full mt-auto pt-16 pb-8 text-center text-sm text-gray-500">
        Built with ❤️ by <a href="https://www.linkedin.com/in/alarosai" target="_blank" rel="noreferrer" className="hover:text-gray-300 transition-colors underline decoration-white/20 underline-offset-4">Alberto La Rosa</a>
      </footer>
    </main>
  );
}
