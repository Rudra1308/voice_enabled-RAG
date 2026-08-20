'use client';

import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, Target } from 'lucide-react';

export default function EvaluationsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/evaluations')
      .then(r => r.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-slate-400">Loading metrics...</div>;
  if (!data) return <div className="p-8 text-slate-400">Failed to load metrics.</div>;

  return (
    <div className="max-w-5xl mx-auto w-full pt-8 pb-4 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100">Evaluations Dashboard</h1>
        <p className="text-slate-400 mt-1">Monitor AI answer quality and RAG metrics over time.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-3 text-slate-400 mb-2">
            <Activity className="h-5 w-5 text-blue-400" />
            <h3 className="font-medium">Total Queries</h3>
          </div>
          <p className="text-3xl font-bold text-slate-100">{data.averages.count}</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-3 text-slate-400 mb-2">
            <ShieldCheck className="h-5 w-5 text-green-400" />
            <h3 className="font-medium">Avg Faithfulness</h3>
          </div>
          <p className="text-3xl font-bold text-slate-100">{(data.averages.faithfulness * 100).toFixed(1)}%</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-3 text-slate-400 mb-2">
            <Target className="h-5 w-5 text-purple-400" />
            <h3 className="font-medium">Avg Relevance</h3>
          </div>
          <p className="text-3xl font-bold text-slate-100">{(data.averages.relevance * 100).toFixed(1)}%</p>
        </div>
      </div>

      <h2 className="text-xl font-bold text-slate-100 mb-4">Recent History</h2>
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50 text-slate-400 uppercase tracking-wider">
            <tr>
              <th className="p-4 font-medium">Query ID</th>
              <th className="p-4 font-medium">Date</th>
              <th className="p-4 font-medium">Faithfulness</th>
              <th className="p-4 font-medium">Relevance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {data.history.length === 0 ? (
              <tr>
                <td colSpan={4} className="p-4 text-center text-slate-500">No evaluations recorded yet.</td>
              </tr>
            ) : (
              data.history.map((h: any) => (
                <tr key={h.id} className="hover:bg-slate-800/20 transition-colors">
                  <td className="p-4 text-slate-300 font-mono text-xs">{h.query_id || 'N/A'}</td>
                  <td className="p-4 text-slate-400">{new Date(h.created_at).toLocaleString()}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${h.faithfulness_score > 0.8 ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                      {(h.faithfulness_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${h.relevance_score > 0.8 ? 'bg-purple-500/10 text-purple-400' : 'bg-orange-500/10 text-orange-400'}`}>
                      {(h.relevance_score * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
