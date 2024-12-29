import { useCallback, useEffect } from "react";
import { IRootState, AppDispatch } from "../store";
import { fetchCurrentUser } from "../store/AuthSlice";
import { useSelector, useDispatch } from "react-redux";

export const useAuth = () => {
    const dispatch = useDispatch<AppDispatch>();
    const { user, isAuthenticated, loading } = useSelector((state: IRootState) => state.auth);

    const initializeAuth = useCallback(async () => {
        if (isAuthenticated && !user && !loading) {
            await dispatch(fetchCurrentUser(""));
        }
    }, [isAuthenticated, user, loading, dispatch]);

    useEffect(() => {
        // Only run when auth state actually changes
        if (isAuthenticated && !user && !loading) {
            initializeAuth();
        }
    }, [isAuthenticated, user, loading]); // Add proper dependencies

    return { user, isAuthenticated, loading, initializeAuth };
};