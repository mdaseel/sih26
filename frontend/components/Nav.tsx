import type { NavLink } from "@/components/AppShell";

/**
 * The citizen portal's sections.
 *
 * Only the list lives here now. The header this file used to render was one of
 * three near-identical copies across the portals; AppShell draws all of them,
 * and each portal supplies its own links.
 *
 * No Grid twin entry. Exploring the feeder is a DISCOM activity; for a citizen
 * the twin is only meaningful as an explanation of their own decided
 * application, which is where it appears. The explorer remains at
 * /discom/grid-twin for the role that reads it.
 */
export const CITIZEN_LINKS: NavLink[] = [
  { href: "/citizen/dashboard", label: "Dashboard" },
  { href: "/citizen/applications", label: "My applications" },
  { href: "/citizen/applications/new", label: "New application" },
  { href: "/citizen/map", label: "Map" },
  { href: "/citizen/vendors", label: "Installers" },
  { href: "/citizen/scheme", label: "PM Surya Ghar" },
];
