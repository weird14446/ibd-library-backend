import { useState, useEffect, useRef } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000/api'

// ==================== Auth Modal Component ====================
function AuthModal({ isOpen, onClose, onLogin }) {
  const [mode, setMode] = useState('login') // 'login' or 'signup'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: '',
    address: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (mode === 'login') {
        const res = await fetch(`${API_URL}/users/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password
          })
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || '로그인 실패')
        onLogin(data.user)
        onClose()
      } else {
        const res = await fetch(`${API_URL}/users/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            name: formData.name,
            phone: formData.phone || null,
            address: formData.address || null
          })
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || '회원가입 실패')
        // 회원가입 성공 후 자동 로그인
        setMode('login')
        setError('')
        alert('회원가입이 완료되었습니다! 로그인해주세요.')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({ email: '', password: '', name: '', phone: '', address: '' })
    setError('')
  }

  const switchMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login')
    resetForm()
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="modal-header">
          <h2>{mode === 'login' ? '🔐 로그인' : '✨ 회원가입'}</h2>
          <p>{mode === 'login' ? '계정에 로그인하세요' : '새 계정을 만들어보세요'}</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {mode === 'signup' && (
            <div className="form-group">
              <label>이름 *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="홍길동"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>이메일 *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="example@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label>비밀번호 *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
              minLength={4}
            />
          </div>

          {mode === 'signup' && (
            <>
              <div className="form-group">
                <label>전화번호</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="010-1234-5678"
                />
              </div>
              <div className="form-group">
                <label>주소</label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  placeholder="서울시 강남구"
                />
              </div>
            </>
          )}

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? '처리 중...' : (mode === 'login' ? '로그인' : '회원가입')}
          </button>
        </form>

        <div className="modal-footer">
          <p>
            {mode === 'login' ? '계정이 없으신가요?' : '이미 계정이 있으신가요?'}
            <button className="link-btn" onClick={switchMode}>
              {mode === 'login' ? '회원가입' : '로그인'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

// ==================== Loans Modal Component ====================
function LoansModal({ isOpen, onClose, user }) {
  const [loans, setLoans] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && user) fetchLoans()
  }, [isOpen, user])

  const fetchLoans = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/loans/?user_id=${user.user_id}`)
      if (!res.ok) throw new Error('대출 목록 로드 실패')
      const data = await res.json()
      // Fetch book details for each loan
      const loansWithBooks = await Promise.all(
        data.map(async (loan) => {
          const bookRes = await fetch(`${API_URL}/books/${loan.book_id}`)
          const book = bookRes.ok ? await bookRes.json() : null
          return { ...loan, book }
        })
      )
      setLoans(loansWithBooks)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleExtend = async (loanId) => {
    try {
      const res = await fetch(`${API_URL}/loans/${loanId}/extend`, { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        alert(data.message)
        fetchLoans()
      } else {
        alert(data.message)
      }
    } catch (err) {
      alert('연장 실패')
    }
  }

  const handleReturn = async (loanId) => {
    try {
      const res = await fetch(`${API_URL}/loans/${loanId}/return`, { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        alert(data.message)
        fetchLoans()
      } else {
        alert(data.message)
      }
    } catch (err) {
      alert('반납 실패')
    }
  }

  if (!isOpen) return null

  const activeLoans = loans.filter(l => l.status === 'BORROWED')
  const returnedLoans = loans.filter(l => l.status === 'RETURNED')

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="modal-header">
          <h2>📚 내 대출 현황</h2>
          <p>대출 중인 도서와 대출 기록을 확인합니다</p>
        </div>

        {loading ? (
          <p style={{ textAlign: 'center', padding: '20px' }}>로딩 중...</p>
        ) : (
          <div className="loans-list">
            {activeLoans.length > 0 && (
              <>
                <h3 style={{ marginBottom: '10px', color: 'var(--primary)' }}>대출 중 ({activeLoans.length}권)</h3>
                {activeLoans.map(loan => (
                  <div key={loan.loan_id} className="loan-item" style={{
                    padding: '15px',
                    marginBottom: '10px',
                    borderRadius: '10px',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong>{loan.book?.title || `Book #${loan.book_id}`}</strong>
                        <p style={{ fontSize: '0.85rem', opacity: 0.7, margin: '5px 0 0' }}>
                          반납 예정일: {new Date(loan.due_date).toLocaleDateString('ko-KR')}
                          {loan.extension_count > 0 && ` (연장 ${loan.extension_count}회)`}
                        </p>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-secondary btn-sm" onClick={() => handleExtend(loan.loan_id)}>연장</button>
                        <button className="btn btn-primary btn-sm" onClick={() => handleReturn(loan.loan_id)}>반납</button>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}

            {returnedLoans.length > 0 && (
              <>
                <h3 style={{ marginTop: '20px', marginBottom: '10px', opacity: 0.6 }}>반납 완료 ({returnedLoans.length}권)</h3>
                {returnedLoans.slice(0, 5).map(loan => (
                  <div key={loan.loan_id} className="loan-item" style={{
                    padding: '10px 15px',
                    marginBottom: '5px',
                    borderRadius: '8px',
                    background: 'rgba(255,255,255,0.02)',
                    opacity: 0.6
                  }}>
                    <span>{loan.book?.title || `Book #${loan.book_id}`}</span>
                    <span style={{ float: 'right', fontSize: '0.8rem' }}>
                      {new Date(loan.return_date).toLocaleDateString('ko-KR')} 반납
                    </span>
                  </div>
                ))}
              </>
            )}

            {loans.length === 0 && (
              <p style={{ textAlign: 'center', padding: '30px', opacity: 0.6 }}>대출 기록이 없습니다</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ==================== Admin Config Modal Component ====================
function AdminConfigModal({ isOpen, onClose, user }) {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) fetchConfigs()
  }, [isOpen])

  const fetchConfigs = async () => {
    try {
      const res = await fetch(`${API_URL}/admin/config`, {
        headers: {
          'x-user-id': user?.user_id?.toString()
        }
      })
      if (!res.ok) throw new Error('설정 로드 실패')
      const data = await res.json()
      setConfigs(data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleUpdate = async (key, newValue) => {
    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/admin/config/${key}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': user?.user_id?.toString()
        },
        body: JSON.stringify({ value: newValue })
      })
      if (!res.ok) throw new Error('설정 저장 실패')
      const updated = await res.json()
      setConfigs(configs.map(c => c.key === key ? updated : c))
      alert('설정이 저장되었습니다')
    } catch (err) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="modal-header">
          <h2>⚙️ 시스템 설정</h2>
          <p>도서관 운영 정책을 설정합니다</p>
        </div>
        <div className="config-list">
          {configs.map(config => (
            <div key={config.key} className="form-group">
              <label>{config.description || config.key}</label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="number"
                  value={config.value}
                  onChange={(e) => {
                    const val = e.target.value
                    setConfigs(configs.map(c => c.key === config.key ? { ...c, value: val } : c))
                  }}
                  style={{ flex: 1 }}
                />
                <button
                  className="btn btn-primary btn-sm"
                  disabled={loading}
                  onClick={() => handleUpdate(config.key, config.value)}
                >
                  저장
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ==================== Header Component ====================
function Header({ user, onLogout, onLoginClick, onProfileClick, onConfigClick, onLoansClick }) {
  return (
    <header className="header">
      <div className="container header-content">
        <div className="logo">
          <span className="logo-icon">📚</span>
          <span className="logo-text">IBD Library</span>
        </div>
        <nav className="nav">
          <a href="#books" className="nav-link active">도서목록</a>
          <a href="#about" className="nav-link">소개</a>
          <a href="#contact" className="nav-link">문의</a>
        </nav>
        {user ? (
          <div className="user-menu">
            {user.role === 'LIBRARIAN' && (
              <button className="btn btn-secondary" onClick={onConfigClick} title="시스템 설정">
                ⚙️
              </button>
            )}
            <button className="btn btn-secondary" onClick={onLoansClick} title="내 대출">
              📚
            </button>
            <button className="user-name-btn" onClick={onProfileClick}>
              👤 {user.name}
            </button>
            <button className="btn btn-secondary" onClick={onLogout}>로그아웃</button>
          </div>
        ) : (
          <button className="btn btn-primary" onClick={onLoginClick}>로그인</button>
        )}
      </div>
    </header>
  )
}

// ==================== Hero Component ====================
function Hero() {
  const [showAiModal, setShowAiModal] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const scrollToBooks = () => {
    document.getElementById('books')?.scrollIntoView({ behavior: 'smooth' })
  }

  const getAiRecommendations = async () => {
    setShowAiModal(true)
    setLoading(true)
    try {
      // 추천 알고리즘 API 호출
      const res = await fetch(`${API_URL}/ai/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 5 })
      })
      if (res.ok) {
        const data = await res.json()
        setRecommendations(data.recommendations || [])
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <section className="hero">
        <div className="container hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              <span className="gradient-text">지식의 바다</span>에서
              <br />원하는 책을 찾아보세요
            </h1>
            <p className="hero-description">
              AI 기반 도서 추천과 스마트한 검색으로
              <br />당신에게 꼭 맞는 책을 찾아드립니다.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary" onClick={scrollToBooks}>
                <span>🔍</span> 도서 검색
              </button>
              <button className="btn btn-secondary" onClick={getAiRecommendations}>
                <span>✨</span> AI 추천받기
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="floating-books">
              <span className="floating-book" style={{ '--delay': '0s' }}>📚</span>
              <span className="floating-book" style={{ '--delay': '0.5s' }}>📖</span>
              <span className="floating-book" style={{ '--delay': '1s' }}>📕</span>
              <span className="floating-book" style={{ '--delay': '1.5s' }}>📗</span>
            </div>
          </div>
        </div>
        <div className="hero-bg"></div>
      </section>

      {/* AI Recommendation Modal */}
      {showAiModal && (
        <div className="modal-overlay" onClick={() => setShowAiModal(false)}>
          <div className="modal-content glass" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <button className="modal-close" onClick={() => setShowAiModal(false)}>✕</button>
            <div className="modal-header">
              <h2>✨ AI 추천 도서</h2>
              <p>당신을 위한 추천 도서입니다</p>
            </div>
            {loading ? (
              <p style={{ textAlign: 'center', padding: '30px' }}>AI가 도서를 분석 중입니다...</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {recommendations.map((book, idx) => (
                  <div key={book.book_id} style={{
                    padding: '15px',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '10px',
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '1.5rem' }}>📘</span>
                      <div>
                        <strong>{book.title}</strong>
                        <p style={{ opacity: 0.7, fontSize: '0.9rem', margin: '3px 0 0' }}>{book.author}</p>
                      </div>
                    </div>
                    {book.description && (
                      <p style={{ marginTop: '10px', opacity: 0.8, fontSize: '0.85rem', lineHeight: 1.5 }}>
                        {book.description.substring(0, 100)}...
                      </p>
                    )}
                  </div>
                ))}
                <button className="btn btn-primary" onClick={() => { setShowAiModal(false); scrollToBooks(); }} style={{ marginTop: '10px' }}>
                  도서 목록에서 보기
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

// ==================== Stats Component ====================
function Stats() {
  const stats = [
    { label: '보유 도서', value: '12,500+', icon: '📚' },
    { label: '등록 회원', value: '3,200+', icon: '👥' },
    { label: '월간 대출', value: '1,800+', icon: '📖' },
    { label: '평균 평점', value: '4.8', icon: '⭐' },
  ]

  return (
    <section className="stats">
      <div className="container stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card glass">
            <span className="stat-icon">{stat.icon}</span>
            <span className="stat-value">{stat.value}</span>
            <span className="stat-label">{stat.label}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

// ==================== Search Component ====================
function SearchBar({ searchTerm, setSearchTerm }) {
  return (
    <div className="search-bar glass">
      <span className="search-icon">🔍</span>
      <input
        type="text"
        className="search-input"
        placeholder="도서명, 저자, ISBN으로 검색..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      {searchTerm && (
        <button className="search-clear" onClick={() => setSearchTerm('')}>✕</button>
      )}
    </div>
  )
}

// ==================== Book Card Component ====================
function BookCard({ book, user, onBorrow, onEdit, onDelete, onView }) {
  const available = book.stock_quantity > 0
  const isLibrarian = user?.role === 'LIBRARIAN'

  return (
    <div className="book-card card" onClick={() => onView(book)}>
      <div className="book-cover">
        <span className="book-emoji">📘</span>
      </div>
      <div className="book-info">
        <h3 className="book-title">{book.title}</h3>
        <p className="book-author">{book.author}</p>
        <p className="book-publisher">{book.publisher} • {book.published_year}</p>
        <div className="book-meta">
          <span className="book-category">{book.category}</span>
          <span className={`book-status ${available ? 'available' : 'unavailable'}`}>
            {available ? `재고 ${book.stock_quantity}권` : '대출 중'}
          </span>
        </div>
      </div>

      {isLibrarian ? (
        <div className="card-actions">
          <button className="btn btn-secondary btn-sm" onClick={() => onEdit(book)}>수정</button>
          <button className="btn btn-danger btn-sm" onClick={() => onDelete(book)}>삭제</button>
        </div>
      ) : (
        <button
          className={`btn ${available ? 'btn-primary' : 'btn-secondary'}`}
          disabled={!available || !user}
          onClick={() => onBorrow(book)}
          title={!user ? '로그인이 필요합니다' : ''}
        >
          {available ? '대출하기' : '예약하기'}
        </button>
      )}
    </div>
  )
}


// ==================== Books Section ====================
function BooksSection({ user }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [category, setCategory] = useState('')
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [selectedBook, setSelectedBook] = useState(null)

  const isLibrarian = user?.role === 'LIBRARIAN'
  const categories = ['소설', '인문', '과학', '역사', '예술', '자기계발']

  useEffect(() => {
    fetchBooks()
  }, [searchTerm])

  const fetchBooks = async () => {
    try {
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)
      if (category) params.append('category', category)

      const res = await fetch(`${API_URL}/books/?${params.toString()}`)
      const data = await res.json()
      setBooks(data)
    } catch (err) {
      console.error('도서 목록 조회 실패:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleBorrow = async (book) => {
    if (!user) {
      alert('로그인이 필요합니다')
      return
    }
    try {
      const res = await fetch(`${API_URL}/loans/borrow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.user_id,
          book_id: book.book_id
        })
      })
      const data = await res.json()
      alert(data.message)
      fetchBooks()
    } catch (err) {
      alert('대출 처리 중 오류가 발생했습니다')
    }
  }

  const handleAddBook = () => {
    setSelectedBook(null)
    setModalOpen(true)
  }

  const handleEditBook = (book) => {
    setSelectedBook(book)
    setModalOpen(true)
  }

  const handleDeleteBook = async (book) => {
    if (!window.confirm(`'${book.title}' 도서를 정말 삭제하시겠습니까?`)) return

    try {
      const res = await fetch(`${API_URL}/books/${book.book_id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('삭제 실패')
      alert('도서가 삭제되었습니다')
      fetchBooks()
    } catch (err) {
      alert(err.message)
    }
  }

  const handleViewBook = (book) => {
    setSelectedBook(book)
    setDetailModalOpen(true)
  }

  const handleSaveBook = () => {
    fetchBooks()
  }

  return (
    <section id="books" className="books-section">
      <div className="container">
        <div className="section-header">
          <div className="section-title-group">
            <h2 className="section-title">📖 도서 목록</h2>
            <p className="section-description">원하는 책을 검색하고 대출해보세요</p>
          </div>
          <div className="section-actions">
            <select
              className="category-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">전체 장르</option>
              {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
            {isLibrarian && (
              <button className="btn btn-primary btn-add-book" onClick={handleAddBook}>
                + 도서 등록
              </button>
            )}
          </div>
        </div>
        <SearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />

        {loading ? (
          <div className="loading">로딩 중...</div>
        ) : (
          <div className="books-grid">
            {books.map((book, index) => (
              <div key={book.book_id} style={{ animationDelay: `${index * 0.1}s` }} className="animate-fade-in">
                <BookCard
                  book={book}
                  user={user}
                  onBorrow={handleBorrow}
                  onEdit={handleEditBook}
                  onDelete={handleDeleteBook}
                  onView={handleViewBook}
                />
              </div>
            ))}
          </div>
        )}

        {!loading && books.length === 0 && (
          <div className="no-results">
            <span className="no-results-icon">🔍</span>
            <p>검색 결과가 없습니다</p>
          </div>
        )}
      </div>
      <BookFormModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        book={selectedBook}
        onSave={handleSaveBook}
      />

      <BookDetailModal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        book={selectedBook}
        user={user}
        onBorrow={handleBorrow}
        onEdit={handleEditBook}
        onDelete={handleDeleteBook}
      />
    </section>
  )
}

// ==================== Footer Component ====================
// ==================== About Section ====================
function About() {
  return (
    <section id="about" className="about-section">
      <div className="container">
        <h2 className="section-title">📖 도서관 소개</h2>
        <div className="about-content glass" style={{ padding: '40px', borderRadius: '20px', marginTop: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px' }}>
            <div>
              <h3 style={{ marginBottom: '15px', color: 'var(--primary)' }}>🎯 비전</h3>
              <p style={{ opacity: 0.85, lineHeight: 1.7 }}>
                IBD Library는 최신 AI 기술을 활용하여 더 스마트하고 편리한 도서관 경험을 제공합니다.
                누구나 쉽게 원하는 책을 찾고 대출할 수 있는 디지털 도서관을 목표로 합니다.
              </p>
            </div>
            <div>
              <h3 style={{ marginBottom: '15px', color: 'var(--primary)' }}>⏰ 운영 시간</h3>
              <p style={{ opacity: 0.85, lineHeight: 1.7 }}>
                <strong>평일:</strong> 09:00 - 21:00<br />
                <strong>주말:</strong> 10:00 - 18:00<br />
                <strong>휴관일:</strong> 매월 첫째, 셋째 월요일
              </p>
            </div>
            <div>
              <h3 style={{ marginBottom: '15px', color: 'var(--primary)' }}>🚀 주요 서비스</h3>
              <ul style={{ opacity: 0.85, lineHeight: 1.8, paddingLeft: '20px' }}>
                <li>온라인 도서 검색 및 대출</li>
                <li>도서 예약 및 연장</li>
                <li>도서 리뷰 및 평점</li>
                <li>사서 추천 도서</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ==================== Contact Section ====================
function Contact() {
  const handleSubmit = (e) => {
    e.preventDefault()
    alert('문의가 접수되었습니다. 빠른 시일 내에 답변드리겠습니다.')
    e.target.reset()
  }

  return (
    <section id="contact" className="contact-section">
      <div className="container">
        <h2 className="section-title">💬 문의하기</h2>
        <div className="contact-content" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', marginTop: '20px' }}>
          <div className="glass" style={{ padding: '30px', borderRadius: '20px' }}>
            <h3 style={{ marginBottom: '20px', color: 'var(--primary)' }}>📍 연락처</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', opacity: 0.85 }}>
              <p>📞 전화: 02-1234-5678</p>
              <p>📧 이메일: contact@ibd-library.com</p>
              <p>📍 주소: 서울특별시 강남구 테헤란로 123, IBD빌딩 3층</p>
              <p>🕐 응대시간: 평일 09:00 - 18:00</p>
            </div>
          </div>
          <form onSubmit={handleSubmit} className="glass" style={{ padding: '30px', borderRadius: '20px' }}>
            <h3 style={{ marginBottom: '20px', color: 'var(--primary)' }}>✉️ 온라인 문의</h3>
            <div className="form-group" style={{ marginBottom: '15px' }}>
              <input type="text" placeholder="이름" required style={{ width: '100%', padding: '12px', borderRadius: '8px', border: 'none', background: 'rgba(255,255,255,0.1)', color: 'inherit' }} />
            </div>
            <div className="form-group" style={{ marginBottom: '15px' }}>
              <input type="email" placeholder="이메일" required style={{ width: '100%', padding: '12px', borderRadius: '8px', border: 'none', background: 'rgba(255,255,255,0.1)', color: 'inherit' }} />
            </div>
            <div className="form-group" style={{ marginBottom: '15px' }}>
              <textarea placeholder="문의 내용" required rows="4" style={{ width: '100%', padding: '12px', borderRadius: '8px', border: 'none', background: 'rgba(255,255,255,0.1)', color: 'inherit', resize: 'vertical' }} />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>문의 보내기</button>
          </form>
        </div>
      </div>
    </section>
  )
}

// ==================== Footer Component ====================
function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-content">
        <div className="footer-brand">
          <span className="logo-icon">📚</span>
          <span>IBD Library</span>
        </div>
        <p className="footer-text">
          Vibe Coding으로 개발된 AI Native 도서관 시스템
        </p>
        <div className="footer-links">
          <a href="#privacy">개인정보처리방침</a>
          <span>•</span>
          <a href="#terms">이용약관</a>
          <span>•</span>
          <a href="#contact">문의하기</a>
        </div>
        <p className="footer-copyright">
          © 2026 IBD Library. Built with ❤️ and AI.
        </p>
      </div>
    </footer>
  )
}

// ==================== Profile Modal Component ====================
function ProfileModal({ isOpen, onClose, user, onUpdate, onDelete }) {
  const [formData, setFormData] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    address: user?.address || '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        phone: user.phone || '',
        address: user.address || '',
        password: ''
      })
    }
  }, [user])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setError('')
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // 비밀번호가 비어있으면 전송하지 않음
      const updateData = { ...formData }
      if (!updateData.password) delete updateData.password

      const res = await fetch(`${API_URL}/users/${user.user_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '수정 실패')

      onUpdate({
        ...user,
        name: data.name,
        phone: data.phone,
        address: data.address
      })
      alert('회원 정보가 수정되었습니다')
      setFormData(prev => ({ ...prev, password: '' })) // 비밀번호 필드 초기화
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/users/${user.user_id}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('탈퇴 실패')

      onDelete()
      alert('회원 탈퇴가 완료되었습니다')
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      setShowDeleteConfirm(false)
    }
  }

  if (!isOpen || !user) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="modal-header">
          <h2>👤 마이페이지</h2>
          <p>{user.email}</p>
        </div>

        {!showDeleteConfirm ? (
          <>
            <form onSubmit={handleUpdate} className="auth-form">
              <div className="form-group">
                <label>이름 *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>전화번호</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="010-1234-5678"
                />
              </div>

              <div className="form-group">
                <label>주소</label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  placeholder="서울시 강남구"
                />
              </div>

              <div className="form-group">
                <label>새 비밀번호 (변경 시에만 입력)</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="변경할 비밀번호를 입력하세요"
                />
              </div>

              {error && <div className="form-error">{error}</div>}

              <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? '처리 중...' : '정보 수정'}
              </button>
            </form>

            <div className="modal-footer">
              <button
                className="link-btn danger"
                onClick={() => setShowDeleteConfirm(true)}
              >
                회원 탈퇴
              </button>
            </div>
          </>
        ) : (
          <div className="delete-confirm">
            <p className="delete-warning">⚠️ 정말 탈퇴하시겠습니까?</p>
            <p className="delete-info">탈퇴 시 모든 데이터가 삭제되며 복구할 수 없습니다.</p>
            <div className="delete-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setShowDeleteConfirm(false)}
              >
                취소
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={loading}
              >
                {loading ? '처리 중...' : '탈퇴하기'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ==================== Book Form Modal Component ====================
function BookFormModal({ isOpen, onClose, book, onSave }) {
  const [formData, setFormData] = useState({
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    published_year: new Date().getFullYear(),
    category: '',
    stock_quantity: 1,
    description: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (book) {
      setFormData({
        isbn: book.isbn || '',
        title: book.title || '',
        author: book.author || '',
        publisher: book.publisher || '',
        published_year: book.published_year || new Date().getFullYear(),
        category: book.category || '',
        stock_quantity: book.stock_quantity || 1,
        description: book.description || ''
      })
    } else {
      setFormData({
        isbn: '',
        title: '',
        author: '',
        publisher: '',
        published_year: new Date().getFullYear(),
        category: '',
        stock_quantity: 1,
        description: ''
      })
    }
  }, [book, isOpen])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'published_year' || name === 'stock_quantity' ? parseInt(value) || 0 : value
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const url = book ? `${API_URL}/books/${book.book_id}` : `${API_URL}/books/`
      const method = book ? 'PUT' : 'POST'

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      const data = await res.json()

      if (!res.ok) throw new Error(data.detail || '저장 실패')

      onSave(data)
      alert(book ? '도서 정보가 수정되었습니다' : '새 도서가 등록되었습니다')
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="modal-header">
          <h2>{book ? '📚 도서 정보 수정' : '📚 새 도서 등록'}</h2>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>ISBN *</label>
            <input name="isbn" value={formData.isbn} onChange={handleChange} required placeholder="978-..." disabled={!!book} />
          </div>

          <div className="form-group">
            <label>도서명 *</label>
            <input name="title" value={formData.title} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>저자 *</label>
            <input name="author" value={formData.author} onChange={handleChange} required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>출판사</label>
              <input name="publisher" value={formData.publisher} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>출판년도</label>
              <input type="number" name="published_year" value={formData.published_year} onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>카테고리</label>
              <input name="category" value={formData.category} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>재고 수량</label>
              <input type="number" name="stock_quantity" value={formData.stock_quantity} onChange={handleChange} min="0" />
            </div>
          </div>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? '처리 중...' : '저장하기'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ==================== Book Detail Modal Component ====================
function BookDetailModal({ isOpen, onClose, book, user, onBorrow, onEdit, onDelete }) {
  const [reviews, setReviews] = useState([])
  const [stats, setStats] = useState({ average_rating: 0, review_count: 0 })
  const [loading, setLoading] = useState(false)
  const [newRating, setNewRating] = useState(5)
  const [newContent, setNewContent] = useState('')
  const [editingReview, setEditingReview] = useState(null)
  const [showReviewForm, setShowReviewForm] = useState(false)

  useEffect(() => {
    if (isOpen && book) {
      fetchReviews()
      fetchStats()
    }
  }, [isOpen, book])

  const fetchReviews = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/reviews/book/${book.book_id}`)
      if (res.ok) setReviews(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/reviews/book/${book.book_id}/stats`)
      if (res.ok) setStats(await res.json())
    } catch (err) {
      console.error(err)
    }
  }

  const handleSubmitReview = async (e) => {
    e.preventDefault()
    if (!user) return alert('로그인이 필요합니다')

    try {
      const url = editingReview
        ? `${API_URL}/reviews/${editingReview.review_id}?user_id=${user.user_id}`
        : `${API_URL}/reviews/`
      const method = editingReview ? 'PUT' : 'POST'
      const body = editingReview
        ? { rating: newRating, content: newContent }
        : { user_id: user.user_id, book_id: book.book_id, rating: newRating, content: newContent }

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || '리뷰 저장 실패')
      }

      alert(editingReview ? '리뷰가 수정되었습니다' : '리뷰가 등록되었습니다')
      setNewRating(5)
      setNewContent('')
      setEditingReview(null)
      setShowReviewForm(false)
      fetchReviews()
      fetchStats()
    } catch (err) {
      alert(err.message)
    }
  }

  const handleEditReview = (review) => {
    setEditingReview(review)
    setNewRating(review.rating)
    setNewContent(review.content || '')
    setShowReviewForm(true)
  }

  const handleDeleteReview = async (reviewId) => {
    if (!confirm('리뷰를 삭제하시겠습니까?')) return
    try {
      const res = await fetch(`${API_URL}/reviews/${reviewId}?user_id=${user.user_id}`, { method: 'DELETE' })
      if (!res.ok && res.status !== 204) throw new Error('삭제 실패')
      fetchReviews()
      fetchStats()
    } catch (err) {
      alert(err.message)
    }
  }

  const StarRating = ({ rating, interactive = false, onRate = () => { } }) => (
    <div className="star-rating" style={{ display: 'inline-flex', gap: '2px' }}>
      {[1, 2, 3, 4, 5].map(star => (
        <span
          key={star}
          onClick={() => interactive && onRate(star)}
          style={{
            cursor: interactive ? 'pointer' : 'default',
            fontSize: '1.2rem',
            color: star <= rating ? '#ffc107' : 'rgba(255,255,255,0.2)'
          }}
        >
          ★
        </span>
      ))}
    </div>
  )

  if (!isOpen || !book) return null

  const available = book.stock_quantity > 0
  const isLibrarian = user?.role === 'LIBRARIAN'
  const userReview = reviews.find(r => r.user_id === user?.user_id)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass book-detail-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="book-detail-layout">
          <div className="book-detail-cover">
            <span className="book-detail-emoji">📘</span>
          </div>

          <div className="book-detail-info">
            <div className="book-detail-header">
              <span className="book-category-tag">{book.category || '기타'}</span>
              <h2 className="book-detail-title">{book.title}</h2>
              <p className="book-detail-author">{book.author}</p>
              <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <StarRating rating={Math.round(stats.average_rating)} />
                <span style={{ opacity: 0.7 }}>{stats.average_rating} ({stats.review_count}개 리뷰)</span>
              </div>
            </div>

            <div className="book-detail-meta">
              <div className="meta-item">
                <span className="meta-label">출판사</span>
                <span className="meta-value">{book.publisher || '-'}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">출판년도</span>
                <span className="meta-value">{book.published_year || '-'}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">ISBN</span>
                <span className="meta-value">{book.isbn || '-'}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">재고</span>
                <span className={`meta-value ${available ? 'text-success' : 'text-danger'}`}>
                  {available ? `${book.stock_quantity}권` : '대출 불가 (0권)'}
                </span>
              </div>
            </div>

            {book.description && (
              <div className="book-description">
                <p>{book.description}</p>
              </div>
            )}

            <div className="book-detail-actions">
              {isLibrarian ? (
                <>
                  <button className="btn btn-secondary" onClick={() => { onEdit(book); onClose(); }}>수정</button>
                  <button className="btn btn-danger" onClick={() => { onDelete(book); onClose(); }}>삭제</button>
                </>
              ) : (
                <button
                  className={`btn ${available ? 'btn-primary' : 'btn-secondary'} btn-lg`}
                  disabled={!available || !user}
                  onClick={() => { onBorrow(book); onClose(); }}
                >
                  {available ? '대출하기' : '예약하기'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        <div style={{ marginTop: '30px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3>📝 리뷰</h3>
            {user && !userReview && !showReviewForm && (
              <button className="btn btn-primary btn-sm" onClick={() => setShowReviewForm(true)}>리뷰 작성</button>
            )}
          </div>

          {showReviewForm && (
            <form onSubmit={handleSubmitReview} style={{ marginBottom: '20px', padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
              <div style={{ marginBottom: '10px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>평점</label>
                <StarRating rating={newRating} interactive={true} onRate={setNewRating} />
              </div>
              <div style={{ marginBottom: '10px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>리뷰 내용</label>
                <textarea
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  placeholder="이 책에 대한 감상을 남겨주세요..."
                  style={{ width: '100%', minHeight: '80px', padding: '10px', borderRadius: '8px', border: 'none', background: 'rgba(255,255,255,0.1)', color: 'inherit', resize: 'vertical' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="btn btn-primary btn-sm">{editingReview ? '수정' : '등록'}</button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => { setShowReviewForm(false); setEditingReview(null); setNewRating(5); setNewContent(''); }}>취소</button>
              </div>
            </form>
          )}

          {loading ? (
            <p style={{ textAlign: 'center', opacity: 0.6 }}>로딩 중...</p>
          ) : reviews.length === 0 ? (
            <p style={{ textAlign: 'center', opacity: 0.6, padding: '20px' }}>아직 리뷰가 없습니다. 첫 리뷰를 작성해보세요!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {reviews.map(review => (
                <div key={review.review_id} style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <StarRating rating={review.rating} />
                      <span style={{ marginLeft: '10px', fontWeight: 'bold' }}>{review.user_name}</span>
                      <span style={{ marginLeft: '10px', fontSize: '0.8rem', opacity: 0.5 }}>
                        {new Date(review.created_at).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                    {user?.user_id === review.user_id && (
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button className="btn btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => handleEditReview(review)}>수정</button>
                        <button className="btn btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem', color: '#ff6b6b' }} onClick={() => handleDeleteReview(review.review_id)}>삭제</button>
                      </div>
                    )}
                  </div>
                  {review.content && <p style={{ marginTop: '8px', opacity: 0.85 }}>{review.content}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ==================== Chatbot Component ====================
function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '안녕하세요! IBD Library AI 사서입니다. 🤖\n무엇을 도와드릴까요?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })

      if (res.ok) {
        const data = await res.json()
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: '죄송합니다, 응답을 처리하는 중 오류가 발생했습니다.' }])
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: '네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating Button */}
      <button
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--primary), var(--accent))',
          border: 'none',
          cursor: 'pointer',
          fontSize: '1.8rem',
          boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
          zIndex: 1000,
          transition: 'transform 0.3s'
        }}
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div
          className="chatbot-window glass"
          style={{
            position: 'fixed',
            bottom: '90px',
            right: '20px',
            width: '350px',
            height: '500px',
            borderRadius: '20px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            zIndex: 999,
            boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
          }}
        >
          {/* Header */}
          <div style={{ padding: '15px 20px', background: 'rgba(139, 92, 246, 0.2)', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <h3 style={{ margin: 0, fontSize: '1rem' }}>🤖 AI 사서</h3>
            <p style={{ margin: '5px 0 0', fontSize: '0.8rem', opacity: 0.7 }}>도서관 질문에 답변해드립니다</p>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  background: msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.1)',
                  padding: '10px 14px',
                  borderRadius: msg.role === 'user' ? '15px 15px 5px 15px' : '15px 15px 15px 5px',
                  maxWidth: '80%',
                  fontSize: '0.9rem',
                  lineHeight: 1.4,
                  whiteSpace: 'pre-wrap'
                }}
              >
                {msg.content}
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: 'flex-start', opacity: 0.6, fontSize: '0.9rem' }}>⏳ 생각 중...</div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={sendMessage} style={{ padding: '15px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="질문을 입력하세요..."
              disabled={loading}
              style={{
                flex: 1,
                padding: '10px 15px',
                borderRadius: '20px',
                border: 'none',
                background: 'rgba(255,255,255,0.1)',
                color: 'inherit',
                fontSize: '0.9rem'
              }}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              style={{
                padding: '10px 15px',
                borderRadius: '20px',
                border: 'none',
                background: 'var(--primary)',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              전송
            </button>
          </form>
        </div>
      )}
    </>
  )
}

// ==================== Main App ====================
function App() {
  const [user, setUser] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [profileModalOpen, setProfileModalOpen] = useState(false)
  const [configModalOpen, setConfigModalOpen] = useState(false)
  const [loansModalOpen, setLoansModalOpen] = useState(false)

  // 로컬 스토리지에서 사용자 정보 복원
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  const handleUpdateUser = (updatedUser) => {
    setUser(updatedUser)
    localStorage.setItem('user', JSON.stringify(updatedUser))
  }

  const handleDeleteUser = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  return (
    <div className="app">
      <Header
        user={user}
        onLogout={handleLogout}
        onLoginClick={() => setAuthModalOpen(true)}
        onProfileClick={() => setProfileModalOpen(true)}
        onConfigClick={() => setConfigModalOpen(true)}
        onLoansClick={() => setLoansModalOpen(true)}
      />
      <main>
        <Hero />
        <Stats />
        <BooksSection user={user} />
        <About />
        <Contact />
      </main>
      <Footer />

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onLogin={handleLogin}
      />

      <ProfileModal
        isOpen={profileModalOpen}
        onClose={() => setProfileModalOpen(false)}
        user={user}
        onUpdate={handleUpdateUser}
        onDelete={handleDeleteUser}
      />

      <AdminConfigModal
        isOpen={configModalOpen}
        onClose={() => setConfigModalOpen(false)}
        user={user}
      />

      <LoansModal
        isOpen={loansModalOpen}
        onClose={() => setLoansModalOpen(false)}
        user={user}
      />

      <Chatbot />
    </div>
  )
}

export default App
