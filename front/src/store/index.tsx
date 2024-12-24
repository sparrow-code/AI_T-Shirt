import { combineReducers, configureStore } from "@reduxjs/toolkit";
import themeConfigSlice from "./themeConfigSlice";
import authReducer from "./AuthSlice";

const rootReducer = combineReducers({
  themeConfig: themeConfigSlice,
  auth: authReducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type IRootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;

export default store;
