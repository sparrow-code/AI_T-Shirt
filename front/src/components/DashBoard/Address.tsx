import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { BillingAddress } from "../../types/auth";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../../store";
import { clearError } from "../../store/AuthSlice";

const initialBillingState: BillingAddress = {
  name: "",
  email: "",
  phone: "",
  address: "",
  city: "",
  state: "",
  zip: "",
};

const Billing = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState<BillingAddress>(initialBillingState);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const dispatch = useDispatch<AppDispatch>();
  const states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    // Add more states as needed
  ];

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id.replace("billing", "").toLowerCase()]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log(formData);
    try {
      await dispatch(clearError());
      // await dispatch(addBilling(formData))
    } catch (err: any) {
      console.log("Error in Address Billing >>", err.message);
    }
  };

  const handleEdit = (index: number, address: BillingAddress) => {
    setEditIndex(index);
    setFormData(address);
  };

  const handleAddNew = () => {
    setEditIndex(null);
    setFormData(initialBillingState);
  };

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <div className="panel">
          <div className="mb-5">
            <h5 className="font-semibold text-lg mb-4">Billing Address</h5>
          </div>
          <div className="mb-5">
            {user?.billing_address?.map((addr: BillingAddress, i: number) => (
              <>
                <div className="border-b border-[#ebedf2] dark:border-[#1b2e4b]">
                  <div className="flex items-start justify-between py-3">
                    <h6 className="text-[#515365] font-bold dark:text-white-dark text-[15px]">
                      Address #{i + 1}
                      <span className="block text-white-dark dark:text-white-light font-normal text-xs mt-1">
                        {addr.address}
                      </span>
                    </h6>
                    <div className="flex items-start justify-between ltr:ml-auto rtl:mr-auto">
                      <button
                        className="btn btn-dark"
                        onClick={() => handleEdit(i, addr)}
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ))}
          </div>
          <button className="btn btn-primary" onClick={handleAddNew}>
            Add Address
          </button>
        </div>
        <div className="panel">
          <div className="mb-5">
            <h5 className="font-semibold text-lg mb-4">
              {editIndex !== null ? "Edit" : "Add"} Billing Address Billing
              Address
            </h5>
            <p>
              {editIndex !== null ? "Update" : "Add"} your{" "}
              <span className="text-primary">Billing</span> Information.
            </p>
          </div>
          <div className="mb-5">
            <form onSubmit={handleSubmit}>
              <div className="mb-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="billingName">Name</label>
                  <input
                    id="billingName"
                    type="text"
                    placeholder="Enter Name"
                    className="form-input"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="billingEmail">Email</label>
                  <input
                    id="billingEmail"
                    type="text"
                    placeholder="Enter E-Mail"
                    className="form-input"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="billingPhone">Phone</label>
                  <input
                    id="billingPhone"
                    type="tel"
                    placeholder="Enter Phone"
                    className="form-input"
                    value={formData.phone}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
              <div className="mb-5">
                <label htmlFor="billingAddress">Address</label>
                <input
                  id="billingAddress"
                  type="text"
                  placeholder="Enter Address"
                  className="form-input"
                  value={formData.address}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-5">
                <div className="md:col-span-2">
                  <label htmlFor="billingCity">City</label>
                  <input
                    id="billingCity"
                    type="text"
                    placeholder="Enter City"
                    className="form-input"
                    value={formData.city}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="billingState">State</label>
                  <select
                    id="billingState"
                    className="form-select text-white-dark"
                    value={formData.state}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Choose...</option>
                    {states.map((state) => (
                      <option key={state} value={state}>
                        {state}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="billingZip">Zip</label>
                  <input
                    id="billingZip"
                    type="text"
                    placeholder="Enter Zip"
                    className="form-input"
                    value={formData.zip}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
              <button type="submit" className="btn btn-primary">
                {editIndex !== null ? "Update" : "Add"} Address
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Billing;
