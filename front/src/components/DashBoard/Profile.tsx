import React, { useEffect, useRef, useState } from "react";
import { Coffee, Mail, MapPin, PenBox, Smartphone, View } from "lucide-react";
import { useDispatch } from "react-redux";
import {
  clearError,
  updateProfile,
  uploadProfilePic,
} from "../../store/AuthSlice";
import { useAuth } from "../../hooks/useAuth";
import { AppDispatch } from "../../store";
interface ProfileProps {
  toggleSection: (data?: any) => void;
}
const ProfileView: React.FC<ProfileProps> = ({ toggleSection }) => {
  const { user } = useAuth();
  return (
    <div className="pt-5">
      <div className="grid grid-cols-1 gap-5 mb-5">
        <div className="panel">
          <div className="flex items-center justify-between mb-5">
            <h5 className="font-semibold text-lg dark:text-white-light">
              Profile
            </h5>
          </div>
          <div className="relative -top-[85px]">
            <button
              onClick={toggleSection}
              className="ltr:ml-auto rtl:mr-auto btn btn-primary p-2 rounded-full"
            >
              <PenBox className="w-6 h-6" />
            </button>
          </div>
          <div className="mb-5">
            <div className="flex flex-col justify-center items-center">
              <img
                src={
                  user?.profile_pic && user.profile_pic.length > 0
                    ? user.profile_pic
                    : "/img/man-avatar.png"
                }
                alt="img"
                className="w-24 h-24 rounded-full object-cover  mb-5"
              />
              <p className="font-semibold text-primary text-xl">{user?.name}</p>
            </div>
            <ul className="mt-5 flex flex-col max-w-[160px] m-auto space-y-4 font-semibold text-white-dark">
              <li className="flex items-center gap-2">
                <Coffee className="w-5 h-5" />
                {user?.profession}
              </li>

              <li className="flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                {user?.address}
              </li>
              <li>
                <button className="flex items-center gap-2">
                  <Mail className="w-5 h-5" />
                  <span className="text-primary">{user?.email}</span>
                </button>
              </li>
              <li className="flex items-center gap-2">
                <Smartphone className="w-5 h-5" />
                <span className="whitespace-nowrap" dir="ltr">
                  {user?.phone}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onloadend = () => {
      if (typeof reader.result === "string") {
        // Get everything after the comma to get just the base64 data
        const base64String = reader.result.split(",")[1];
        resolve(base64String);
      } else {
        reject(new Error("Failed to read file as data URL"));
      }
    };

    reader.onerror = () => {
      reject(new Error("Error reading file"));
    };

    reader.readAsDataURL(file);
  });
};

const ProfileEdit: React.FC<ProfileProps> = ({ toggleSection }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useAuth();
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  type InputChangeEvent = React.ChangeEvent<HTMLInputElement>;
  const handleFileChange = async (e: InputChangeEvent) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const base64String = await readFileAsBase64(file);
      setPreview(`data:${file.type};base64,${base64String}`);

      const resAction = dispatch(uploadProfilePic(base64String));
      if (uploadProfilePic.fulfilled.match(resAction)) {
        const resData = resAction.payload;
        if (resData.status) {
          alert(resData.message || "Image Upload Succesfully");
        } else {
          alert(resData.message || "Login failed!");
        }
      }
    } catch (err) {
      if (err instanceof Error) {
        console.log("Error Occured", err.message);
      }
    }
  };

  const submitForm = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const formData = {
      name: form.get("name") as string,
      profession: form.get("profession") as string,
      country: form.get("country") as string,
      address: form.get("address") as string,
      location: form.get("location") as string,
      phone: form.get("phone") as string,
      web: form.get("web") as string,
    };

    try {
      await dispatch(clearError());
      const resAction = await dispatch(updateProfile(formData));
      if (updateProfile.fulfilled.match(resAction)) {
        const res = resAction.payload;

        if (res.status) {
          alert(res.message || "Profile Updated successful!");
        } else {
          alert(res.message || "Profile Updation failed!");
        }
      }
    } catch (err: any) {
      console.log("Profile Update Error >>", err.message);
    }
  };
  return (
    <div>
      <form
        className="border border-[#ebedf2] dark:border-[#191e3a] rounded-md p-4 mb-5 bg-white dark:bg-black"
        onSubmit={submitForm}
      >
        <h6 className="text-lg font-bold mb-5">General Information</h6>
        <div className="relative -top-20">
          <button
            onClick={toggleSection}
            className="ltr:ml-auto rtl:mr-auto btn btn-primary p-2 rounded-full"
          >
            <View className="w-6 h-6" />
          </button>
        </div>
        <div className="flex flex-col sm:flex-row">
          <div className="ltr:sm:mr-4 rtl:sm:ml-4 w-full sm:w-2/12 mb-5">
            <img
              src={
                user?.profile_pic && user.profile_pic.length > 0
                  ? user.profile_pic
                  : "/img/man-avatar.png"
              }
              alt="img"
              className="w-20 h-20 md:w-32 md:h-32 rounded-full object-cover mx-auto cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            />
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              accept="image/*"
              onChange={handleFileChange}
            />
          </div>
          <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label htmlFor="name">Full Name</label>
              <input
                id="name"
                name="name"
                type="text"
                defaultValue={user?.name}
                placeholder="John Doe"
                className="form-input"
              />
            </div>
            <div>
              <label htmlFor="profession">Profession</label>
              <input
                id="profession"
                name="profession"
                defaultValue={user?.profession}
                type="text"
                placeholder="Graphics Designer"
                className="form-input"
              />
            </div>
            <div>
              <label htmlFor="country">Country</label>
              <select
                defaultValue={user?.country}
                id="country"
                name="country"
                className="form-select text-white-dark"
              >
                <option value="Choose Your Country" disabled>
                  Choose You Country
                </option>
                <option value="India">India</option>
              </select>
            </div>
            <div>
              <label htmlFor="address">Address</label>
              <input
                id="address"
                name="address"
                type="text"
                defaultValue={user?.address}
                placeholder="India"
                className="form-input"
              />
            </div>
            <div>
              <label htmlFor="location">Location</label>
              <input
                id="location"
                name="location"
                type="text"
                defaultValue={user?.location}
                placeholder="Location"
                className="form-input"
              />
            </div>
            <div>
              <label htmlFor="phone">Phone</label>
              <input
                id="phone"
                name="phone"
                type="text"
                defaultValue={user?.phone}
                placeholder="+91 0123456789"
                className="form-input"
              />
            </div>
            <div>
              <label htmlFor="web">Website</label>
              <input
                id="web"
                name="web"
                type="text"
                placeholder="Enter URL"
                className="form-input"
              />
            </div>
            <div className="sm:col-span-2 mt-3">
              <button type="submit" className="btn btn-primary">
                Save
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export { ProfileView, ProfileEdit };
