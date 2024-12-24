import React, { Suspense } from "react";
import { BrowserRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { CartProvider } from "react-use-cart";
import CommonRoutes from "./routes/routes";
import ErrorBoundary from "./components/ErrorBoundary";

import { Provider } from "react-redux";
import store from "./store";

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ErrorBoundary>
        <HelmetProvider>
          <CartProvider>
            <BrowserRouter>
              <CommonRoutes />
            </BrowserRouter>
          </CartProvider>
        </HelmetProvider>
      </ErrorBoundary>
    </Provider>
  );
};

export default App;
