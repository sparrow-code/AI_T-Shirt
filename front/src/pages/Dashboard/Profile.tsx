import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { setPageTitle } from "../../store/themeConfigSlice";
import { useDispatch } from "react-redux";
import { ProfileEdit, ProfileView } from "../../components/DashBoard/Profile";
import { BadgeDollarSign, Home } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import Billing from "../../components/DashBoard/Address";

const AccountSetting = () => {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(setPageTitle("Account Setting"));
  });
  const { user } = useAuth();
  const [tabs, setTabs] = useState<string>("home");
  const [section, setSection] = useState<string>("view");
  const toggleTabs = (name: string) => {
    setTabs(name);
  };

  return (
    <div>
      <ul className="flex space-x-2 rtl:space-x-reverse">
        <li>
          <Link to="/dashboard" className="text-primary hover:underline">
            Dashboard
          </Link>
        </li>
        <li className="before:content-['/'] ltr:before:mr-2 rtl:before:ml-2">
          <span>Profile</span>
        </li>
      </ul>
      <div className="pt-5">
        <div className="flex items-center justify-between mb-5">
          <h5 className="font-semibold text-lg dark:text-white-light">
            Settings
          </h5>
        </div>
        <div>
          <ul className="sm:flex font-semibold border-b border-[#ebedf2] dark:border-[#191e3a] mb-5 whitespace-nowrap overflow-y-auto">
            <li className="inline-block">
              <button
                onClick={() => toggleTabs("home")}
                className={`flex gap-2 p-4 border-b border-transparent hover:border-primary hover:text-primary ${
                  tabs === "home" ? "!border-primary text-primary" : ""
                }`}
              >
                <Home className="w-5 h-5" />
                Home
              </button>
            </li>
            <li className="inline-block">
              <button
                onClick={() => toggleTabs("payment-details")}
                className={`flex gap-2 p-4 border-b border-transparent hover:border-primary hover:text-primary ${
                  tabs === "payment-details"
                    ? "!border-primary text-primary"
                    : ""
                }`}
              >
                <BadgeDollarSign className="w-5 h-5" />
                Payment Details
              </button>
            </li>
          </ul>
        </div>
        {tabs === "home" ? (
          section === "view" ? (
            <ProfileView toggleSection={() => setSection("edit")} />
          ) : (
            <ProfileEdit toggleSection={() => setSection("view")} />
          )
        ) : (
          ""
        )}
        {tabs === "payment-details" ? <Billing /> : ""}
      </div>
    </div>
  );
};

export default AccountSetting;
