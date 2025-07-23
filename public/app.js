function App() {
  const [csv, setCsv] = React.useState(null);
  const [log, setLog] = React.useState([]);
  const [form, setForm] = React.useState({
    imap: '',
    smtp: '',
    user: '',
    password: '',
    token: ''
  });

  const signIn = () => {
    if (!window.google || !window.google.accounts) return;
    const client = window.google.accounts.oauth2.initTokenClient({
      client_id: window.GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID',
      scope:
        'https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.send',
      callback: (resp) => {
        if (resp.access_token) {
          setForm((f) => ({ ...f, token: resp.access_token }));
        }
      },
    });
    client.requestAccessToken();
  };

  const fetchLog = async () => {
    const res = await fetch('/api/log');
    const data = await res.json();
    setLog(data);
  };

  const upload = async () => {
    if (!csv) return;
    const fd = new FormData();
    fd.append('file', csv);
    const res = await fetch('/api/upload', {method: 'POST', body: fd});
    const data = await res.json();
    setForm({...form, csv: data.path});
    fetchLog();
  };

  const createDrafts = async () => {
    const res = await fetch('/api/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(form)
    });
    await res.json();
    fetchLog();
  };

  const sendEmails = async () => {
    const res = await fetch('/api/send', {
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
        <button onClick={signIn}>Sign in with Google</button>
        {form.token && <span style={{marginLeft: '8px'}}>Signed in</span>}
      </div>
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
