import React, { useState } from 'react';
import { IngestResult } from '../types/ingestion';

interface Props {
    result: IngestResult;
}

export const IngestionResultCard: React.FC<Props> = ({ result }) => {
    const [showMapping, setShowMapping] = useState(false);
    const [showRejections, setShowRejections] = useState(false);

    const isSuccess = result.rows_accepted > 0;
    const hasRejections = result.rows_rejected > 0;
    const isLLM = result.mapping_method === 'llm';

    return (
        <div className="w-full max-w-4xl mx-auto mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden text-sm">
            <div className={`p-4 border-b ${isSuccess ? 'bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-800/50' : 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-800/50'}`}>
                <div className="flex justify-between items-center">
                    <h3 className={`font-semibold ${isSuccess ? 'text-green-800 dark:text-green-300' : 'text-red-800 dark:text-red-300'}`}>
                        {isSuccess ? 'Analysis Complete' : 'Analysis Failed'}
                    </h3>
                    {isLLM && (
                        <span className="px-2.5 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full border border-blue-200 dark:border-blue-800">
                            AI-assisted column detection
                        </span>
                    )}
                </div>
            </div>

            <div className="p-6">
                <div className="grid grid-cols-3 gap-4 mb-6 text-center">
                    <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">{result.rows_total}</div>
                        <div className="text-xs text-gray-500 mt-1 uppercase tracking-wider">Rows Imported</div>
                    </div>
                    <div className={`p-4 rounded-lg ${hasRejections ? 'bg-red-50 dark:bg-red-900/10' : 'bg-gray-50 dark:bg-gray-900/50'}`}>
                        <div className={`text-2xl font-bold ${hasRejections ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>
                            {result.rows_rejected}
                        </div>
                        <div className={`text-xs mt-1 uppercase tracking-wider ${hasRejections ? 'text-red-500' : 'text-gray-500'}`}>Rows Rejected</div>
                    </div>
                    <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                        <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{result.decisions_generated}</div>
                        <div className="text-xs text-gray-500 mt-1 uppercase tracking-wider">Decisions Generated</div>
                    </div>
                </div>

                {result.warnings && result.warnings.length > 0 && (
                    <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800/50">
                        <h4 className="font-semibold text-amber-800 dark:text-amber-300 mb-2">Warnings</h4>
                        <ul className="list-disc pl-5 space-y-1 text-amber-700 dark:text-amber-400/90 text-xs text-left">
                            {result.warnings?.map((w, i) => (
                                <li key={i}>{w}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {hasRejections && (
                    <div className="mb-4">
                        <button
                            onClick={() => setShowRejections(!showRejections)}
                            className="w-full flex justify-between items-center p-3 bg-red-50 hover:bg-red-100 dark:bg-red-900/10 dark:hover:bg-red-900/20 text-red-800 dark:text-red-300 rounded-lg transition-colors border border-red-100 dark:border-red-900/30"
                        >
                            <span className="font-medium">{result.rows_rejected} rows could not be imported</span>
                            <svg className={`w-5 h-5 transform transition-transform ${showRejections ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                        </button>

                        {showRejections && (
                            <div className="mt-2 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden">
                                <table className="w-full text-left text-xs">
                                    <thead className="bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                                        <tr>
                                            <th className="px-4 py-2 font-medium w-16">Row</th>
                                            <th className="px-4 py-2 font-medium">Reason</th>
                                            <th className="px-4 py-2 font-medium text-right">Raw Data</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                                        {result.rejections_summary?.map((rej, i) => (
                                            <tr key={i}>
                                                <td className="px-4 py-2 text-gray-500 whitespace-nowrap">{rej.row}</td>
                                                <td className="px-4 py-2 text-red-600 dark:text-red-400">{rej.reason}</td>
                                                <td className="px-4 py-2 text-gray-400 font-mono truncate max-w-xs text-right" title={rej.raw}>
                                                    {rej.raw?.length > 50 ? rej.raw.substring(0, 50) + '...' : rej.raw}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                    <button
                        onClick={() => setShowMapping(!showMapping)}
                        className="w-full flex justify-between items-center p-4 bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
                    >
                        <div className="flex flex-col items-start gap-1">
                            <span className="font-medium">Column Mapping Used</span>
                            <span className="text-xs text-gray-500">
                                Matched with {Math.round(result.confidence_score * 100)}% confidence using {result.mapping_method} matching
                            </span>
                        </div>
                        <svg className={`w-5 h-5 transform transition-transform ${showMapping ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                    </button>

                    {showMapping && (
                        <div className="border-t border-gray-200 dark:border-gray-700">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400">
                                    <tr>
                                        <th className="px-4 py-2 font-medium">Your Column</th>
                                        <th className="px-4 py-2 font-medium">Our Field</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                    {Object.entries(result.column_mapping).map(([canonical, source]) => (
                                        <tr key={canonical} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                            <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">{source}</td>
                                            <td className="px-4 py-3 text-brand-600 dark:text-brand-400 font-mono text-xs">{canonical}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
