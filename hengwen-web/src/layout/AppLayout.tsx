import { NavLink, Outlet, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "首页" },
  { to: "/history", label: "历史" },
  { to: "/settings", label: "设置" },
];

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="flex min-h-svh flex-col">
      <header className="border-b border-line bg-paper shadow-paper">
        <div className="mx-auto flex h-16 w-full max-w-[960px] items-center justify-between gap-8 px-12 max-md:h-14 max-md:gap-4 max-md:px-5">
          <NavLink
            to="/"
            className="flex shrink-0 items-center text-ink"
            aria-label="衡文首页"
          >
            <span className="font-serif text-h2 font-semibold">衡文</span>
          </NavLink>
          <nav className="flex gap-8 max-md:gap-4" aria-label="主导航">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  [
                    "relative py-2 text-body text-ink-2 transition-colors duration-micro hover:text-ink",
                    isActive ? "font-semibold text-accent" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 bg-paper">
        <div className="mx-auto w-full max-w-[960px] px-12 pb-24 pt-16 max-md:px-6 max-md:pb-12 max-md:pt-12">
          <div key={location.pathname} className="page-enter">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
