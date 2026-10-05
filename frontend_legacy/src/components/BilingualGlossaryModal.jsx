import React, { useState, useEffect } from 'react';
import {
  fetchGlossaryTerms,
  fetchGlossaryCategories,
  fetchGlossaryExamples,
} from '../services/api';
import {
  BookOpen,
  Search,
  X,
  Copy,
  Check,
  Sparkles,
  ExternalLink,
  Layers,
  ArrowRight,
} from 'lucide-react';

export default function BilingualGlossaryModal({ isOpen, onClose, onSelectExample }) {
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);
  const [terms, setTerms] = useState([]);
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('terms'); // 'terms' | 'examples'
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    if (!isOpen) return;

    // Load categories and examples once when opened
    fetchGlossaryCategories().then(setCategories).catch(console.error);
    fetchGlossaryExamples().then(setExamples).catch(console.error);
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;

    setLoading(true);
    const debounce = setTimeout(() => {
      fetchGlossaryTerms(query, selectedCategory)
        .then((data) => {
          setTerms(data?.terms || []);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    }, 200);

    return () => clearTimeout(debounce);
  }, [isOpen, query, selectedCategory]);

  if (!isOpen) return null;

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1800);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="glossary-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* Modal Header */}
        <div className="glossary-modal-header">
          <div className="glossary-title-group">
            <div className="glossary-icon-badge">
              <BookOpen size={20} />
            </div>
            <div>
              <h2 className="glossary-title">ពាក្យគន្លឹះគណិតវិទ្យា (Bilingual Math Glossary)</h2>
              <p className="glossary-subtitle">
                ស្តង់ដារបាក់ឌុប BacII & CSCA — លោកគ្រូ ជាង សុខគង់ (CHEANG SOKKONG)
              </p>
            </div>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* View Toggle Tabs */}
        <div className="glossary-view-tabs">
          <button
            type="button"
            className={`glossary-tab ${activeTab === 'terms' ? 'active' : ''}`}
            onClick={() => setActiveTab('terms')}
          >
            <Layers size={16} />
            <span>ពាក្យគន្លឹះទាំងអស់ ({terms.length})</span>
          </button>
          <button
            type="button"
            className={`glossary-tab ${activeTab === 'examples' ? 'active' : ''}`}
            onClick={() => setActiveTab('examples')}
          >
            <Sparkles size={16} />
            <span>ឧទាហរណ៍ក្នុងប្រឡង (Exam Examples)</span>
          </button>
        </div>

        {activeTab === 'terms' ? (
          <>
            {/* Search and Category Filter */}
            <div className="glossary-filter-section">
              <div className="glossary-search-box">
                <Search size={18} className="search-icon" />
                <input
                  type="text"
                  placeholder="ស្វែងរកជាភាសាខ្មែរ ឬ អង់គ្លេស... (ឧ. sequence, ស្វ៊ីត, limit, គណនា, derivative)"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  autoFocus
                />
                {query && (
                  <button
                    type="button"
                    className="clear-query-btn"
                    onClick={() => setQuery('')}
                  >
                    <X size={16} />
                  </button>
                )}
              </div>

              {/* Category Chips */}
              <div className="category-chips">
                <button
                  type="button"
                  className={`chip ${selectedCategory === '' ? 'active' : ''}`}
                  onClick={() => setSelectedCategory('')}
                >
                  ទាំងអស់ (All)
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    className={`chip ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Terms List Grid */}
            <div className="glossary-terms-scroll">
              {loading ? (
                <div className="glossary-loading">
                  <div className="spinner"></div>
                  <span>កំពុងទាញយកទិន្នន័យ...</span>
                </div>
              ) : terms.length === 0 ? (
                <div className="glossary-empty">
                  <p>រកមិនឃើញពាក្យដែលត្រូវនឹង "{query}" ទេ</p>
                  <small>សូមសាកល្បងស្វែងរកដោយប្រើពាក្យផ្សេង</small>
                </div>
              ) : (
                <div className="terms-grid">
                  {terms.map((item, idx) => (
                    <div key={`${item.english}-${idx}`} className="term-card">
                      <div className="term-card-header">
                        <span className="term-category-badge">{item.category}</span>
                        {item.symbol && (
                          <span
                            className="term-symbol-badge"
                            title="Click to copy symbol"
                            onClick={() => handleCopy(item.symbol, `sym-${idx}`)}
                          >
                            {item.symbol}
                          </span>
                        )}
                      </div>

                      <div className="term-names">
                        <div className="term-khmer">{item.khmer}</div>
                        <div className="term-english">{item.english}</div>
                      </div>

                      {item.explanation && (
                        <p className="term-explanation">{item.explanation}</p>
                      )}

                      <div className="term-actions">
                        <button
                          type="button"
                          className="copy-term-btn"
                          onClick={() =>
                            handleCopy(`${item.english} = ${item.khmer}`, `card-${idx}`)
                          }
                          title="ចម្លងពាក្យទាំងពីរ"
                        >
                          {copiedId === `card-${idx}` ? (
                            <>
                              <Check size={14} className="text-success" />
                              <span>បានចម្លង</span>
                            </>
                          ) : (
                            <>
                              <Copy size={14} />
                              <span>ចម្លង</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          /* Exam Examples Tab */
          <div className="glossary-examples-scroll">
            <div className="examples-header-banner">
              <h3>របៀបប្រើប្រាស់ពាក្យបញ្ជាក្នុងប្រធានលំហាត់ថ្នាក់ទី ១២ បាក់ឌុប</h3>
              <p>
                ចុចលើប៊ូតុង "ដោះស្រាយក្នុង Math Lab" ដើម្បីសាកល្បងដោះស្រាយលំហាត់គំរូភ្លាមៗ!
              </p>
            </div>

            <div className="examples-list">
              {examples.map((ex, i) => (
                <div key={i} className="example-item-card">
                  <div className="example-topic-pill">{ex.topic}</div>
                  <div className="example-bilingual-content">
                    <div className="example-en">
                      <span className="lang-tag">EN:</span>
                      <span>{ex.english}</span>
                    </div>
                    <div className="example-km">
                      <span className="lang-tag">ខ្មែរ:</span>
                      <span>{ex.khmer}</span>
                    </div>
                  </div>
                  {onSelectExample && (
                    <button
                      type="button"
                      className="use-example-btn"
                      onClick={() => {
                        onSelectExample(ex.khmer);
                        onClose();
                      }}
                    >
                      <span>ដោះស្រាយក្នុង Solver</span>
                      <ArrowRight size={15} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Modal Footer */}
        <div className="glossary-modal-footer">
          <div className="glossary-source-attribution">
            <span>ប្រភព៖ </span>
            <a
              href="https://www.edu-ikh.com/2026/02/english-khmer.html"
              target="_blank"
              rel="noreferrer"
            >
              EDU-IKH Math Terminology (Cheang Sokkong)
              <ExternalLink size={12} style={{ marginLeft: 4 }} />
            </a>
          </div>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            បិទ (Close)
          </button>
        </div>
      </div>
    </div>
  );
}
