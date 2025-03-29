"use client"; // Needed for Input and potentially future user dropdown

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "../ui/input";
import { Menu, Search } from "lucide-react"; // Import icons

const Header = () => {
  // Placeholder Logo - Replace with your actual logo component/SVG/Image
  const Logo = () => (
    <Link
      href="/"
      className="flex items-center gap-2 font-bold text-xl text-green-600 dark:text-green-500"
    >
      {/* Replace with your SVG or Image component */}
      <svg
        width="40"
        height="40"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M50 0C22.3858 0 0 22.3858 0 50C0 77.6142 22.3858 100 50 100C77.6142 100 100 77.6142 100 50C100 22.3858 77.6142 0 50 0ZM50 90C27.9086 90 10 72.0914 10 50C10 27.9086 27.9086 10 50 10C72.0914 10 90 27.9086 90 50C90 72.0914 72.0914 90 50 90Z"
          fill="currentColor"
        />
        <path
          d="M35 40H65M35 50H65M35 60H55"
          stroke="currentColor"
          strokeWidth="5"
          strokeLinecap="round"
        />
      </svg>
      DevAut
    </Link>
  );

  const navItems = [
    { label: "Home", href: "/" },
    { label: "About", href: "/about" },
    { label: "Courses", href: "/courses" },
    { label: "Activities", href: "/activities" },
    { label: "Contact Info", href: "/contact" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-6 md:gap-10">
          <Logo />
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="text-muted-foreground transition-colors hover:text-foreground"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {/* Search Bar */}
          <div className="relative hidden sm:block">
            <Menu className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Hinted search text"
              className="w-full rounded-md bg-muted pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring md:w-[200px] lg:w-[300px]"
            />
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          </div>

          {/* Auth Buttons */}
          <Button variant="ghost" size="sm">
            Sign in
          </Button>
          <Button size="sm">Sign up</Button>

          {/* Mobile Menu Button (Optional - add functionality later) */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle Menu</span>
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;
