import Link from "next/link";
import {
  LayoutGrid,
  Twitter,
  Instagram,
  Youtube,
  Linkedin,
} from "lucide-react"; // Import icons

const Footer = () => {
  // Placeholder Logo Icon - Replace with your actual icon
  const LogoIcon = () => (
    <LayoutGrid className="h-8 w-8 text-green-600 dark:text-green-500" />
  );

  const socialLinks = [
    { icon: Twitter, href: "#", label: "Twitter" },
    { icon: Instagram, href: "#", label: "Instagram" },
    { icon: Youtube, href: "#", label: "YouTube" },
    { icon: Linkedin, href: "#", label: "LinkedIn" },
  ];

  const footerLinks = {
    "Use cases": [
      { label: "UI design", href: "#" },
      { label: "UX design", href: "#" },
      { label: "Wireframing", href: "#" },
      { label: "Diagramming", href: "#" },
      { label: "Brainstorming", href: "#" },
      { label: "Online whiteboard", href: "#" },
      { label: "Team collaboration", href: "#" },
    ],
    Explore: [
      { label: "Design", href: "#" },
      { label: "Prototyping", href: "#" },
      { label: "Development features", href: "#" },
      { label: "Design systems", href: "#" },
      { label: "Collaboration features", href: "#" },
      { label: "Design process", href: "#" },
      { label: "FigJam", href: "#" }, // Example
    ],
    Resources: [
      { label: "Blog", href: "#" },
      { label: "Best practices", href: "#" },
      { label: "Colors", href: "#" },
      { label: "Color wheel", href: "#" },
      { label: "Support", href: "#" },
      { label: "Developers", href: "#" },
      { label: "Resource library", href: "#" },
    ],
  };

  return (
    <footer className="border-t bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto max-w-7xl px-4 md:px-6">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-4 lg:grid-cols-5">
          {/* Logo and Social */}
          <div className="md:col-span-1 lg:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <LogoIcon />
              {/* Optional: Add Text Logo here if desired */}
              {/* <span className="font-bold text-lg">DevAut</span> */}
            </div>
            <p className="text-sm text-muted-foreground mb-6">
              AI-powered learning paths for developers.
            </p>
            <div className="flex space-x-4">
              {socialLinks.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label={link.label}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <link.icon className="h-5 w-5" />
                </Link>
              ))}
            </div>
          </div>

          {/* Footer Links */}
          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title} className="md:col-span-1">
              <h4 className="mb-4 font-semibold text-sm uppercase tracking-wider text-foreground">
                {title}
              </h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Copyright */}
        <div className="mt-12 border-t pt-8 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} DevAut. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
