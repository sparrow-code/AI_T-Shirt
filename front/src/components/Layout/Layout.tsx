import React, { FC, ReactNode, Suspense } from "react";
import "../../index.css";
import { Helmet } from "react-helmet";
import Footer from "../Footer";
import Navbar from "../Navbar";
import LoadingSpinner from "./LoadingSpinner";

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

const Layout: FC<LayoutProps> = ({ children, title }) => {
  return (
    <>
      <Helmet>
        <title>{title}</title>
      </Helmet>
      <div>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Navbar />
          <main className="flex-grow">
            <Suspense fallback={<LoadingSpinner />}>{children}</Suspense>
          </main>
          <Footer />
        </div>
      </div>
    </>
  );
};

export default Layout;
