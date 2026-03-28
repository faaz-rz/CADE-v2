import { useAuth0 } from '@auth0/auth0-react';

export const usePermission = (minRole: string): boolean => {
    const { isAuthenticated, user } = useAuth0();

    if (!isAuthenticated || !user) {
        return false;
    }

    const roleHierarchy: Record<string, number> = {
        'VIEWER': 0,
        'ANALYST': 1,
        'APPROVER': 2,
        'ADMIN': 3
    };

    const namespace = 'https://capitalrisk.app/role';
    const rawUserRole = user[namespace] || 'VIEWER';
    
    // Support local role override for demos
    const overrideRole = localStorage.getItem('demo_role_override');
    const effectiveRole = overrideRole ? overrideRole : rawUserRole;

    const userRoleLevel = roleHierarchy[effectiveRole as string] ?? 0;
    const requiredLevel = roleHierarchy[minRole] ?? 99; // Default to unreachable if unknown

    return userRoleLevel >= requiredLevel;
};
