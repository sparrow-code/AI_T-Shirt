import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { apiService } from "../service/apiService";
import {
  LoginCredentials,
  AuthResponse,
  AuthState,
  SignUpResponse,
  SignUpCredentials,
} from "../types/auth";
import { AxiosError } from "axios";
import Cookie from "../utils/cookie";
import { Sign } from "crypto";

const initialState: AuthState = {
  token: Cookie.get("access_token") || null,
  isAuthenticated: !!Cookie.get("access_token"),
  loading: false,
  error: null,
};

export const signupUser = createAsyncThunk<SignUpResponse, SignUpCredentials>(
  "auth/signup",
  async (SignUpCredentials, { rejectWithValue }) => {
    try {
      const response = await apiService.post<SignUpResponse>(
        "/auth/register",
        SignUpCredentials
      );

      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        return rejectWithValue(error.response.data?.message || "Signup failed");
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

export const loginUser = createAsyncThunk<AuthResponse, LoginCredentials>(
  "auth/login",
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await apiService.post<AuthResponse>(
        "/auth/login/json",
        credentials
      );
      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        return rejectWithValue(error.response.data?.message || "Login failed");
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

// export const verify

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout: (state) => {
      Cookie.remove("access_token");
      state.token = null;
      state.isAuthenticated = false;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // ? Login Reducer
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // ? Signup Reducer
      .addCase(signupUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(signupUser.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.token = null;
      })
      .addCase(signupUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
