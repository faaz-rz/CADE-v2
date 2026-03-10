import React, { useState } from 'react';
import { DecisionService } from '../services/api';
import { UploadCloud, FileSpreadsheet, Loader2, ArrowLeft, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { IngestionResultCard } from '../components/IngestionResultCard';
import { IngestResult } from '../types/ingestion';

export const UploadPage: React.FC = () => {
    const [uploadState, setUploadState] = useState<'IDLE' | 'UPLOADING' | 'SUCCESS' | 'ERROR'>('IDLE');
    const [result, setResult] = useState<IngestResult | null>(null);
    const [errorMsg, setErrorMsg] = useState('');

    const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.length) return;
        const file = e.target.files[0];
        setUploadState('UPLOADING');
        setErrorMsg('');

        try {
            const res = await DecisionService.upload(file);
            if (res.data?.status === 'success' || res.data?.rows_accepted !== undefined) {
                setResult(res.data as IngestResult);
            } else if ((res as any).rows_accepted !== undefined) {
                setResult(res as unknown as IngestResult);
            } else {
                setResult(res.data as IngestResult);
            }
            setUploadState('SUCCESS');
        } catch (error: any) {
            console.error('Upload failed:', error);
            const message = error.response?.data?.message || 'Upload failed. Please check your file format.';
            setErrorMsg(message);
            setUploadState('ERROR');
        }
    };

    return (
        <div className="max-w-2xl mx-auto py-10 px-4">
            <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 mb-8">
                <ArrowLeft className="w-4 h-4" /> Back to Inbox
            </Link>

            <h1 className="text-3xl font-bold text-gray-900 mb-2">Ingest Financial Data</h1>
            <p className="text-gray-500 mb-8">Upload your CSV or Excel exports to generate new recommendations.</p>

            <div className={`transition-colors relative ${uploadState === 'SUCCESS' ? '' : 'border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 p-12 text-center hover:border-brand-400 hover:bg-brand-50/30'}`}>
                {uploadState === 'IDLE' && (
                    <>
                        <input
                            type="file"
                            onChange={handleFile}
                            onClick={(e) => { (e.target as HTMLInputElement).value = ''; }}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            accept=".csv,.xlsx"
                        />
                        <div className="flex flex-col items-center pointer-events-none">
                            <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mb-4">
                                <UploadCloud className="w-6 h-6 text-brand-600" />
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">Click to upload or drag and drop</h3>
                            <p className="text-sm text-gray-500 mb-4">CSV or Excel (max 10MB)</p>
                            <div className="flex items-center gap-2 text-xs text-gray-400 bg-white px-3 py-1.5 rounded-full border border-gray-200">
                                <FileSpreadsheet className="w-3 h-3" />
                                Supported: expense_report.csv, vendor_list.xlsx
                            </div>
                        </div>
                    </>
                )}

                {uploadState === 'UPLOADING' && (
                    <div className="flex flex-col items-center">
                        <Loader2 className="w-10 h-10 text-brand-600 animate-spin mb-4" />
                        <p className="text-gray-900 font-medium">Processing & Generating Decisions...</p>
                        <p className="text-xs text-gray-500 mt-2">Running risk analysis & extraction models</p>
                    </div>
                )}

                {uploadState === 'SUCCESS' && result && (
                    <div className="flex flex-col items-center">
                        <IngestionResultCard result={result} />
                        <div className="mt-8 flex gap-4">
                            <button onClick={() => setUploadState('IDLE')} className="px-8 py-3 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition shadow-sm hover:shadow">
                                Upload Another File
                            </button>
                            <Link to="/" className="px-8 py-3 bg-brand-600 text-white font-medium rounded-lg hover:bg-brand-700 transition shadow-sm hover:shadow">
                                View Generated Decisions
                            </Link>
                        </div>
                    </div>
                )}

                {uploadState === 'ERROR' && (
                    <div className="flex flex-col items-center">
                        <div className="text-red-600 font-semibold mb-2">Ingestion Error</div>
                        <div className="text-red-500 text-sm mb-6">{errorMsg}</div>
                        <button onClick={() => setUploadState('IDLE')} className="z-10 inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-gray-300 text-sm font-medium text-gray-700 rounded-lg shadow-sm hover:bg-gray-50 transition-colors">
                            <RefreshCw className="w-4 h-4" /> Try Again
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};
