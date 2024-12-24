export interface LoginCredentials {
    email: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}


export interface AuthState {
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}
export interface SignUpCredentials {
    name: string;
    email: string;
    password: string;
}
export interface SignUpResponse {
    status: boolean;
    message: string;
}