import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api'

const FALLBACK_MODES = [
  { id: 'red', label: 'Anger / Overwhelmed', subtitle: 'A pressure-release space without judgment.', color: '#ff304f', icon: '⚡', opening: 'I’m here. You don’t need to make it sound reasonable first. Tell me what’s pushing you past your limit right now.' },
  { id: 'blue', label: 'Sad / Lonely', subtitle: 'A quiet place to say what feels heavy.', color: '#3f8cff', icon: '◌', opening: 'Hey. You don’t have to carry this conversation alone right now. What feels the heaviest tonight?' },
  { id: 'yellow', label: 'Anxiety / Overthinking', subtitle: 'One thought at a time. No pressure to solve everything.', color: '#ffd43b', icon: '✦', opening: 'Let’s take this one thought at a time. What is your mind looping on right now?' },
  { id: 'green', label: 'Calm / Want to Talk', subtitle: 'Open conversation, reflection, or just company.', color: '#36e79a', icon: '⌁', opening: 'Good to have you here. We can talk about anything—your day, a problem, an idea, or absolutely nothing important. Where should we start?' },
]

function App() {
  const [modes, setModes] = useState(FALLBACK_MODES)
  const [selected, setSelected] = useState(null)
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [booting, setBooting] = useState(true)
  const [online, setOnline] = useState(false)
  const [safety, setSafety] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const endRef = useRef(null)
  const textInput = useRef(null)

  const activeMode = useMemo(() => modes.find((item) => item.id === selected), [modes, selected])

  useEffect(() => {
    const boot = async () => {
      try {
        const [modeData, health, past] = await Promise.all([api.modes(), api.health(), api.sessions()])
        setModes(modeData)
        setOnline(health.status === 'ok')
        setHistory(past)
      } catch {
        setOnline(false)
      } finally {
        setBooting(false)
      }
    }
    boot()
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, safety])

  async function refreshHistory() {
    try { setHistory(await api.sessions()) } catch { /* keep local UI usable */ }
  }

  async function chooseMode(mode) {
    setSelected(mode.id)
    setSafety(null)
    setLoading(true)
    try {
      const created = await api.createSession(mode.id)
      setSession(created)
      const loaded = await api.messages(created.id)
      setMessages(loaded)
      await refreshHistory()
    } catch {
      const localId = `local-${crypto.randomUUID()}`
      setSession({ id: localId, mode: mode.id, title: mode.label })
      setMessages([{ id: `opening-${localId}`, role: 'assistant', content: mode.opening, safety_flag: false }])
    } finally {
      setLoading(false)
      setTimeout(() => textInput.current?.focus(), 160)
    }
  }

  async function openHistory(item) {
    setSelected(item.mode)
    setSession(item)
    setSafety(null)
    setShowHistory(false)
    try {
      setMessages(await api.messages(item.id))
    } catch {
      setMessages([])
    }
    setTimeout(() => textInput.current?.focus(), 160)
  }

  async function sendMessage(event) {
    event?.preventDefault()
    const content = input.trim()
    if (!content || loading || !session) return

    setInput('')
    setLoading(true)
    setSafety(null)

    if (String(session.id).startsWith('local-')) {
      const userMsg = { id: crypto.randomUUID(), role: 'user', content, safety_flag: false }
      setMessages((prev) => [...prev, userMsg])
      const mode = modes.find((m) => m.id === session.mode) || FALLBACK_MODES[0]
      setTimeout(() => {
        setMessages((prev) => [...prev, {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: localFallback(mode.id, content),
          safety_flag: false,
        }])
        setLoading(false)
      }, 450)
      return
    }

    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content, safety_flag: false, optimistic: true }])
    try {
      const result = await api.send(session.id, content)
      setMessages((prev) => prev.filter((m) => !m.optimistic).concat([result.user_message, result.assistant_message]))
      setSafety(result.safety)
      await refreshHistory()
    } catch (error) {
      setMessages((prev) => prev.filter((m) => !m.optimistic))
      setInput(content)
      setSafety({ level: 'error', message: 'The connection to the AI service failed. Your text is still here—try again.' })
    } finally {
      setLoading(false)
      setTimeout(() => textInput.current?.focus(), 80)
    }
  }

  function resetToHome() {
    setSelected(null)
    setSession(null)
    setMessages([])
    setSafety(null)
    setInput('')
  }

  if (booting) return <div className="boot"><div className="boot-core" /><div>initializing emotional interface…</div></div>

  return (
    <main className={`app ${selected ? `mode-${selected}` : ''}`} style={{ '--accent': activeMode?.color || '#8b5cf6' }}>
      <div className="noise" />
      <div className="orb orb-a" />
      <div className="orb orb-b" />

      <header className="topbar">
        <button className="brand" onClick={resetToHome} aria-label="Return home">
          <span className="brand-mark"><span /><span /><span /></span>
          <span>
            <strong>LET THEM SPEAK</strong>
            <small>BEFORE THEY BREAK</small>
          </span>
        </button>
        <div className="top-actions">
          <span className={`status ${online ? 'online' : ''}`}><i /> {online ? 'AI CORE ONLINE' : 'OFFLINE FALLBACK'}</span>
          <button className="glass-button" onClick={() => setShowHistory((v) => !v)}>History</button>
        </div>
      </header>

      {showHistory && (
        <aside className="history-panel">
          <div className="panel-header"><span>YOUR CONVERSATIONS</span><button onClick={() => setShowHistory(false)}>×</button></div>
          {history.length === 0 ? <p className="empty">Your saved conversations will appear here.</p> : history.map((item) => (
            <button className="history-item" key={item.id} onClick={() => openHistory(item)}>
              <span className="history-dot" style={{ background: modes.find((m) => m.id === item.mode)?.color }} />
              <span><b>{item.title}</b><small>{item.mode}</small></span>
              <em>→</em>
            </button>
          ))}
          <p className="privacy-note">This demo stores chat history in its server database under an anonymous device ID. It is not designed for highly sensitive identifiers.</p>
        </aside>
      )}

      {!selected ? (
        <section className="home-screen">
          <div className="hero-copy">
            <div className="eyebrow"><span className="pulse" /> A QUIET PLACE TO SAY THE UNSAID</div>
            <h1>Let them speak<br /><span>before they break.</span></h1>
            <p>Choose what your mind feels like right now. The AI companion changes its tone, questions, and pace to meet you there.</p>
          </div>

          <div className="mode-grid">
            {modes.map((mode) => (
              <button key={mode.id} className={`mode-card ${mode.id}`} style={{ '--card-accent': mode.color }} onClick={() => chooseMode(mode)}>
                <div className="card-glow" />
                <div className="mode-icon">{mode.icon === 'bolt' ? '⚡' : mode.icon === 'cloud' ? '◌' : mode.icon === 'spark' ? '✦' : '⌁'}</div>
                <div className="mode-copy"><span className="mode-kicker">{mode.id.toUpperCase()}</span><h2>{mode.label}</h2><p>{mode.subtitle}</p></div>
                <span className="arrow">↗</span>
              </button>
            ))}
          </div>

          <div className="trust-strip"><span>AI COMPANION</span><i /> <span>CONTEXT AWARE</span><i /> <span>NO DIAGNOSIS</span><i /> <span>SAFETY-FIRST</span></div>
        </section>
      ) : (
        <section className="chat-screen">
          <div className="chat-shell">
            <div className="chat-head">
              <button className="back-button" onClick={resetToHome}>← <span>modes</span></button>
              <div className="active-mode-label"><span className="active-dot" /> {activeMode?.label}</div>
              <div className="conversation-id">SESSION {String(session?.id).slice(0, 8).toUpperCase()}</div>
            </div>

            <div className="conversation">
              <div className="robot-stage">
                <Robot color={activeMode?.color || '#8b5cf6'} speaking={loading} />
                <div className="robot-status">{loading ? 'thinking…' : 'listening'}</div>
              </div>

              <div className="messages">
                {messages.map((message) => (
                  <div className={`message-row ${message.role === 'user' ? 'user-row' : 'ai-row'}`} key={message.id}>
                    <div className={`message ${message.role === 'user' ? 'user-message' : 'ai-message'}`}>
                      {message.content}
                    </div>
                  </div>
                ))}
                {loading && <div className="message-row ai-row"><div className="typing"><span /><span /><span /></div></div>}
                {safety?.immediate_danger && (
                  <div className="safety-card">
                    <div className="safety-icon">!</div>
                    <div><strong>You deserve real-world support right now.</strong><p>Call <a href="tel:112">112</a> for an emergency in India, or call <a href="tel:14416">Tele-MANAS 14416</a> for mental-health support. Please stay with someone you trust.</p></div>
                  </div>
                )}
                {safety?.level === 'error' && <div className="error-note">{safety.message}</div>}
                <div ref={endRef} />
              </div>
            </div>

            <form className="composer" onSubmit={sendMessage}>
              <div className="composer-inner">
                <textarea
                  ref={textInput}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(e) } }}
                  placeholder={activeMode?.id === 'red' ? 'Say the angry part exactly as it is…' : activeMode?.id === 'blue' ? 'You can start anywhere…' : activeMode?.id === 'yellow' ? 'What is your mind stuck on?' : 'Start talking…'}
                  rows="1"
                  aria-label="Message"
                />
                <button className="send-button" disabled={!input.trim() || loading}><span>Send</span> ↗</button>
              </div>
              <div className="composer-footer"><span>Enter to send · Shift+Enter for a new line</span><span>Not a therapist · Not for emergencies</span></div>
            </form>
          </div>
        </section>
      )}

      <footer className="footer">© 2026 LET THEM SPEAK · A supportive AI interface, not medical care.</footer>
    </main>
  )
}

function localFallback(mode, text) {
  const short = text.length > 120 ? `${text.slice(0, 120)}…` : text
  const responses = {
    red: `I hear the pressure in that. You said: “${short}” — what part do you most want to get off your chest first?`,
    blue: `I’m listening. You don’t have to make it smaller than it feels. When you think about “${short}”, what hurts most?`,
    yellow: `Let’s slow the loop down. You said: “${short}”. Which part is a fact you know, and which part is a fear your mind is predicting?`,
    green: `Got you. “${short}” gives us somewhere to start. What would you like me to be curious about with you?`,
  }
  return responses[mode] || responses.green
}

function Robot({ color, speaking }) {
  return (
    <div className={`robot ${speaking ? 'speaking' : ''}`} style={{ '--robot-color': color }}>
      <div className="robot-aura" />
      <div className="robot-head">
        <div className="robot-ear left" /><div className="robot-ear right" />
        <div className="robot-face">
          <div className="robot-eyes"><i /><i /></div>
          <div className="robot-mouth"><span /><span /><span /></div>
        </div>
      </div>
      <div className="robot-neck" />
      <div className="robot-body"><div className="body-line" /><div className="core-ring"><span /></div></div>
    </div>
  )
}

export default App
