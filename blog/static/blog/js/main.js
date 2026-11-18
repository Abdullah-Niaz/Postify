/* ==========================================================================
   POSTIFY — "THE LIVING JOURNAL"
   Client Controller & Interactive Behaviors
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initBookmarking();
  initVoting();
  initDeletion();
  initCommentSubmission();
  initReadingCompanion();
  initAuthoringStudio();
  initShareAction();
});

/* ==========================================================================
   1. Editorial Toast / Snackbar
   ========================================================================== */
function showMessage(message, iconClass = 'fa-solid fa-feather-pointed') {
  const snackbar = document.getElementById('snackbar');
  if (!snackbar) return;

  snackbar.innerHTML = `<i class="${iconClass}"></i> <span>${escapeHtml(message)}</span>`;
  snackbar.className = 'show';

  // Clear existing timer if any
  if (snackbar.hideTimeout) {
    clearTimeout(snackbar.hideTimeout);
  }

  snackbar.hideTimeout = setTimeout(() => {
    snackbar.className = snackbar.className.replace('show', '');
  }, 3000);
}

/* Safe HTML escaping helper */
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/* Get CSRF Token Helper */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/* ==========================================================================
   2. Bookmarking System
   ========================================================================== */
function initBookmarking() {
  const saveBtns = document.querySelectorAll('.save-btn, .save');
  if (!saveBtns || saveBtns.length === 0) return;

  saveBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const articleId = btn.dataset.id || btn.id;
      if (!articleId || btn.disabled) return;
      btn.disabled = true;
      btn.setAttribute('aria-busy', 'true');

      const url = `/save/${articleId}`;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
      })
        .then((res) => {
          if (!res.ok) throw new Error('Network error');
          return res.json();
        })
        .then((data) => {
          const isSaved = data.saved !== undefined ? data.saved : (data.message !== 'removed');
          
          // Update all instances of this bookmark button on page (e.g. hero & sidebar)
          const matchedBtns = Array.from(saveBtns).filter(b => (b.dataset.id || b.id) === articleId);
          matchedBtns.forEach((b) => {
            b.setAttribute('aria-pressed', String(isSaved));
            b.setAttribute('aria-label', isSaved ? 'Remove from reading list' : 'Save story');
            const icon = b.querySelector('i');
            const label = b.querySelector('.action-btn-label, .save-txt');
            const checkIndicator = b.querySelector('.check-indicator');

            if (isSaved) {
              b.classList.add('saved');
              if (icon) {
                icon.className = 'fa-solid fa-bookmark' + (b.classList.contains('companion-action-btn') ? ' me-2' : '');
              }
              if (label) label.textContent = 'Saved';
              if (checkIndicator) checkIndicator.classList.remove('d-none');
            } else {
              b.classList.remove('saved');
              if (icon) {
                icon.className = 'fa-regular fa-bookmark' + (b.classList.contains('companion-action-btn') ? ' me-2' : '');
              }
              if (label) label.textContent = b.classList.contains('companion-action-btn') ? 'Bookmark' : 'Save';
              if (checkIndicator) checkIndicator.classList.add('d-none');
            }
          });

          if (isSaved) {
            showMessage('Dispatch saved to your Reading List', 'fa-solid fa-bookmark');
          } else {
            showMessage('Removed from your Reading List', 'fa-regular fa-bookmark');
          }
        })
        .catch((err) => {
          console.error('Bookmark error:', err);
          showMessage('Unable to update bookmark. Please verify sign-in.', 'fa-solid fa-circle-exclamation');
        }).finally(() => {
          btn.disabled = false;
          btn.removeAttribute('aria-busy');
        });
    });
  });
}

/* ==========================================================================
   3. Upvoting System
   ========================================================================== */
function initVoting() {
  const voteBtns = document.querySelectorAll('.vote-btn, .vote');
  if (!voteBtns || voteBtns.length === 0) return;

  voteBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const articleId = btn.dataset.id || btn.dataset.vote;
      if (!articleId || btn.disabled) return;
      btn.disabled = true;
      btn.setAttribute('aria-busy', 'true');

      const url = `/vote/${articleId}`;

      fetch(url, {
        method: 'PUT',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
      })
        .then((res) => {
          if (!res.ok) throw new Error('Network error');
          return res.json();
        })
        .then((data) => {
          const isVoted = data.voted !== undefined ? data.voted : (data.messege === 'upvote' || data.message === 'upvote');
          const count = data.count;

          // Update matching buttons across page
          const matched = document.querySelectorAll(`.vote-btn[data-id="${articleId}"], .vote[data-vote="${articleId}"]`);
          matched.forEach((b) => {
            b.setAttribute('aria-pressed', String(isVoted));
            b.setAttribute('aria-label', isVoted ? 'Remove upvote' : 'Upvote story');
            const countEl = b.querySelector('.vote-count, .vote-num');
            if (countEl && count !== undefined) {
              countEl.textContent = count;
            }
            if (isVoted) {
              b.classList.add('voted');
            } else {
              b.classList.remove('voted');
            }
          });

          if (isVoted) {
            showMessage('Upvoted dispatch', 'fa-solid fa-arrow-up');
          } else {
            showMessage('Upvote rescinded', 'fa-solid fa-arrow-down');
          }
        })
        .catch((err) => {
          console.error('Vote error:', err);
          showMessage('Unable to record vote. Please check your connection.', 'fa-solid fa-circle-exclamation');
        }).finally(() => {
          btn.disabled = false;
          btn.removeAttribute('aria-busy');
        });
    });
  });
}

/* ==========================================================================
   4. Deletion with Confirmation
   ========================================================================== */
function initDeletion() {
  const deleteBtns = document.querySelectorAll('.delete-btn, .delete');
  if (!deleteBtns || deleteBtns.length === 0) return;

  deleteBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const articleId = btn.dataset.id || btn.dataset.delete;
      if (!articleId) return;

      const parentCard = document.querySelector(`[data-card="${articleId}"]`);

      swal({
        title: 'Retract this dispatch?',
        text: 'This will permanently remove this article from the Living Journal archives.',
        icon: 'warning',
        buttons: ['Preserve Entry', 'Retract Dispatch'],
        dangerMode: true,
      }).then((confirmed) => {
        if (confirmed) {
          fetch(`/delete/${articleId}`, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': getCookie('csrftoken') || '',
            },
          })
            .then((res) => res.json())
            .then((data) => {
              if (data.message === 'deleted') {
                swal('Dispatch Retracted', 'The article has been expunged from the archives.', 'success')
                  .then(() => {
                    if (parentCard) {
                      parentCard.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                      parentCard.style.opacity = '0';
                      parentCard.style.transform = 'translateY(10px)';
                      setTimeout(() => parentCard.remove(), 400);
                    } else {
                      window.location.href = '/';
                    }
                  });
              } else {
                swal('Retraction Failed', 'Could not delete article. Authorization required.', 'error');
              }
            })
            .catch(() => {
              swal('Error', 'Server communication failure.', 'error');
            });
        }
      });
    });
  });
}

/* ==========================================================================
   5. Secure Discussion & Comment Submission
   ========================================================================== */
function initCommentSubmission() {
  const commentForm = document.getElementById('comment-form');
  const commentBtn = document.getElementById('add-comment');
  const commentInput = document.getElementById('comment-content');
  const commentsStream = document.querySelector('.comments-stream, .all-comments');
  const commentCountEl = document.getElementById('comment-count');
  const noCommentSlate = document.getElementById('no-comment');

  if (!commentForm && !commentBtn) return;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!commentInput) return;

    const content = commentInput.value.trim();
    if (!content) return;

    const articleId = (commentForm && commentForm.dataset.articleId) ||
                      (commentBtn && commentBtn.dataset.comment);
    if (!articleId) return;

    if (commentBtn) {
      commentBtn.disabled = true;
      commentBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Inscribing…';
    }

    fetch(`/articles/comment/${articleId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken') || '',
      },
      body: JSON.stringify({ comment: content }),
    })
      .then((res) => {
        if (!res.ok) throw new Error('Submission failed');
        return res.json();
      })
      .then((data) => {
        if (noCommentSlate) {
          noCommentSlate.remove();
        }

        // Construct new comment card safely via DOM API (XSS prevention)
        const card = document.createElement('div');
        card.className = 'editorial-comment-card one-comment';

        const header = document.createElement('div');
        header.className = 'comment-card-header';

        const authorBadge = document.createElement('div');
        authorBadge.className = 'comment-author-badge';

        const avatar = document.createElement('span');
        avatar.className = 'comment-avatar';
        avatar.textContent = (data.owner || 'A').slice(0, 1).toUpperCase();

        const authorName = document.createElement('span');
        authorName.className = 'comment-author-name';
        authorName.textContent = '@' + data.owner;

        authorBadge.appendChild(avatar);
        authorBadge.appendChild(authorName);

        const timestamp = document.createElement('time');
        timestamp.className = 'comment-timestamp';
        timestamp.textContent = data.created || 'Just now';

        header.appendChild(authorBadge);
        header.appendChild(timestamp);

        const body = document.createElement('div');
        body.className = 'comment-body content';

        const p = document.createElement('p');
        p.textContent = data.content;
        body.appendChild(p);

        card.appendChild(header);
        card.appendChild(body);

        if (commentsStream) {
          commentsStream.insertBefore(card, commentsStream.firstChild);
        }

        if (commentCountEl && data.numbComments !== undefined) {
          commentCountEl.textContent = data.numbComments;
        }

        commentInput.value = '';
        showMessage('Perspective published to discussion', 'fa-solid fa-comment-check');
      })
      .catch((err) => {
        console.error('Comment error:', err);
        showMessage('Failed to publish comment. Please try again.', 'fa-solid fa-triangle-exclamation');
      })
      .finally(() => {
        if (commentBtn) {
          commentBtn.disabled = false;
          commentBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Publish Comment';
        }
      });
  };

  if (commentForm) {
    commentForm.addEventListener('submit', handleSubmit);
  } else if (commentBtn) {
    commentBtn.addEventListener('click', handleSubmit);
  }
}

/* ==========================================================================
   6. Reading Companion: Progress Bar & Dynamic Table of Contents
   ========================================================================== */
function initReadingCompanion() {
  const progressBar = document.getElementById('reading-progress-bar');
  const percentEl = document.getElementById('reading-progress-percent');
  const proseContainer = document.getElementById('article-prose');
  const readingTimeEl = document.getElementById('reading-time-estimate');

  if (proseContainer) {
    // 1. Reading Time Estimation
    const wordCount = proseContainer.textContent.trim().split(/\s+/).length;
    const minutes = Math.max(1, Math.ceil(wordCount / 210));
    if (readingTimeEl) {
      readingTimeEl.innerHTML = `<i class="fa-regular fa-clock me-1"></i> ${minutes} min read`;
    }

    // 2. Dynamic Table of Contents (TOC)
    const headings = proseContainer.querySelectorAll('h2, h3');
    const tocContainer = document.getElementById('toc-container');
    const tocList = document.getElementById('toc-list');

    if (headings.length >= 2 && tocContainer && tocList) {
      tocList.innerHTML = '';
      headings.forEach((h, index) => {
        // Ensure heading has an ID
        if (!h.id) {
          h.id = 'section-' + (index + 1) + '-' + h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-');
        }

        const li = document.createElement('li');
        li.className = 'toc-item' + (h.tagName === 'H3' ? ' sub-item' : '');

        const a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent;

        li.appendChild(a);
        tocList.appendChild(li);
      });

      tocContainer.style.display = 'block';
    }

    // 3. Scroll Reading Progress Tracking
    const updateProgress = () => {
      const rect = proseContainer.getBoundingClientRect();
      const totalHeight = proseContainer.offsetHeight;
      const windowHeight = window.innerHeight;

      // Calculate how far past the start of the prose we've scrolled
      const scrolled = windowHeight - rect.top;
      let percent = Math.min(100, Math.max(0, Math.round((scrolled / (totalHeight + windowHeight * 0.4)) * 100)));

      if (rect.bottom < windowHeight) {
        percent = 100;
      }
      if (rect.top > 0) {
        percent = Math.min(100, Math.max(0, Math.round(((windowHeight - rect.top) / totalHeight) * 100)));
      }

      if (progressBar) progressBar.style.width = percent + '%';
      if (percentEl) percentEl.textContent = percent;
    };

    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }
}

/* ==========================================================================
   7. Authoring Studio: Live Image & Markdown Preview
   ========================================================================== */
function initAuthoringStudio() {
  // Live Image File Preview
  const imageInput = document.querySelector('input[type="file"][name="artImage"]');
  const previewWrapper = document.getElementById('image-preview-container');
  const previewImg = document.getElementById('image-preview-element');

  if (imageInput && previewWrapper && previewImg) {
    imageInput.addEventListener('change', () => {
      const file = imageInput.files && imageInput.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          previewWrapper.classList.add('active');
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Markdown Editor vs Live Preview Tabs
  const tabWrite = document.getElementById('tab-write');
  const tabPreview = document.getElementById('tab-preview');
  const writePane = document.getElementById('editor-write-pane');
  const previewPane = document.getElementById('editor-preview-pane');
  const contentInput = document.querySelector('textarea[name="content"]');
  const previewContent = document.getElementById('rendered-preview-content');

  if (tabWrite && tabPreview && writePane && previewPane && contentInput) {
    tabWrite.addEventListener('click', () => {
      tabWrite.classList.add('active');
      tabWrite.setAttribute('aria-selected', 'true');
      tabPreview.classList.remove('active');
      tabPreview.setAttribute('aria-selected', 'false');

      writePane.style.display = 'block';
      previewPane.classList.remove('active');
    });

    tabPreview.addEventListener('click', () => {
      tabPreview.classList.add('active');
      tabPreview.setAttribute('aria-selected', 'true');
      tabWrite.classList.remove('active');
      tabWrite.setAttribute('aria-selected', 'false');

      writePane.style.display = 'none';
      previewPane.classList.add('active');

      // Simple, safe client-side Markdown rendering
      const rawText = contentInput.value;
      if (previewContent) {
        if (!rawText.trim()) {
          previewContent.innerHTML = '<em>No manuscript prose written yet. Switch back to Editor to compose.</em>';
        } else {
          previewContent.innerHTML = renderMarkdownClient(rawText);
        }
      }
    });
  }
}

/* Client-Side Lightweight Markdown Formatter */
function renderMarkdownClient(md) {
  let html = escapeHtml(md);

  // Headers (## Header)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Blockquotes (> Quote)
  html = html.replace(/^\> (.*$)/gim, '<blockquote><p>$1</p></blockquote>');

  // Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

  // Code blocks (```code```)
  html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');

  // Inline code (`code`)
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

  // Paragraphs
  const paragraphs = html.split(/\n\s*\n/);
  return paragraphs
    .map((p) => {
      const trimmed = p.trim();
      if (!trimmed) return '';
      if (trimmed.startsWith('<h') || trimmed.startsWith('<blockquote') || trimmed.startsWith('<pre')) {
        return trimmed;
      }
      return `<p>${trimmed.replace(/\n/g, '<br/>')}</p>`;
    })
    .join('');
}

/* ==========================================================================
   8. Copy Share Link Action
   ========================================================================== */
function initShareAction() {
  const shareBtn = document.getElementById('btn-copy-share');
  if (!shareBtn) return;

  shareBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const url = window.location.href;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url)
        .then(() => {
          showMessage('Dispatch link copied to clipboard', 'fa-solid fa-link');
        })
        .catch(() => {
          showMessage('URL: ' + url, 'fa-solid fa-link');
        });
    } else {
      showMessage('URL: ' + url, 'fa-solid fa-link');
    }
  });
}
