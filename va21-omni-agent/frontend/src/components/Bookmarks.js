import React, { useState, useEffect, useCallback } from 'react';
import './Bookmarks.css';

const Bookmarks = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newBookmark, setNewBookmark] = useState({ title: '', url: '', category: 'General', tags: '' });
  const [editingId, setEditingId] = useState(null);

  const categories = ['General', 'Research', 'Security', 'Development', 'Documentation', 'Tools'];

  useEffect(() => {
    // Load bookmarks from localStorage
    const saved = localStorage.getItem('va21-bookmarks');
    if (saved) {
      setBookmarks(JSON.parse(saved));
    }
  }, []);

  const saveBookmarks = useCallback((newBookmarks) => {
    localStorage.setItem('va21-bookmarks', JSON.stringify(newBookmarks));
    setBookmarks(newBookmarks);
  }, []);

  const addBookmark = (e) => {
    e.preventDefault();
    const bookmark = {
      id: Date.now().toString(),
      title: newBookmark.title,
      url: newBookmark.url,
      category: newBookmark.category,
      tags: newBookmark.tags.split(',').map(t => t.trim()).filter(t => t),
      createdAt: new Date().toISOString(),
      favicon: getFaviconUrl(newBookmark.url)
    };

    if (editingId) {
      const updated = bookmarks.map(b => b.id === editingId ? { ...bookmark, id: editingId } : b);
      saveBookmarks(updated);
      setEditingId(null);
    } else {
      saveBookmarks([...bookmarks, bookmark]);
    }

    setNewBookmark({ title: '', url: '', category: 'General', tags: '' });
    setShowAddModal(false);
  };

  const deleteBookmark = (id) => {
    const updated = bookmarks.filter(b => b.id !== id);
    saveBookmarks(updated);
  };

  const editBookmark = (bookmark) => {
    setNewBookmark({
      title: bookmark.title,
      url: bookmark.url,
      category: bookmark.category,
      tags: bookmark.tags.join(', ')
    });
    setEditingId(bookmark.id);
    setShowAddModal(true);
  };

  const getFaviconUrl = (url) => {
    try {
      const domain = new URL(url).hostname;
      // Use DuckDuckGo's privacy-respecting favicon service instead of Google
      return `https://icons.duckduckgo.com/ip3/${domain}.ico`;
    } catch {
      return null;
    }
  };

  const filteredBookmarks = bookmarks.filter(b => 
    b.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.url.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const groupedBookmarks = filteredBookmarks.reduce((acc, bookmark) => {
    if (!acc[bookmark.category]) {
      acc[bookmark.category] = [];
    }
    acc[bookmark.category].push(bookmark);
    return acc;
  }, {});

  const openUrl = (url) => {
    if (window.electronAPI?.openExternal) {
      window.electronAPI.openExternal(url);
    } else {
      window.open(url, '_blank');
    }
  };

  return (
    <div className="bookmarks-container">
      <div className="bookmarks-header">
        <h2>🔖 Bookmarks</h2>
        <div className="bookmarks-actions">
          <input
            type="text"
            placeholder="Search bookmarks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bookmarks-search"
          />
          <button className="add-bookmark-btn" onClick={() => setShowAddModal(true)}>
            + Add Bookmark
          </button>
        </div>
      </div>

      <div className="bookmarks-stats">
        <div className="stat-item">
          <span className="stat-value">{bookmarks.length}</span>
          <span className="stat-label">Total Bookmarks</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{Object.keys(groupedBookmarks).length}</span>
          <span className="stat-label">Categories</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">
            {bookmarks.reduce((acc, b) => acc + b.tags.length, 0)}
          </span>
          <span className="stat-label">Tags</span>
        </div>
      </div>

      <div className="bookmarks-content">
        {Object.keys(groupedBookmarks).length === 0 ? (
          <div className="bookmarks-empty">
            <span className="empty-icon">🔖</span>
            <h3>No bookmarks yet</h3>
            <p>Add your first bookmark to get started</p>
            <button onClick={() => setShowAddModal(true)}>Add Bookmark</button>
          </div>
        ) : (
          Object.entries(groupedBookmarks).map(([category, items]) => (
            <div key={category} className="bookmark-category">
              <h3 className="category-title">
                <span className="category-icon">📁</span>
                {category}
                <span className="category-count">{items.length}</span>
              </h3>
              <div className="bookmark-grid">
                {items.map(bookmark => (
                  <div key={bookmark.id} className="bookmark-card">
                    <div className="bookmark-card-header">
                      {bookmark.favicon && (
                        <img 
                          src={bookmark.favicon} 
                          alt="" 
                          className="bookmark-favicon"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      )}
                      <span className="bookmark-title">{bookmark.title}</span>
                    </div>
                    <div className="bookmark-url" title={bookmark.url}>
                      {bookmark.url.length > 40 ? bookmark.url.substring(0, 40) + '...' : bookmark.url}
                    </div>
                    {bookmark.tags.length > 0 && (
                      <div className="bookmark-tags">
                        {bookmark.tags.map((tag, i) => (
                          <span key={i} className="bookmark-tag">{tag}</span>
                        ))}
                      </div>
                    )}
                    <div className="bookmark-actions">
                      <button onClick={() => openUrl(bookmark.url)} title="Open">
                        🔗
                      </button>
                      <button onClick={() => editBookmark(bookmark)} title="Edit">
                        ✏️
                      </button>
                      <button onClick={() => deleteBookmark(bookmark.id)} title="Delete">
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {showAddModal && (
        <div className="bookmark-modal-overlay" onClick={() => { setShowAddModal(false); setEditingId(null); }}>
          <div className="bookmark-modal" onClick={e => e.stopPropagation()}>
            <h3>{editingId ? 'Edit Bookmark' : 'Add New Bookmark'}</h3>
            <form onSubmit={addBookmark}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={newBookmark.title}
                  onChange={(e) => setNewBookmark({...newBookmark, title: e.target.value})}
                  placeholder="Bookmark title"
                  required
                />
              </div>
              <div className="form-group">
                <label>URL</label>
                <input
                  type="url"
                  value={newBookmark.url}
                  onChange={(e) => setNewBookmark({...newBookmark, url: e.target.value})}
                  placeholder="https://example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select
                  value={newBookmark.category}
                  onChange={(e) => setNewBookmark({...newBookmark, category: e.target.value})}
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Tags (comma-separated)</label>
                <input
                  type="text"
                  value={newBookmark.tags}
                  onChange={(e) => setNewBookmark({...newBookmark, tags: e.target.value})}
                  placeholder="security, research, ai"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => { setShowAddModal(false); setEditingId(null); }}>
                  Cancel
                </button>
                <button type="submit" className="primary">
                  {editingId ? 'Save Changes' : 'Add Bookmark'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Bookmarks;
