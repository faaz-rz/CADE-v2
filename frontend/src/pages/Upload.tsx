import React, { useState } from 'react';
import { DecisionService } from '../services/api';
import { UploadCloud, FileSpreadsheet, Loader2, ArrowLeft } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export const UploadPage: React.FC = () => {
    const navigate = useNavigate();
    const [uploading, setUploading] = useState(false);

    const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.length) return;
        const file = e.target.files[0];
        setUploading(true);

        try {
            await DecisionService.upload(file);
            // Simulate processing delay for effect
            setTimeout(() => {
                navigate('/');
            }, 1000);
        } catch (error: any) {
            console.error('Upload failed:', error);
            const message = error.response?.data?.detail || 'Upload failed. Please check your file format.';
            alert(message);
            setUploading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto py-10 px-4">
            <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 mb-8">
                <ArrowLeft className="w-4 h-4" /> Back to Inbox
            </Link>

            <h1 className="text-3xl font-bold text-gray-900 mb-2">Ingest Financial Data</h1>
            <p className="text-gray-500 mb-8">Upload your CSV or Excel exports to generate new recommendations.</p>

            <div className="border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 p-12 text-center transition-colors hover:border-brand-400 hover:bg-brand-50/30 relative">
                <input
                    type="file"
                    onChange={handleFile}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    accept=".csv,.xlsx"
                    disabled={uploading}
                />

                {uploading ? (
                    <div className="flex flex-col items-center">
                        <Loader2 className="w-10 h-10 text-brand-600 animate-spin mb-4" />
                        <p className="text-gray-900 font-medium">Processing & Generating Decisions...</p>
                        <p className="text-xs text-gray-500 mt-2">Running risk analysis models</p>
                    </div>
                ) : (
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
                )}
            </div>
        </div>
    );
};
