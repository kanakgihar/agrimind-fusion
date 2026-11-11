export const Spinner = ({ label }) => <span className="row"><span className="spin" aria-hidden="true" />{label && <span className="muted">{label}</span>}</span>;

export const Empty = ({ title, children }) => (
  <div className="empty"><h3>{title}</h3><div>{children}</div></div>
);

export const ErrorBox = ({ error }) => (error ? <div className="banner err" role="alert">{error}</div> : null);

export const Badge = ({ kind, children }) => <span className={`badge ${kind}`}>{children}</span>;

export const Bar = ({ value }) => <div className="bar" role="img" aria-label={`${Math.round(value * 100)} percent`}><i style={{ width: `${Math.max(0, Math.min(1, value)) * 100}%` }} /></div>;

export function Confirm({ title, text, confirmLabel = "Delete", onConfirm, onCancel }) {
  return (
    <div className="modal-bg" role="dialog" aria-modal="true" aria-label={title}>
      <div className="modal">
        <h3>{title}</h3><p>{text}</p>
        <div className="row"><button className="btn danger" onClick={onConfirm}>{confirmLabel}</button><button className="btn ghost" onClick={onCancel}>Cancel</button></div>
      </div>
    </div>
  );
}

export const Field = ({ label, children }) => <div><label className="f">{label}</label>{children}</div>;
