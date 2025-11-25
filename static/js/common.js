/**
 * Общие утилиты для AI Code Agent
 */

// ============================================
// Управление темой
// ============================================

const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        this.setupToggle();
        this.updateHighlightTheme(savedTheme);
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateIcon(theme);
        this.updateHighlightTheme(theme);
    },

    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },

    updateIcon(theme) {
        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            const icon = toggle.querySelector('.theme-icon');
            if (icon) {
                icon.textContent = theme === 'dark' ? '☀️' : '🌙';
            } else {
                toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
            }
        }
    },

    setupToggle() {
        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggle());
        }
    },

    updateHighlightTheme(theme) {
        document.querySelectorAll('link[href*="highlight"]').forEach(link => {
            if (link.href.includes('github-dark')) {
                link.media = theme === 'dark' ? 'all' : 'not all';
            } else {
                link.media = theme === 'dark' ? 'not all' : 'all';
            }
        });
    }
};

// ============================================
// Markdown обработка
// ============================================

const MarkdownProcessor = {
    init() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && typeof hljs !== 'undefined' && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.warn('Ошибка подсветки синтаксиса:', err);
                        }
                    }
                    if (typeof hljs !== 'undefined') {
                        try {
                            return hljs.highlightAuto(code).value;
                        } catch (err) {
                            console.warn('Ошибка авто-подсветки:', err);
                        }
                    }
                    return code;
                },
                breaks: true,
                gfm: true,
                sanitize: false
            });
        }
    },

    parse(text) {
        if (typeof marked === 'undefined') {
            return escapeHtml(text);
        }
        try {
            return marked.parse(text);
        } catch (e) {
            console.error('Ошибка парсинга Markdown:', e);
            return escapeHtml(text);
        }
    },

    highlightCode(element) {
        if (typeof hljs === 'undefined') return;
        
        if (element && element.querySelectorAll) {
            element.querySelectorAll('pre code').forEach((block) => {
                try {
                    hljs.highlightElement(block);
                } catch (e) {
                    console.warn('Ошибка подсветки блока кода:', e);
                }
            });
        }
    }
};

// ============================================
// Утилиты
// ============================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showAlert(message, type = 'info', containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    if (!container) {
        // Создаем контейнер если его нет
        const newContainer = document.createElement('div');
        newContainer.id = containerId;
        newContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000; max-width: 400px;';
        document.body.appendChild(newContainer);
        return showAlert(message, type, containerId);
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, 5000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// Копирование в буфер обмена
// ============================================

const ClipboardManager = {
    async copyToClipboard(text) {
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
                return true;
            } else {
                // Fallback для старых браузеров
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.opacity = '0';
                document.body.appendChild(textArea);
                textArea.select();
                const success = document.execCommand('copy');
                document.body.removeChild(textArea);
                return success;
            }
        } catch (err) {
            console.error('Ошибка копирования:', err);
            return false;
        }
    },

    showCopyButton(preElement) {
        if (preElement.querySelector('.copy-btn')) return;
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '📋 Копировать';
        copyBtn.title = 'Копировать код';
        
        copyBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const code = preElement.querySelector('code') || preElement;
            const text = code.textContent || code.innerText;
            
            const success = await this.copyToClipboard(text);
            if (success) {
                copyBtn.innerHTML = '✅ Скопировано!';
                copyBtn.style.background = 'var(--success)';
                copyBtn.style.color = 'white';
                copyBtn.style.borderColor = 'var(--success)';
                
                setTimeout(() => {
                    copyBtn.innerHTML = '📋 Копировать';
                    copyBtn.style.background = '';
                    copyBtn.style.color = '';
                    copyBtn.style.borderColor = '';
                }, 2000);
            } else {
                copyBtn.innerHTML = '❌ Ошибка';
                setTimeout(() => {
                    copyBtn.innerHTML = '📋 Копировать';
                }, 2000);
            }
        });
        
        preElement.style.position = 'relative';
        preElement.appendChild(copyBtn);
    },

    init() {
        // Добавляем кнопки копирования ко всем блокам кода
        const observer = new MutationObserver((mutations) => {
            document.querySelectorAll('pre code, pre').forEach(pre => {
                if (!pre.querySelector('.copy-btn')) {
                    this.showCopyButton(pre);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Инициализация для существующих элементов
        document.querySelectorAll('pre code, pre').forEach(pre => {
            this.showCopyButton(pre);
        });
    }
};

// ============================================
// Улучшенные уведомления (Toast)
// ============================================

const ToastManager = {
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    },

    warning(message) {
        this.show(message, 'warning');
    },

    info(message) {
        this.show(message, 'info');
    }
};

// ============================================
// Горячие клавиши
// ============================================

const KeyboardShortcuts = {
    shortcuts: new Map(),
    
    register(key, callback, description = '') {
        this.shortcuts.set(key, { callback, description });
    },
    
    init() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyString(e);
            const shortcut = this.shortcuts.get(key);
            if (shortcut) {
                e.preventDefault();
                shortcut.callback(e);
            }
        });
    },
    
    getKeyString(e) {
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('Ctrl');
        if (e.shiftKey) parts.push('Shift');
        if (e.altKey) parts.push('Alt');
        parts.push(e.key);
        return parts.join('+');
    }
};

// ============================================
// Инициализация при загрузке
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    MarkdownProcessor.init();
    ClipboardManager.init();
    KeyboardShortcuts.init();
    
    // Регистрируем стандартные горячие клавиши
    KeyboardShortcuts.register('Ctrl+k', () => {
        const input = document.querySelector('#userInput, #chatInput');
        if (input) input.focus();
    }, 'Фокус на поле ввода');
    
    KeyboardShortcuts.register('Ctrl+/', () => {
        ThemeManager.toggle();
    }, 'Переключить тему');
});

// Добавляем CSS для анимации slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);

// Экспорт для использования в других скриптах
window.ThemeManager = ThemeManager;
window.MarkdownProcessor = MarkdownProcessor;
window.ClipboardManager = ClipboardManager;
window.ToastManager = ToastManager;
window.KeyboardShortcuts = KeyboardShortcuts;
window.escapeHtml = escapeHtml;
window.showAlert = showAlert;
window.formatBytes = formatBytes;
window.debounce = debounce;
window.throttle = throttle;
