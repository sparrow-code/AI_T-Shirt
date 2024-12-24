import { PropsWithChildren, Suspense } from "react";

import "../../tailwind.css";

import Navbar from "../Navbar";
import LoadingSpinner from "./LoadingSpinner";
import Footer from "../Footer";
const BlankLayout = ({ children }: PropsWithChildren) => {
  return (
    <>
      <Navbar />
      <div className="text-black dark:text-white-dark min-h-screen">
        <Suspense fallback={<LoadingSpinner />}>{children}</Suspense>
      </div>
      <Footer />
    </>
  );
};

export default BlankLayout;
