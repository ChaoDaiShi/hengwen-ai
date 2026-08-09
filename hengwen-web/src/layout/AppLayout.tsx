import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "首页" },
  { to: "/history", label: "历史" },
  { to: "/settings", label: "设置" },
];

export default function AppLayout() {
  return (
    <div className="flex min-h-svh flex-col">
      <header className="border-b border-line bg-paper">
        <div className="mx-auto flex h-16 w-full max-w-[960px] items-center justify-between gap-8 px-12 max-md:h-14 max-md:px-6 max-md:gap-6">
          <NavLink
            to="/"
            className="font-serif text-[20px] font-medium leading-[1.4] text-ink"
          >
            衡文
          </NavLink>
          <nav className="flex gap-8 max-md:gap-6" aria-label="主导航">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  [
                    "relative py-2 text-body text-ink-2 transition-colors duration-150 hover:text-ink",
                    isActive
                      ? 'after:absolute after:bottom-[-4px] after:left-0 after:right-0 after:h-0.5 after:bg-accent after:content-[""]'
                      : "",
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
          <Outlet />
        </div>
      </main>
    </div>
  );
}
