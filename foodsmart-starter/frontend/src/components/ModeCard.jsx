export default function ModeCard({ title, subtitle, active, onClick, icon }) {
  return (
    <button className={`mode-card ${active ? 'active' : ''}`} onClick={onClick}>
      <div className="mode-card-header">
        <span>{icon}</span>
        <span>{title}</span>
      </div>
      <p>{subtitle}</p>
    </button>
  )
}
