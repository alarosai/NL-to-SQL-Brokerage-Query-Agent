"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Database, Key, Link2 } from 'lucide-react';
import Link from 'next/link';

const TABLES = [
  {
    name: 'accounts',
    description: 'Synthetic brokerage accounts.',
    columns: [
      { name: 'account_id', type: 'INTEGER', isPk: true },
      { name: 'name', type: 'TEXT' },
      { name: 'country', type: 'TEXT' },
      { name: 'account_type', type: 'TEXT' },
      { name: 'created_at', type: 'TEXT' },
    ]
  },
  {
    name: 'instruments',
    description: 'Real NASDAQ/NYSE tickers with company names.',
    columns: [
      { name: 'ticker', type: 'TEXT', isPk: true },
      { name: 'name', type: 'TEXT' },
      { name: 'asset_class', type: 'TEXT' },
      { name: 'exchange', type: 'TEXT' },
    ]
  },
  {
    name: 'orders',
    description: 'Historical trade orders.',
    columns: [
      { name: 'order_id', type: 'INTEGER', isPk: true },
      { name: 'account_id', type: 'INTEGER', isFk: 'accounts.account_id' },
      { name: 'ticker', type: 'TEXT', isFk: 'instruments.ticker' },
      { name: 'side', type: 'TEXT' },
      { name: 'qty', type: 'INTEGER' },
      { name: 'price', type: 'REAL' },
      { name: 'status', type: 'TEXT' },
      { name: 'created_at', type: 'TEXT' },
    ]
  },
  {
    name: 'positions',
    description: 'Aggregated positions derived from filled orders.',
    columns: [
      { name: 'account_id', type: 'INTEGER', isFk: 'accounts.account_id' },
      { name: 'ticker', type: 'TEXT', isFk: 'instruments.ticker' },
      { name: 'shares_held', type: 'INTEGER' },
      { name: 'avg_cost', type: 'REAL' },
      { name: 'last_updated', type: 'TEXT' },
    ]
  },
  {
    name: 'prices',
    description: 'Historical OHLCV market data.',
    columns: [
      { name: 'ticker', type: 'TEXT', isFk: 'instruments.ticker' },
      { name: 'date', type: 'TEXT' },
      { name: 'open', type: 'REAL' },
      { name: 'high', type: 'REAL' },
      { name: 'low', type: 'REAL' },
      { name: 'close', type: 'REAL' },
      { name: 'volume', type: 'INTEGER' },
    ]
  }
];

export default function SchemaPage() {
  return (
    <main className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col items-center">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full flex items-center justify-between mb-16 mt-4"
      >
        <Link 
          href="/" 
          className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 text-gray-300 hover:text-white transition-all shadow-lg backdrop-blur-md"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Query Agent
        </Link>
        <div className="flex items-center gap-3 bg-indigo-500/10 border border-indigo-500/20 px-6 py-2.5 rounded-full">
          <Database className="w-5 h-5 text-indigo-400" />
          <h1 className="text-xl font-bold tracking-tight text-indigo-100">
            Database Schema
          </h1>
        </div>
        <div className="w-[180px]" /> {/* Spacer for centering */}
      </motion.div>

      {/* ERD Grid */}
      <motion.div 
        initial="hidden"
        animate="show"
        variants={{
          hidden: { opacity: 0 },
          show: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
          }
        }}
        className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
      >
        {TABLES.map((table) => (
          <motion.div
            key={table.name}
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
            className="glass rounded-2xl overflow-hidden shadow-2xl flex flex-col hover:border-indigo-500/30 transition-colors duration-500 group"
          >
            {/* Table Header */}
            <div className="bg-black/40 border-b border-white/5 p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-colors duration-500">
                  <Database className="w-4 h-4" />
                </div>
                <h2 className="text-xl font-bold text-gray-100 tracking-tight">{table.name}</h2>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">{table.description}</p>
            </div>

            {/* Table Columns */}
            <div className="flex-1 p-0 overflow-hidden relative">
              <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />
              <table className="w-full text-sm text-left">
                <tbody>
                  {table.columns.map((col) => (
                    <tr key={col.name} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors">
                      <td className="px-5 py-3 font-mono text-indigo-300 flex items-center gap-2">
                        {col.isPk && <span title="Primary Key"><Key className="w-3.5 h-3.5 text-amber-500 shrink-0" /></span>}
                        {col.isFk && <span title={`Foreign Key to ${col.isFk}`}><Link2 className="w-3.5 h-3.5 text-blue-400 shrink-0" /></span>}
                        {!col.isPk && !col.isFk && <div className="w-3.5 h-3.5 shrink-0" />}
                        <span>{col.name}</span>
                      </td>
                      <td className="px-5 py-3 text-gray-500 font-mono text-xs text-right whitespace-nowrap">
                        {col.type}
                        {col.isFk && (
                          <span className="block text-[10px] text-blue-400/70 mt-0.5 bg-blue-500/10 inline-block px-1.5 py-0.5 rounded border border-blue-500/20">
                            → {col.isFk}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Footer */}
      <footer className="w-full mt-auto pt-24 pb-8 text-center text-sm text-gray-500">
        Built with ❤️ by <a href="https://www.linkedin.com/in/alarosai" target="_blank" rel="noreferrer" className="hover:text-gray-300 transition-colors underline decoration-white/20 underline-offset-4">Alberto La Rosa</a>
      </footer>
    </main>
  );
}
