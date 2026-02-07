import React, { useRef, useState } from 'react';
import { Upload, Loader2, AlertCircle } from 'lucide-react';
import { DecisionService } from '../services/api';

interface UploadDataButtonProps {
    onUploadComplete: () => void;
}

export const UploadDataButton: React.FC<UploadDataButtonProps> = ({ onUploadComplete }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setError(null);

        try {
            await DecisionService.upload(file);
            onUploadComplete();
        } catch (e: any) {
            console.error(e);
            setError("Upload failed. Please check the file format.");
            // Clear error after 3 seconds
            setTimeout(() => setError(null), 3000);
        } finally {
            setUploading(false);
            // Reset input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    return (
        <div className="relative">
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept=".csv,.xlsx"
            />

            {error && (
                <div className="absolute bottom-full mb-2 right-0 bg-red-100 text-red-700 text-xs px-2 py-1 rounded whitespace-nowrap flex items-center shadow-sm animate-in fade-in slide-in-from-bottom-1">
                    <AlertCircle className="w-3 h-3 mr-1" /> {error}
                </div>
            )}

            <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
            >
                {uploading ? (
                    <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
                ) : (
                    <Upload className="w-4 h-4 text-gray-500" />
                )}
                {uploading ? 'Analyzing...' : 'Upload Data'}
            </button>
        </div>
    );
};
