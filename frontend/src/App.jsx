import { useState, useEffect } from 'react'
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

// ==================== Header Component ====================
function Header({ user, onLogout, onLoginClick, onProfileClick }) {
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
  return (
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
            <button className="btn btn-primary">
              <span>🔍</span> 도서 검색
            </button>
            <button className="btn btn-secondary">
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
  if (!isOpen || !book) return null

  const available = book.stock_quantity > 0
  const isLibrarian = user?.role === 'LIBRARIAN'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass book-detail-modal" onClick={(e) => e.stopPropagation()}>
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
      </div>
    </div>
  )
}

// ==================== Main App ====================
function App() {
  const [user, setUser] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [profileModalOpen, setProfileModalOpen] = useState(false)

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
      />
      <main>
        <Hero />
        <Stats />
        <BooksSection user={user} />
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
    </div>
  )
}

export default App
