export interface LoginCredentials {
    email: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    status: boolean;
    message: string
}


export interface AuthState {
    token: string | null;
    isAuthenticated: boolean;
    user: User | null;
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

export interface TokenResponse {
    status: boolean;
    access_token: string;
    token_type: string;
    message: string;
}

export interface BillingAddress {
    name: string;
    email: string;
    phone: string;
    address: string;
    city: string;
    state: string;
    zip: string;
}

export interface User {
    uid: string;
    name: string;
    email: string;
    profile_pic: string;
    profession: string;
    country: string;
    address: string;
    location: string;
    phone: string;
    billing_address: [BillingAddress] | null;
    web: string;
    role: string;
    credits: number;
    is_verify: boolean;
    is_active: boolean;
}

export interface UserResponse {
    status: boolean;
    message: string;
    user: User;
}

export interface UserPicResponse {
    status: boolean,
    message: string,
    url: string
}

export interface UserRequest {
    name: string;
    profession: string;
    country: string;
    address: string;
    location: string;
    phone: string;
    web: string;
}

export interface UserResponse {
    status: boolean;
    message: string;
}