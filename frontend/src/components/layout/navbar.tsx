import { FC } from "react";

const Navbar: FC = () => {
  return (
    <nav className="bg-[#1A1431] p-4">
      <div className="flex items-center justify-between w-full">
        <div className="logo">
          <h1 className="text-[#0EF156] font-Jersey 25 "> aq iqneba logo</h1>
        </div>

        <div className="flex p-4 space-x-4">
          <h1 className="text-[#0EF156]">courses</h1>
          <h1 className="text-[#0EF156]">leaderboard</h1>
          <h1 className="text-[#0EF156]">competitions</h1>
        </div>

        <div className="flex items-center space-x-4">
          <button className="bg-[#0EF156] rounded-[5px] w-[80px]">
            {" "}
            LOG IN{" "}
          </button>
          <a> </a>
          <button className="bg-[#0EF156] rounded-[5px] w-[80px]">
            SIGN UP
          </button>
        </div>

        <div className="profile">
          <h1 className="text-[#0EF156]">my profile</h1>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
