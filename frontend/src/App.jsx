import { useState } from 'react'
import './App.css'

// Sample book data
const sampleBooks = [
  { id: 1, title: '클린 코드', author: '로버트 C. 마틴', category: '프로그래밍', available: true, cover: '📘' },
  { id: 2, title: '디자인 패턴', author: 'GoF', category: '프로그래밍', available: true, cover: '📗' },
  { id: 3, title: '리팩터링', author: '마틴 파울러', category: '프로그래밍', available: false, cover: '📙' },
  { id: 4, title: '도메인 주도 설계', author: '에릭 에반스', category: '아키텍처', available: true, cover: '📕' },
  { id: 5, title: '실용주의 프로그래머', author: '데이비드 토머스', category: '프로그래밍', available: true, cover: '📔' },
  { id: 6, title: '소프트웨어 장인', author: '산드로 만쿠소', category: '커리어', available: false, cover: '📓' },
]

// Header Component
function Header() {
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
        <button className="btn btn-primary">로그인</button>
      </div>
    </header>
  )
}

// Hero Component
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

// Stats Component
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

// Search Component
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

// Book Card Component
function BookCard({ book }) {
  return (
    <div className="book-card card">
      <div className="book-cover">
        <span className="book-emoji">{book.cover}</span>
      </div>
      <div className="book-info">
        <h3 className="book-title">{book.title}</h3>
        <p className="book-author">{book.author}</p>
        <div className="book-meta">
          <span className="book-category">{book.category}</span>
          <span className={`book-status ${book.available ? 'available' : 'unavailable'}`}>
            {book.available ? '대출 가능' : '대출 중'}
          </span>
        </div>
      </div>
      <button className={`btn ${book.available ? 'btn-primary' : 'btn-secondary'}`} disabled={!book.available}>
        {book.available ? '대출하기' : '예약하기'}
      </button>
    </div>
  )
}

// Books Section
function BooksSection() {
  const [searchTerm, setSearchTerm] = useState('')
  
  const filteredBooks = sampleBooks.filter(book =>
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <section id="books" className="books-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">📖 도서 목록</h2>
          <p className="section-description">원하는 책을 검색하고 대출해보세요</p>
        </div>
        <SearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
        <div className="books-grid">
          {filteredBooks.map((book, index) => (
            <div key={book.id} style={{ animationDelay: `${index * 0.1}s` }} className="animate-fade-in">
              <BookCard book={book} />
            </div>
          ))}
        </div>
        {filteredBooks.length === 0 && (
          <div className="no-results">
            <span className="no-results-icon">🔍</span>
            <p>검색 결과가 없습니다</p>
          </div>
        )}
      </div>
    </section>
  )
}

// Footer Component
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

// Main App
function App() {
  return (
    <div className="app">
      <Header />
      <main>
        <Hero />
        <Stats />
        <BooksSection />
      </main>
      <Footer />
    </div>
  )
}

export default App
