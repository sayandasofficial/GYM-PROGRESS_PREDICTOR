const menuItems = [
  { id: 'dashboard', icon: '📊', label: 'Dashboard' },
  { id: 'progress', icon: '📈', label: 'Progress' },
  { id: 'nutrition', icon: '🥗', label: 'Nutrition' },
  { id: 'ai-trainer', icon: '🤖', label: 'AI Trainer' },
  { id: 'settings', icon: '⚙️', label: 'Settings' },
];

function Sidebar({ activeMenu, onMenuChange, isOpen }) {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">🏋️</span>
          <span className="logo-text">FitsAI</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeMenu === item.id ? 'active' : ''}`}
            onClick={() => onMenuChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">👤</div>
          <div className="user-details">
            <span className="user-name">Guest User</span>
            <span className="user-plan">AI Assisted</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
