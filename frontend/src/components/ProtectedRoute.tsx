import { useAuth0 } from '@auth0/auth0-react';
import { Navigate } from 'react-router-dom';
import { usePermission } from '../hooks/usePermission';

interface ProtectedRouteProps {
    minRole: string;
    children: React.ReactNode;
}

export const ProtectedRoute = ({ minRole, children }: ProtectedRouteProps) => {
    const { isAuthenticated, isLoading } = useAuth0();
    const hasPermission = usePermission(minRole);

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="text-gray-500">Authenticating...</div>
            </div>
        );
    }

    if (!isAuthenticated) return <Navigate to="/" replace />;
    if (!hasPermission) return <Navigate to="/" replace />;

    return <>{children}</>;
};
