function Header({ pageTitle }) {
  return (
    <header className="top-header">
      <div>
        <p className="header-kicker">Cybersecurity Awareness Service Desk</p>
        <h1>{pageTitle}</h1>
      </div>
    </header>
  );
}

export default Header;
