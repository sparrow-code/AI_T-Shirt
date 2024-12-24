import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "../components/Layout/Layout";
import DashBoardLayout from "../components/Layout/DashBoardLayout";
import BlankLayout from "../components/Layout/BlankLayout";
import SignupPage from "../pages/SignUp";

// Lazy-loaded pages
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
const LoginPage = React.lazy(() => import("../pages/Login"));

// A higher-order component to apply the appropriate layout
const withLayout = (
  LayoutComponent: React.FC<{ children: React.ReactNode }>,
  Component: React.FC
) => {
  return (
    <LayoutComponent>
      <React.Suspense fallback={<div>Loading...</div>}>
        <Component />
      </React.Suspense>
    </LayoutComponent>
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
      <Route path="/login" element={withLayout(BlankLayout, LoginPage)} />
      <Route path="/sign-up" element={withLayout(BlankLayout, SignupPage)} />

      {/* Catch-all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
