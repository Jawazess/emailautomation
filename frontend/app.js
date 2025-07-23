function App() {
  const [csv, setCsv] = React.useState(null);
  const [log, setLog] = React.useState([]);
  const [form, setForm] = React.useState({imap: '', smtp: '', user: '', password: ''});

  const fetchLog = async () => {
    const res = await fetch('/log');
    const data = await res.json();
    setLog(data);
  };

  const upload = async () => {
    if (!csv) return;
    const fd = new FormData();
    fd.append('file', csv);
    const res = await fetch('/upload', {method: 'POST', body: fd});
    const data = await res.json();
    setForm({...form, csv: data.path});
    fetchLog();
  };

  const createDrafts = async () => {
    const res = await fetch('/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(form)
    });
    await res.json();
    fetchLog();
  };

  const sendEmails = async () => {
    const res = await fetch('/send', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(form)
    });
    await res.json();
    fetchLog();
  };

  React.useEffect(() => { fetchLog(); }, []);

  return (
    <div>
      <h1>Email Draft Automation</h1>
      <input type="file" accept=".csv" onChange={e => setCsv(e.target.files[0])} />
      <button onClick={upload}>Upload CSV</button>
      <div>
        <input placeholder="IMAP server" value={form.imap} onChange={e => setForm({...form, imap: e.target.value})} />
        <input placeholder="SMTP server" value={form.smtp} onChange={e => setForm({...form, smtp: e.target.value})} />
        <input placeholder="Email" value={form.user} onChange={e => setForm({...form, user: e.target.value})} />
        <input placeholder="Password" type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
        <button onClick={createDrafts}>Create Drafts</button>
        <button onClick={sendEmails}>Send Emails</button>
      </div>
      <h3>Log</h3>
      <div className="log">
        {log.map((l, i) => <div key={i}>{l}</div>)}
      </div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
