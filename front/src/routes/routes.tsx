// ! Library
import React from "react";
import { useAuth } from "../hooks/useAuth";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

// ! Layout
import Layout from "../components/Layout/Layout";
import DashBoardLayout from "../components/Layout/DashBoardLayout";
import BlankLayout from "../components/Layout/BlankLayout";

// ! Un Protected Pages
const Home = React.lazy(() => import("../pages/Home"));
const Shop = React.lazy(() => import("../pages/Shop"));
const ProductDetail = React.lazy(() => import("../pages/ProductDetail"));
const Cart = React.lazy(() => import("../pages/Cart"));
const Blog = React.lazy(() => import("../pages/Blog"));
const About = React.lazy(() => import("../pages/About"));
const Legal = React.lazy(() => import("../pages/Legal"));
const CustomDesign = React.lazy(
  () => import("../pages/CustomDesign/CustomDesign")
);
const Signup = React.lazy(() => import("../pages/SignUp"));
const Login = React.lazy(() => import("../pages/Login"));

// ! Protected Pages
const DashBoard = React.lazy(() => import("../pages/Dashboard/Index"));
const Profile = React.lazy(() => import("../pages/Dashboard/Profile"));

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

// A higher-order component to apply the appropriate layout
const withLayout = (
  LayoutComponent: React.FC<{ children: React.ReactNode }>,
  Component: React.FC,
  isProtected: boolean = false
) => {
  const WrappedComponent = (
    <LayoutComponent>
      <React.Suspense fallback={<div>Loading...</div>}>
        <Component />
      </React.Suspense>
    </LayoutComponent>
  );

  return isProtected ? (
    <ProtectedRoute>{WrappedComponent}</ProtectedRoute>
  ) : (
    WrappedComponent
  );
};

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Routes with Main Layout */}
      <Route path="/" element={withLayout(Layout, Home)} />
      <Route path="/shop" element={withLayout(Layout, Shop)} />
      <Route path="/product/:id" element={withLayout(Layout, ProductDetail)} />
      <Route path="/cart" element={withLayout(Layout, Cart)} />
      <Route path="/blog" element={withLayout(Layout, Blog)} />
      <Route path="/about" element={withLayout(Layout, About)} />
      <Route path="/legal" element={withLayout(Layout, Legal)} />
      <Route path="/custom-design" element={withLayout(Layout, CustomDesign)} />

      {/* Routes with Blank Layout */}
      <Route path="/login" element={withLayout(BlankLayout, Login)} />
      <Route path="/sign-up" element={withLayout(BlankLayout, Signup)} />
      <Route path="/verify/:token" element={withLayout(BlankLayout, Signup)} />

      {/* Protected Routes With Dashboard Layout */}
      <Route
        path="/dashboard"
        element={withLayout(DashBoardLayout, DashBoard, true)}
      />
      <Route
        path="/dashboard/orders"
        element={withLayout(DashBoardLayout, DashBoard, true)}
      />
      <Route
        path="/dashboard/designs"
        element={withLayout(DashBoardLayout, DashBoard, true)}
      />
      <Route
        path="/dashboard/profile"
        element={withLayout(DashBoardLayout, Profile, true)}
      />

      {/* Catch-all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
