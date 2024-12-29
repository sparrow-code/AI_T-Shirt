import PerfectScrollbar from "react-perfect-scrollbar";
import { useDispatch, useSelector } from "react-redux";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { toggleSidebar } from "../../../store/themeConfigSlice";
import { AppDispatch, IRootState } from "../../../store";
import { useEffect } from "react";
import {
  ChevronFirst,
  Gauge,
  Shirt,
  Palette,
  Package,
  User2Icon,
  LogOut,
} from "lucide-react";
import { useAuth } from "../../../hooks/useAuth";
import { clearError, logout } from "../../../store/AuthSlice";

const Sidebar = () => {
  const { user } = useAuth();
  const themeConfig = useSelector((state: IRootState) => state.themeConfig);
  const semidark = useSelector(
    (state: IRootState) => state.themeConfig.semidark
  );
  const location = useLocation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  useEffect(() => {
    const selector = document.querySelector(
      '.sidebar ul a[href="' + window.location.pathname + '"]'
    );

    console.log(selector);

    if (selector) {
      selector.classList.add("active");
      const ul: any = selector.closest("ul.sub-menu");
      console.log(ul);
      if (ul) {
        let ele: any =
          ul.closest("li.menu").querySelectorAll(".nav-link") || [];
        if (ele.length) {
          ele = ele[0];
          setTimeout(() => {
            ele.click();
          });
        }
      }
    }
  }, []);

  // ? close sidebar on route change
  useEffect(() => {
    if (window.innerWidth < 1024 && themeConfig.sidebar) {
      dispatch(toggleSidebar());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  type MouseClickEvent = React.MouseEvent<HTMLButtonElement>;
  const handleLogout = async (e: MouseClickEvent) => {
    e.preventDefault;

    try {
      await dispatch(clearError());
      dispatch(logout());
      navigate("/", { replace: true });
    } catch (err) {}
  };

  return (
    <div className={semidark ? "dark" : ""}>
      <nav
        className={`sidebar fixed min-h-screen h-full top-0 bottom-0 w-[260px] shadow-[5px_0_25px_0_rgba(94,92,154,0.1)] z-50 transition-all duration-300 ${
          semidark ? "text-white-dark" : ""
        }`}
      >
        <div className="bg-white dark:bg-black h-full">
          <div className="flex justify-between items-center px-4 py-3">
            <NavLink to="/" className="main-logo flex items-center shrink-0">
              <Shirt className="h-6 w-6 text-indigo-600 mr-2" />
              <span className="font-bold text-xl text-gray-900">AI Tees</span>
            </NavLink>

            <button
              type="button"
              className="collapse-icon w-8 h-8 rounded-full flex items-center hover:bg-gray-500/10 dark:hover:bg-dark-light/10 dark:text-white-light transition duration-300 rtl:rotate-180"
              onClick={() => dispatch(toggleSidebar())}
            >
              <ChevronFirst className="w-5 h-5 m-auto" />
            </button>
          </div>

          <PerfectScrollbar className="h-[calc(100vh-80px)] relative">
            <ul className="relative font-semibold space-y-0.5 p-4 py-0">
              {/* Dashboard */}
              <li className="nav-item">
                <NavLink to="/dashboard" className="group">
                  <div className="flex items-center">
                    <Gauge className="group-hover:!text-primary" />
                    <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                      {"dashboard"}
                    </span>
                  </div>
                </NavLink>
              </li>

              <li className="nav-item">
                <NavLink to="/dashboard/designs" className="group">
                  <div className="flex items-center">
                    <Palette className="group-hover:!text-primary" />
                    <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                      {"Designs"}
                    </span>
                  </div>
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/dashboard/orders" className="group">
                  <div className="flex items-center">
                    <Package className="group-hover:!text-primary" />

                    <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                      {"Order"}
                    </span>
                  </div>
                </NavLink>
              </li>
              {user?.role === "admin" && (
                <>
                  <li className="nav-item">
                    <NavLink to="/dashboard/products" className="group">
                      <div className="flex items-center">
                        <Shirt className="group-hover:!text-primary" />
                        <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                          {"Products"}
                        </span>
                      </div>
                    </NavLink>
                  </li>
                  <li className="nav-item">
                    <NavLink to="/dashboard/users" className="group">
                      <div className="flex items-center">
                        <Shirt className="group-hover:!text-primary" />
                        <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                          {"Users"}
                        </span>
                      </div>
                    </NavLink>
                  </li>
                </>
              )}
              <li className="nav-item">
                <NavLink to="/dashboard/profile" className="group">
                  <div className="flex items-center">
                    <User2Icon className="group-hover:!text-primary" />

                    <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                      {"Profile"}
                    </span>
                  </div>
                </NavLink>
              </li>
              <li className="nav-item">
                <button onClick={handleLogout} className="group">
                  <div className="flex items-center">
                    <LogOut className="group-hover:!text-primary" />
                    <span className="ltr:pl-3 rtl:pr-3 text-black dark:text-[#506690] dark:group-hover:text-white-dark">
                      {"Logout"}
                    </span>
                  </div>
                </button>
              </li>
            </ul>
          </PerfectScrollbar>
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;
