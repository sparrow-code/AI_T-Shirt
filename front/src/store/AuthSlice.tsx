import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { apiService } from "../service/apiService";
import {
  LoginCredentials,
  AuthResponse,
  AuthState,
  SignUpResponse,
  SignUpCredentials,
  TokenResponse,
  UserResponse,
  UserPicResponse,
  UserRequest,
} from "../types/auth";
import { AxiosError } from "axios";
import Cookie from "../utils/cookie";

const initialState: AuthState = {
  token: Cookie.get("access_token") || null,
  isAuthenticated: !!Cookie.get("access_token"),
  user: null,
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

export const verifyToken = createAsyncThunk<TokenResponse, string>(
  "auth/verify",
  async (token, { rejectWithValue }) => {
    try {
      const response = await apiService.get<TokenResponse>(
        `/auth/verify/${token}` // Fixed URL construction
      );

      // If verification failed
      if (!response.status) {
        return rejectWithValue(response.message);
      }

      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data) {
        return rejectWithValue(
          error.response.data.message || "Verification failed"
        );
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

export const updateProfile = createAsyncThunk<UserResponse, UserRequest>(
  "auth/profile",
  async (updateForm, { rejectWithValue }) => {
    try {
      const token = Cookie.get("access_token");

      if (!token) {
        return rejectWithValue("User not authenticated");
      }

      const response = await apiService.put<UserResponse>(
        "/auth/profile",
        updateForm
      );

      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        return rejectWithValue(
          error.response.data?.message || "Profile update failed"
        );
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

export const fetchCurrentUser = createAsyncThunk<UserResponse, string>(
  "auth/me",
  async (_, { rejectWithValue }) => {
    console.log("Fetch User Called ");
    try {
      const token = Cookie.get("access_token");
      if (!token) {
        return rejectWithValue("User not authenticated");
      }

      const response = await apiService.get<UserResponse>("/auth/me");
      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        return rejectWithValue(error.response.data?.message || "Me failed");
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

export const uploadProfilePic = createAsyncThunk<UserPicResponse, string>(
  "auth/upload/profile-pic",
  async (pic_object, { rejectWithValue }) => {
    try {
      const token = Cookie.get("access_token");
      if (!token) {
        return rejectWithValue("User not authenticated");
      }
      const response = await apiService.post<UserPicResponse>(
        "/auth/upload/profile-pic",
        { pic_object }
      );
      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        return rejectWithValue(
          error.response.data?.message || "Profile Pic Upload Failed failed"
        );
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

export const logout = createAsyncThunk<SignUpResponse, void>(
  "auth/logout",
  async (_, { rejectWithValue }) => {
    try {
      const token = Cookie.get("access_token");
      if (!token) {
        return rejectWithValue("User not authenticated");
      }
      const response = await apiService.get<SignUpResponse>(`/auth/logout`);

      if (!response.status) {
        return rejectWithValue(response.message);
      }

      return response;
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data) {
        return rejectWithValue(
          error.response.data.message || "Verification failed"
        );
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
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
      })
      // ? Verify Reducer
      .addCase(verifyToken.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyToken.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
      })
      .addCase(verifyToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // ? Me Reducer
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      // ? Profile Pic
      .addCase(uploadProfilePic.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadProfilePic.fulfilled, (state, action) => {
        state.loading = false;
        if (state.user) {
          state.user.profile_pic = action.payload.url;
        }
      })
      .addCase(uploadProfilePic.rejected, (state, action) => {
        state.loading = true;
      })
      // ? Logout Reducer
      .addCase(logout.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(logout.fulfilled, (state, action) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = null;
      })
      .addCase(logout.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      .addCase(updateProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
