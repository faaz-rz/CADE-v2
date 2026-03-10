import React from 'react';
import { Upload } from 'lucide-react';
import { Link } from 'react-router-dom';

interface UploadDataButtonProps {
    onUploadComplete?: () => void;
}

export const UploadDataButton: React.FC<UploadDataButtonProps> = () => {
    return (
        <Link
            to="/upload"
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
        >
            <Upload className="w-4 h-4 text-gray-500" />
            Upload Data
        </Link>
    );
};
